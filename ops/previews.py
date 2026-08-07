"""Bookkeeping for a pending preview: what was shown, and what it was quoted at.

Step 7 of RUNBOOK-FULFILL verifies a payment against `expected_lamports` and
delivers `final_html`, both read off the pending entry. Those two fields plus
the price they were derived from have to move together, at the first preview
and again at every revision. Updating one without the others either rejects a
customer who paid exactly what the latest email quoted, or ships the version
they asked to change.

This module also owns the words that go around those numbers — the how-to-pay
walkthrough and the payment block of a preview email. Both the shop page and
every preview email have to say the same thing about buying SOL, and step 6c
lists roughly ten things a preview email must contain. Written out by hand each
run, that list drifts; here it is one function call.
"""
import math

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


PAGE = "page"
EMAIL = "email"

_WHERE = {
    PAGE: ("the address in your preview email",
           "Reply to the preview email with that string"),
    EMAIL: ("the address above",
            "Reply to this email with that string"),
}


def how_to_pay_html(where: str) -> str:
    """The how-to-pay walkthrough, in the one place both users of it read from.

    The shop page's crypto FAQ and every preview email have to answer "how do
    I actually pay" identically — a buyer who reads one and then the other and
    finds them disagreeing has no way to tell which is true. Two copies of this
    paragraph is how that happens, so there is one, and `where` only swaps the
    two phrases that genuinely differ by context.
    """
    if where not in _WHERE:
        raise ValueError(f"where must be {PAGE!r} or {EMAIL!r}, got {where!r}")
    address_phrase, reply_phrase = _WHERE[where]
    return (
        "Fair — this is the clunkiest part of buying from me and I'd rather "
        "say so than pretend. You need about $16 of SOL. Buy it on an exchange "
        "like Coinbase or Kraken, or inside a wallet app like Phantom that "
        "sells it to you directly; most of them will ask you to verify your "
        "ID, which is their requirement, not mine, and I never see any of it. "
        f"Then send the amount to {address_phrase}. The exact figure drifts "
        "with the SOL price, so being slightly under is fine — anything "
        "within 5% counts as paid. Once the transfer clears, your wallet or "
        "exchange shows a <b>transaction signature</b> in its history (some "
        "call it a transaction ID or TxID) — a long string of letters and "
        f"numbers. {reply_phrase} and the final PDF comes straight back. "
        "Roughly ten minutes the first time, less after. If that's more "
        "trouble than a $15 gift is worth to you, walk away and owe nothing; "
        "that's a real answer, not a sales line.")


def quoted_sol(entry: dict) -> str:
    """The SOL figure to put in an email, derived from the stamped quote.

    Read off `expected_lamports` — the number step 7 will verify against — and
    never recomputed from a price, which is the whole reason `stamp()` exists.
    Rounded *up* to four decimals so the printed figure is never below the
    lamports it was derived from; a buyer who pays exactly what they read pays
    at or above the quote, never a hair under it.
    """
    lamports = entry["expected_lamports"]
    return f"{math.ceil(lamports / 1e5) / 1e4:.4f}"


def payment_block_html(entry: dict, wallet_address: str) -> str:
    """Everything a preview email must say about money, from the stamped entry.

    Step 6c of RUNBOOK-FULFILL requires the price, the wallet address, the
    exact SOL amount, how to pay, what a revision costs, and what walking away
    costs. A run writes the warm, specific part of the email itself and appends
    this; it does not retype this list and it does not compute the SOL figure a
    second time. The AI disclosure is deliberately absent — `emailer.
    send_delivery` appends it to every outgoing message already.
    """
    price = entry["price_cents"] / 100
    return (
        f'<p><b>If you want it:</b> ${price:.2f}, which is '
        f'<b>{quoted_sol(entry)} SOL</b> right now, sent to:</p>'
        f'<p><code>{wallet_address}</code></p>'
        "<p>Reply to this email with your transaction signature and the "
        "final version — same artifact, no watermark — arrives immediately. "
        "Want changes first? Just say what's off and I'll revise it; that "
        "costs nothing and there's no limit. Walking away costs nothing "
        "either, and you never have to tell me.</p>"
        "<p><b>Never used crypto?</b> "
        + how_to_pay_html(EMAIL) + "</p>")
