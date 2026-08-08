# Runbook: Weekly Deep Run ("board meeting")

Run after the Sunday fulfillment run. This is where the business thinks
about strategy, not fulfillment. Read this alongside `MANDATE.md` — the
mandate's "Manager principles" section is the standing goal; this file is
the weekly checklist for acting on it.

1. Read `MANDATE.md`.
2. Compute the week from the ledger (`ops.ledger.load` + `summary`, plus
   per-format counts from `sale` events' product names): sales, revenue,
   refunds, refusals, previews sent, preview-to-sale conversion rate,
   fulfillment latency.
3. Decisions — for each one, record a `decision` ledger event with a
   `reasoning` field before acting:
   - **Carry the open questions.** `ls journal/*needs-human*` and read each
     one. Answer the ones that are mine to answer; for the rest, restate the
     question plainly in this week's entry so it stays in front of Anay
     instead of aging out of the feed. A question raised once and never
     repeated is a question nobody is going to answer (added 2026-08-08,
     with three open at the time).
   - **No new product lines.** Three formats exist (crossword, dossier,
     briefing). Do not add a fourth, ever, regardless of what a support
     message or a slow week suggests — the founder was explicit about
     this. All effort goes into converting, pricing, and distributing the
     three that exist.
   - **Kill is still allowed** for a format with zero previews requested
     two weeks running and no qualitative signal — but "kill" means stop
     promoting it and drop it from the site, never means "replace it with
     something new."
   - **Price:** move a price only on evidence (previews requested but no
     payment follow-through suggests price friction; payment friction with
     no complaints suggests room to raise). Max ±$5/week. Edit
     `price_cents` in `data/products.json` directly — there is no external
     product API (Tally forms don't carry price; price is enforced at
     payment verification time in the fulfillment runbook).
   - **Conversion, not just traffic:** if previews are requested but
     payment never follows, that is the most important signal in the
     ledger. Investigate before anything else — revise the preview email's
     ask, shorten the gap between preview and pay, or reconsider price.
     A dead format gets killed; a leaky funnel gets fixed.
4. Marketing: day-to-day distribution now runs continuously via
   `RUNBOOK-GROWTH.md` (every ~4 hours, not just weekly — added 2026-07-31
   after realizing the business only ever marketed itself when a human
   was actively in the chat). This weekly slot is for the one thing the
   growth cycle shouldn't decide alone: a genuinely significant post
   (a real milestone, a strategic pivot, a week-in-review), on a channel
   not overused, always disclosed as AI, always linking the dashboard.
   If genuinely nothing changed, say the honest week-in-review instead of
   nothing. Answering inbound engagement (HN/Bluesky/Moltbook comments and
   replies)
   happens every run, not just weekly, and does not count against this cap.
5. Write the board-meeting journal entry: the numbers, each decision with
   its reasoning, and one honest sentence about how the experiment is
   going. Net profit is the only metric that matters long-term; say so
   plainly if the week was flat or bad.
6. Rebuild dashboard, commit, push, deploy (as in the fulfillment runbook).
