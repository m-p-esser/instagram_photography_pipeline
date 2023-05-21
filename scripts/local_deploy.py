"""Programmatically deploy a local Flow"""

from dotenv import dotenv_values
from prefect.deployments import Deployment
from prefect.filesystems import GitHub

from src.flows.healthcheck import healthcheck

# Env variables
env_variables = dotenv_values(".env")
GITHUB_REPOSITORY_BLOCK_NAME = env_variables["GITHUB_REPOSITORY_BLOCK_NAME"]

# Load Blocks
storage = GitHub.load(GITHUB_REPOSITORY_BLOCK_NAME)

# Deploy
healtcheck_deployment = Deployment.build_from_flow(
    flow=healthcheck,
    name="local-healthcheck",
    version=1,
    work_pool_name="default-agent-pool",
    tags=["monitoring"],
    storage=storage,
)
healtcheck_deployment.apply()
