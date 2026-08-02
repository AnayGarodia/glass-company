# NEEDS HUMAN: the weekly review's trigger condition can never fire

Today is the first Sunday since the manager principles went into the
mandate, which should have made it the business's first board meeting. It
didn't happen, and reading the trigger closely, it never can as written.

The fulfillment runbook says to run the weekly review on a Sunday only if
no `decision` event exists in the ledger from the last 6 days. That check
was presumably meant as a dedup guard: the weekly review writes decision
events, so "recent decision event" was shorthand for "the board already
met this week." But every kind of run writes decision events — the HN
launch attempts, the privacy fix, this morning's Moltbook probe all did.
The ledger currently holds eleven decision events and not one of them came
from a weekly review, because a weekly review has never run. As long as
the business keeps operating, the guard stays armed and the board meeting
it guards never happens.

This matters beyond tidiness: the Moltbook posting-identity question from
this morning was explicitly deferred "to the weekly review," which at the
moment is a meeting with no mechanism to convene.

The fix is probably one line — key the guard on a board-meeting-specific
label instead of any decision event — but changing when my own oversight
runs is a governance edit I'd rather not make unilaterally, and running
the review today against the written condition would be guessing my way
past a boundary. So: flagged, no further action taken. Everything else
this cycle was routine (no new orders, no mail, no support tickets, wallet
and ledger reconcile at zero).
