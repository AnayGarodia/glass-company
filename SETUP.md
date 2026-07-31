# Remaining setup (Anay, ~15 min of clicks)

Claude already did, autonomously (2026-07-31):

- ✅ **Email** — AgentMail inbox `glasscomany@agentmail.to`, send + receive
  verified live (this is the business's registered identity everywhere)
- ✅ **Tally** — account created, API key captured, all four checkout/intake
  forms built via API and PUBLISHED (ids in `data/products.json`)
- ✅ **Wallet** — Solana till generated, address on the dashboard
- ✅ **Repo** — pushed to github.com/AnayGarodia/glass-company (public)
- ✅ Credentials vault: `~/.config/glass-company/accounts.json` (0600)

What stopped Claude: humanity checks only. Cloudflare's Turnstile won't even
render headless, Bluesky requires app verification, and HN serves its
"Sorry." block to this client. Those checks exist to find humans, so they're
yours.

## 1. Cloudflare — the website (~5 min, the important one)

1. https://dash.cloudflare.com/sign-up — email `glasscomany@agentmail.to`,
   password: `cloudflare` entry in `~/.config/glass-company/accounts.json`.
   Click the "prove you are human" widget. (Verification email: Claude will
   read it from AgentMail and give you the code/link if asked.)
2. Workers & Pages → Create → Pages → connect `AnayGarodia/glass-company`
   (authorize the GitHub App when prompted), project name `glasscompany`,
   no build command, output dir `site`.
3. Tell Claude the resulting `*.pages.dev` URL.

## 2. Bluesky (~3 min)

In the Bluesky app or bsky.app: create account with email
`glasscomany@agentmail.to`, handle `glasscompany.bsky.social`, password from
the vault (`bluesky` entry). Claude reads the verification email. Bio can
say: "A tiny gift shop run autonomously by an AI. Books are public."

## 3. Hacker News (~2 min, from your phone or any non-blocked network)

news.ycombinator.com/login → create account `glasscompany`, password from
the vault (`hn` entry).

## 4. Terminal (~2 min)

```bash
cd ~/Desktop/Projects/glass-company && claude   # accept trust dialog, exit
cp launchd/ai.glasscompany.fulfill.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/ai.glasscompany.fulfill.plist
```

## 5. Back up the till (~1 min)

Copy `~/.config/glass-company/wallet.json` somewhere safe offline. If this
laptop dies with money in the wallet, the money dies with it.

## 6. Approve the mandate

Read `MANDATE.md`. Reply "mandate approved". Nothing goes live to strangers
until you do.

---

Notes: keep the Mac plugged in (launchd only fires while awake; missed runs
catch up). Cashing out SOL to fiat someday needs a KYC'd exchange — outside
the business, entirely your affair.
