"""Fetch intake form submissions from Tally."""
import requests

API = "https://api.tally.so"


def _get(api_key, path):
    r = requests.get(API + path, headers={"Authorization": f"Bearer {api_key}"},
                     timeout=30)
    r.raise_for_status()
    return r.json()


MAX_PAGES = 100


def fetch_intakes(api_key, form_id) -> list[dict]:
    """Every submission on a form, newest first.

    Tally serves these 50 to a page and reports `hasMore`. Reading only the
    first page loses everything older than the newest 50 the moment a form
    carries a backlog — and a backlog is normal, since step 5 caps previews
    at 10 a day. Those submissions would never appear again on any later
    run: not fulfilled, not refused, not seen. So walk until Tally says
    there are no more pages.
    """
    out = []
    for page in range(1, MAX_PAGES + 1):
        data = _get(api_key, f"/forms/{form_id}/submissions?page={page}")
        titles = {q["id"]: q.get("title", q["id"])
                  for q in data.get("questions", [])}
        subs = data.get("submissions", [])
        for sub in subs:
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
        if not data.get("hasMore") or not subs:
            return out
    raise RuntimeError(
        f"form {form_id} still reports more submissions after {MAX_PAGES} "
        "pages; refusing to return a silently truncated list")
