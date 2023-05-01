import json

from instagrapi import Client
from instagrapi.types import HttpUrl, User
from prefect import flow, get_run_logger, task
from prefect.blocks.system import Secret
from prefect.filesystems import LocalFileSystem
from prefect_gcp import GcpCredentials

from src.instagram import challenge_resolver
from src.utils import serializer
from src.utils.config import InstagramRequestParams


@task
def init_client(instagram_account: str, instagram_password: str) -> Client:
    client = Client()

    # CHALLENGE_EMAIL = Secret.load("instagram-mail-adress").get()
    # CHALLENGE_PASSWORD = Secret.load("instagram-mail-password").get()

    # # client.challenge_code_handler = challenge_resolver.challenge_code_handler
    # # client.change_password_handler = challenge_resolver.change_password_handler

    client.login(instagram_account, instagram_password)
    return client


@task
def get_user_ids(client: Client, config: InstagramRequestParams) -> list[str]:
    user_names = config.user_names
    user_ids = []
    for i in user_names:
        user_short = client.user_info_by_username(i)
        user_id = user_short.__dict__["pk"]
        user_ids.append(user_id)
    return user_names


@task
def get_user_data(client: Client, config: InstagramRequestParams) -> list[User]:
    user_names = config.user_names
    users = []
    for i in user_names:
        user = client.user_info_by_username(i)
        users.append(user)
    return users


@task
def store_user_data_in_gcs(users: list[User]):
    for i in users:
        print(i)


@flow(name="Get Raw User Data", log_prints=True)
def store_user_data_flow(
    instagram_account: str, instagram_password: str, config: InstagramRequestParams
):
    client = init_client(instagram_account, instagram_password)
    # user_ids = get_user_ids(client, config)
    users = get_user_data(client, config)
    store_user_data_in_gcs(users)


if __name__ == "__main__":
    store_user_data_flow(
        instagram_account=Secret.load("instagram-account-username").get(),
        instagram_password=Secret.load("instagram-account-password").get(),
        config=InstagramRequestParams(),
    )
