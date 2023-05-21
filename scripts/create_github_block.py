""" Programmatically create a Github Prefect block"""

from dotenv import dotenv_values
from prefect.filesystems import GitHub

env_variables = dotenv_values(".env")

GITHUB_REPOSITORY_BLOCK_NAME = env_variables["GITHUB_REPOSITORY_BLOCK_NAME"]

block = GitHub(
    repository="https://github.com/m-p-esser/instagram_photography_pipeline/",
)
block.save(GITHUB_REPOSITORY_BLOCK_NAME, overwrite=True)
