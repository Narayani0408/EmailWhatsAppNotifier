import json
import os

from gmail_service import get_gmail_service
from email_utils import get_email_body, clean_email_body
from whatsapp_service import send_whatsapp_message


STATE_FILE = "state.json"


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as file:
            return json.load(file)

    return {}


def save_state(state):
    with open(STATE_FILE, "w") as file:
        json.dump(state, file, indent=4)


def get_new_messages(service, start_history_id):
    response = service.users().history().list(
        userId="me",
        startHistoryId=start_history_id,
        maxResults=500
    ).execute()

    new_messages = []

    for history in response.get("history", []):
        print("History record:", history)

        for message_added in history.get("messagesAdded", []):
            message_id = message_added["message"]["id"]

            if message_id not in new_messages:
                new_messages.append(message_id)

    print("Found message IDs:", new_messages)

    return new_messages


def process_email(service, message_id):
    message = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()

    headers = message["payload"]["headers"]

    sender = "Unknown"
    subject = "No Subject"

    for header in headers:
        if header["name"].lower() == "from":
            sender = header["value"]

        elif header["name"].lower() == "subject":
            subject = header["value"]

    body = get_email_body(message["payload"])
    clean_body = clean_email_body(body)

    words = clean_body.split()

    if len(words) > 30:
        summary = " ".join(words[:30]) + "..."
    else:
        summary = clean_body

    notification = f"""📧 New Email
👤 From: {sender}
📝 Subject: {subject}
💬 Summary: {summary}"""

    print("\n📱 WhatsApp Notification")
    print("-------------------------")
    print(notification)
    print("-------------------------")

    return send_whatsapp_message(notification)


def main():
    service = get_gmail_service()

    profile = service.users().getProfile(
        userId="me"
    ).execute()

    print("Gmail account:", profile["emailAddress"])

    profile_history_id = profile["historyId"]

    state = load_state()

    # First run
    if "historyId" not in state:
        state["historyId"] = profile_history_id
        state["processed_ids"] = []

        save_state(state)

        print("✅ Gmail history initialized.")
        print("No old emails will be sent to WhatsApp.")

        return

    start_history_id = state["historyId"]
    processed_ids = set(state.get("processed_ids", []))

    print("Previous History ID:", start_history_id)
    print("Current History ID:", profile_history_id)

    try:
        new_messages = get_new_messages(
            service,
            start_history_id
        )

    except Exception as e:
        print("❌ History error:", e)
        return

    if not new_messages:
        print("📭 No new email.")
    else:
        print("🎉 New email(s) detected!")

        for message_id in new_messages:

            if message_id in processed_ids:
                print("Already processed:", message_id)
                continue

            print("Processing:", message_id)

            success = process_email(
                service,
                message_id
            )

            if success:
                processed_ids.add(message_id)
                print("✅ WhatsApp sent successfully.")

    state["historyId"] = profile_history_id
    state["processed_ids"] = list(processed_ids)

    save_state(state)

    print("✅ State saved.")


if __name__ == "__main__":
    main()