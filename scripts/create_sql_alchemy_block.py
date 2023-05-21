"""Programmatically create SQL Alchemy block for Prefect"""

from prefect_gcp import GcpCredentials
from prefect_sqlalchemy import SqlAlchemyConnector, ConnectionComponents, SyncDriver
from dotenv import dotenv_values

# Load env variables
env_variables = dotenv_values(".env")

# Get Schema Names
SCHEMA_NAMES = []
for k, v in env_variables.items():
    if "SCHEMA" in k:
        SCHEMA_NAMES.append(v)
print(SCHEMA_NAMES)


for SCHEMA in SCHEMA_NAMES:
    block = SqlAlchemyConnector(
        connection_info=ConnectionComponents(
            driver=SyncDriver.MYSQL_PYMYSQL,
            database=SCHEMA,
            username=env_variables["PROD_DATABASE_USER"],
            password=env_variables["PROD_DATABASE_PASSWORD"],
            host=env_variables["PROD_DATABASE_HOST"],
            port=env_variables["PROD_DATABASE_PORT"],
        )
    )
    block_name = env_variables["PROD_DATABASE_NAME"] + "-" + SCHEMA.lower()
    block.save(block_name, overwrite=True)
