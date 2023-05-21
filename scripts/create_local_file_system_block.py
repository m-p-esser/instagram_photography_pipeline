"""Programmatically create Fileystem block for Prefect"""

from prefect.filesystems import LocalFileSystem
from dotenv import dotenv_values

env_variables = dotenv_values(".env")

DATA_FILESYSTEM_BASE_PATH = env_variables["DATA_FILESYSTEM_BASE_PATH"]

block = LocalFileSystem(
    basepath=DATA_FILESYSTEM_BASE_PATH,
)

block.save("data-filesystem", overwrite=True)

TEMP_FILESYSTEM_BASE_PATH = env_variables["TEMP_FILESYSTEM_BASE_PATH"]

block = LocalFileSystem(
    basepath=TEMP_FILESYSTEM_BASE_PATH,
)

block.save("temp-filesystem", overwrite=True)
