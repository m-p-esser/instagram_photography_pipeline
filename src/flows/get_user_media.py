import datetime
import json
import time

import instagrapi
import pandas as pd
import pandera as pa
from google.cloud import storage
from instagrapi.types import Media, User
from prefect import flow, get_run_logger, task
from prefect.blocks.system import Secret
from prefect.task_runners import ConcurrentTaskRunner, SequentialTaskRunner
from prefect_gcp import GcpCredentials
from prefect_sqlalchemy import SqlAlchemyConnector

from src.google_cloud.client import (
    construct_gcs_client,
    upload_blob_from_dataframe,
    upload_blob_from_string,
)
from src.instagram.client import construct_instagrapi_client
from src.utils.config import (
    DataProcessingParams,
    InstagramRequestParams,
    SourceToTargetKeyMapping,
)
from src.utils.transform import blobs_to_dataframe


@task
def init_instagrapi_client(
    instagram_account: str, instagram_password: str
) -> instagrapi.Client:
    logger = get_run_logger()

    logger.info("Logging in to Instagram")
    instagrapi_client = construct_instagrapi_client(
        instagram_account, instagram_password
    )

    return instagrapi_client


@task
def init_gcs_client(gcp_credential_block_name: str) -> storage.Client:
    logger = get_run_logger()

    gcs_client = construct_gcs_client(gcp_credential_block_name)

    logger.info(
        f"Constructed GCS Client from GCP Credential Block: {gcp_credential_block_name}"
    )

    return gcs_client


@task
def get_user_ids_from_database(database_block_name: str) -> list[int]:
    logger = get_run_logger()

    TABLE_NAME = "`USER.user`"

    with SqlAlchemyConnector.load(database_block_name) as connector:
        logger.info(f"Connected to Database with Block name: {database_block_name}")
        logger.info(f"Quering {TABLE_NAME} Table")
        user_ids = connector.fetch_all(
            """
            SELECT user_id FROM USER.user
            """
        )

    logger.info(f"Returning {len(user_ids)} User IDs")

    user_ids = [i[0] for i in user_ids]

    return user_ids


@task
def get_media_data(
    instagrapi_client: instagrapi.Client,
    user_id: int,
    chunk_size: int,
    sleep_seconds_between_chunks: int = 2,
) -> list[Media]:
    logger = get_run_logger()

    medias = instagrapi_client.user_medias(
        user_id=user_id, amount=chunk_size, sleep=sleep_seconds_between_chunks
    )

    logger.info(f"Stored {len(medias)} Media object for User ID '{user_id}' in memory")

    return medias


@task
def store_raw_media_data(gcs_client: storage.Client, media: Media, bucket_name: str):
    logger = get_run_logger()

    media_id, user_id = media.pk, media.user.pk
    today = datetime.date.today()  # YYYY-MM-DD
    blob_name = f"media/{media_id}_{user_id}_{today}.json"
    logger.info(f"Blob that will be created will be named: {blob_name}")

    upload_blob_from_string(gcs_client, media, bucket_name, blob_name)

    logger.info(
        f"Uploaded Blob '{blob_name}' to Bucket '{bucket_name}' in Google Cloud Storage"
    )


@task
def get_media_data_to_be_transformed(
    gcs_client: storage.Client, date: str, prefix: str, bucket_name: str
) -> list[storage.blob.Blob]:
    logger = get_run_logger()

    logger.info(f"Loading list of blobs for data {date}")

    blobs = []

    blob_iterator = gcs_client.list_blobs(bucket_name)

    for blob in blob_iterator:
        if prefix in blob.name:
            if date in blob.name:
                if f"{prefix}/" != blob.name:  # Check if virtual Folder
                    blobs.append(blob)

    logger.info(f"{len(blobs)} Blobs in list")

    return blobs


@task
def media_data_to_df(
    gcs_client: storage.Client, blobs: list[storage.blob.Blob], keys: list[str]
) -> pd.DataFrame:
    logger = get_run_logger()

    logger.info(f"Starting to process {len(blobs)} Blob(s)")

    data_df = blobs_to_dataframe(gcs_client, blobs, keys)

    logger.info(f"Transformed {len(blobs)} Blob(s) to a Dataframe")
    logger.info(
        f"Created Dataframe with {data_df.shape[0]} Rows and {data_df.shape[1]} Columns"
    )
    logger.info(
        f"The created Dataframe contains the following columns: {data_df.columns}"
    )

    return data_df


@task
def transform_media_df(media_df: pd.DataFrame) -> pd.DataFrame:
    media_df["pk"] = media_df["pk"].astype("int64")
    media_df["user_id"] = media_df["user_id"].astype("int64")
    media_df["publication_datetime"] = pd.to_datetime(media_df["taken_at"])
    media_df["location_id"] = media_df["location"].apply(
        lambda x: x["location_id"] if isinstance(x, dict) else None
    )
    media_df.drop(columns=["taken_at", "location"], inplace=True)

    return media_df


@task
def validate_transformed_media_data(transformed_media_df: pd.DataFrame):
    """Validation for `MEDIA.media` table"""

    logger = get_run_logger()

    schema = pa.DataFrameSchema(
        {
            "pk": pa.Column(dtype=int, unique=True, report_duplicates="exclude_last"),
            "user_id": pa.Column(dtype=int),
            "location_id": pa.Column(dtype=str, nullable=True),
            "media_type": pa.Column(dtype=int, nullable=True),
            "title": pa.Column(dtype=str, nullable=True),
            "caption_text": pa.Column(dtype=str, nullable=True),
            "thumbnail_url": pa.Column(dtype=str, nullable=True),
            "product_type": pa.Column(dtype=str, nullable=True),
            "video_url": pa.Column(dtype=str, nullable=True),
            "video_duration": pa.Column(dtype=float, nullable=True),
            "comments_disabled": pa.Column(dtype=bool),
            # "publication_datetime": pa.Column(dtype=datetime64[ns]),
        }
    )
    logger.info(f"Validating with the following Schema: {schema}")
    schema.validate(transformed_media_df)
    logger.info("Dataframe has been validated successfully")


@task
def load_media_data_to_sql(
    transformed_media_df: pd.DataFrame,
    database_block_name: str,
    is_initial_data_ingestion: bool = False,
):
    logger = get_run_logger()

    logger.info(
        f"Dataframe that should be ingested, contains {transformed_media_df.shape[0]} rows"
    )
    data = transformed_media_df.to_dict(orient="records")

    TABLE_NAME = "`MEDIA.media`"

    with SqlAlchemyConnector.load(database_block_name) as connector:
        logger.info(f"Connected to Database with Block name: {database_block_name}")
        if is_initial_data_ingestion:
            logger.info(f"Truncating table: {TABLE_NAME}")
            connector.execute("SET FOREIGN_KEY_CHECKS = 0;")
            connector.execute(f"TRUNCATE TABLE {TABLE_NAME};")
            connector.execute("SET FOREIGN_KEY_CHECKS = 1;")
        logger.info(f"Writing to {TABLE_NAME} Table")
        connector.execute_many(
            """
            INSERT INTO MEDIA.media (media_id, user_id, location_id, media_type_id, title, caption, thumbnail_url, product_type, video_url, video_duration_seconds, has_comments_disabled, publication_date)
            VALUES (:pk, :user_id, :location_id, :media_type, :title, :caption_text, :thumbnail_url, :product_type, :video_url, :video_duration_seconds, :comments_disabled, :taken_at)
            ON DUPLICATE KEY UPDATE media_id=VALUES(media_id), user_id=VALUES(user_id), location_id=VALUES(location_id), media_type_id=VALUES(media_type_id), title=VALUES(title), caption=VALUES(caption), thumbnail_url=VALUES(thumbnail_url), product_type=VALUES(product_type), video_url=VALUES(video_url), video_duration_seconds=VALUES(video_duration_seconds), has_comments_disabled=VALUES(has_comments_disabled), publication_date=VALUES(publication_date)
            """,
            seq_of_parameters=data,
        )

    logger.info(
        f"Wrote {len(data)} rows to Database with Prefect Block name '{database_block_name}'"
    )


@flow(name="Get Raw Media Data", log_prints=True, task_runner=ConcurrentTaskRunner)
def store_raw_media_data_flow(
    instagram_account: str,
    instagram_password: str,
    gcp_credential_block_name: str,
    processing_params: DataProcessingParams,
    config: InstagramRequestParams,
):
    instagrapi_client = init_instagrapi_client(instagram_account, instagram_password)
    gcs_client = init_gcs_client(gcp_credential_block_name)
    user_ids = get_user_ids_from_database(processing_params.user_database_block_name)

    user_limit = config.media_data_user_limit
    chunk_size = config.media_data_chunk_size

    user_medias = {}

    for i in user_ids[0:user_limit]:
        medias = get_media_data(instagrapi_client, i, chunk_size)
        user_medias[i] = medias

    medias = user_medias[38578982]
    media = medias[0]

    store_raw_media_data(gcs_client, media, "instagram-raw")


@flow(name="Transform Media Data", log_prints=True, task_runner=SequentialTaskRunner)
def transform_media_data_flow(
    gcp_credential_block_name: str,
    mapping: SourceToTargetKeyMapping,
    processing_params: DataProcessingParams,
):
    gcs_client = init_gcs_client(gcp_credential_block_name)

    blobs = get_media_data_to_be_transformed(
        gcs_client, "2023-05-20", "media", "instagram-raw"
    )

    # Transformed data which will be stored in `MEDIA.media` later on
    media_df = media_data_to_df(gcs_client, blobs, mapping.media_keys)
    media_df = transform_media_df(media_df)
    validate_transformed_media_data(media_df)
    upload_blob_from_dataframe(gcs_client, media_df, "instagram-processed", "media")

    place_holder_df = pd.DataFrame()

    return (media_df, place_holder_df)


@flow(name="Store Final Media Data", log_prints=True, task_runner=SequentialTaskRunner)
def store_final_user_data_flow(
    transformed_media_dfs: tuple,
    processing_params: DataProcessingParams,
):
    media_df = transformed_media_dfs[0]
    load_media_data_to_sql(
        media_df,
        processing_params.user_database_block_name,
        processing_params.is_initial_data_ingestion,
    )


if __name__ == "__main__":
    store_raw_media_data_flow(
        instagram_account=Secret.load("instagram-account-username").get(),
        instagram_password=Secret.load("instagram-account-password").get(),
        gcp_credential_block_name="instagram-prefect-sa",
        processing_params=DataProcessingParams(),
        config=InstagramRequestParams(),
    )

    transformed_media_dfs = transform_media_data_flow(
        gcp_credential_block_name="instagram-prefect-sa",
        mapping=SourceToTargetKeyMapping(),
        processing_params=DataProcessingParams(),
    )

    store_final_user_data_flow(
        transformed_user_dfs=transformed_media_dfs,
        processing_params=DataProcessingParams(),
    )
