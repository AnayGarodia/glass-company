from unittest import mock
from ops import solpay

ADDR = "GLASSxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx1"
TX = {
    "meta": {"err": None, "preBalances": [5_000_000_000, 1_000_000],
             "postBalances": [4_899_995_000, 100_001_000_000 // 1000]},
    "transaction": {"message": {"accountKeys": ["SENDERxxxx", ADDR]}},
}


def test_wallet_roundtrip(tmp_path):
    p = tmp_path / "wallet.json"
    addr = solpay.generate_wallet(p)
    assert addr == str(solpay.load_wallet(p).pubkey())
    assert solpay.generate_wallet(p) == addr  # idempotent, no overwrite


def test_verify_payment_ok():
    tx = {"meta": {"err": None, "preBalances": [5_000_000_000, 1_000_000],
                   "postBalances": [4_898_000_000, 101_000_000]},
          "transaction": {"message": {"accountKeys": ["SENDERxxxx", ADDR]}}}
    with mock.patch.object(solpay, "_rpc", return_value=tx):
        v = solpay.verify_payment("sig", ADDR, 100_000_000)
    assert v["ok"] is True
    assert v["lamports"] == 100_000_000
    assert v["sender"] == "SENDERxxxx"


def test_verify_payment_underpaid_and_missing():
    tx = {"meta": {"err": None, "preBalances": [1, 1_000_000],
                   "postBalances": [0, 2_000_000]},
          "transaction": {"message": {"accountKeys": ["S", ADDR]}}}
    with mock.patch.object(solpay, "_rpc", return_value=tx):
        assert solpay.verify_payment("sig", ADDR, 100_000_000)["ok"] is False
    with mock.patch.object(solpay, "_rpc", return_value=None):
        v = solpay.verify_payment("sig", ADDR, 1)
        assert v["ok"] is False and "not found" in v["reason"]


def test_send_sol_builds_and_sends(tmp_path):
    kp_addr = solpay.generate_wallet(tmp_path / "w.json")
    wallet = solpay.load_wallet(tmp_path / "w.json")
    dest = solpay.generate_wallet(tmp_path / "w2.json")
    calls = []

    def fake_rpc(method, params, rpc=None):
        calls.append(method)
        if method == "getLatestBlockhash":
            return {"value": {"blockhash": "4uQeVj5tqViQh7yWWGStvkEG1Zmhx6uasJtWCJziofM"}}
        if method == "sendTransaction":
            return "fake-signature"
        raise AssertionError(method)

    with mock.patch.object(solpay, "_rpc", side_effect=fake_rpc):
        sig = solpay.send_sol(wallet, dest, 1_000)
    assert sig == "fake-signature"
    assert calls == ["getLatestBlockhash", "sendTransaction"]
    assert kp_addr != dest


def test_usd_to_lamports():
    # $15.00 at $150.00/SOL = 0.1 SOL
    assert solpay.usd_cents_to_lamports(1500, 15000) == 100_000_000


def test_min_accepted_lamports_is_five_percent_under_the_quote():
    assert solpay.min_accepted_lamports(100_000_000) == 95_000_000


def test_quoted_amount_still_verifies_after_a_sol_price_drop():
    # A buyer pays the exact figure their preview quoted at $150.00/SOL.
    quoted = solpay.usd_cents_to_lamports(1500, 15000)
    # SOL then falls 20% before they get around to paying. The threshold must
    # come from the quote they were given, not from $15 at today's price.
    assert quoted >= solpay.min_accepted_lamports(quoted)
    recomputed_today = solpay.usd_cents_to_lamports(1500, 12000)
    assert quoted < solpay.min_accepted_lamports(recomputed_today)
