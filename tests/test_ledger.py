import json
import pytest
from ops import ledger


def test_record_and_load(tmp_path):
    p = tmp_path / "ledger.jsonl"
    e = ledger.record({"ts": "2026-07-30T12:00:00Z", "type": "sale",
                       "order_id": "1", "amount_cents": 1500}, path=p)
    assert e["type"] == "sale"
    events = ledger.load(p)
    assert events == [e]


def test_record_rejects_bad_type(tmp_path):
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
