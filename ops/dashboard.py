"""Build the public glass dashboard: static HTML from ledger + journal."""
import html as htmlmod
import json
from datetime import datetime, timezone
from pathlib import Path

from ops import ledger
from ops.render import fill

PRODUCTS_PATH = Path(__file__).resolve().parent.parent / "data" / "products.json"


def _dollars(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    return f"{sign}${abs(cents) / 100:.2f}"


JOURNAL_RECENT = 12


def _journal_article(f: Path) -> str:
    lines = f.read_text().splitlines()
    title = lines[0].lstrip("# ").strip() if lines else f.stem
    body = htmlmod.escape("\n".join(lines[1:]).strip())
    return (f"<article><h3>{htmlmod.escape(title)}</h3>"
            f"<div class='date'>{f.stem[:10]}</div>"
            f"<pre>{body}</pre></article>")


def _journal_html(journal_dir: Path) -> str:
    """Newest JOURNAL_RECENT entries open; everything older folded into one
    <details>. The rule is recency only — never which entry it is — so the
    archive stays complete and nothing gets quietly curated out."""
    if not journal_dir.exists():
        return "<p>No entries yet.</p>"
    # Date prefix first, then write time — filenames alone sort several
    # same-day entries alphabetically, which scrambled 2026-07-31's order.
    files = sorted(journal_dir.glob("*.md"),
                   key=lambda p: (p.stem[:10], p.stat().st_mtime),
                   reverse=True)
    if not files:
        return "<p>No entries yet.</p>"
    parts = [_journal_article(f) for f in files[:JOURNAL_RECENT]]
    older = files[JOURNAL_RECENT:]
    if older:
        parts.append(
            f"<details><summary>Older entries ({len(older)})</summary>"
            + "\n".join(_journal_article(f) for f in older)
            + "</details>")
    return "\n".join(parts)


def _load_products() -> dict:
    if not PRODUCTS_PATH.exists():
        return {}
    return json.loads(PRODUCTS_PATH.read_text())


BLURBS = {
    "crossword": "A real, solvable crossword whose answers are your inside "
                 "jokes, your places, your people. Clues written for an "
                 "audience of one.",
    "dossier": "An affectionate intelligence file: codename, redaction bars, "
               "field observations. Warm, funny, never mean.",
    "briefing": "Your occasion — proposal, bachelor party, big goodbye — "
                "issued as a TOP SECRET operations packet.",
}


def _products_html(data: dict) -> str:
    cards = []
    sol_price = data.get("sol_price_usd_cents") or 0
    for p in data.get("products", []):
        url = p.get("form_url") or "#"
        fmt = p.get("format", "")
        sol = ""
        if sol_price:
            sol = f" · ≈ {p['price_cents'] / sol_price:.3f} SOL"
        cards.append(
            f"<div class='product'>"
            f"<a href='assets/sample-{fmt}.pdf'>"
            f"<img src='assets/sample-{fmt}.png' alt='Sample {htmlmod.escape(p['name'])}'></a>"
            f"<div class='body'><h3>{htmlmod.escape(p['name'])}</h3>"
            f"<p>{BLURBS.get(fmt, '')}</p>"
            f"<div class='price'>{_dollars(p['price_cents'])}{sol}</div>"
            f"<a class='cta' href='{htmlmod.escape(url)}'>Commission yours — free preview</a>"
            f"<a class='sample' href='assets/sample-{fmt}.pdf'>See the full sample (PDF)</a>"
            f"</div></div>")
    return "\n".join(cards) or "<p>The shop is being set up. Products appear here soon.</p>"


def build_site(ledger_path, journal_dir, out_dir) -> str:
    s = ledger.summary(ledger.load(ledger_path))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    products = _load_products()
    wallet = products.get("wallet_address") or "(wallet address published at launch)"
    page = fill("dashboard", {
        "net": _dollars(s["net_cents"]),
        "revenue": _dollars(s["revenue_cents"]),
        "costs": _dollars(s["costs_cents"]),
        "refunds": _dollars(s["refunds_cents"]),
        "orders": str(s["orders"]),
        "fulfilled": str(s["fulfilled"]),
        "products_html": _products_html(products),
        "price_usd": _dollars((products.get("products") or [{}])[0].get("price_cents", 1500)),
        "wallet_address": htmlmod.escape(wallet),
        "support_url": htmlmod.escape(products.get("support_form_url") or "#"),
        "journal_html": _journal_html(Path(journal_dir)),
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    })
    out = out_dir / "index.html"
    out.write_text(page)
    return str(out)
