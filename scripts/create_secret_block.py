"""Programmatically create a Secret Block for Prefect"""

from dotenv import dotenv_values
from prefect.blocks.system import Secret

env_variables = dotenv_values(".env")

# Instagram Account Name
block = Secret(value=env_variables["INSTAGRAM_ACCOUNT_USERNAME"])
block.save(name="instagram-account-username", overwrite=True)

# Instagram Account Password
block = Secret(value=env_variables["INSTAGRAM_ACCOUNT_PASSWORD"])
block.save(name="instagram-account-password", overwrite=True)

# Instagram Mail Adress
block = Secret(value=env_variables["INSTAGRAM_MAIL_ADRESS"])
block.save(name="instagram-mail-adress", overwrite=True)

# Instagram Mail Password
block = Secret(value=env_variables["INSTAGRAM_MAIL_PASSWORD"])
block.save(name="instagram-mail-password", overwrite=True)
