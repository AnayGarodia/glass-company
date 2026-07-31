# Glass Company Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the $0-setup autonomous artifact shop: deterministic Python plumbing (orders, intake, email, generation, dashboard) orchestrated by a scheduled `claude -p` run, per `docs/superpowers/specs/2026-07-30-glass-company-design.md`.

**Architecture:** Small pure-Python modules under `ops/` do everything deterministic (Lemon Squeezy polling, Tally intake, Resend email, crossword layout, HTML→PDF, ledger, dashboard build). A launchd job runs `claude -p` with a runbook; Claude uses the modules as tools and does the judgment work (clue writing, dossier prose, QA, refusals, journal entries). State is JSONL + markdown in-repo; the public dashboard is a static site rebuilt and pushed each run (Cloudflare Pages auto-deploys).

**Tech Stack:** Python 3.11+ (stdlib + `requests` + `pytest` only), headless Chrome for PDF rendering, Lemon Squeezy API, Tally API, Resend API, launchd, Cloudflare Pages.

## Global Constraints

- Spend $0 before first revenue; $50 lifetime cap (spec).
- No new Python dependencies beyond `requests` and `pytest`.
- All money values stored as integer cents.
- All state lives in the repo: `data/ledger.jsonl`, `journal/*.md`, `site/`.
- Secrets come from env vars only (`LEMONSQUEEZY_API_KEY`, `TALLY_API_KEY`, `RESEND_API_KEY`), loaded from `~/.config/glass-company/env`; never committed.
- Every public post and customer email is disclosed as AI-authored.
- Dossier-format safety gate per spec: gift framing, no minors, no harassment → refuse + instant refund.
- Python files: one responsibility each, keep under ~150 lines.

## File Structure

```
glass-company/
  MANDATE.md                    # autonomy boundaries (spec §Mandate)
  SETUP.md                      # Anay's one-time setup checklist
  RUNBOOK-FULFILL.md            # per-run orchestration instructions for claude -p
  RUNBOOK-WEEKLY.md             # weekly deep-run instructions
  ops/
    __init__.py
    ledger.py                   # append-only event log + P&L summary
    lemonsqueezy.py             # orders + refunds client
    tally.py                    # intake form responses client
    emailer.py                  # Resend send w/ attachment + inbound poll
    crossword.py                # criss-cross grid placement (pure)
    render.py                   # template fill + headless-Chrome PDF
    dashboard.py                # ledger+journal → static site/
  templates/
    crossword.html
    dossier.html
    briefing.html
    dashboard.html
  bin/
    fulfill-run.sh              # env + claude -p wrapper (launchd target)
  launchd/
    ai.glasscompany.fulfill.plist
  data/ledger.jsonl             # created at runtime
  journal/                      # decision journal entries
  site/                         # generated dashboard (committed, CF Pages root)
  tests/
    test_ledger.py
    test_lemonsqueezy.py
    test_tally.py
    test_emailer.py
    test_crossword.py
    test_render.py
    test_dashboard.py
```

---

### Task 1: Ledger

**Files:**
- Create: `ops/__init__.py` (empty), `ops/ledger.py`
- Test: `tests/test_ledger.py`

**Interfaces:**
- Produces: `record(event: dict, path=DEFAULT_PATH) -> dict` — appends one JSON line; requires keys `ts` (ISO str), `type` (str, one of `sale|cost|refund|fulfillment|decision|refusal`); returns the event. `load(path) -> list[dict]`. `summary(events: list[dict]) -> dict` with keys `revenue_cents, costs_cents, refunds_cents, net_cents, orders, fulfilled`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_ledger.py
import json
from ops import ledger

def test_record_and_load(tmp_path):
    p = tmp_path / "ledger.jsonl"
    e = ledger.record({"ts": "2026-07-30T12:00:00Z", "type": "sale",
                       "order_id": "1", "amount_cents": 1500}, path=p)
    assert e["type"] == "sale"
    events = ledger.load(p)
    assert events == [e]

def test_record_rejects_bad_type(tmp_path):
    import pytest
    with pytest.raises(ValueError):
        ledger.record({"ts": "x", "type": "party"}, path=tmp_path / "l.jsonl")

def test_summary():
    events = [
        {"ts": "t", "type": "sale", "order_id": "1", "amount_cents": 1500},
        {"ts": "t", "type": "sale", "order_id": "2", "amount_cents": 1500},
        {"ts": "t", "type": "refund", "order_id": "2", "amount_cents": 1500},
        {"ts": "t", "type": "cost", "label": "domain", "amount_cents": 1000},
        {"ts": "t", "type": "fulfillment", "order_id": "1"},
    ]
    s = ledger.summary(events)
    assert s == {"revenue_cents": 3000, "costs_cents": 1000,
                 "refunds_cents": 1500, "net_cents": 500,
                 "orders": 2, "fulfilled": 1}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_ledger.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'ops'` (or ImportError)

- [ ] **Step 3: Write minimal implementation**

```python
# ops/ledger.py
"""Append-only business event log. One JSON object per line."""
import json
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "ledger.jsonl"
VALID_TYPES = {"sale", "cost", "refund", "fulfillment", "decision", "refusal"}


def record(event: dict, path=DEFAULT_PATH) -> dict:
    if event.get("type") not in VALID_TYPES:
        raise ValueError(f"bad event type: {event.get('type')!r}")
    if "ts" not in event:
        raise ValueError("event needs ts")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")
    return event


def load(path=DEFAULT_PATH) -> list[dict]:
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def summary(events: list[dict]) -> dict:
    rev = sum(e.get("amount_cents", 0) for e in events if e["type"] == "sale")
    costs = sum(e.get("amount_cents", 0) for e in events if e["type"] == "cost")
    refunds = sum(e.get("amount_cents", 0) for e in events if e["type"] == "refund")
    return {
        "revenue_cents": rev,
        "costs_cents": costs,
        "refunds_cents": refunds,
        "net_cents": rev - costs - refunds,
        "orders": len({e.get("order_id") for e in events if e["type"] == "sale"}),
        "fulfilled": sum(1 for e in events if e["type"] == "fulfillment"),
    }
```

Also create empty `ops/__init__.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_ledger.py -v`
Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add ops/__init__.py ops/ledger.py tests/test_ledger.py
git commit -m "feat: append-only ledger with P&L summary"
```

---

### Task 2: Lemon Squeezy client

**Files:**
- Create: `ops/lemonsqueezy.py`
- Test: `tests/test_lemonsqueezy.py`

**Interfaces:**
- Consumes: env var `LEMONSQUEEZY_API_KEY`.
- Produces: `list_orders(api_key) -> list[dict]` — each `{"order_id": str, "order_number": int, "email": str, "product_name": str, "total_cents": int, "status": str, "created_at": str}`. `refund_order(api_key, order_id: str) -> bool`. Base URL constant `API = "https://api.lemonsqueezy.com/v1"`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_lemonsqueezy.py
from unittest import mock
from ops import lemonsqueezy as ls

FAKE_ORDERS = {"data": [{
    "id": "42",
    "attributes": {
        "order_number": 1001, "user_email": "a@b.com",
        "first_order_item": {"product_name": "Custom Crossword"},
        "total": 1500, "status": "paid",
        "created_at": "2026-07-30T12:00:00Z"},
}]}

def test_list_orders_normalizes():
    with mock.patch.object(ls, "_get", return_value=FAKE_ORDERS) as g:
        orders = ls.list_orders("key")
    g.assert_called_once_with("key", "/orders")
    assert orders == [{"order_id": "42", "order_number": 1001,
                       "email": "a@b.com", "product_name": "Custom Crossword",
                       "total_cents": 1500, "status": "paid",
                       "created_at": "2026-07-30T12:00:00Z"}]

def test_refund_posts():
    with mock.patch.object(ls, "_post", return_value={"data": {}}) as p:
        assert ls.refund_order("key", "42") is True
    p.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_lemonsqueezy.py -v`
Expected: FAIL with ImportError/AttributeError

- [ ] **Step 3: Write minimal implementation**

```python
# ops/lemonsqueezy.py
"""Thin Lemon Squeezy API client. Money in integer cents."""
import requests

API = "https://api.lemonsqueezy.com/v1"


def _headers(api_key):
    return {"Authorization": f"Bearer {api_key}",
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json"}


def _get(api_key, path):
    r = requests.get(API + path, headers=_headers(api_key), timeout=30)
    r.raise_for_status()
    return r.json()


def _post(api_key, path, payload):
    r = requests.post(API + path, headers=_headers(api_key), json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def list_orders(api_key) -> list[dict]:
    data = _get(api_key, "/orders")
    out = []
    for item in data.get("data", []):
        a = item["attributes"]
        out.append({
            "order_id": item["id"],
            "order_number": a["order_number"],
            "email": a["user_email"],
            "product_name": (a.get("first_order_item") or {}).get("product_name", ""),
            "total_cents": a["total"],
            "status": a["status"],
            "created_at": a["created_at"],
        })
    return out


def refund_order(api_key, order_id: str) -> bool:
    _post(api_key, f"/orders/{order_id}/refund", {})
    return True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_lemonsqueezy.py -v`
Expected: 2 PASS

- [ ] **Step 5: Commit**

```bash
git add ops/lemonsqueezy.py tests/test_lemonsqueezy.py
git commit -m "feat: Lemon Squeezy orders + refund client"
```

---

### Task 3: Tally intake client

**Files:**
- Create: `ops/tally.py`
- Test: `tests/test_tally.py`

**Interfaces:**
- Consumes: env var `TALLY_API_KEY`; Tally form has a required field labeled exactly `Order number`.
- Produces: `fetch_intakes(api_key, form_id) -> list[dict]` — each `{"order_number": int | None, "submitted_at": str, "fields": dict[str, str]}` where `fields` maps question label → answer text. Order number parsed from the `Order number` field (`None` if unparseable — runbook handles the mismatch).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_tally.py
from unittest import mock
from ops import tally

FAKE = {"submissions": [{
    "submittedAt": "2026-07-30T13:00:00Z",
    "responses": [
        {"question": {"title": "Order number"}, "answer": {"value": "1001"}},
        {"question": {"title": "Who is this for?"}, "answer": {"value": "My wife Maya"}},
    ]}]}

def test_fetch_intakes_normalizes():
    with mock.patch.object(tally, "_get", return_value=FAKE):
        intakes = tally.fetch_intakes("key", "form123")
    assert intakes == [{
        "order_number": 1001,
        "submitted_at": "2026-07-30T13:00:00Z",
        "fields": {"Order number": "1001", "Who is this for?": "My wife Maya"},
    }]

def test_bad_order_number_is_none():
    bad = {"submissions": [{"submittedAt": "t", "responses": [
        {"question": {"title": "Order number"}, "answer": {"value": "dunno"}}]}]}
    with mock.patch.object(tally, "_get", return_value=bad):
        assert tally.fetch_intakes("k", "f")[0]["order_number"] is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_tally.py -v`
Expected: FAIL with ImportError/AttributeError

- [ ] **Step 3: Write minimal implementation**

```python
# ops/tally.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_tally.py -v`
Expected: 2 PASS

- [ ] **Step 5: Commit**

```bash
git add ops/tally.py tests/test_tally.py
git commit -m "feat: Tally intake submissions client"
```

---

### Task 4: Emailer (Resend)

**Files:**
- Create: `ops/emailer.py`
- Test: `tests/test_emailer.py`

**Interfaces:**
- Consumes: env var `RESEND_API_KEY`.
- Produces: `send_delivery(api_key, to: str, subject: str, html: str, pdf_path: str | None = None, sender: str = DEFAULT_SENDER) -> str` (returns Resend message id). `DEFAULT_SENDER = "The Glass Company <onboarding@resend.dev>"` (swap after a domain exists). Every email footer discloses AI authorship — enforced here, not in the runbook.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_emailer.py
import base64
from unittest import mock
from ops import emailer

def test_send_delivery_builds_payload(tmp_path):
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"%PDF-fake")
    with mock.patch.object(emailer, "_post", return_value={"id": "msg_1"}) as p:
        mid = emailer.send_delivery("key", "a@b.com", "Your crossword",
                                    "<p>hi</p>", pdf_path=str(pdf))
    assert mid == "msg_1"
    payload = p.call_args.args[2]
    assert payload["to"] == ["a@b.com"]
    assert "run autonomously by an AI" in payload["html"]
    att = payload["attachments"][0]
    assert att["filename"] == "x.pdf"
    assert base64.b64decode(att["content"]) == b"%PDF-fake"

def test_send_without_attachment():
    with mock.patch.object(emailer, "_post", return_value={"id": "m"}) as p:
        emailer.send_delivery("key", "a@b.com", "s", "<p>x</p>")
    assert "attachments" not in p.call_args.args[2]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_emailer.py -v`
Expected: FAIL with ImportError/AttributeError

- [ ] **Step 3: Write minimal implementation**

```python
# ops/emailer.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_emailer.py -v`
Expected: 2 PASS

- [ ] **Step 5: Commit**

```bash
git add ops/emailer.py tests/test_emailer.py
git commit -m "feat: Resend delivery email with disclosure footer"
```

---

### Task 5: Crossword generator

**Files:**
- Create: `ops/crossword.py`
- Test: `tests/test_crossword.py`

**Interfaces:**
- Produces: `generate(words: list[str], seed: int = 0) -> dict | None`. Words are answers (A–Z only after normalization). Returns `None` if fewer than 70% of words place. Result dict: `{"placements": [{"word": str, "row": int, "col": int, "dir": "across"|"down", "number": int}], "rows": int, "cols": int, "cells": {"r,c": "LETTER"}}` — coordinates normalized to start at 0; numbering assigned top-left to bottom-right like a real puzzle. Clues are written by Claude at runtime; this module does layout only.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_crossword.py
from ops import crossword

WORDS = ["MAYA", "AMSTERDAM", "TIRAMISU", "SCRABBLE", "OCTOBER", "BEACH"]

def test_generates_connected_grid():
    g = crossword.generate(WORDS, seed=1)
    assert g is not None
    assert len(g["placements"]) >= 5  # 70% of 6 rounds up to 5
    # every placement's letters must be consistent with the cell map
    for p in g["placements"]:
        for i, ch in enumerate(p["word"]):
            r = p["row"] + (i if p["dir"] == "down" else 0)
            c = p["col"] + (i if p["dir"] == "across" else 0)
            assert g["cells"][f"{r},{c}"] == ch
    # normalized: min row/col is 0
    coords = [tuple(map(int, k.split(","))) for k in g["cells"]]
    assert min(r for r, _ in coords) == 0 and min(c for _, c in coords) == 0

def test_numbers_are_unique_per_start():
    g = crossword.generate(WORDS, seed=1)
    starts = {(p["row"], p["col"], p["dir"]) for p in g["placements"]}
    assert len(starts) == len(g["placements"])

def test_impossible_words_return_none():
    assert crossword.generate(["QQQQ", "ZZZZ", "XXXX"], seed=0) is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_crossword.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Write minimal implementation**

```python
# ops/crossword.py
"""Criss-cross crossword layout. Pure, deterministic per seed. Layout only."""
import random


def _fits(cells, word, r, c, d):
    dr, dc = (0, 1) if d == "across" else (1, 0)
    crossed = False
    # cell before start and after end must be empty
    if (r - dr, c - dc) in cells or (r + dr * len(word), c + dc * len(word)) in cells:
        return False
    for i, ch in enumerate(word):
        rr, cc = r + dr * i, c + dc * i
        if (rr, cc) in cells:
            if cells[(rr, cc)] != ch:
                return False
            crossed = True
        else:
            # neighbors perpendicular to direction must be empty
            pr, pc = (1, 0) if d == "across" else (0, 1)
            if (rr + pr, cc + pc) in cells or (rr - pr, cc - pc) in cells:
                return False
    return crossed


def generate(words, seed: int = 0):
    words = [w.upper().replace(" ", "") for w in words]
    rng = random.Random(seed)
    order = sorted(words, key=len, reverse=True)
    cells: dict = {}
    placements = []
    first = order[0]
    for i, ch in enumerate(first):
        cells[(0, i)] = ch
    placements.append({"word": first, "row": 0, "col": 0, "dir": "across"})
    for word in order[1:]:
        options = []
        for i, ch in enumerate(word):
            for (r, c), cell_ch in cells.items():
                if cell_ch != ch:
                    continue
                options.append((r - i, c, "down", word))
                options.append((r, c - i, "across", word))
        rng.shuffle(options)
        for r, c, d, w in options:
            if _fits(cells, w, r, c, d):
                dr, dc = (0, 1) if d == "across" else (1, 0)
                for i, wch in enumerate(w):
                    cells[(r + dr * i, c + dc * i)] = wch
                placements.append({"word": w, "row": r, "col": c, "dir": d})
                break
    if len(placements) < max(2, -(-len(words) * 7 // 10)):  # ceil(70%)
        return None
    minr = min(r for r, _ in cells)
    minc = min(c for _, c in cells)
    for p in placements:
        p["row"] -= minr
        p["col"] -= minc
    norm_cells = {f"{r - minr},{c - minc}": ch for (r, c), ch in cells.items()}
    starts = sorted({(p["row"], p["col"]) for p in placements})
    numbers = {rc: i + 1 for i, rc in enumerate(starts)}
    for p in placements:
        p["number"] = numbers[(p["row"], p["col"])]
    return {
        "placements": placements,
        "rows": max(r for r, _ in cells) - minr + 1,
        "cols": max(c for _, c in cells) - minc + 1,
        "cells": norm_cells,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_crossword.py -v`
Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add ops/crossword.py tests/test_crossword.py
git commit -m "feat: criss-cross crossword layout generator"
```

---

### Task 6: Artifact templates + PDF renderer

**Files:**
- Create: `ops/render.py`, `templates/crossword.html`, `templates/dossier.html`, `templates/briefing.html`
- Test: `tests/test_render.py`

**Interfaces:**
- Consumes: crossword result dict from Task 5 (for the crossword template, Claude converts it to HTML table markup at runtime per RUNBOOK).
- Produces: `fill(template_name: str, context: dict[str, str]) -> str` — loads `templates/<name>.html`, substitutes `$key` placeholders via `string.Template.substitute` (KeyError on missing → caught by runbook QA). `render_pdf(html: str, out_pdf: str) -> str` — writes html to a temp file, renders via headless Chrome, returns `out_pdf`. `CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`.
- Templates define the visual quality bar: print CSS, real typography, A4. Each template's variable slots: crossword → `$title $subtitle $grid_html $across_clues $down_clues`; dossier → `$subject_name $codename $body_html`; briefing → `$operation_name $occasion $body_html`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_render.py
import os, subprocess
import pytest
from ops import render

def test_fill_substitutes():
    html = render.fill("dossier", {"subject_name": "Maya", "codename": "NIGHTINGALE",
                                   "body_html": "<p>classified</p>"})
    assert "NIGHTINGALE" in html and "classified" in html
    assert "$" not in html.replace("$;", "")  # no unfilled slots

def test_fill_missing_key_raises():
    with pytest.raises(KeyError):
        render.fill("dossier", {"subject_name": "Maya"})

@pytest.mark.skipif(not os.path.exists(render.CHROME), reason="no Chrome")
def test_render_pdf(tmp_path):
    out = render.render_pdf("<h1>hello</h1>", str(tmp_path / "o.pdf"))
    assert open(out, "rb").read(4) == b"%PDF"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_render.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Write minimal implementation**

```python
# ops/render.py
"""Fill HTML artifact templates and print them to PDF with headless Chrome."""
import subprocess, tempfile
from pathlib import Path
from string import Template

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def fill(template_name: str, context: dict) -> str:
    tpl = (TEMPLATES / f"{template_name}.html").read_text()
    return Template(tpl).substitute(context)


def render_pdf(html: str, out_pdf: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html)
        src = f.name
    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={out_pdf}", f"file://{src}"],
        check=True, capture_output=True, timeout=120)
    return out_pdf
```

Then create the three templates. They share a print-CSS base; each has a distinct visual identity. Full `templates/dossier.html` (the other two follow the same skeleton with their own slots and styling — write them fully in the implementation, not copies of dossier):

```html
<!-- templates/dossier.html -->
<!doctype html><html><head><meta charset="utf-8"><style>
  @page { size: A4; margin: 0; }
  body { margin: 0; font-family: "Courier New", monospace; background: #f4f1e8;
         color: #1a1a1a; }
  .page { width: 210mm; min-height: 297mm; padding: 22mm; box-sizing: border-box; }
  .stamp { border: 4px double #a00; color: #a00; display: inline-block;
           padding: 4px 14px; font-weight: bold; letter-spacing: 4px;
           transform: rotate(-6deg); font-size: 20px; }
  h1 { font-size: 30px; letter-spacing: 2px; border-bottom: 3px solid #1a1a1a;
       padding-bottom: 8px; }
  .meta { font-size: 13px; margin: 14px 0 26px; }
  .redact { background: #1a1a1a; color: #1a1a1a; padding: 0 6px; }
  .body p { line-height: 1.7; font-size: 14px; }
  .footer { margin-top: 30mm; font-size: 11px; color: #666; }
</style></head><body><div class="page">
  <div class="stamp">DECLASSIFIED</div>
  <h1>SUBJECT: $subject_name</h1>
  <div class="meta">CODENAME: <b>$codename</b> &nbsp;·&nbsp; CLEARANCE: EYES ONLY
    &nbsp;·&nbsp; FILE: GC-<span class="redact">████</span></div>
  <div class="body">$body_html</div>
  <div class="footer">Prepared with affection by The Glass Company — a business
    run autonomously by an AI. This document is a gift, and entirely fictional
    where it isn't entirely true.</div>
</div></body></html>
```

`templates/crossword.html`: clean editorial style (Georgia/serif, generous margins), slots `$title $subtitle $grid_html $across_clues $down_clues`, grid rendered as a CSS-styled `<table>` (Claude builds `$grid_html` table markup from the Task 5 dict per RUNBOOK), clue lists in two columns.
`templates/briefing.html`: dark-cover spy style (black cover block, stencil headline `OPERATION: $operation_name`, `$occasion` strapline, `$body_html` sections).
Both must be complete standalone files with the same `@page`/`.page` print CSS pattern as dossier — no shared includes.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_render.py -v`
Expected: 2-3 PASS (PDF test skips if Chrome absent)

- [ ] **Step 5: Visual check — render one sample of each template to PDF and eyeball**

```bash
python3 - <<'EOF'
from ops import render
samples = {
  "dossier": {"subject_name": "Test Subject", "codename": "SAMPLE",
              "body_html": "<p>Line one.</p><p>Line two.</p>"},
  "crossword": {"title": "The Test Crossword", "subtitle": "A sample",
                "grid_html": "<table><tr><td>A</td></tr></table>",
                "across_clues": "<li>One</li>", "down_clues": "<li>Two</li>"},
  "briefing": {"operation_name": "SAMPLE", "occasion": "Testing",
               "body_html": "<p>Brief.</p>"},
}
for name, ctx in samples.items():
    render.render_pdf(render.fill(name, ctx), f"/tmp/sample-{name}.pdf")
    print(name, "ok")
EOF
```

Open the three PDFs; each must look designed (typography, margins, identity), not like a default browser print.

- [ ] **Step 6: Commit**

```bash
git add ops/render.py templates/ tests/test_render.py
git commit -m "feat: artifact templates + headless-Chrome PDF renderer"
```

---

### Task 7: Dashboard site generator

**Files:**
- Create: `ops/dashboard.py`, `templates/dashboard.html`
- Test: `tests/test_dashboard.py`

**Interfaces:**
- Consumes: `ledger.load()` / `ledger.summary()` (Task 1); journal entries `journal/*.md` (filename `YYYY-MM-DD-slug.md`, first line `# Title`).
- Produces: `build_site(ledger_path, journal_dir, out_dir) -> str` — writes `out_dir/index.html`, returns path. Page shows: net P&L headline (dollars, cent precision), revenue/costs/refunds, order + fulfilled counts, full decision journal (newest first, rendered as `<pre>`-safe text), and an honest "What is this" section. Uses `templates/dashboard.html` with slots `$net $revenue $costs $refunds $orders $fulfilled $journal_html $updated`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_dashboard.py
from ops import dashboard, ledger

def test_build_site(tmp_path):
    lp = tmp_path / "ledger.jsonl"
    ledger.record({"ts": "2026-07-30T12:00:00Z", "type": "sale",
                   "order_id": "1", "amount_cents": 1500}, path=lp)
    jd = tmp_path / "journal"; jd.mkdir()
    (jd / "2026-07-30-first-sale.md").write_text("# First sale\n\nSomeone paid!")
    out = dashboard.build_site(lp, jd, tmp_path / "site")
    html = open(out).read()
    assert "$15.00" in html          # revenue and net
    assert "First sale" in html
    assert "run autonomously by an AI" in html

def test_empty_state(tmp_path):
    out = dashboard.build_site(tmp_path / "none.jsonl", tmp_path / "nojournal",
                               tmp_path / "site")
    assert "$0.00" in open(out).read()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_dashboard.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Write minimal implementation**

```python
# ops/dashboard.py
"""Build the public glass dashboard: static HTML from ledger + journal."""
import html as htmlmod
from datetime import datetime, timezone
from pathlib import Path
from ops import ledger
from ops.render import fill


def _dollars(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    return f"{sign}${abs(cents) / 100:.2f}"


def _journal_html(journal_dir: Path) -> str:
    if not journal_dir.exists():
        return "<p>No entries yet.</p>"
    parts = []
    for f in sorted(journal_dir.glob("*.md"), reverse=True):
        text = f.read_text()
        lines = text.splitlines()
        title = lines[0].lstrip("# ").strip() if lines else f.stem
        body = htmlmod.escape("\n".join(lines[1:]).strip())
        parts.append(f"<article><h3>{htmlmod.escape(title)}</h3>"
                     f"<div class='date'>{f.stem[:10]}</div>"
                     f"<pre>{body}</pre></article>")
    return "\n".join(parts) or "<p>No entries yet.</p>"


def build_site(ledger_path, journal_dir, out_dir) -> str:
    s = ledger.summary(ledger.load(ledger_path))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    page = fill("dashboard", {
        "net": _dollars(s["net_cents"]),
        "revenue": _dollars(s["revenue_cents"]),
        "costs": _dollars(s["costs_cents"]),
        "refunds": _dollars(s["refunds_cents"]),
        "orders": str(s["orders"]),
        "fulfilled": str(s["fulfilled"]),
        "journal_html": _journal_html(Path(journal_dir)),
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    })
    out = out_dir / "index.html"
    out.write_text(page)
    return str(out)
```

`templates/dashboard.html`: complete standalone page, slots as above. Design bar: this page is the launch story — dark, austere, numbers huge (the net P&L is the hero, 96px), monospace figures, journal below. Must include a "What is this" section stating verbatim: "This business is run autonomously by an AI (Claude). The human set up the payment accounts and left. Every dollar and every decision appears on this page." Products section links to the three Lemon Squeezy checkout URLs (placeholder hrefs `#` until store exists; the fulfillment run rewrites them from `data/products.json` — written during launch, Task 9).

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_dashboard.py -v`
Expected: 2 PASS

- [ ] **Step 5: Commit**

```bash
git add ops/dashboard.py templates/dashboard.html tests/test_dashboard.py
git commit -m "feat: public glass dashboard generator"
```

---

### Task 8: Mandate, runbooks, launchd wiring

**Files:**
- Create: `MANDATE.md`, `RUNBOOK-FULFILL.md`, `RUNBOOK-WEEKLY.md`, `bin/fulfill-run.sh`, `launchd/ai.glasscompany.fulfill.plist`

**Interfaces:**
- Consumes: every `ops/` module above.
- Produces: the orchestration layer. `bin/fulfill-run.sh` sources `~/.config/glass-company/env` and runs `claude -p "$(cat RUNBOOK-FULFILL.md)" --permission-mode acceptEdits` from the repo root. launchd plist runs it every 30 min between 08:00–23:00 local. No tests (declarative + prose); verified in Task 9 smoke run.

- [ ] **Step 1: Write MANDATE.md**

Content requirements (write in full, first person, addressed to the operating Claude): the May/May-not lists copied from the spec §Mandate verbatim; budget state ($50 lifetime cap, $0 spent target pre-revenue); refund policy (instant, no questions); safety gate for dossier orders (buyer must know subject personally, no minors, refuse harassment/surveillance/doxxing → `refusal` ledger event + refund + polite email); disclosure rule (every email and post identifies as AI); escalation rule (anything outside the mandate → write a journal entry titled "NEEDS HUMAN" and do nothing else about it).

- [ ] **Step 2: Write RUNBOOK-FULFILL.md**

The per-run checklist, in full, ordered:
1. Read `MANDATE.md`.
2. `ls data/` and read `data/state.json` (JSON: `{"fulfilled_order_ids": [], "seen_intake_ts": []}`; create if missing).
3. Poll orders: `ls.list_orders(env key)`. New paid orders not in `fulfilled_order_ids` → record `sale` ledger events.
4. Fetch intakes: `tally.fetch_intakes(...)`, match `order_number` to orders.
5. For each order with intake: safety-gate check per MANDATE; then generate the artifact — crossword: pick 8–14 answer words from intake facts, `crossword.generate(words)`, retry other seeds/word subsets if `None`, write clues yourself, build `$grid_html` table (numbered cells, empty cells `class="blk"`), `render.fill` + `render.render_pdf`; dossier/briefing: write `$body_html` yourself from intake facts (funny, warm, specific — never mean), fill + render.
6. Self-QA the PDF (open it, check: names spelled right, every fact used correctly, crossword solvable against clue list, layout unbroken). Fail → regenerate once; fail again → journal entry "NEEDS HUMAN", skip delivery.
7. Deliver via `emailer.send_delivery`, record `fulfillment` event, update `state.json`.
8. Orders paid >24h with no intake → send reminder email; >7 days → `ls.refund_order`, record `refund`. Poll the Tally *support* form (id in `data/products.json` under `"support_form_id"`) the same way as intake; any refund request → refund instantly + confirmation email; other messages → answer honestly or journal "NEEDS HUMAN".
9. Rebuild dashboard: `dashboard.build_site("data/ledger.jsonl", "journal", "site")`.
10. If anything notable happened, write a journal entry (`journal/YYYY-MM-DD-slug.md`).
11. `git add -A && git commit -m "ops: fulfillment run" && git push` (push triggers Cloudflare Pages deploy).
12. Total run should be idempotent: re-running with no new orders changes nothing but the dashboard timestamp.

- [ ] **Step 3: Write RUNBOOK-WEEKLY.md**

Weekly deep run, in full: compute per-format sales from ledger; decide kills/launches/pricing (record each as a `decision` ledger event with reasoning); execute product changes in Lemon Squeezy dashboard via API where possible, else journal "NEEDS HUMAN"; one marketing action max per week (a post where self-promo is allowed, disclosed as AI, linking the dashboard); write the "board meeting" journal entry; rebuild + push.

- [ ] **Step 4: Write bin/fulfill-run.sh and the launchd plist**

```bash
#!/bin/bash
# bin/fulfill-run.sh — launchd entrypoint for the fulfillment run
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; source "$HOME/.config/glass-company/env"; set +a
/usr/local/bin/claude -p "$(cat RUNBOOK-FULFILL.md)" \
  --permission-mode acceptEdits --max-turns 60 \
  >> logs/fulfill.log 2>&1
```

(`chmod +x bin/fulfill-run.sh`; create `logs/` with a `.gitkeep`; add `logs/*.log` to `.gitignore`. Verify the `claude` binary path with `which claude` and use that path.)

```xml
<!-- launchd/ai.glasscompany.fulfill.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>ai.glasscompany.fulfill</string>
  <key>ProgramArguments</key><array>
    <string>/Users/aakritigarodia/Desktop/Projects/glass-company/bin/fulfill-run.sh</string>
  </array>
  <key>StartInterval</key><integer>1800</integer>
  <key>StandardErrorPath</key>
  <string>/Users/aakritigarodia/Desktop/Projects/glass-company/logs/launchd.err</string>
</dict></plist>
```

(Weekly run: reuse the same wrapper pattern — the Sunday fulfillment run also executes RUNBOOK-WEEKLY.md; keep one plist.)
Note: RUNBOOK-FULFILL.md step 1 gains a line — "If today is Sunday and no `decision` event exists in the last 6 days, also execute RUNBOOK-WEEKLY.md."

- [ ] **Step 5: Commit**

```bash
git add MANDATE.md RUNBOOK-FULFILL.md RUNBOOK-WEEKLY.md bin/ launchd/ .gitignore logs/.gitkeep
git commit -m "feat: mandate, runbooks, launchd ops loop"
```

---

### Task 9: Setup guide, launch content, smoke run

**Files:**
- Create: `SETUP.md`, `data/products.json`, `site/` (first real build), launch post drafts in `journal/`

**Interfaces:**
- Consumes: everything.
- Produces: `SETUP.md` — Anay's exact one-time checklist; `data/products.json` — `{"support_form_id": str, "products": [{"format": "crossword", "name": str, "price_cents": int, "checkout_url": str, "tally_form_id": str}]}` (ids/urls filled after accounts exist); launch drafts.

- [ ] **Step 1: Write SETUP.md**

Exact steps with URLs: 1) create Lemon Squeezy account + store, complete KYC, create API key at Settings → API, put in `~/.config/glass-company/env` as `LEMONSQUEEZY_API_KEY=...`; 2) create Resend account, API key → `RESEND_API_KEY=...`; 3) create Tally account, one intake form per format plus one support/refund form (field specs listed per form, first field exactly `Order number`), API key → `TALLY_API_KEY=...`; 4) create the three products in Lemon Squeezy (names/prices/descriptions provided verbatim in the file, $15 each, checkout success URL → the Tally form); 5) push repo to GitHub, connect Cloudflare Pages, build output dir `site/`; 6) `chmod 600` the env file; 7) `launchctl load ~/Library/LaunchAgents/ai.glasscompany.fulfill.plist` (after copying the plist there); 8) read and approve MANDATE.md by replying in chat.

- [ ] **Step 2: Write product copy and launch drafts**

Full store copy for the three products (title, 2-3 paragraph description, the exact intake questions per format) written into SETUP.md for Anay to paste. Launch drafts written as `journal/2026-XX-XX-launch-{hn,reddit}.md`: Show HN post (title + body, first person AI, links dashboard, honest about the experiment) and one subreddit post. Drafts marked `status: draft — do not post until store is live`.

- [ ] **Step 3: Full test suite + first dashboard build**

Run: `python3 -m pytest tests/ -v` — all pass.
Then build the real site once: `python3 -c "from ops.dashboard import build_site; build_site('data/ledger.jsonl','journal','site')"` and verify `site/index.html` renders (open it).

- [ ] **Step 4: Smoke-run the fulfillment loop without accounts**

Run `bin/fulfill-run.sh` manually once with a stub env file (fake keys). Expected: the run reads the mandate, finds no orders (API 401s are caught and journaled as "NEEDS HUMAN: no valid API keys yet"), rebuilds the dashboard, commits. Verify the journal entry and commit exist. This proves the loop is safe to schedule before accounts exist.

- [ ] **Step 5: Commit**

```bash
git add SETUP.md data/products.json site/ journal/
git commit -m "feat: setup guide, launch content, first dashboard build"
```

---

## Verification (whole-plan)

1. `python3 -m pytest tests/ -v` — all green.
2. Three sample PDFs at `/tmp/sample-*.pdf` look designed.
3. `site/index.html` opens and shows $0.00 honestly.
4. Manual `bin/fulfill-run.sh` completes idempotently twice in a row.
5. SETUP.md is executable by Anay in ~45 min without asking me anything.
