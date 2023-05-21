import logging

import instagrapi
from instagrapi.exceptions import (
    BadPassword,
    ChallengeRequired,
    FeedbackRequired,
    LoginRequired,
    PleaseWaitFewMinutes,
    RecaptchaChallengeForm,
    ReloginAttemptExceeded,
    SelectContactPointRecoveryForm,
)
from prefect.blocks.system import Secret

from src.instagram.challenge_resolver import challenge_code_handler

logger = logging.getLogger()


def login_user(
    instagram_account: str, instagram_password: str
) -> tuple[instagrapi.Client, str]:
    cl = instagrapi.Client()

    cl.dump_settings("session.json")

    # Add random delay between requests
    cl.delay_range = [1, 2.5]

    # Add Handler for code challenge
    cl.challenge_code_handler = challenge_code_handler

    # Attempt to load Session information
    try:
        session = cl.load_settings("session.json")
    except Exception as e:
        logger.info(
            f"Couldn't load Session Information: {e}.\n Dumping Session information, so it can be used in the next run"
        )
        cl.dump_settings("session.json")

    login_trough_session = False
    login_trough_password = False
    logged_in = False

    if session:
        try:
            cl.set_settings(session)
            logged_in = cl.login(instagram_account, instagram_password)

            # Check if Session is valid
            try:
                cl.get_timeline_feed()

            except LoginRequired:
                logger.info(
                    "Session is invalid, need to login trough Username and Password"
                )

                old_session = cl.get_settings()
                cl.set_settings({})  # use the same device uuids across logins
                cl.set_uuids(old_session["uuids"])
                cl.login(instagram_account, instagram_password)

            login_trough_session = True

        except Exception as e:
            logger.info(f"Couldn't login user trough Session Information: {e}")

    if not login_trough_session:
        try:
            logger.info("Attempting to login user trough Username and Password")
            if cl.login(instagram_account, instagram_password):
                login_trough_password = True
                logged_in = True
        except Exception as e:
            logger.info(f"Couldn't login user trough Username and Password: {e}")

    if not login_trough_password and not login_trough_session:
        logger.info("Couldn't login user trough Password or Session")

    return (cl, logged_in)


if __name__ == "__main__":
    instagram_account = Secret.load("instagram-account-username").get()
    instagram_password = Secret.load("instagram-account-password").get()
    login_user(instagram_account, instagram_password)
