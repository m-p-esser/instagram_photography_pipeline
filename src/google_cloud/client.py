import datetime
import json

import pandas as pd
from google.cloud import storage
from prefect import get_run_logger
from prefect_gcp import GcpCredentials

from src.utils.serializer import CustomJSONEncoder


def construct_gcs_client(gcp_credential_block_name: str) -> storage.Client:
    gcp_credentials = GcpCredentials.load(gcp_credential_block_name)
    project_id = gcp_credentials.project
    gcs_client = storage.Client(project=project_id)

    return gcs_client


def upload_blob_from_string(
    gcs_client: storage.Client, object, bucket_name: str, blob_name
) -> storage.blob.Blob:
    gcs_bucket = gcs_client.get_bucket(bucket_name)
    media_json_string = json.dumps(object, cls=CustomJSONEncoder)
    blob = gcs_bucket.blob(blob_name)
    blob.upload_from_string(data=media_json_string, content_type="application/json")

    return blob


def upload_blob_from_dataframe(
    gcs_client: storage.Client,
    df: pd.DataFrame,
    bucket_name: str,
    file_prefix: str,
) -> storage.blob.Blob:
    logger = get_run_logger()

    today = datetime.date.today()  # YYYY-MM-DD
    file_name = f"{file_prefix}_{today}.parquet"
    file_path = f"temp/{file_name}"
    df.to_parquet(file_path)
    logger.info(f"Wrote local file to this path: {file_path}")

    gcs_bucket = gcs_client.get_bucket(bucket_name)
    blob = gcs_bucket.blob(f"{file_prefix}/{file_name}")
    with open(file_path, "rb") as fp:
        blob.upload_from_file(fp)
        logger.info(
            f"Wrote {file_path} to Google Cloud Storage in bucket '{bucket_name}'"
        )
    # pathlib.Path(fp).unlink()
    # logger.info(f"Remove local file {file_path}")

    return blob
