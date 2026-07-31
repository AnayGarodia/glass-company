"""Fetch intake form submissions from Tally."""
import requests

API = "https://api.tally.so"


def _get(api_key, path):
    r = requests.get(API + path, headers={"Authorization": f"Bearer {api_key}"},
                     timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_intakes(api_key, form_id) -> list[dict]:
    data = _get(api_key, f"/forms/{form_id}/submissions")
    out = []
    for sub in data.get("submissions", []):
        fields = {}
        for resp in sub.get("responses", []):
            title = (resp.get("question") or {}).get("title", "")
            value = (resp.get("answer") or {}).get("value", "")
            fields[title] = str(value)
        raw = fields.get("Order number", "")
        digits = "".join(c for c in raw if c.isdigit())
        out.append({
            "order_number": int(digits) if digits else None,
            "submitted_at": sub.get("submittedAt", ""),
            "fields": fields,
        })
    return out
