"""Send customer email via Resend. Discloses AI authorship in every message."""
import base64
from pathlib import Path
import requests

API = "https://api.resend.com"
DEFAULT_SENDER = "The Glass Company <onboarding@resend.dev>"
DISCLOSURE = ('<hr><p style="color:#888;font-size:12px">This business is run '
              "autonomously by an AI (Claude). Replies are read and answered "
              "by the AI. Refunds are instant and no-questions-asked.</p>")


def _post(api_key, path, payload):
    r = requests.post(API + path, json=payload,
                      headers={"Authorization": f"Bearer {api_key}"}, timeout=30)
    r.raise_for_status()
    return r.json()


def send_delivery(api_key, to, subject, html, pdf_path=None,
                  sender=DEFAULT_SENDER) -> str:
    payload = {"from": sender, "to": [to], "subject": subject,
               "html": html + DISCLOSURE}
    if pdf_path:
        p = Path(pdf_path)
        payload["attachments"] = [{
            "filename": p.name,
            "content": base64.b64encode(p.read_bytes()).decode(),
        }]
    return _post(api_key, "/emails", payload)["id"]
