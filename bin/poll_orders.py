"""Poll LemonSqueezy for orders; print JSON or an error marker."""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ops import lemonsqueezy

key = os.environ.get("LEMONSQUEEZY_API_KEY", "")
if not key:
    print("NO_KEY_IN_ENV")
    sys.exit(0)

try:
    orders = lemonsqueezy.list_orders(key)
    print(json.dumps(orders, indent=2, default=str))
except Exception as e:
    print("ERROR:", type(e).__name__, e)
