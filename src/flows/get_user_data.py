import datetime
import json

import instagrapi
import pandas as pd
import pandera as pa
from google.cloud import storage
from instagrapi.types import HttpUrl, User
from prefect import flow, get_run_logger, task
from prefect.blocks.system import Secret
from prefect.filesystems import GCS, LocalFileSystem
from prefect.task_runners import ConcurrentTaskRunner, SequentialTaskRunner
from prefect_gcp import GcpCredentials

from src.instagram import challenge_resolver
from src.utils.config import InstagramRequestParams
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
def get_user_ids(
    instagrapi_client: instagrapi.Client, config: InstagramRequestParams
) -> list[str]:
    logger = get_run_logger()

    user_names = config.user_names
    logger.info(f"Processing {len(user_names)} Usernames")
    logger.info(f"Getting User Ids for the following Usernames: \n {user_names}")

    user_ids = []
    for i in user_names:
        logger.info(f"Getting User IDs for Username: {i}")
        user_short = instagrapi_client.user_info_by_username(i)
        user_id = user_short.__dict__["pk"]
        user_ids.append(user_id)
    logger.info(f"Stored User IDs for {len(user_ids)} Usernames")

    return user_names


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
        logger.info(f"Getting User Date for Username: {i}")
        user = instagrapi_client.user_info_by_username(i)
        users.append(user)

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
    # logger = get_run_logger()

    blobs = []
    # blob_iterator = gcs_client.list_blobs("instagram-raw")
    sorted_blobs = sorted(blobs, key=lambda blob: blob.created, reverse=True)
    print(sorted_blobs)

    # if sorted_blobs:
    #     i.split("/")[-1].split(".")[0].split("_")[-1]

    # )  # bucket_name, prefix)
    # for i in blob_iterator:
    #     print(i)
    #     blobs.append(i)

    # blob_names = [i.name for _, i in enumerate(blobs)]
    # logger.info(f"{len(blob_names)} Blobs of loaded Blobs have a name")

    # # First remove parent directory, then remove file extension, then isolate date string
    # blob_date_strings = [
    #     i.split("/")[-1].split(".")[0].split("_")[-1] for i in blob_names
    # ]
    # logger.info(f"{len(blob_date_strings)} Blobs have a date string in the name")
    # logger.info(
    #     f"Here is an example Date String contained in the First Blob: {blob_date_strings[0]}"
    # )
    # logger.info(
    #     f"Here is an example Date String contained in the Last Blob: {blob_date_strings[-1]}"
    # )

    # blob_dates = [datetime.date.strptime(i, "%Y-%m-%d") for i in blob_date_strings]
    # logger.info(
    #     f"The Date String of {len(blob_dates)} has now been converted to a Date Object"
    # )
    # logger.info(
    #     f"Here is an example Date Object contained in the First Blob: {blob_dates[0]}"
    # )
    # logger.info(
    #     f"Here is an example Date Object contained in the Last Blob: {blob_dates[-1]}"
    # )

    # max_date = max(list(set(blob_dates)))
    # logger.info(f"The Max Date in all Date Objects is: {max_date}")

    # return max_date


@task
def create_date_range(max_date: datetime.date) -> list[datetime.date]:
    logger = get_run_logger()

    end_date = datetime.date.today()
    start_date = max_date.copy()
    logger.info(f"Creating a Date Range from {start_date} to {end_date}")

    days_between_start_and_end_date = end_date - start_date
    logger.info(
        f"{days_between_start_and_end_date} Days between {start_date} and {end_date}"
    )

    date_range = []

    for i in range(days_between_start_and_end_date.days + 1):
        date = start_date + datetime.timedelta(days=i)
        date_range.append(date)

    logger.info(f"Created a Data Range of {len(date_range)} Days")
    logger.info(f"Date Range: {date_range}")

    return date_range


@task
def get_user_data_to_be_transformed(
    gcs_client: storage.Client, min_date: datetime.date, max_date: datetime.date
):
    logger = get_run_logger()

    logger.info(
        f"Loading list of blobs. Using {min_date} as start_offset and {max_date} as end_offset"
    )
    blob_iterator = gcs_client.list_blobs(
        bucket_or_name="instagram-raw",
        prefix="user",
        start_offset=min_date,
        end_offset=max_date,
    )
    blobs = [i for i in blob_iterator]
    logger.info(f"Stored list with {len(blobs)} Blob(s) in memory")

    return blobs


@task
def transform_user_data(blobs) -> pd.DataFrame:
    logger = get_run_logger()

    users = []

    logger.info(f"Starting to process {len(blobs)} Blob(s)")
    for blob in blobs:
        logger.info(f"Processing Blob: {blob.name}")
        bytes = blob.download_as_bytes()
        user_dict = json.loads(bytes)

        user = {}

        keys = [
            "pk",
            "username",
            "full_name",
            "is_verified",
            "account_type",
            "is_business",
            "business_category_name",
            "category_name",
            "category",
        ]

        for k in keys:
            user_attribute = user_dict.get(k, None)
            user[k] = user_attribute

        users.append(user)

    logger.info(f"Transforming {len(blobs)} Blob(s) to a Dataframe")
    transformed_user_df = pd.DataFrame(users)
    logger.info(
        f"Created Dataframe with {transform_user_data.shape[0]} Rows and {transform_user_data.shape[1]} Columns"
    )
    logger.info(
        f"The created Dataframe contains the following columns: {transformed_user_df.columns}"
    )

    return transformed_user_df


@task
def validate_transformed_user_data(transformed_user_df: pd.DataFrame):
    logger = get_run_logger()

    schema = pa.DataFrameSchema(
        {
            "pk": pa.Column(dtype=int, unique=True, report_duplicates="exclude_last"),
            "username": pa.Column(
                dtype=str,
                unique=True,
                report_duplicates="exclude_last",
                checks=[pa.Check.str_contains("_")],
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
def load_user_data_to_sql(transformed_user_df: pd.DataFrame):
    pass

    # What options do i have

    # Pandas
    # ORM (SQL Alchemy) -> Direct SQL

    # MAKE SURE TO RENAME COLUMNS TO MATCH SQL TABLES

    ######## INSERT/UPDATE, INSERT IF NEW USER, UPDATE IF EXISTS


@task
def upload_transformed_user_data(
    gcs_client: storage.Client, user_df: pd.DataFrame
) -> storage.bucket.Bucket.blob:
    # Write to local File
    today = datetime.date.today()  # YYYY-MM-DD
    file_name = f"user_{today}.parquet"
    file_path = f"temp/{file_name}"
    user_df.to_parquet(file_path)

    # Load local file to GCS
    gcs_bucket = gcs_client.get_bucket("instagram-processed")
    blob = gcs_bucket.blob(f"user/{file_name}")
    with open(file_path, "rb") as fp:
        blob.upload_from_file(fp)

    return blob


@flow(name="Get Raw User Data", log_prints=True, task_runner=ConcurrentTaskRunner)
def store_raw_user_data_flow(
    instagram_account: str, instagram_password: str, config: InstagramRequestParams
):
    instagrapi_client = init_instagrapi_client(instagram_account, instagram_password)
    gcs_client = init_gcs_client()

    # user_ids = get_user_ids(instagrapi_client, config)
    users = get_user_data(instagrapi_client, config)

    for i in users:
        store_raw_user_data(gcs_client, i, "instagram-raw")


@flow(name="Transform User Data", log_prints=True, task_runner=SequentialTaskRunner)
def transform_user_data_flow():
    gcs_client = init_gcs_client()

    max_date = get_date_newest_file(gcs_client, "instagram-raw", "user")
    # SHOULD Be instagram-processed

    date_range = create_date_range(max_date)
    # min_date = min(date_range)
    max_date = max(date_range)

    # blobs = get_user_data_to_be_transformed(gcs_client, min_date, max_date)
    # transformed_user_df = transform_user_data(gcs_client, blobs)

    # validate_transformed_user_data(transformed_user_df)

    # upload_transformed_user_data(gcs_client, transformed_user_df)


if __name__ == "__main__":
    store_raw_user_data_flow(
        instagram_account=Secret.load("instagram-account-username").get(),
        instagram_password=Secret.load("instagram-account-password").get(),
        config=InstagramRequestParams(),
    )
    transform_user_data_flow()
