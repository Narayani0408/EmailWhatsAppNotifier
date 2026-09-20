from flask import Flask, request
import base64
import json

from gmail_service import get_gmail_service
from gmail_history import (
    get_new_messages,
    process_email,
    load_state,
    save_state
)

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()

    print("\n========== PUB/SUB MESSAGE ==========")

    try:
        message = data["message"]
        encoded_data = message.get("data")

        if not encoded_data:
            print("❌ No data found")
            return "EVENT_RECEIVED", 200

        # Decode Gmail notification
        decoded_data = base64.b64decode(
            encoded_data
        ).decode("utf-8")

        gmail_data = json.loads(decoded_data)

        email_address = gmail_data.get("emailAddress")
        new_history_id = gmail_data.get("historyId")

        print("📧 Gmail:", email_address)
        print("🆕 History ID:", new_history_id)

        # Connect to Gmail
        service = get_gmail_service()

        # Load state
        state = load_state()
        old_history_id = state.get("historyId")

        print("Previous History ID:", old_history_id)

        # First notification
        if not old_history_id:
            state["historyId"] = new_history_id
            state["processed_ids"] = []
            save_state(state)

            print("✅ History initialized.")
            return "EVENT_RECEIVED", 200

        # Get new emails
        new_messages = get_new_messages(
            service,
            old_history_id
        )

        print("New message IDs:", new_messages)

        processed_ids = set(
            state.get("processed_ids", [])
        )

        # Process emails
        for message_id in new_messages:

            if message_id in processed_ids:
                continue

            print("📧 Processing:", message_id)

            success = process_email(
                service,
                message_id
            )

            if success:
                processed_ids.add(message_id)
                print("✅ WhatsApp sent.")

        # Save state
        state["historyId"] = new_history_id
        state["processed_ids"] = list(processed_ids)

        save_state(state)

        print("✅ State updated.")

        return "EVENT_RECEIVED", 200

    except Exception as e:

        print("❌ Error:", e)

        return "ERROR", 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )