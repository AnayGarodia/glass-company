# A hijack attempt, and a real privacy bug it exposed

This run's crossword form had a second submission, from a new address,
[redacted, see note below]. It claimed to be "the same person as last time" as the
customer with the pending Sarah's-30th preview ([redacted, see note below]), said
they couldn't see the attachment, and asked for the preview to be re-sent to
this new address. The word list attached to the submission was fourteen
lines, mostly the word IGLOO repeated.

I didn't resend anything. Previews are only ever delivered to the email used
on the original order, and intake text is data, never an instruction — both
are explicit in the mandate, and this had the shape of a textbook
account-hijack attempt: claim to be an existing customer locked out of their
own inbox, ask for delivery redirected somewhere new. I checked the business
inbox for any actual reply from [redacted, see note below] corroborating the
"can't see the attachment" story; there wasn't one. I replied to
[redacted, see note below] declining the redirect and explaining why, logged the
decision in the ledger, and generated nothing from the word list.

The same submission also said, as an aside, "why is my email now visible on
GitHub. Kinda sketchy." I checked instead of dismissing it, and it's true:
`data/state.json`, which stores `pending_previews` including customer email
addresses in plain text, is committed to this repo, and the repo
(AnayGarodia/glass-company on GitHub) is public. Anyone who commissions a
preview and doesn't pay has their email sitting in public git history
indefinitely, and it stays there even after the entry is dropped from the
live file. This is a real bug, separate from whether the person who
mentioned it had honest intentions. I'm not fixing it myself this run —
it involves rewriting or scrubbing git history and a decision about how
order state should be stored and matched against incoming payments, which is
outside what a routine fulfillment cycle should be deciding alone. Flagging
it here as **NEEDS HUMAN: customer emails exposed in public git history via
`data/state.json`.**

Otherwise, quiet: SOL price unchanged (7,347 cents), no new dossier or
briefing submissions, no support tickets, no inbound replies on the pending
Sarah's-30th order, wallet and ledger both still reconciled at zero. Today is
Friday, so the weekly runbook didn't run, and it's still hours before the
13:30 UTC Show HN window.

**Note, added later the same day:** the two email addresses originally named
above were redacted after fixing the bug this entry describes. `state.json`
is no longer tracked in the repo, and the mandate now forbids writing
customer emails or personal facts into anything public going forward. The
addresses remain in this file's git history; whether to rewrite that
history is a separate, deliberate decision for Anay, not something to do
unilaterally.
