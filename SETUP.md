# One-time setup (Anay, ~45 min, then never again)

Target cost: **$0**. After this checklist, the business runs itself —
including marketing. Order matters: the website must exist before Lemon
Squeezy asks for its URL.

Already done by Claude: repo is public at
https://github.com/AnayGarodia/glass-company with the dashboard pre-built in
`site/`.

## 1. Cloudflare Pages — the website (~10 min)

1. https://dash.cloudflare.com → Workers & Pages → Create → Pages →
   "Connect to Git" → pick `AnayGarodia/glass-company`.
2. Project name: `glasscompany`. Build command: *(leave empty)*.
   Build output directory: `site`.
3. Deploy. The site is now at `https://glasscompany.pages.dev` (or similar —
   note the exact URL, you need it in step 2 and Claude needs it in chat).

## 2. Lemon Squeezy — payments (~15 min + 1–2 day KYC wait)

1. Create an account at https://app.lemonsqueezy.com/register
2. Create a store: name **The Glass Company**, website = your pages.dev URL
   from step 1. Complete payout/KYC (bank details).
3. Settings → API → create an API key.
4. Create three products, **$15.00** each (descriptions to paste are in
   `PRODUCT-COPY.md`). Set each product's checkout success message to link
   the matching Tally form from step 4.
5. Copy the three checkout URLs for Claude.

## 3. Resend — delivery email (~5 min)

Create an account at https://resend.com → API Keys → create one.
(Sending from `onboarding@resend.dev` until the business earns a domain.)

## 4. Tally — intake + support forms (~15 min)

Create an account at https://tally.so, then **four forms**. Every form's
FIRST question must be a short-answer field titled exactly `Order number`.

**Form A — Crossword intake:** Order number · Who is this for, and what's
the occasion? · 10–15 single words that mean something (names, places, pets,
inside jokes — these become answers) · For each word, one line on why it
matters · Anything to avoid?

**Form B — Dossier intake:** Order number · Subject's name · Your
relationship to them (must know them personally) · The occasion · 5–10 funny
facts/quirks/legends about them · Anything off-limits?

**Form C — Briefing intake:** Order number · Operation occasion (bachelor
party, proposal, birthday…) · Who's involved (names/roles) · The actual plan,
roughly · Tone: how far can the jokes go?

**Form D — Support & refunds:** Order number · What do you need? (refund /
question / problem) · Details

Then Settings → API keys → create one. Note each form's ID (in its URL).

## 5. Env file (~2 min)

```bash
cat > ~/.config/glass-company/env <<'EOF'
LEMONSQUEEZY_API_KEY=paste-here
TALLY_API_KEY=paste-here
RESEND_API_KEY=paste-here
EOF
chmod 600 ~/.config/glass-company/env
```

## 6. Marketing logins (~5 min)

Claude does all marketing, but posts from your existing accounts (always
disclosed as AI-written). Make sure you're logged in to Hacker News and
Reddit in Chrome, then in a Claude session in this repo run
`/setup-browser-cookies` so the headless browser inherits those sessions.

## 7. Trust the workspace (~1 min)

```bash
cd ~/Desktop/Projects/glass-company && claude
```
Accept the trust dialog, then exit. Without this, scheduled runs can't use
the command allowlist and every run stalls. (Claude deliberately does not
grant itself this — it's the one permission a human must hand over.)

## 8. Schedule the ops loop (~1 min)

```bash
cp launchd/ai.glasscompany.fulfill.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/ai.glasscompany.fulfill.plist
```

Note: launchd only fires while the Mac is awake. Missed runs catch up on the
next one, so worst-case fulfillment latency is your sleep schedule — still
inside the 24h promise. Keep the Mac plugged in.

## 9. Approve the mandate

Read `MANDATE.md`. Reply in chat with "mandate approved" (or your edits).
Nothing goes live to strangers until you do.

---

**Paste into chat when done:** the pages.dev URL · 3 checkout URLs · 4 Tally
form IDs · the 3 API keys go only in the env file, never in chat.
