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
