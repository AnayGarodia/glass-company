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


def _journal_html(journal_dir: Path) -> str:
    if not journal_dir.exists():
        return "<p>No entries yet.</p>"
    parts = []
    for f in sorted(journal_dir.glob("*.md"), reverse=True):
        lines = f.read_text().splitlines()
        title = lines[0].lstrip("# ").strip() if lines else f.stem
        body = htmlmod.escape("\n".join(lines[1:]).strip())
        parts.append(f"<article><h3>{htmlmod.escape(title)}</h3>"
                     f"<div class='date'>{f.stem[:10]}</div>"
                     f"<pre>{body}</pre></article>")
    return "\n".join(parts) or "<p>No entries yet.</p>"


def _load_products() -> dict:
    if not PRODUCTS_PATH.exists():
        return {}
    return json.loads(PRODUCTS_PATH.read_text())


def _products_html(data: dict) -> str:
    cards = []
    sol_price = data.get("sol_price_usd_cents") or 0
    for p in data.get("products", []):
        url = p.get("form_url") or "#"
        sol = ""
        if sol_price:
            amount = p["price_cents"] / sol_price
            sol = f" · ≈ {amount:.3f} SOL"
        cards.append(
            f"<a class='product' href='{htmlmod.escape(url)}'>"
            f"<h3>{htmlmod.escape(p['name'])}</h3>"
            f"<div class='price'>{_dollars(p['price_cents'])}{sol}</div></a>")
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
        "wallet_address": htmlmod.escape(wallet),
        "journal_html": _journal_html(Path(journal_dir)),
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    })
    out = out_dir / "index.html"
    out.write_text(page)
    return str(out)
