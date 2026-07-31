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
