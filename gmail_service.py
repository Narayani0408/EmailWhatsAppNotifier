import os
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():
    creds = None

    # -----------------------------
    # CLOUD / RENDER
    # -----------------------------
    credentials_json = os.getenv("GMAIL_CREDENTIALS_JSON")
    token_json = os.getenv("GMAIL_TOKEN_JSON")

    if credentials_json and token_json:
        client_config = json.loads(credentials_json)
        token_data = json.loads(token_json)

        creds = Credentials.from_authorized_user_info(
            token_data,
            SCOPES
        )

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

    # -----------------------------
    # LOCAL COMPUTER
    # -----------------------------
    else:
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file(
                "token.json",
                SCOPES
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json",
                    SCOPES
                )

                creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())

    # -----------------------------
    # BUILD GMAIL SERVICE
    # -----------------------------
    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    return service