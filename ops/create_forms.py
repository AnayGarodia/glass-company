"""One-shot: create the four Tally forms via API and write ids/urls to products.json.

Run: .venv/bin/python3 -m ops.create_forms
"""
import json
import os
import uuid
from pathlib import Path

import requests

API = "https://api.tally.so"
PRODUCTS = Path(__file__).resolve().parent.parent / "data" / "products.json"

PAY_NOTE = ("First: send the SOL amount shown on glasscompany.pages.dev to the "
            "wallet address there. Then paste your transaction signature below.")


def _b(btype, payload, group_type=None):
    return {"uuid": str(uuid.uuid4()), "type": btype,
            "groupUuid": str(uuid.uuid4()),
            "groupType": group_type or btype, "payload": payload}


def _q(label):
    return _b("TITLE", {"html": label}, "QUESTION")


def _text(placeholder, required=True):
    return _b("INPUT_TEXT", {"isRequired": required, "placeholder": placeholder})


def _area(placeholder, required=True):
    return _b("TEXTAREA", {"isRequired": required, "placeholder": placeholder})


def _email():
    return _b("INPUT_EMAIL", {"isRequired": True, "placeholder": "you@example.com"})


def _common_head(title):
    return [
        _b("FORM_TITLE", {"html": title}, "TEXT"),
        _q("Email (your artifact is delivered here)"), _email(),
        _q("Transaction signature — " + PAY_NOTE),
        _text("e.g. 5KtP...9xQz (from your wallet's transaction history)"),
    ]


FORMS = {
    "crossword": _common_head("The Custom Crossword — intake") + [
        _q("Who is this for, and what's the occasion?"),
        _area("e.g. my wife Maya, our 5th anniversary"),
        _q("10–15 single words that matter (names, places, pets, inside jokes) — one per line"),
        _area("MAYA\nAMSTERDAM\nTIRAMISU\n..."),
        _q("For each word, one line on why it matters"),
        _area("MAYA — obviously\nAMSTERDAM — where we met\n..."),
        _q("Anything to avoid?"), _area("Optional", required=False),
    ],
    "dossier": _common_head("The Declassified Dossier — intake") + [
        _q("Subject's name"), _text("Who is this file about?"),
        _q("Your relationship to them (you must know them personally)"),
        _text("e.g. best friend since college"),
        _q("The occasion"), _text("e.g. 30th birthday"),
        _q("5–10 funny true stories, quirks, or legends about them"),
        _area("The more specific, the better the file."),
        _q("Anything off-limits?"), _area("Optional", required=False),
    ],
    "briefing": _common_head("The Mission Briefing — intake") + [
        _q("The occasion"), _text("e.g. bachelor party, proposal, new job"),
        _q("Who's involved? (names and roles)"),
        _area("e.g. Jake (groom), Sam (best man)..."),
        _q("The actual plan, roughly"),
        _area("What's happening, when, where — I'll dramatize it."),
        _q("How far can the jokes go?"), _text("e.g. roast him gently / no mercy"),
    ],
    "support": [
        _b("FORM_TITLE", {"html": "The Glass Company — support & refunds"}, "TEXT"),
        _q("Email (the one you ordered with)"), _email(),
        _q("Transaction signature of your order"), _text("From your payment"),
        _q("What do you need?"), _text("refund / question / problem"),
        _q("Details"), _area("Refunds are instant and no-questions-asked."),
    ],
}


def main():
    key = os.environ["TALLY_API_KEY"]
    data = json.loads(PRODUCTS.read_text())
    for name, blocks in FORMS.items():
        r = requests.post(API + "/forms",
                          headers={"Authorization": f"Bearer {key}"},
                          json={"status": "PUBLISHED", "blocks": blocks},
                          timeout=30)
        r.raise_for_status()
        form = r.json()
        fid = form["id"]
        url = f"https://tally.so/r/{fid}"
        if name == "support":
            data["support_form_id"] = fid
            data["support_form_url"] = url
        else:
            for p in data["products"]:
                if p["format"] == name:
                    p["tally_form_id"] = fid
                    p["form_url"] = url
        print(f"{name}: {fid} {url}")
    PRODUCTS.write_text(json.dumps(data, indent=2))
    print("products.json updated")


if __name__ == "__main__":
    main()
