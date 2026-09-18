import os
import requests
from dotenv import load_dotenv


load_dotenv()


ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
TO_NUMBER = os.getenv("WHATSAPP_TO_NUMBER")


API_URL = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"


def send_whatsapp_message(message):

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": TO_NUMBER,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=data
    )

    print("Status Code:", response.status_code)
    print("Response:", response.json())