import time
import os

from gmail_service import get_gmail_service
from email_utils import get_email_body, clean_email_body
from whatsapp_service import send_whatsapp_message


CHECK_INTERVAL = 60  # Check every 60 seconds


def check_for_new_email(service):

    results = service.users().messages().list(
        userId="me",
        maxResults=1
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        print("No emails found.")
        return

    current_email_id = messages[0]["id"]

    # Read previously processed email ID
    if os.path.exists("last_email.txt"):
        with open("last_email.txt", "r") as file:
            last_email_id = file.read().strip()
    else:
        last_email_id = ""

    print("\nChecking Gmail...")
    print("Previous Email ID:", last_email_id)
    print("Current Email ID:", current_email_id)

    # Check if email is new
    if current_email_id == last_email_id:
        print("No new email.")
        return

    print("🎉 NEW EMAIL FOUND!")

    # Get complete email
    message = service.users().messages().get(
        userId="me",
        id=current_email_id,
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

    # Get email body
    payload = message["payload"]

    body = get_email_body(payload)
    clean_body = clean_email_body(body)

    # Create short summary
    words = clean_body.split()

    if len(words) > 30:
        summary = " ".join(words[:30]) + "..."
    else:
        summary = clean_body

    # Create WhatsApp notification
    notification = f"""📧 New Email
👤 From: {sender}
📝 Subject: {subject}
💬 Summary: {summary}"""

    print("\n📱 WhatsApp Message")
    print("-------------------------")
    print(notification)
    print("-------------------------")

    # Send WhatsApp message
    success = send_whatsapp_message(notification)

    # Save email ID only if WhatsApp request succeeds
    if success:
        with open("last_email.txt", "w") as file:
            file.write(current_email_id)

        print("✅ Email ID saved.")
    else:
        print("❌ Email ID NOT saved because WhatsApp failed.")


# Connect to Gmail once
service = get_gmail_service()

print("====================================")
print("📧 Email → WhatsApp Automatic Checker")
print("====================================")
print("Checking Gmail every 60 seconds...")
print("Press CTRL + C to stop.\n")


# Keep running forever
while True:

    try:
        check_for_new_email(service)

    except Exception as e:
        print("❌ Error:", e)

    print("\nWaiting 60 seconds...")
    time.sleep(CHECK_INTERVAL)