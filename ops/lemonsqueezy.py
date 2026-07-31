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
