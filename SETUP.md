# One-time setup — a pairing session (~40 min, then never again)

Model: **the business owns everything, including the till.** No Anay
accounts anywhere — payments arrive in SOL to a wallet Claude generates and
holds. Claude drives every browser form; Anay is present for exactly two
things:

1. **Humanity checks** — Claude does not solve CAPTCHAs, so Anay clicks
   them when they appear.
2. **Four terminal commands** at the end (trust + scheduling).

Rule for every signup: registered truthfully as an AI-run business; if a
service demands a phone number, drop it. All credentials go in
`~/.config/glass-company/` (never in the repo, never in chat).

Target cost: **$0**.

## 1. Business email (~5 min)

Create `theglasscompany@proton.me` (or nearest available) at
https://proton.me — email + password only, no phone. Anay clicks the
CAPTCHA. This address is the registered identity for every account below.

## 2. Business Cloudflare + the website (~10 min)

(Repo hosting stays on Anay's GitHub — `AnayGarodia/glass-company`, already
public — per Anay's call; the code is the one artifact that was Anay's to
begin with.) Sign up at https://dash.cloudflare.com/sign-up with the
business email. Workers & Pages → Create → Pages → connect
`AnayGarodia/glass-company` (Anay authorizes the Cloudflare GitHub App when
prompted). Project name `glasscompany`, no build command, output directory
`site`. The site is now `https://glasscompany.pages.dev`.

## 3. The wallet (~2 min, Claude only)

Claude runs `ops.solpay.generate_wallet()` — keys land in
`~/.config/glass-company/wallet.json` (mode 600), the address goes in
`data/products.json` and onto the dashboard. **Anay: copy that file
somewhere safe offline** (it's the till; if this laptop dies, the money
shouldn't).

## 4. Resend (~5 min)

https://resend.com with the business email → API key.

## 5. Tally (~15 min)

https://tally.so with the business email. Four forms. Product forms are the
whole checkout: pay first, then the form. Field order matters.

**Forms A/B/C — one per product (Crossword / Dossier / Briefing):**
1. `Email` (email field)
2. `Transaction signature` (short answer — "paste the signature of your SOL
   payment; the address and current amount are on glasscompany.pages.dev")
3. Then the product's intake questions:
   - **A — Crossword:** who is this for + occasion · 10–15 single words
     that matter (names, places, pets, inside jokes) · one line per word on
     why · anything to avoid?
   - **B — Dossier:** subject's name · your relationship (must know them
     personally) · occasion · 5–10 funny true stories/quirks · anything
     off-limits?
   - **C — Briefing:** occasion · who's involved (names/roles) · the rough
     plan · how far can the jokes go?

**Form D — Support & refunds:** `Email` · `Transaction signature` ·
refund / question / problem · details.

Settings → API key. Note the four form IDs and public URLs.

## 6. Env file (~1 min)

```bash
cat > ~/.config/glass-company/env <<'EOF'
TALLY_API_KEY=paste-here
RESEND_API_KEY=paste-here
EOF
chmod 600 ~/.config/glass-company/env
```

## 7. Marketing accounts — the business's own voice (~10 min)

- **Hacker News:** create account `glasscompany` at
  https://news.ycombinator.com/login (Anay clicks any CAPTCHA).
- **Bluesky:** create `@glasscompany.bsky.social` at https://bsky.app —
  email only. Bio states it's an AI-run business.
- **Moltbook:** Claude already owns `moltke` — nothing to do.
- **Reddit:** skipped at launch; a fresh account can't post in most
  subreddits. May be created later and left to age.

## 8. Trust the workspace (~1 min)

```bash
cd ~/Desktop/Projects/glass-company && claude
```
Accept the trust dialog, exit. (Claude deliberately does not grant itself
this — it's the one permission a human must hand over.)

## 9. Schedule the ops loop (~1 min)

```bash
cp launchd/ai.glasscompany.fulfill.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/ai.glasscompany.fulfill.plist
```

launchd fires only while the Mac is awake; missed runs catch up on the next
one. Keep the Mac plugged in.

## 10. Approve the mandate

Read `MANDATE.md`. Reply "mandate approved" (or your edits). Nothing goes
live to strangers until you do.

---

**Claude needs in chat afterwards:** pages.dev URL · 4 Tally form IDs +
public URLs. Passwords and keys go only in `~/.config/glass-company/`.

**Cashing out (someday, optional):** SOL in the business wallet stays SOL.
Converting it to bank dollars requires a KYC'd exchange account — that's
outside the business and entirely Anay's affair.
