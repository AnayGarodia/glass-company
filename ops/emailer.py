"""Business email via AgentMail (agent-native inbox). Send + read.

Discloses AI authorship in every outgoing message.
"""
import base64
from pathlib import Path
import requests

API = "https://api.agentmail.to/v0"
INBOX = "glasscomany@agentmail.to"
DISCLOSURE = ('<hr><p style="color:#888;font-size:12px">This business is run '
              "autonomously by an AI (Claude). Replies are read and answered "
              "by the AI. Refunds are instant and no-questions-asked.</p>")


def _post(api_key, path, payload):
    r = requests.post(API + path, json=payload,
                      headers={"Authorization": f"Bearer {api_key}"}, timeout=30)
    r.raise_for_status()
    return r.json()


def _get(api_key, path):
    r = requests.get(API + path,
                     headers={"Authorization": f"Bearer {api_key}"}, timeout=30)
    r.raise_for_status()
    return r.json()


def send_delivery(api_key, to, subject, html, pdf_path=None,
                  inbox=INBOX) -> str:
    payload = {"to": to, "subject": subject, "html": html + DISCLOSURE}
    if pdf_path:
        p = Path(pdf_path)
        payload["attachments"] = [{
            "filename": p.name,
            "content_type": "application/pdf",
            "content_disposition": "attachment",
            "content": base64.b64encode(p.read_bytes()).decode(),
        }]
    return _post(api_key, f"/inboxes/{inbox}/messages/send", payload)["message_id"]


def fetch_inbound(api_key, inbox=INBOX) -> list[dict]:
    """List messages in the business inbox (verification mail, replies)."""
    return _get(api_key, f"/inboxes/{inbox}/messages").get("messages", [])


def get_message(api_key, message_id, inbox=INBOX) -> dict:
    return _get(api_key, f"/inboxes/{inbox}/messages/{message_id}")
