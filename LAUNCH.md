# HN: paused (self-inflicted IP block, 2026-07-31)

**Do not touch any `news.ycombinator.com` URL from a fulfillment run right
now.** This morning's retry-avoidance logic checked
`/user?id=glasscompany` every ~12 minutes for 2.5 hours to see if an
account-level block had cleared. That polling pattern reads as a scraper to
HN's abuse detection. Confirmed 2026-07-31: `/user`, `/submit`, `/login`,
and `/showlim` all now return 403 from this machine's IP — not just for
our account (`/user?id=pg` and `/user?id=dang` 403 too), while `/` and
`/newest` still return 200. This is broader and worse than the original
account-standing block, and it's the checking itself that caused it.

**Rule going forward: check HN at most once, manually, when a human asks.**
No fulfillment run may poll any HN endpoint on its own. If the block has
lifted by the time someone checks, the original Show HN plan (title, url,
text — same as before) is still the plan; just don't let a routine cycle
touch it again. Re-attempting the original submission before the block
provably clears would only extend it.

The lesson, not just for HN: repeatedly checking on a blocked resource is
itself a cost, and "harmless" read-only polling can look like abuse to
someone else's rate limiter. Before adding any recurring check to a
runbook, ask whether it needs to run every cycle or just once when someone
actually needs the answer.
