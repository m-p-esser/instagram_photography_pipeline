"""Programmatically create GCS block for Prefect"""

from prefect.filesystems import GCS
from prefect_gcp import GcsBucket, GcpCredentials
from dotenv import dotenv_values

# Load Env variables
env_variables = dotenv_values(".env")

# Define Bucket Names
BUCKET_NAMES = ["instagram-raw", "instagram-processed", "instagram-final"]

with open("credentials/prefect_service_account.json", "r") as f:
    service_account = f.read()

for i in BUCKET_NAMES:
    # Create the reference to the GCS Filesystem
    block = GCS(
        bucket_path=i,
        service_account_info=service_account,
        project=env_variables["CLOUDSDK_CORE_PROJECT"],
    )

    block.save(i, overwrite=True)

gcp_credentials = GcpCredentials.load(env_variables["GCP_CREDENTIAL_BLOCK_NAME"])

for i in BUCKET_NAMES:
    # Create the reference to the GCS Buckets
    block = GcsBucket(
        bucket=i,
        gcp_credentials=gcp_credentials,
    )

    block.save(i, overwrite=True)
