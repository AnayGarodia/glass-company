# The Glass Company — Design Spec

**Date:** 2026-07-30
**Status:** Approved direction; pending user review of this spec
**Owner:** Claude (autonomous operator). Anay's role: one-time setup, then nothing.

## What this is

A fully autonomous one-product business, run 100% by Claude, in public. It sells
personalized artifacts (custom PDFs generated from facts the buyer supplies) and
publishes every decision, every dollar, and its full P&L on a live public
dashboard. The transparency is the marketing: "watch an AI company try to earn
its first dollar."

**Success criterion (v1):** a stranger — someone Anay does not know — pays real
money for a product. Secondary: the iteration loop (format kills/launches,
pricing, channels) runs weekly without human input.

**Budget:** $50 cap, but target $0 spent before first revenue so the first
sale is already net profit. No domain at launch — free `*.pages.dev`
subdomain; buy a domain only out of revenue. Hosting and email on free tiers.

## Product

Personalized artifact shop. Buyer pays, fills an intake form with facts about
the recipient/occasion, and receives a designed PDF by email within a few
hours (SLA: next ops run + generation time; promise "within 24h", deliver much
faster).

Launch formats, ~$15 each:

1. **Custom crossword** — a real, solvable crossword built from the buyer's
   life: inside jokes, shared history, names, places. Anniversary/birthday gift.
2. **Declassified dossier** — an affectionate intelligence-file "roast" of a
   friend or partner, redaction bars and all. Gift-framed, consent-gated (see
   Safety).
3. **Mission briefing** — any occasion (proposal, bachelor party, new job)
   rendered as a spy-thriller operations packet for the participants.

Formats are the primary iteration variable. Weekly: kill formats with no sales
interest, launch new ones, adjust prices. The portfolio is expected to churn.

Quality bar: each artifact gets a self-QA pass before delivery (crossword must
actually solve; names/facts must be used correctly; layout must look designed,
not templated). A bad artifact triggers regeneration, not delivery.

## Money (amended 2026-07-30: zero Anay accounts, at Anay's direction)

- **Business-owned Solana wallet** — the AI generates and holds the keys
  (`~/.config/glass-company/wallet.json`); no card processor, because every
  card processor requires human KYC and Anay's accounts are off-limits.
- Buyers pay SOL to the published address, then fill the product's Tally
  form (email + transaction signature + intake facts). The ops run verifies
  the payment on-chain before fulfilling; 5% price slack for SOL movement.
- Known trade-off, accepted: crypto checkout loses most mainstream gift
  buyers; launch channels (HN, Bluesky, Moltbook) skew crypto-capable, and
  "the AI owns the till" strengthens the story.
- Funds stay in the wallet; cashing out to fiat is outside the business.
- **Refund policy: instant, no questions.** Keeps support fully autonomous.
- Costs ledger: every dollar spent (domain, ads, fees) recorded and published.

## Autonomous ops loop

Same proven pattern as fable-trader: launchd + `claude -p` + a mandate file.

- **Fulfillment run (every 30 min, waking hours):** poll Lemon Squeezy API for
  new orders → fetch intake data → generate artifact → self-QA → deliver via
  Resend → mark fulfilled → update dashboard data → append journal entry.
  Also: process support/refund requests, which arrive via a Tally support
  form linked in every customer email (pollable via the same Tally API as
  intake — no inbound email infra needed).
- **Weekly deep run:** conversion analysis (visits → checkouts → sales per
  format), kill/launch format decisions, pricing changes, marketing actions,
  published as a "board meeting" journal entry.
- **State** lives in the project repo (orders ledger, journal, dashboard data);
  dashboard deploys on git push via Cloudflare Pages.

### Mandate (autonomy boundaries)

- May: create/edit products and prices, post to approved channels (disclosed
  as AI), spend up to the remaining budget, issue refunds, refuse orders.
- May not: exceed $50 total spend, create accounts requiring KYC, misrepresent
  itself as human, contact anyone off-platform except customers about their
  orders.

## The glass dashboard

Public static site on the shop domain (Cloudflare Pages, free):

- Live P&L to the cent (revenue, fees, costs, net).
- Order counter and fulfillment times.
- **Decision journal:** every business decision with its reasoning, timestamped.
- "What is this" page: honest explanation that an AI runs the business and the
  human does nothing.

The dashboard is both accountability and the growth engine. Launch posts point
at it, not at the shop.

## Marketing

- Launch: Show HN + 2-3 relevant subreddits, first-person, fully disclosed
  ("I'm Claude; I run this business; the human set up payment accounts and
  left"). The dashboard is the story.
- Ongoing: journal-as-content; occasional posts when something genuinely
  interesting happens (first sale, first refund, a format dies). No spam, no
  undisclosed AI posting, respect each community's self-promo rules.
- Paid experiments only if organic stalls, from remaining budget, logged.

## Safety & content policy

- Dossier/personalized formats: gift framing required — buyer must know the
  subject personally; no minors as roast subjects; no requests that smell like
  harassment, surveillance, or doxxing. Refuse + instant refund + polite note.
- No real-person defamation; artifacts are clearly fictional/affectionate.
- All public posting is disclosed as AI-authored.

## Anay's one-time setup (~45 min, then nothing)

1. Lemon Squeezy account (KYC) + API key to Claude.
2. Resend account + API key to Claude (send from Resend's shared domain until
   we own one; buy a domain only after first revenue).
3. Cloudflare Pages connected to the repo (free `*.pages.dev` subdomain).
4. Approve the mandate file.

Target setup cost: $0. First sale is therefore net profit.

## Risks

- **Lemon Squeezy approval latency** (1-2 days, needs Anay) — start setup first.
- **Zero orders** is a live possibility; the response is weekly format/channel
  iteration, and the dashboard makes even failure worth watching.
- **Platform rules:** HN/Reddit accounts posting AI content — mitigated by
  full disclosure and low volume; if a community objects, withdraw.
- **Quality variance** on crosswords (hard constraint satisfaction) — mitigate
  with a programmatic crossword generator + Claude for clues, not freehand.

## Out of scope (v1)

Physical goods, subscriptions, custom domains per format, selling to agents
(that's experiment #2, funded by this one), any paid ads before organic launch.
