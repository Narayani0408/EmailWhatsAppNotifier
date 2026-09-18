from flask import Flask, request
import base64
import json

from gmail_service import get_gmail_service
from gmail_history import get_new_messages, process_email, load_state, save_state


app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()

    print("\n========== PUB/SUB MESSAGE ==========")
    print(data)

    try:
        # Pub/Sub message
        message = data["message"]

        encoded_data = message.get("data")

        if not encoded_data:
            print("❌ No data found")
            return "EVENT_RECEIVED", 200

        # Decode Pub/Sub data
        decoded_data = base64.b64decode(
            encoded_data
        ).decode("utf-8")

        print("\nDecoded Gmail notification:")
        print(decoded_data)

        gmail_data = json.loads(decoded_data)

        email_address = gmail_data.get("emailAddress")
        new_history_id = gmail_data.get("historyId")

        print("\nGmail Account:")
        print(email_address)

        print("New History ID:")
        print(new_history_id)

        # Connect to Gmail
        service = get_gmail_service()

        # Load previous state
        state = load_state()

        old_history_id = state.get("historyId")

        print("\nPrevious History ID:")
        print(old_history_id)

        if not old_history_id:
            print("⚠️ No previous history ID found.")
            state["historyId"] = new_history_id
            state["processed_ids"] = []
            save_state(state)

            return "EVENT_RECEIVED", 200

        # Find new emails
        new_messages = get_new_messages(
            service,
            old_history_id
        )

        print("\nNew message IDs:")
        print(new_messages)

        processed_ids = set(
            state.get("processed_ids", [])
        )

        # Process each new email
        for message_id in new_messages:

            if message_id in processed_ids:
                print(
                    "Already processed:",
                    message_id
                )
                continue

            print(
                "\n📧 Processing new email:",
                message_id
            )

            success = process_email(
                service,
                message_id
            )

            if success:
                processed_ids.add(message_id)

                print(
                    "✅ WhatsApp notification sent."
                )

        # Save latest history ID
        state["historyId"] = new_history_id
        state["processed_ids"] = list(processed_ids)

        save_state(state)

        print("\n✅ State updated.")

    except Exception as e:

        print(
            "❌ Error processing Pub/Sub message:",
            e
        )

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )