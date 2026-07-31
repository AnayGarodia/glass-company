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
    titles = {q["id"]: q.get("title", q["id"]) for q in data.get("questions", [])}
    out = []
    for sub in data.get("submissions", []):
        fields = {}
        for resp in sub.get("responses", []):
            title = titles.get(resp.get("questionId"), resp.get("questionId", ""))
            value = resp.get("answer")
            if isinstance(value, dict):
                value = value.get("value", "")
            elif isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            fields[title] = str(value if value is not None else "")
        out.append({
            "submission_id": sub.get("id", ""),
            "submitted_at": sub.get("submittedAt", ""),
            "fields": fields,
        })
    return out
