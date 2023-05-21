"""Programmatically create Cloud Run block for Prefect"""

from dotenv import dotenv_values
from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_run import CloudRunJob

# Env variables
env_variables = dotenv_values(".env")
GCP_CREDENTIAL_BLOCK_NAME = env_variables["GCP_CREDENTIAL_BLOCK_NAME"]
FLOW_NAME = env_variables["HEALTHCHECK_FLOW_NAME"]
PYTHON_VERSION = env_variables["PYTHON_VERSION"]
PREFECT_IMAGE_VERSION = env_variables["PREFECT_IMAGE_VERSION"]
REGION = env_variables["CLOUDSDK_COMPUTE_REGION"]
GCR_HEALTHCHECK_BLOCK_NAME = env_variables["GCR_HEALTHCHECK_BLOCK_NAME"]

# Credentials
credentials = GcpCredentials.load(GCP_CREDENTIAL_BLOCK_NAME)
project_id = credentials.project

# Build Artifact Registry adress in Google Cloud

registry_adress = f"{REGION}-docker.pkg.dev/{project_id}/prefect-flows"

block = CloudRunJob(
    credentials=credentials,
    project_id=project_id,
    image=f"{registry_adress}/{FLOW_NAME}:{PREFECT_IMAGE_VERSION}-python{PYTHON_VERSION}",
    region=REGION,
)
block.save(name=GCR_HEALTHCHECK_BLOCK_NAME, overwrite=True)
