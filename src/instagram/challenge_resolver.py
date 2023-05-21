"""Module to handle Email/SMS challenges"""
# Sourced from https://github.com/adw0rd/instagrapi/blob/master/examples/challenge_resolvers.py

import base64
import email
import imaplib
import json
import logging
import os.path
import random
import re
import time

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from instagrapi.mixins.challenge import ChallengeChoice

logger = logging.getLogger()


# Sourced from https://developers.google.com/gmail/api/quickstart/python
def get_code_from_email(mail_adress: str):
    """Extract Code from GMail mails"""

    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",
    ]

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    if os.path.exists("credentials/token.json"):
        creds = Credentials.from_authorized_user_file("credentials/token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                # your creds file here. Please create json file as here https://cloud.google.com/docs/authentication/getting-started
                "credentials/credentials.json",
                SCOPES,
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("credentials/token.json", "w") as token:
            token.write(creds.to_json())
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = (
            service.users()
            .messages()
            .list(userId="me", labelIds=["INBOX"], q="is:unread")
            .execute()
        )
        messages = results.get("messages", [])

        if not messages:
            logger.info("No new messages.")

        else:
            # message_count = 0
            for message in messages:
                msg = (
                    service.users()
                    .messages()
                    .get(userId="me", id=message["id"])
                    .execute()
                )

                # Get mail text and decode it to utf-8
                if "data" not in msg["payload"]["body"]:
                    logger.info("No data in message. Moving on to next message")
                    continue

                data = msg["payload"]["body"]["data"]
                byte_code = base64.urlsafe_b64decode(data)
                text = byte_code.decode("utf-8")
                print(text)

                # Search for the code in the email
                match = re.search(">([^>]*?({u})[^<]*?)<".format(u=mail_adress), text)

                if not match:
                    continue
                logger.info(f"Match from email: {match.group(1)}")
                match = re.search(r">(\d{6})<", text)

                if not match:
                    logger.info('Skip this email, "code" not found')
                    continue

                code = match.group(1)

                if code:
                    return code

    except Exception as e:
        logger.info(f"An error occurred: {e}")
        return False


def get_code_from_sms(username: str):
    raise NotImplementedError
    # while True:
    #     code = input(f"Enter code (6 digits) for {username}: ").strip()
    #     if code and code.isdigit():
    #         return code


def challenge_code_handler(choice, username: str = None):
    if choice == ChallengeChoice.SMS:
        return get_code_from_sms(username=username)
    elif choice == ChallengeChoice.EMAIL:
        return get_code_from_email(mail_adress=username)
    return False


def change_password_handler(username: str):
    # Simple way to generate a random string
    chars = list("abcdefghijklmnopqrstuvwxyz1234567890!&£@#")
    password = "".join(random.sample(chars, 10))
    return password
