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
