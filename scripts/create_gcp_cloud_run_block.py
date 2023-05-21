"""Programmatically create Cloud Run block for Prefect"""

from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_run import CloudRunJob
from dotenv import dotenv_values

# Load env variables
env_variables = dotenv_values(".env")
GCP_CREDENTIAL_BLOCK_NAME = env_variables["GCP_CREDENTIAL_BLOCK_NAME"]

credentials = GcpCredentials.load(GCP_CREDENTIAL_BLOCK_NAME)
project_id = credentials.project

# Artifact Registry in Google Cloud
registry_adress = f"europe-west3-docker.pkg.dev/{project_id}/prefect-flows"

flow_name = "hello-world"

block = CloudRunJob(
    credentials=credentials,
    project_id=project_id,
    image=f"{registry_adress}/{flow_name}:2.10.4-python3.9",
    region="europe-west3",
)

block.save(name="hello-world-cloud-run-block", overwrite=True)
