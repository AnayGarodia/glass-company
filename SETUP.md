# One-time setup (Anay, ~45 min, then never again)

Target cost: **$0**. After this checklist, the business runs itself.

## 1. Lemon Squeezy (payments) — ~15 min + KYC wait

1. Create an account at https://app.lemonsqueezy.com/register
2. Create a store (name: **The Glass Company**). Complete the payout/KYC
   steps (bank details). Approval can take 1–2 days; do this first.
3. Settings → API → create an API key.
4. Create the env file:
   ```bash
   mkdir -p ~/.config/glass-company
   cat > ~/.config/glass-company/env <<'EOF'
   LEMONSQUEEZY_API_KEY=paste-here
   TALLY_API_KEY=paste-here
   RESEND_API_KEY=paste-here
   EOF
   chmod 600 ~/.config/glass-company/env
   ```

## 2. Resend (delivery email) — ~5 min

1. Create an account at https://resend.com
2. API Keys → create one → put it in the env file.
   (We send from `onboarding@resend.dev` until the business earns a domain.)

## 3. Tally (intake + support forms) — ~15 min

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

Then: account Settings → API keys → create one → env file. Note each form's
ID (in its URL) and give all four IDs to Claude in chat.

## 4. Lemon Squeezy products — ~10 min (copy-paste)

Create three products, $15.00 each, in the store. After each product is
created, set its checkout success message to link the matching Tally form.
Paste these:

**Product 1 — name:** `The Custom Crossword`
**Description:**
> A real, solvable crossword built from your life — the inside jokes, the
> places, the names only you two know. You give me 10–15 words and what they
> mean to you; I compose the grid, write clues that will make them grin, and
> deliver a print-ready PDF within 24 hours (usually much faster). Designed
> by an AI with taste; one of one; answers included on request.

**Product 2 — name:** `The Declassified Dossier`
**Description:**
> An affectionate intelligence file on someone you love: codename, redaction
> bars, field observations, known associates. You supply 5–10 true stories;
> I write the file warm, funny, and never mean. Print-ready PDF within 24
> hours. Gift framing required — this is for someone you actually know.

**Product 3 — name:** `The Mission Briefing`
**Description:**
> Turn any occasion into a spy-thriller operations packet: the bachelor
> party becomes OPERATION GOLDEN HOUR, the proposal becomes a two-phase
> extraction. You tell me the plan and the people; I issue the briefing.
> Print-ready PDF within 24 hours, marked TOP SECRET, entirely yours.

Copy each product's checkout URL and paste it, with the Tally form IDs, into
chat with Claude. Claude fills `data/products.json`.

## 5. GitHub + Cloudflare Pages (public dashboard) — ~10 min

1. Push this repo to a new GitHub repo (public or private — the site is what
   becomes public).
2. https://dash.cloudflare.com → Workers & Pages → Create → Pages →
   connect the repo. Build command: *(none)*. Output directory: `site`.
3. Note the `*.pages.dev` URL — that's the shop.

## 6. Trust the workspace (~1 min)

The scheduled runs use the command allowlist in `.claude/settings.json`,
which Claude Code ignores until a human trusts the workspace once:

```bash
cd ~/Desktop/Projects/glass-company && claude
```

Accept the trust dialog, then exit. (Claude deliberately does not grant
itself this — it's the one permission a human must hand over.)

## 7. Schedule the ops loop

```bash
cp launchd/ai.glasscompany.fulfill.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/ai.glasscompany.fulfill.plist
```

## 8. Approve the mandate

Read `MANDATE.md`. Reply in chat with "mandate approved" (or your edits).
Nothing goes live to strangers until you do.
