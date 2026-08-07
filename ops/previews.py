"""Bookkeeping for a pending preview: what was shown, and what it was quoted at.

Step 7 of RUNBOOK-FULFILL verifies a payment against `expected_lamports` and
delivers `final_html`, both read off the pending entry. Those two fields plus
the price they were derived from have to move together, at the first preview
and again at every revision. Updating one without the others either rejects a
customer who paid exactly what the latest email quoted, or ships the version
they asked to change.
"""
from . import solpay


def stamp(entry: dict, *, final_html: str, price_cents: int,
          sol_price_usd_cents: int, now_iso: str) -> dict:
    """Record on `entry` the artifact shown and the amount quoted for it.

    Call this for the first preview and again for every revision, and quote
    the returned `expected_lamports` in the email being sent — the email and
    the entry must come from this one computation, not from two that happen
    to agree.

    `preview_date` is set once and never moved, so the 14-day expiry runs from
    when the customer first heard from us rather than resetting on each
    revision. `quoted_at` carries the time of this stamp.
    """
    entry["final_html"] = final_html
    entry["price_cents"] = price_cents
    entry["sol_price_usd_cents_at_preview"] = sol_price_usd_cents
    entry["expected_lamports"] = solpay.usd_cents_to_lamports(
        price_cents, sol_price_usd_cents)
    entry["quoted_at"] = now_iso
    entry.setdefault("preview_date", now_iso)
    return entry
