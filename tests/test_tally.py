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
