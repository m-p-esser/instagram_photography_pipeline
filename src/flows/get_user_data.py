import datetime
import json

import instagrapi
import pandas as pd
import pandera as pa
from google.cloud import storage
from instagrapi.types import User
from prefect import flow, get_run_logger, task
from prefect.blocks.system import Secret
from prefect.task_runners import ConcurrentTaskRunner, SequentialTaskRunner
from prefect_gcp import GcpCredentials
from prefect_sqlalchemy import SqlAlchemyConnector

from src.utils.config import (
    DataProcessingParams,
    InstagramRequestParams,
    SourceToTargetKeyMapping,
)
from src.utils.serializer import CustomJSONEncoder


@task
def init_instagrapi_client(
    instagram_account: str, instagram_password: str
) -> instagrapi.Client:
    logger = get_run_logger()

    instagrapi_client = instagrapi.Client()

    # CHALLENGE_EMAIL = Secret.load("instagram-mail-adress").get()
    # CHALLENGE_PASSWORD = Secret.load("instagram-mail-password").get()

    # # client.challenge_code_handler = challenge_resolver.challenge_code_handler
    # # client.change_password_handler = challenge_resolver.change_password_handler

    logger.info("Logging in to Instagram")
    sucessful = instagrapi_client.login(instagram_account, instagram_password)

    if not sucessful:
        raise Exception("Could not log in to Instagram")

    return instagrapi_client


@task
def init_gcs_client() -> storage.Client:
    logger = get_run_logger()

    gcp_credentials = GcpCredentials.load("instagram-prefect-sa")
    project_id = gcp_credentials.project
    logger.info(f"Loaded GCP Credentials: {gcp_credentials}")

    gcs_client = storage.Client(project=project_id)
    return gcs_client


@task
def get_user_data(
    instagrapi_client: instagrapi.Client, config: InstagramRequestParams
) -> list[User]:
    logger = get_run_logger()

    user_names = config.user_names
    logger.info(f"Processing {len(user_names)} Usernames")
    logger.info(f"Getting User Ids for the following Usernames: \n {user_names}")

    user_names = config.user_names
    users = []
    for i in user_names:
        logger.info(f"Getting User data for Username: {i}")
        try:
            user = instagrapi_client.user_info_by_username(i)
            users.append(user)
        except Exception as e:
            logger.error(
                f"Exception {e} occured while collecting User data for Username: {i}"
            )

    logger.info(f"Stored User Data for {len(users)} Usernames")

    return users


@task
def store_raw_user_data(gcs_client: storage.Client, user: User, bucket_name: str):
    logger = get_run_logger()

    gcs_bucket = gcs_client.get_bucket(bucket_name)

    user_id, user_name = user.pk, user.username
    today = datetime.date.today()  # YYYY-MM-DD
    blob_name = f"user/{user_id}_{user_name}_{today}.json"
    logger.info(f"Blob that will be created will be named: {blob_name}")

    user_json_string = json.dumps(user, cls=CustomJSONEncoder)
    blob = gcs_bucket.blob(blob_name)
    blob.upload_from_string(data=user_json_string, content_type="application/json")
    logger.info(
        f"Uploaded Blob '{blob_name}' to Bucket '{bucket_name}' in Google Cloud Storage"
    )


@task
def get_date_newest_file(
    gcs_client: storage.Client, bucket_name: str, prefix: str
) -> datetime.date:
    """Get the date of the newest file stored as Blob in GCS

    Args:
        gcs_client (storage.Client): Google Cloud Storage Client
        bucket_name (str): Google Cloud Storage Bucket
        prefix (str): Child Folder of Bucket

    Returns:
        datetime.date: Newest/Max date in Blob Filename(s)
    """
    logger = get_run_logger()

    blob_iterator = gcs_client.list_blobs(bucket_name)

    blobs = []

    # Print blobs at current
    for blob in blob_iterator:
        if prefix in blob.name:
            if f"{prefix}/" != blob.name:  # Check if virtual Folder
                blobs.append(blob)

    logger.info(f"{len(blobs)} Blobs in list")

    if len(blobs) == 0:
        max_date = datetime.date.today()

    if len(blobs) > 0:
        # First remove parent directory, then remove file extension, then isolate date string
        blob_date_strings = [
            i.name.split("/")[-1].split(".")[0].split("_")[-1] for i in blobs
        ]

        logger.info(f"{len(blob_date_strings)} Blobs have a date string in the name")
        logger.info(
            f"Here is an example Date String contained in the First Blob: {blob_date_strings[0]}"
        )
        logger.info(
            f"Here is an example Date String contained in the Last Blob: {blob_date_strings[-1]}"
        )

        blob_dates = [
            datetime.datetime.strptime(i, "%Y-%m-%d").date() for i in blob_date_strings
        ]

        logger.info(
            f"The Date String of {len(blob_dates)} has now been converted to a Date Object"
        )
        logger.info(
            f"Here is an example Date Object contained in the First Blob: {blob_dates[0]}"
        )
        logger.info(
            f"Here is an example Date Object contained in the Last Blob: {blob_dates[-1]}"
        )

        max_date = max(list(set(blob_dates)))

    # max_date_string = max_date.strftime("%Y-%m-%d")

    logger.info(f"The Max Date in all Date Objects is: {max_date}")

    return max_date


@task
def create_date_range(max_date: datetime.date) -> list[datetime.date]:
    logger = get_run_logger()

    end_date = datetime.date.today()
    start_date = max_date
    logger.info(f"Creating a Date Range from {start_date} to {end_date}")

    days_between_start_and_end_date = (end_date - start_date).days
    logger.info(
        f"{days_between_start_and_end_date} Days between {start_date} and {end_date}"
    )

    date_range = []

    for i in range(days_between_start_and_end_date + 1):
        date = start_date + datetime.timedelta(days=i)
        date_range.append(date)

    logger.info(f"Created a Data Range of {len(date_range)} Day(s)")
    logger.info(f"Date Range: {date_range}")

    return date_range


@task
def get_user_data_to_be_transformed(
    gcs_client: storage.Client,
    min_date: str,
    max_date: str,
    prefix: str,
    bucket_name: str,
) -> list[storage.blob.Blob]:
    logger = get_run_logger()

    logger.info(f"Loading list of blobs. Using {min_date} and {max_date} as filter")

    blobs = []

    blob_iterator = gcs_client.list_blobs(bucket_name)

    for blob in blob_iterator:
        if prefix in blob.name:
            if max_date in blob.name:
                if f"{prefix}/" != blob.name:  # Check if virtual Folder
                    blobs.append(blob)

    logger.info(f"{len(blobs)} Blobs in list")

    return blobs


@task
def user_data_to_df(
    gcs_client: storage.Client, blobs: list[storage.blob.Blob], keys: list[str]
) -> pd.DataFrame:
    """Store Data in Dataframe

    Args:
        gcs_client (storage.Client): GCS Client
        blobs (list[storage.blob.Blob]): List of Blobs
        keys (list[str]): Keys in Raw data that should be mapped to Database Table

    Returns:
        pd.DataFrame: Dataframe holding all User data for this run
    """

    logger = get_run_logger()

    users = []

    logger.info(f"Starting to process {len(blobs)} Blob(s)")
    for blob in blobs:
        logger.info(f"Processing Blob: {blob}")
        bytes = blob.download_as_bytes(gcs_client)
        user_dict = json.loads(bytes)

        user = {}

        for k in keys:
            user_attribute = user_dict.get(k, None)
            user[k] = user_attribute

        users.append(user)

    logger.info(f"Transforming {len(blobs)} Blob(s) to a Dataframe")
    user_data_df = pd.DataFrame(users)
    logger.info(
        f"Created Dataframe with {user_data_df.shape[0]} Rows and {user_data_df.shape[1]} Columns"
    )
    logger.info(
        f"The created Dataframe contains the following columns: {user_data_df.columns}"
    )

    return user_data_df


@task
def transform_user_profile_setting_data(df: pd.DataFrame) -> pd.DataFrame:
    df["pk"] = df["pk"].astype("int64")
    df["biography"] = df["biography"].str.replace("\n", " ")
    df["has_bio"] = df["biography"].apply(lambda x: True if x[0] is not None else False)
    df["has_profile_pic"] = df["profile_pic_url"].apply(
        lambda x: True if x[0] is not None else False
    )
    return df


@task
def transform_user_data(df: pd.DataFrame) -> pd.DataFrame:
    df["pk"] = df["pk"].astype("int64")
    return df


@task
def validate_transformed_user_data(transformed_user_df: pd.DataFrame):
    """Validation for `USER.user` table"""
    logger = get_run_logger()

    schema = pa.DataFrameSchema(
        {
            "pk": pa.Column(dtype=int, unique=True, report_duplicates="exclude_last"),
            "username": pa.Column(
                dtype=str,
                unique=True,
                report_duplicates="exclude_last",
            ),
            "full_name": pa.Column(dtype=str),
            "is_verified": pa.Column(dtype=bool),
            "account_type": pa.Column(dtype=str, nullable=True),
            "is_business": pa.Column(dtype=bool),
            "business_category_name": pa.Column(dtype=str, nullable=True),
            "category_name": pa.Column(dtype=str, nullable=True),
            "category": pa.Column(dtype=str, nullable=True),
        }
    )
    logger.info(f"Validating with the following Schema: {schema}")
    schema.validate(transformed_user_df)
    logger.info("Dataframe has been validated successfully")


@task
def validate_transformed_user_profile_setting_data(transformed_user_df: pd.DataFrame):
    """Validation for `USER.user_profile_setting` table"""
    logger = get_run_logger()

    schema = pa.DataFrameSchema(
        {
            "pk": pa.Column(dtype=int, unique=True, report_duplicates="exclude_last"),
            "profile_pic_url": pa.Column(dtype=str),  # Probably should be nullable
            "profile_pic_url_hd": pa.Column(dtype=str, nullable=True),
            "has_profile_pic": pa.Column(dtype=bool),
            "is_private": pa.Column(dtype=bool),
            "has_bio": pa.Column(dtype=bool),
            "biography": pa.Column(dtype=str, nullable=True),
            "external_url": pa.Column(dtype=str, nullable=True),
        }
    )
    logger.info(f"Validating with the following Schema: {schema}")
    schema.validate(transformed_user_df)
    logger.info("Dataframe has been validated successfully")


@task
def upload_transformed_user_data(
    gcs_client: storage.Client,
    user_df: pd.DataFrame,
    bucket_name: str,
    file_prefix: str,
) -> storage.bucket.Bucket.blob:
    logger = get_run_logger()

    today = datetime.date.today()  # YYYY-MM-DD
    file_name = f"{file_prefix}_{today}.parquet"
    file_path = f"temp/{file_name}"
    user_df.to_parquet(file_path)
    logger.info(f"Wrote local file to this path: {file_path}")

    gcs_bucket = gcs_client.get_bucket(bucket_name)
    blob = gcs_bucket.blob(f"user/{file_name}")
    with open(file_path, "rb") as fp:
        blob.upload_from_file(fp)
        logger.info(
            f"Wrote {file_path} to Google Cloud Storage in bucket '{bucket_name}'"
        )
    # pathlib.Path(fp).unlink()
    # logger.info(f"Remove local file {file_path}")

    return blob


@task
def load_user_data_to_sql(
    transformed_user_df: pd.DataFrame,
    database_block_name: str,
    is_initial_data_ingestion: bool = False,
):
    logger = get_run_logger()

    logger.info(
        f"Dataframe that should be ingested, contains {transformed_user_df.shape[0]} rows"
    )
    data = transformed_user_df.to_dict(orient="records")

    TABLE_NAME = "`USER.user`"

    with SqlAlchemyConnector.load(database_block_name) as connector:
        logger.info(f"Connected to Database with Block name: {database_block_name}")
        if is_initial_data_ingestion:
            logger.info(f"Truncating table: {TABLE_NAME}")
            connector.execute("SET FOREIGN_KEY_CHECKS = 0;")
            connector.execute("TRUNCATE TABLE USER.user;")
            connector.execute("SET FOREIGN_KEY_CHECKS = 1;")
        logger.info(f"Writing to {TABLE_NAME} Table")
        connector.execute_many(
            """
            INSERT INTO USER.user (user_id, account_type_id, user_name, full_name, is_verified, is_business, business_category_name, category_name, category)
            VALUES (:pk, :account_type, :username, :full_name, :is_verified, :is_business, :business_category_name, :category_name, :category)
            ON DUPLICATE KEY UPDATE account_type_id=VALUES(account_type_id), user_name=VALUES(user_name), full_name=VALUES(full_name), is_verified=VALUES(is_verified), is_business=VALUES(is_business), business_category_name=VALUES(business_category_name), category_name=VALUES(category_name), category=VALUES(category);
            """,
            seq_of_parameters=data,
        )

    logger.info(
        f"Wrote {len(data)} rows to Database with Prefect Block name '{database_block_name}'"
    )


@task
def load_user_profile_setting_data_to_sql(
    transformed_user_df: pd.DataFrame,
    database_block_name: str,
    is_initial_data_ingestion: bool = False,
):
    logger = get_run_logger()

    logger.info(
        f"Dataframe that should be ingested, contains {transformed_user_df.shape[0]} rows"
    )
    data = transformed_user_df.to_dict(orient="records")

    TABLE_NAME = "`USER.user_profile_setting`"

    with SqlAlchemyConnector.load(database_block_name) as connector:
        logger.info(f"Connected to Database with Block name: {database_block_name}")
        if is_initial_data_ingestion:
            logger.info(f"Truncating table: {TABLE_NAME}")
            connector.execute("SET FOREIGN_KEY_CHECKS = 0;")
            connector.execute("TRUNCATE TABLE USER.user_profile_setting;")
            connector.execute("SET FOREIGN_KEY_CHECKS = 1;")
        logger.info(f"Writing to {TABLE_NAME} Table")
        connector.execute_many(
            """
            INSERT INTO USER.user_profile_setting (user_id, profile_pic_url, profile_pic_url_hd, has_profile_pic, is_private, has_bio, bio, external_url)
            VALUES (:pk, :profile_pic_url, :profile_pic_url_hd, :has_profile_pic, :is_private, :has_bio, :biography, :external_url)
            ON DUPLICATE KEY UPDATE profile_pic_url=VALUES(profile_pic_url), profile_pic_url_hd=VALUES(profile_pic_url_hd), has_profile_pic=VALUES(has_profile_pic), is_private=VALUES(is_private), has_bio=VALUES(has_bio), external_url=VALUES(external_url)
            """,
            seq_of_parameters=data,
        )

    logger.info(
        f"Wrote {len(data)} rows to Database with Prefect Block name '{database_block_name}'"
    )


@flow(name="Get Raw User Data", log_prints=True, task_runner=ConcurrentTaskRunner)
def store_raw_user_data_flow(
    instagram_account: str, instagram_password: str, config: InstagramRequestParams
):
    instagrapi_client = init_instagrapi_client(instagram_account, instagram_password)
    gcs_client = init_gcs_client()

    users = get_user_data(instagrapi_client, config)

    for i in users:
        store_raw_user_data(gcs_client, i, "instagram-raw")


@flow(name="Transform User Data", log_prints=True, task_runner=SequentialTaskRunner)
def transform_user_data_flow(
    mapping: SourceToTargetKeyMapping, processing_params: DataProcessingParams
):
    gcs_client = init_gcs_client()

    max_date = get_date_newest_file(gcs_client, "instagram-processed", "user")

    date_range = create_date_range(max_date)

    min_date_string = min(date_range).strftime("%Y-%m-%d")
    max_date_string = max(date_range).strftime("%Y-%m-%d")

    blobs = get_user_data_to_be_transformed(
        gcs_client, min_date_string, max_date_string, "user", "instagram-raw"
    )

    # Transformed data which will be stored in `USER.user` later on
    user_df = user_data_to_df(gcs_client, blobs, mapping.user_keys)
    user_df = transform_user_data(user_df)
    validate_transformed_user_data(user_df)
    upload_transformed_user_data(gcs_client, user_df, "instagram-processed", "user")

    # Transformed data which will be stored in `USER.user_profile_setting` later on
    user_profile_setting_df = user_data_to_df(
        gcs_client, blobs, mapping.user_profile_setting_keys
    )
    user_profile_setting_df = transform_user_profile_setting_data(
        user_profile_setting_df
    )
    validate_transformed_user_profile_setting_data(user_profile_setting_df)
    upload_transformed_user_data(
        gcs_client,
        user_profile_setting_df,
        "instagram-processed",
        "user_profile_setting",
    )

    return (user_df, user_profile_setting_df)


@flow(name="Store Final User Data", log_prints=True, task_runner=SequentialTaskRunner)
def store_final_user_data_flow(
    transformed_user_dfs: tuple,
    processing_params: DataProcessingParams,
):
    user_df = transformed_user_dfs[0]
    load_user_data_to_sql(
        user_df,
        processing_params.user_database_block_name,
        processing_params.is_initial_data_ingestion,
    )

    user_profile_setting_df = transformed_user_dfs[1]
    load_user_profile_setting_data_to_sql(
        user_profile_setting_df,
        processing_params.user_database_block_name,
        processing_params.is_initial_data_ingestion,
    )


if __name__ == "__main__":
    store_raw_user_data_flow(
        instagram_account=Secret.load("instagram-account-username").get(),
        instagram_password=Secret.load("instagram-account-password").get(),
        config=InstagramRequestParams(),
    )
    transformed_user_dfs = transform_user_data_flow(
        mapping=SourceToTargetKeyMapping(), processing_params=DataProcessingParams()
    )

    store_final_user_data_flow(
        transformed_user_dfs=transformed_user_dfs,
        processing_params=DataProcessingParams(),
    )
