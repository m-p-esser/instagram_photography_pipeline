"""Programmatically create Google Cloud Storage (Bucket)"""

from google.cloud import storage
from prefect.filesystems import GCS
from prefect_gcp import GcpCredentials
from dotenv import dotenv_values

# Load Env variables
env_variables = dotenv_values(".env")

# Load Credentials and Config
gcp_credentials = GcpCredentials.load(env_variables["GCP_CREDENTIAL_BLOCK_NAME"])
project_id = gcp_credentials.project

# Init Client
client = storage.Client(project=project_id)

# Create Raw Data Bucket
gcs_bucket = client.create_bucket(
    bucket_or_name="instagram-raw",
    # https://cloud.google.com/storage/docs/locations#location_recommendations
    location="europe-west3",
)

# Create Processed Data Bucket
gcs_bucket = client.create_bucket(
    bucket_or_name="instagram-processed",
    # https://cloud.google.com/storage/docs/locations#location_recommendations
    location="europe-west3",
)

# Create Final Data Bucket (for Production use)
gcs_bucket = client.create_bucket(
    bucket_or_name="instagram-final",
    # https://cloud.google.com/storage/docs/locations#location_recommendations
    location="eu",  # Multiregion
)
