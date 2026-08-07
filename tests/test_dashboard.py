import re

from ops import dashboard, ledger, previews


def test_build_site(tmp_path):
    lp = tmp_path / "ledger.jsonl"
    ledger.record({"ts": "2026-07-30T12:00:00Z", "type": "sale",
                   "order_id": "1", "amount_cents": 1500}, path=lp)
    jd = tmp_path / "journal"
    jd.mkdir()
    (jd / "2026-07-30-first-sale.md").write_text("# First sale\n\nSomeone paid!")
    out = dashboard.build_site(lp, jd, tmp_path / "site")
    html = open(out).read()
    assert "$15.00" in html
    assert "First sale" in html
    assert "run autonomously by an AI" in html


def test_page_renders_the_shared_how_to_pay_copy(tmp_path):
    # The FAQ's crypto walkthrough and the preview email's must be the same
    # words, so the page reads it from ops.previews rather than keeping its
    # own copy in the template.
    out = dashboard.build_site(tmp_path / "none.jsonl", tmp_path / "nojournal",
                               tmp_path / "site")
    html = open(out).read()
    page_copy = previews.how_to_pay_html(previews.PAGE)
    assert html.count(page_copy) == 1
    assert "$16 of SOL" in html and "within 5% counts as paid" in html
    # $how_to_pay_html itself must not survive into the page.
    assert not re.search(r"\$[a-z_]{4,}", html)


def test_empty_state(tmp_path):
    out = dashboard.build_site(tmp_path / "none.jsonl", tmp_path / "nojournal",
                               tmp_path / "site")
    assert "$0.00" in open(out).read()
