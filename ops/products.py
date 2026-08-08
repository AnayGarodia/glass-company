"""The product catalogue and its one mutable field, the SOL price.

The price sync rewrites this file every run. Writing it with a bare
json.dump drops the trailing newline, which puts a spurious "no newline at
end of file" hunk in nearly every auto-commit; save() keeps the newline so
the diff is the one line that actually changed.
"""
import json
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "products.json"


def load(path=DEFAULT_PATH) -> dict:
    return json.loads(Path(path).read_text())


def save(products: dict, path=DEFAULT_PATH) -> dict:
    Path(path).write_text(json.dumps(products, indent=2) + "\n")
    return products


def set_sol_price(price_cents: int, path=DEFAULT_PATH) -> tuple[int, int]:
    """Write the new SOL price, returning (old, new)."""
    products = load(path)
    old = products["sol_price_usd_cents"]
    products["sol_price_usd_cents"] = price_cents
    save(products, path)
    return old, price_cents
