from ops import previews, solpay


def _first():
    return previews.stamp(
        {"email": "buyer@example.com", "format": "crossword"},
        final_html="<p>version one</p>",
        price_cents=1500,
        sol_price_usd_cents=15000,
        now_iso="2026-08-01T00:00:00Z",
    )


def test_first_stamp_records_artifact_price_and_quote():
    e = _first()
    assert e["final_html"] == "<p>version one</p>"
    assert e["sol_price_usd_cents_at_preview"] == 15000
    assert e["expected_lamports"] == solpay.usd_cents_to_lamports(1500, 15000)
    assert e["preview_date"] == "2026-08-01T00:00:00Z"
    assert e["quoted_at"] == "2026-08-01T00:00:00Z"


def test_revision_replaces_the_artifact_that_gets_delivered():
    # The customer asked for changes and approved version two. Payment
    # delivers `final_html`, so a revision that leaves it alone ships the
    # version they asked to change.
    e = _first()
    previews.stamp(e, final_html="<p>version two</p>", price_cents=1500,
                   sol_price_usd_cents=15000, now_iso="2026-08-03T00:00:00Z")
    assert e["final_html"] == "<p>version two</p>"


def test_revision_keeps_the_original_preview_date():
    # Expiry runs from first contact; a chain of revisions must not keep the
    # entry alive indefinitely.
    e = _first()
    previews.stamp(e, final_html="<p>version two</p>", price_cents=1500,
                   sol_price_usd_cents=15000, now_iso="2026-08-03T00:00:00Z")
    assert e["preview_date"] == "2026-08-01T00:00:00Z"
    assert e["quoted_at"] == "2026-08-03T00:00:00Z"


def test_revision_requotes_so_a_correct_payment_is_not_rejected():
    # SOL rose 25% between the first preview and the revision, so the
    # revision email quotes fewer lamports for the same $15. Verification
    # must use the re-stamped figure; the stale one would reject a customer
    # who paid exactly what they were last told.
    e = _first()
    stale = e["expected_lamports"]
    previews.stamp(e, final_html="<p>version two</p>", price_cents=1500,
                   sol_price_usd_cents=18750, now_iso="2026-08-03T00:00:00Z")
    paid = e["expected_lamports"]
    assert paid >= solpay.min_accepted_lamports(e["expected_lamports"])
    assert paid < solpay.min_accepted_lamports(stale)


WALLET = "9ynbqPp5HG2YKNZSVF6MacWUbyMhoNeaudU5q63oBUhs"


def test_quoted_sol_comes_from_the_stamped_lamports_not_a_recomputation():
    # The entry's stored quote is deliberately inconsistent with its price and
    # SOL price, as it would be if someone edited one field by hand. The email
    # must quote what step 7 will actually verify against.
    e = _first()
    e["expected_lamports"] = 202784913
    assert previews.quoted_sol(e) == "0.2028"
    assert WALLET in previews.payment_block_html(e, WALLET)
    assert "0.2028 SOL" in previews.payment_block_html(e, WALLET)


def test_quoted_figure_is_never_below_the_amount_it_was_derived_from():
    # Printed to four decimals, so it must round up: a buyer who sends exactly
    # what they read must land at or above the quote, never a hair under it.
    for lamports in (1, 202784913, 202700001, 100000000, 999999999):
        e = dict(_first(), expected_lamports=lamports)
        assert round(float(previews.quoted_sol(e)) * 1e9) >= lamports


def test_payment_block_says_everything_step_6c_requires():
    e = _first()
    block = previews.payment_block_html(e, WALLET)
    assert "$15.00" in block                      # the price
    assert WALLET in block                        # where it goes
    assert previews.quoted_sol(e) in block        # the exact amount
    assert "transaction signature" in block       # how to claim the final
    assert "what's off" in block                  # revisions are free
    assert "Walking away costs nothing" in block  # no obligation
    for phrase in ("$16 of SOL", "verify your ID", "within 5%", "TxID"):
        assert phrase in block                    # the how-to-pay walkthrough


def test_payment_block_leaves_the_ai_disclosure_to_the_mailer():
    # emailer.send_delivery appends DISCLOSURE to every outgoing message; a
    # second copy here would put two in each preview.
    from ops.emailer import DISCLOSURE
    block = previews.payment_block_html(_first(), WALLET)
    assert "autonomously by an AI" not in block
    assert DISCLOSURE not in block


def test_page_and_email_give_the_same_how_to_pay_answer():
    page = previews.how_to_pay_html(previews.PAGE)
    email = previews.how_to_pay_html(previews.EMAIL)
    for phrase in ("$16 of SOL", "Coinbase or Kraken", "verify your ID",
                   "within 5% counts as paid", "transaction signature",
                   "TxID", "$15 gift is worth", "ten minutes the first time"):
        assert phrase in page and phrase in email
    # Only the two context-dependent phrases differ.
    assert "the address in your preview email" in page
    assert "the address above" in email
