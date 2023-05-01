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
from instagrapi import Client
from instagrapi.mixins.challenge import ChallengeChoice
from prefect.blocks.system import Secret

################################################################################################

# Get Secret Information
CHALLENGE_EMAIL = Secret.load("instagram-mail-adress").get()
CHALLENGE_PASSWORD = Secret.load("instagram-mail-password").get()

IG_USERNAME = Secret.load("instagram-account-username").get()
IG_PASSWORD = Secret.load("instagram-account-password").get()

################################################################################################

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]

################################################################################################


# Sourced from https://developers.google.com/gmail/api/quickstart/python
def get_code_from_email(username: str):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
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
            print("No new messages.")
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
                    print("No data in message. Moving on to next message")
                    continue
                data = msg["payload"]["body"]["data"]
                byte_code = base64.urlsafe_b64decode(data)
                text = byte_code.decode("utf-8")
                print(text)

                # Search for the code in the email
                match = re.search(">([^>]*?({u})[^<]*?)<".format(u=username), text)
                if not match:
                    continue
                print("Match from email:", match.group(1))
                match = re.search(r">(\d{6})<", text)
                if not match:
                    print('Skip this email, "code" not found')
                    continue
                code = match.group(1)
                if code:
                    return code

    except Exception as error:
        print(f"An error occurred: {error}")
        return False


def get_code_from_sms(username: str):
    while True:
        code = input(f"Enter code (6 digits) for {username}: ").strip()
        if code and code.isdigit():
            return code
    return None


def challenge_code_handler(username: str, choice):
    if choice == ChallengeChoice.SMS:
        return get_code_from_sms(username)
    elif choice == ChallengeChoice.EMAIL:
        return get_code_from_email(username)
    return False


def change_password_handler(username: str):
    # Simple way to generate a random string
    chars = list("abcdefghijklmnopqrstuvwxyz1234567890!&£@#")
    password = "".join(random.sample(chars, 10))
    return password


if __name__ == "__main__":
    IG_USERNAME = Secret.load("instagram-account-username").get()
    IG_PASSWORD = Secret.load("instagram-account-password").get()
    cl = Client()
    cl.login(IG_USERNAME, IG_PASSWORD, relogin=True)

    # IG_USERNAME = Secret.load("instagram-account-username").get()
    # get_code_from_email(IG_USERNAME)
    # CHALLENGE_EMAIL = Secret.load("instagram-mail-adress").get()
    # CHALLENGE_PASSWORD = Secret.load("instagram-mail-password").get()
    # get_code_from_email(IG_USERNAME)

    # cl.challenge_code_handler = challenge_code_handler
    # cl.change_password_handler = change_password_handler
