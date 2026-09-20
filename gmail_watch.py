import os
import json

from dotenv import load_dotenv
from gmail_service import get_gmail_service

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")

TOPIC_NAME = f"projects/{PROJECT_ID}/topics/gmail-notifications"

STATE_FILE = "state.json"


def save_watch_state(history_id, expiration):
    state = {
        "watchHistoryId": history_id,
        "expiration": expiration
    }

    with open(STATE_FILE, "w") as file:
        json.dump(state, file, indent=4)


def main():
    service = get_gmail_service()

    print("Starting Gmail Watch...")
    print("Topic:", TOPIC_NAME)

    request = {
        "labelIds": ["INBOX"],
        "topicName": TOPIC_NAME
    }

    response = service.users().watch(
        userId="me",
        body=request
    ).execute()

    print("\n========== GMAIL WATCH ==========")
    print("History ID:", response["historyId"])
    print("Expiration:", response["expiration"])
    print("=================================")

    save_watch_state(
        response["historyId"],
        response["expiration"]
    )

    print("\n✅ Gmail Watch successfully created.")
    print("✅ State saved.")
    print("📧 Gmail is now watching your inbox.")


if __name__ == "__main__":
    main()