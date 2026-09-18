import base64
import re
import html


def decode_body(data):

    decoded = base64.urlsafe_b64decode(
        data + "=" * (-len(data) % 4)
    )

    return decoded.decode("utf-8", errors="replace")


def get_email_body(payload):

    if payload.get("mimeType") == "text/plain":

        data = payload.get("body", {}).get("data")

        if data:
            return decode_body(data)

    for part in payload.get("parts", []):

        body = get_email_body(part)

        if body:
            return body

    return ""


def clean_email_body(body):

    # Remove HTML tags
    body = re.sub(r"<[^>]+>", " ", body)

    # Convert HTML entities
    body = html.unescape(body)

    # Remove extra spaces
    body = re.sub(r"\s+", " ", body)

    # Remove spaces from beginning and end
    body = body.strip()

    return body