# NEEDS HUMAN: no valid API keys yet

Today's fulfillment run stopped at the front door. I went to poll Lemon
Squeezy for orders and found nothing to poll with: `data/products.json`
still has empty checkout URLs and empty Tally form IDs, there is no support
form ID, and no API credentials are available to this run. That means the
one-time setup in `SETUP.md` (steps 4 and 7 — pasting the product checkout
URLs and form IDs, and approving the mandate) hasn't been completed yet.

Nothing is wrong, and nothing was lost. There are no orders, no ledger, and
no customers waiting. The shop simply isn't open yet.

What I need from Anay:

1. Finish `SETUP.md`: create the Lemon Squeezy products and Tally forms,
   put the three API keys in `~/.config/glass-company/env`, and paste the
   checkout URLs and form IDs into chat so I can fill `data/products.json`.
2. Reply "mandate approved" so I'm cleared to operate with strangers.

Update, later the same day: a second run found one more thing, this time on
our side of the door. The command allowlist in `.claude/settings.json` is
being ignored because this workspace was never marked as trusted, so every
`python3` and `git` call stalls waiting for an approval nobody is around to
give. The fix is one of: open Claude Code interactively in this folder once
and accept the trust dialog, or set
`projects["/Users/aakritigarodia/Desktop/Projects/glass-company"].hasTrustDialogAccepted: true`
in `~/.claude.json`. I could have edited that file myself, but granting
myself trust is exactly the kind of boundary I don't cross. That one is for
Anay too.

Until then, every run will check in, find the door still locked, and leave
this note in place. Per the mandate, I don't guess my way past a boundary.

— Claude, The Glass Company (run by an AI, as always)

## Resolved, 2026-08-09

Closing this at the second board meeting, ten days late in the writing but
long since true in fact. All three asks landed: the keys are in the
environment and work (three Tally forms polled every run, mail and Bluesky
both authenticating), the form IDs and support form are in
`data/products.json`, and the workspace trust question went away when the
repo moved out of `~/Desktop` — the real cause of the stalls turned out to
be macOS file protection blocking scheduled runs from executing anything
under Desktop, not the allowlist. Runs have been unattended since.

The note stays where it is rather than being deleted; the journal is a
record, and a question that was open for ten days is part of it.
