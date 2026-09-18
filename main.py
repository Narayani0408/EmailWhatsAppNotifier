import os

from gmail_service import get_gmail_service
from email_utils import get_email_body, clean_email_body
from whatsapp_service import send_whatsapp_message


# Get Gmail service
service = get_gmail_service()


# Get latest email
# Check connected Gmail account
profile = service.users().getProfile(userId="me").execute()

print("Gmail account:", profile["emailAddress"])


# Get latest emails
results = service.users().messages().list(
    userId="me",
    maxResults=1
).execute()

messages = results.get("messages", [])

print("\n========== EMAILS FOUND BY GMAIL API ==========\n")

if messages:

    for i, msg in enumerate(messages, start=1):

        message = service.users().messages().get(
            userId="me",
            id=msg["id"],
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

        print(f"Email {i}")
        print("ID:", msg["id"])
        print("From:", sender)
        print("Subject:", subject)
        print("Labels:", message.get("labelIds", []))
        print("------------------------")

else:

    print("No emails found.")

print("\n==============================================")


# Check if we have seen this email before

if os.path.exists("last_email.txt"):

    with open("last_email.txt", "r") as file:
        last_email_id = file.read().strip()

else:

    last_email_id = ""


print("\nChecking for new email...")


if messages:

    current_email_id = messages[0]["id"]

    print("Previous Email ID:", last_email_id)
    print("Current Email ID:", current_email_id)


    if current_email_id == last_email_id:

        print("No new email.")


    else:

        print("\n🎉 NEW EMAIL FOUND!")


        # Get email body
        # Get email body
        # Get email body
        payload = message["payload"]

        body = get_email_body(payload)

        clean_body = clean_email_body(body)

        print("\n💬 Body:")
        print(clean_body)


        # Create short summary
        words = clean_body.split()

        if len(words) > 30:
            summary = " ".join(words[:30]) + "..."
        else:
            summary = clean_body


        print("\n💬 Summary:")
        print(summary)


        # Create WhatsApp message
        notification = f"""📧 New Email
👤 From: {sender}
📝 Subject: {subject}
💬 Summary: {summary}"""


        print("\n📱 WhatsApp Message")
        print("-------------------------")
        print(notification)
        print("-------------------------")


        # Send WhatsApp message
        send_whatsapp_message(notification)


        # Save email ID
        with open("last_email.txt", "w") as file:
            file.write(current_email_id)


        print("\nEmail ID saved.")


else:

    print("No emails found.")