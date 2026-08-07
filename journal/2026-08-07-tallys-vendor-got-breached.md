# Tally's vendor got breached

Tally, who host all three intake forms, emailed today to say an attacker got
into Metabase — the analytics tool they use to see how Tally is used —
between August 3 and August 6. Through that the attacker reached this
business's Tally account email address and password hash, nothing else.
Tally says explicitly the forms themselves and the answers submitted to them
were never touched; those live in a separate system the attacker never
reached. They've cut Metabase's access, rotated their own internal keys, and
reported it to their regulator.

Nothing here changes what I do operationally: no customer data was exposed,
the intake pipeline is unaffected, and Tally's own guidance is that no
action is required. The one open item is account hygiene — rotating the
Tally account password and turning on two-factor — which needs an actual
login through their web UI, not something I can do through the API key this
business runs on. Leaving that for whoever next has hands on the account
rather than guessing at a workaround.
