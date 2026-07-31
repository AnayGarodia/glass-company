# Remaining setup (Anay, ~1 min)

Update 2026-07-31 (later the same day): **project moved to `~/glass-company`.**
macOS silently blocks launchd background agents from executing scripts under
`~/Desktop`, `~/Documents`, `~/Downloads` (TCC privacy protection) — that had
been the real reason every scheduled run was failing with "Operation not
permitted." Moved the whole repo out from under Desktop to fix it for good.
This means the trust grant from before no longer applies to the new path.

✅ Cloudflare, Bluesky, Tally, AgentMail, HN account, wallet backup — all
already done. The only thing left:

## Trust the new location (~1 min)

```bash
cd ~/glass-company && claude   # accept trust dialog, exit
```

Then reload the scheduled job at its new path (Claude will do this, but the
command is here for reference):

```bash
launchctl unload ~/Library/LaunchAgents/ai.glasscompany.fulfill.plist 2>/dev/null
cp ~/glass-company/launchd/ai.glasscompany.fulfill.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/ai.glasscompany.fulfill.plist
```

That's it. Nothing else is needed from you going forward.
