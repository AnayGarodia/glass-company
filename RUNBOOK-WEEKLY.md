# Runbook: Weekly Deep Run ("board meeting")

Run after the Sunday fulfillment run. This is where the business thinks.

1. Read `MANDATE.md`.
2. Compute the week from the ledger (`ops.ledger.load` + `summary`, plus
   per-format counts from `sale` events' product names): sales, revenue,
   refunds, refusals, fulfillment latency.
3. Decisions — for each one, record a `decision` ledger event with a
   `reasoning` field before acting:
   - **Kill:** a format with zero sales two weeks running and no qualitative
     signal (support questions, near-misses) gets retired.
   - **Launch:** if a format died or an intake/support message suggested a
     better product, design one new format (name, price, intake questions,
     template reuse or new template committed to `templates/`).
   - **Price:** move a price only on evidence (e.g. sales but complaints, or
     traffic but no conversion), max ±$5/week.
4. Execute product changes via the Lemon Squeezy API where possible; anything
   needing dashboard access → journal "NEEDS HUMAN: <exact steps>".
   Update `data/products.json` to match reality.
5. Marketing: at most one action this week. A post only where self-promo is
   allowed, always disclosed as AI, always linking the dashboard, never the
   same community twice in a row. If nothing has changed worth telling
   people, do nothing — silence beats spam.
6. Write the board-meeting journal entry: the numbers, each decision with its
   reasoning, and one honest sentence about how the experiment is going.
7. Rebuild dashboard, commit, push (as in the fulfillment runbook).
