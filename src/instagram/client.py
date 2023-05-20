import instagrapi


def construct_instagrapi_client(
    instagram_account: str, instagram_password: str
) -> instagrapi.Client:
    instagrapi_client = instagrapi.Client()

    # CHALLENGE_EMAIL = Secret.load("instagram-mail-adress").get()
    # CHALLENGE_PASSWORD = Secret.load("instagram-mail-password").get()

    # # client.challenge_code_handler = challenge_resolver.challenge_code_handler
    # # client.change_password_handler = challenge_resolver.change_password_handler

    sucessful = instagrapi_client.login(instagram_account, instagram_password)

    if not sucessful:
        raise Exception("Could not log in to Instagram")

    return instagrapi_client
