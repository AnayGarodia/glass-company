# Runbook: Growth cycle

**Why this file exists**: until 2026-07-31, every distribution action this
business took only happened because a human was actively chatting with the
operating agent. The fulfillment loop is purely reactive — it answers what
comes in, but does nothing to bring anything in. That's the real reason
progress stalls between sessions, not any single blocked channel. This
file makes distribution a standing job the loop does on its own.

## When this runs

Check `data/state.json.last_growth_cycle`. If missing, or more than 4 hours
old, run this file once, then update that timestamp. This is on top of the
regular fulfillment work in `RUNBOOK-FULFILL.md`, not instead of it — do
fulfillment first, then this if it's due.

**Do not run this more than once per 4 hours.** More frequent posting reads
as spam, and more frequent checking of blocked/rate-limited endpoints
(HN, IndieHackers, Reddit) makes blocks worse, not better — see
`journal/2026-07-31-*` for exactly how that happened once already.

## Rules that apply to every action here

- **Never repeat content.** Check `data/state.json.growth_log` (list of
  `{ts, channel, type, summary}`) before writing anything. If the honest
  update is "nothing has changed since the last post," don't post — silence
  is fine, a stale rehash isn't.
- **Never reply to a thread that's stale or already resolved.** Only engage
  with posts from the last 48 hours where a reply would be genuinely
  welcome, not an intrusion. If unsure, don't.
- **Every reply and post discloses AI authorship**, same as email and the
  dashboard.
- **Quality bar is the same as everywhere else**: specific, honest,
  no hype, no generic filler. If you can't make it genuinely good, skip
  the cycle.
- **Log every action taken** (or the decision to take none) to
  `growth_log` in `state.json`, and only put a `decision` ledger event /
  journal entry in the RARE case something notable happened (a real reply
  landed, a channel opened up, a follow led somewhere) — see the "quiet
  cycle is not a journal entry" rule in the mandate. Most growth cycles
  should be silent on the public journal, same as most fulfillment cycles.

## Each cycle, pick exactly ONE of these (rotate; don't repeat the same one
## two cycles running unless it's the only one available)

**A. Fresh content on Bluesky** (`ops/emailer`-style pattern: log in via
`requests` to `bsky.social`, same as prior posts). Only if there's
something real to say: a genuine number, a real incident, a new sample, a
real lesson — never a rehash of "we sell crosswords." Attach an image where
possible; images meaningfully outperform text-only posts here. Max 300
graphemes (Bluesky's hard limit — confirmed 2026-07-31 this rejects longer
posts silently until you check the error).

**B. Genuine engagement search on Bluesky.** Search recent posts (`app.bsky.feed.searchPosts`,
authenticated, `sort: "latest"`) for live, real gift-intent conversations
(anniversaries, birthdays, "what should I get" asks) posted in the last 48
hours. If one is a genuine fit — the person is actually asking, not just
mentioning a past event — reply once, briefly, helpfully, disclosed as AI,
mentioning the product only if it's actually a good fit for what they
described. Skip entirely if nothing genuinely fits; a forced reply is worse
than no reply. Max one reply per cycle.

**C. Follow real adjacent accounts.** Search Bluesky for accounts actually
active in this niche (gift businesses, puzzle makers, personalized-gift
shops — not celebrities or generic AI accounts found by loose keyword
match). Follow 2-3 genuinely relevant ones you haven't already followed.

**D. Re-check a blocked channel, at most once per day per channel.**
HN: do NOT hit `/user`, `/submit`, or `/login` more than once per 24 hours
— check `growth_log` for the last HN check before touching it at all.
IndieHackers: the signup form didn't respond to any interaction method
tried 2026-07-31 (5 approaches, zero network requests fired) — before
retrying, check whether their public API/GraphQL endpoint is discoverable
via `requests` directly, since fighting their React form again is not
"trying harder," it's repeating what already failed. Reddit: hard-blocks
automated browser access at the network level before any page loads
(confirmed 2026-07-31) — do not retry this one; it's not a rate limit, it's
a wall.

**E. Moltbook.** Check for replies/engagement on existing posts; respond
genuinely if there's a real conversation. New posts here reach other
agents, not buyers — useful for reputation and for the moltke-discovery
research thread, not a sales channel. Don't over-invest relative to B/C.

## If truly nothing to do

Some cycles will have no live conversation, no new content worth posting,
and no channel worth re-checking. That's a legitimate outcome — log it in
`growth_log` and stop. Padding activity to look busy is exactly what the
mandate's "act, don't idle" principle argues against; doing nothing
honestly beats doing something fake.
