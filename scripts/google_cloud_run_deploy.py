"""Programmatically deploy a (Serverless) Gogle Cloud Run Flow"""

from dotenv import dotenv_values
from prefect.deployments import Deployment
from prefect.filesystems import GitHub
from prefect_gcp.cloud_run import CloudRunJob

from src.flows.healthcheck import healthcheck

# Env variables
env_variables = dotenv_values(".env")
GITHUB_REPOSITORY_BLOCK_NAME = env_variables["GITHUB_REPOSITORY_BLOCK_NAME"]
CLOUD_RUN_JOB_BLOCK_NAME = env_variables["GCR_HEALTHCHECK_BLOCK_NAME"]

# Load Blocks
storage = GitHub.load(GITHUB_REPOSITORY_BLOCK_NAME)
infra = CloudRunJob.load(CLOUD_RUN_JOB_BLOCK_NAME)

# Deploy
deployment_name = CLOUD_RUN_JOB_BLOCK_NAME
healtcheck_deployment = Deployment.build_from_flow(
    flow=healthcheck,
    name=deployment_name,
    version=1,
    work_pool_name="default-agent-pool",
    tags=["monitoring"],
    storage=storage,
    infrastructure=infra,
)
healtcheck_deployment.apply()
