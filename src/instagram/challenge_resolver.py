"""Module to handle Email/SMS challenges"""
# Sourced from https://github.com/adw0rd/instagrapi/blob/master/examples/challenge_resolvers.py

import email
import imaplib
import random
import re

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


def get_code_from_email(username: str):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(CHALLENGE_EMAIL, CHALLENGE_PASSWORD)
    mail.select("inbox")
    result, data = mail.search(None, "(UNSEEN)")
    assert result == "OK", "Error1 during get_code_from_email: %s" % result
    ids = data.pop().split()
    for num in reversed(ids):
        mail.store(num, "+FLAGS", "\\Seen")  # mark as read
        result, data = mail.fetch(num, "(RFC822)")
        assert result == "OK", "Error2 during get_code_from_email: %s" % result
        msg = email.message_from_string(data[0][1].decode())
        payloads = msg.get_payload()
        if not isinstance(payloads, list):
            payloads = [msg]
        code = None
        for payload in payloads:
            body = payload.get_payload(decode=True).decode()
            if "<div" not in body:
                continue
            match = re.search(">([^>]*?({u})[^<]*?)<".format(u=username), body)
            if not match:
                continue
            print("Match from email:", match.group(1))
            match = re.search(r">(\d{6})<", body)
            if not match:
                print('Skip this email, "code" not found')
                continue
            code = match.group(1)
            if code:
                return code
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
    cl = Client()
    cl.challenge_code_handler = challenge_code_handler
    cl.change_password_handler = change_password_handler
    cl.login(IG_USERNAME, IG_PASSWORD)
