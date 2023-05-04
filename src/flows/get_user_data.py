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
from prefect_gcp import GcpCredentials

from src.instagram import challenge_resolver
from src.utils.config import InstagramRequestParams
from src.utils.serializer import CustomJSONEncoder


@task
def init_instagrapi_client(
    instagram_account: str, instagram_password: str
) -> instagrapi.Client:
    instagrapi_client = instagrapi.Client()

    # CHALLENGE_EMAIL = Secret.load("instagram-mail-adress").get()
    # CHALLENGE_PASSWORD = Secret.load("instagram-mail-password").get()

    # # client.challenge_code_handler = challenge_resolver.challenge_code_handler
    # # client.change_password_handler = challenge_resolver.change_password_handler

    instagrapi_client.login(instagram_account, instagram_password)
    return instagrapi_client


@task
def init_gcs_client() -> storage.Client:
    gcp_credentials = GcpCredentials.load("instagram-prefect-sa")
    project_id = gcp_credentials.project
    gcs_client = storage.Client(project=project_id)
    return gcs_client


@task
def get_user_ids(
    instagrapi_client: instagrapi.Client, config: InstagramRequestParams
) -> list[str]:
    user_names = config.user_names
    user_ids = []
    for i in user_names:
        user_short = instagrapi_client.user_info_by_username(i)
        user_id = user_short.__dict__["pk"]
        user_ids.append(user_id)
    return user_names


@task
def get_user_data(
    instagrapi_client: instagrapi.Client, config: InstagramRequestParams
) -> list[User]:
    user_names = config.user_names
    users = []
    for i in user_names:
        user = instagrapi_client.user_info_by_username(i)
        users.append(user)
    return users


@task
def store_user_data(gcs_client: storage.Client, users: list[User]):
    gcs_bucket = gcs_client.get_bucket("instagram-raw")

    # Store Data in GCS Bucket
    for i in users:
        # Construct Filename
        user_id, user_name = i.pk, i.username
        today = datetime.date.today()  # YYYY-MM-DD
        blob_name = f"user/{user_id}_{user_name}_{today}.json"

        # Prepare data and upload
        user_json_string = json.dumps(i, cls=CustomJSONEncoder)
        blob = gcs_bucket.blob(blob_name)
        blob.upload_from_string(data=user_json_string, content_type="application/json")


@task
def transform_user_data(gcs_client: storage.Client) -> pd.DataFrame:
    blobs = gcs_client.list_blobs("instagram-raw", prefix="user")

    users = []

    for blob in blobs:
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

    # Convert List of Dicts to Dataframe
    transformed_user_df = pd.DataFrame(users)

    return transformed_user_df


@task
def validate_transformed_user_data(transformed_user_df: pd.DataFrame):
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

    schema.validate(transformed_user_df)


@task
def load_user_data_to_sql():
    pass


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


@flow(name="Get Raw User Data", log_prints=True)
def store_user_data_flow(
    instagram_account: str, instagram_password: str, config: InstagramRequestParams
):
    instagrapi_client = init_instagrapi_client(instagram_account, instagram_password)
    gcs_client = init_gcs_client()

    # Request data
    # user_ids = get_user_ids(client, config)
    users = get_user_data(instagrapi_client, config)

    # ETL
    store_user_data(gcs_client, users)
    transformed_user_df = transform_user_data(gcs_client)
    validate_transformed_user_data(transformed_user_df)
    upload_transformed_user_data(gcs_client, transformed_user_df)


if __name__ == "__main__":
    store_user_data_flow(
        instagram_account=Secret.load("instagram-account-username").get(),
        instagram_password=Secret.load("instagram-account-password").get(),
        config=InstagramRequestParams(),
    )
