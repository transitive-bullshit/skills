---
name: x-data
description: "Read or research X/Twitter posts, URLs, profiles, threads, or the user's X history using the cheapest available source."
---

# X data

For X reads in any project, use this order and stop when the requested evidence is sufficient:

1. **Local Birdclaw snapshot.** Search the current indexed archive first, including supplied post URLs and recent content. Use the installed `birdclaw` CLI or read-only SQLite at `~/.birdclaw/birdclaw.sqlite`. A URL supplies a tweet ID; it does not bypass the archive.
2. **Globally installed `bird`.** Fill archive gaps through the existing authenticated browser session. The personal account is `@transitive_bs`; verify it with `bird --plain whoami` before account-specific reads or syncs. Use installed command help rather than assuming a command exists.
3. **Public FxTwitter API.** If `bird` fails or lacks the required operation, try `https://api.fxtwitter.com` for public data. It cannot supply private DMs, authenticated bookmarks, or other account-private data; mark that tier inapplicable for those requests.
4. **Paid `xurl`.** Use the [xurl reference](../xurl/SKILL.md) only after the cheaper applicable sources failed or could not provide the required evidence. Keep calls bounded and report why the paid fallback was needed.

Freshness is part of sufficiency. Check the archive's observation/sync timestamps; if the request needs current engagement, profile state, or posts beyond its coverage, retrieve only those missing or stale fields in the same order. Preserve archive context and distinguish cached observations from live results. An empty result is a coverage gap, not proof that a post or person never existed.

## Common reads

```bash
birdclaw --json show tweet POST_ID
birdclaw --json show thread POST_ID
birdclaw --json search tweets "query" --limit 50
birdclaw --json search tweets --author transitive_bs --since YYYY-MM-DD --limit 100
```

For archive analysis, local DMs, identity resolution, or synchronization, read the [Birdclaw skill](../birdclaw/SKILL.md) when installed. Its optional enrichment can touch live transports: use `--no-xurl-fallback` for identity/DM enrichment, and explicit `--mode bird` for syncs. `auto` may fall back to paid `xurl` before trying FxTwitter.

After the local probe, common `bird` reads are:

```bash
bird read POST_ID_OR_URL --json
bird thread POST_ID_OR_URL --max-pages 2 --json
bird search "from:transitive_bs query" -n 20 --json
bird user-tweets transitive_bs -n 20 --json
```

After `bird` fails, fetch a public post with:

```bash
curl --fail --silent --show-error --max-time 30 \
  -H 'User-Agent: personal-x-data/1.0' \
  "https://api.fxtwitter.com/2/status/POST_ID"
```

Validate both HTTP status and the JSON `code`, and require a usable `status` object. Other v2 endpoints and response shapes are documented by [FxEmbed](https://github.com/FxEmbed/FxEmbed/blob/main/docs/src/content/docs/api/introduction.mdx); the live spec is `https://api.fxtwitter.com/2/openapi.json`. Send only the public identifier or query needed for the lookup. Private archive/DM context stays local.

## Writes and account actions

The archive and FxTwitter are read sources. For an authorized X post or reply, prefer a supported `bird` command; use `xurl` if that operation is unavailable or fails. Apply the lookup order to any reads needed to prepare the action. A read or sync request does not authorize posting, messaging, or changing the account.

Use existing authentication without printing cookies, tokens, or credential files. If sandbox restrictions block an installed transport, use the normal tool approval path when available before treating it as an authentication failure.
