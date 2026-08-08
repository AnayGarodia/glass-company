"""Business-owned Solana wallet: keygen, payment verification, refunds.

The wallet is the till. Keys live outside the repo
(~/.config/glass-company/wallet.json). All amounts in lamports.
"""
import json
from pathlib import Path

import requests
from solders.hash import Hash
from solders.keypair import Keypair
from solders.message import Message
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction

RPC = "https://api.mainnet-beta.solana.com"
WALLET_PATH = Path.home() / ".config" / "glass-company" / "wallet.json"
LAMPORTS_PER_SOL = 1_000_000_000


def _rpc(method, params, rpc=RPC):
    r = requests.post(rpc, json={"jsonrpc": "2.0", "id": 1,
                                 "method": method, "params": params}, timeout=30)
    r.raise_for_status()
    body = r.json()
    if "error" in body:
        raise RuntimeError(f"rpc {method}: {body['error']}")
    return body["result"]


def generate_wallet(path=WALLET_PATH) -> str:
    """Create the wallet if missing; return its address either way."""
    path = Path(path)
    if path.exists():
        return str(load_wallet(path).pubkey())
    kp = Keypair()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(list(bytes(kp))))
    path.chmod(0o600)
    return str(kp.pubkey())


def load_wallet(path=WALLET_PATH) -> Keypair:
    return Keypair.from_bytes(bytes(json.loads(Path(path).read_text())))


def verify_payment(tx_sig: str, address: str, min_lamports: int, rpc=RPC) -> dict:
    """Check that tx_sig is a finalized transfer of >= min_lamports to address.

    Returns {"ok": bool, "lamports": int, "sender": str | None, "reason": str}.
    """
    tx = _rpc("getTransaction",
              [tx_sig, {"encoding": "json", "commitment": "finalized",
                        "maxSupportedTransactionVersion": 0}], rpc=rpc)
    if tx is None:
        return {"ok": False, "lamports": 0, "sender": None,
                "reason": "transaction not found or not finalized"}
    if tx["meta"].get("err") is not None:
        return {"ok": False, "lamports": 0, "sender": None,
                "reason": "transaction failed on-chain"}
    keys = tx["transaction"]["message"]["accountKeys"]
    if address not in keys:
        return {"ok": False, "lamports": 0, "sender": None,
                "reason": "payment address not in transaction"}
    i = keys.index(address)
    received = tx["meta"]["postBalances"][i] - tx["meta"]["preBalances"][i]
    sender = keys[0]  # fee payer
    if received < min_lamports:
        return {"ok": False, "lamports": received, "sender": sender,
                "reason": f"received {received} < required {min_lamports}"}
    return {"ok": True, "lamports": received, "sender": sender, "reason": "ok"}


CUSTODIAL_BALANCE_LAMPORTS = 100 * LAMPORTS_PER_SOL
CUSTODIAL_BURST = 100
CUSTODIAL_BURST_SECONDS = 3600


def looks_custodial(address: str, rpc=RPC) -> dict:
    """Is `address` plausibly an exchange's wallet rather than a buyer's own?

    `verify_payment` reports the fee payer as the sender, and a refund goes
    back to it. When a buyer withdraws SOL straight from Coinbase to us, that
    fee payer is Coinbase's hot wallet: a refund sent there leaves the wallet,
    never reaches the customer, and cannot be undone. Verified against mainnet
    2026-08-08 — real withdrawals from a known exchange hot wallet do carry the
    exchange as fee payer.

    Best-effort by construction. Two signals, either one enough: a balance no
    gift buyer would hold, and a burst of transactions no individual produces.
    A service routing withdrawals through fresh, near-empty intermediate
    addresses would pass this; the how-to-pay copy asking buyers to send from
    their own wallet is what actually shrinks the exposure. False positives are
    cheap (one email asking the customer to confirm), a false negative is money
    gone, so this errs toward flagging.

    Returns {"custodial": bool, "balance": int, "reason": str}.
    """
    balance = _rpc("getBalance", [address], rpc=rpc)["value"]
    if balance >= CUSTODIAL_BALANCE_LAMPORTS:
        return {"custodial": True, "balance": balance,
                "reason": f"holds {balance / LAMPORTS_PER_SOL:,.0f} SOL, far "
                          "more than someone who bought $16 of it to pay me"}
    sigs = _rpc("getSignaturesForAddress",
                [address, {"limit": CUSTODIAL_BURST}], rpc=rpc)
    times = sorted(s["blockTime"] for s in sigs if s.get("blockTime"))
    if len(sigs) >= CUSTODIAL_BURST and len(times) >= 2:
        span = times[-1] - times[0]
        if span <= CUSTODIAL_BURST_SECONDS:
            return {"custodial": True, "balance": balance,
                    "reason": f"{len(sigs)} transactions in {span}s — the "
                              "traffic of a service, not a person"}
    return {"custodial": False, "balance": balance,
            "reason": "looks like an individual's own wallet"}


def send_sol(wallet: Keypair, to_address: str, lamports: int, rpc=RPC) -> str:
    """Send lamports (refunds). Returns the transaction signature."""
    blockhash = Hash.from_string(
        _rpc("getLatestBlockhash", [{"commitment": "finalized"}],
             rpc=rpc)["value"]["blockhash"])
    ix = transfer(TransferParams(from_pubkey=wallet.pubkey(),
                                 to_pubkey=Pubkey.from_string(to_address),
                                 lamports=lamports))
    msg = Message.new_with_blockhash([ix], wallet.pubkey(), blockhash)
    tx = Transaction([wallet], msg, blockhash)
    import base64
    return _rpc("sendTransaction",
                [base64.b64encode(bytes(tx)).decode(), {"encoding": "base64"}],
                rpc=rpc)


def sol_price_usd_cents() -> int:
    """Current SOL price in USD cents, via CoinGecko (no account needed)."""
    r = requests.get("https://api.coingecko.com/api/v3/simple/price",
                     params={"ids": "solana", "vs_currencies": "usd"}, timeout=30)
    r.raise_for_status()
    return round(r.json()["solana"]["usd"] * 100)


def usd_cents_to_lamports(usd_cents: int, sol_price_usd_cents: int) -> int:
    return round(usd_cents * LAMPORTS_PER_SOL / sol_price_usd_cents)


PAYMENT_TOLERANCE = 0.05


def min_accepted_lamports(quoted_lamports: int) -> int:
    """Smallest payment that counts as paid against a quoted amount.

    `quoted_lamports` must be the figure the preview email actually quoted
    (`pending_previews[].expected_lamports`), not an amount recomputed at
    today's SOL price. The quote is the promise; the shop page and the
    preview email both say anything within 5% of it counts as paid.
    """
    return int(quoted_lamports * (1 - PAYMENT_TOLERANCE))
