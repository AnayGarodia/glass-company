from ops import dashboard, ledger


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


def test_empty_state(tmp_path):
    out = dashboard.build_site(tmp_path / "none.jsonl", tmp_path / "nojournal",
                               tmp_path / "site")
    assert "$0.00" in open(out).read()
