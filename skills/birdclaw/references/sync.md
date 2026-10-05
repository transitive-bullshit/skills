# Incremental personal X sync

Use this procedure for the existing 12-hour `sync-birdclaw-x-archive` task or a requested incremental refresh of `@transitive_bs`. All three sync surfaces use explicit `bird`; an unavailable bird transport produces a partial report rather than an unattended paid API fallback. Public ad hoc lookups still follow [x-data](../../x-data/SKILL.md).

## Preflight

- Record the UTC start time, run `birdclaw --json db stats`, and run a read-only SQLite `pragma quick_check` against `~/.birdclaw/birdclaw.sqlite`.
- Verify `bird --plain whoami` identifies `@transitive_bs` (user ID `327034465`) through the existing browser session. Use the normal approved command path for Keychain/network restrictions; never inline or display cookies/tokens.
- Inspect the account's bird cursor:

```sql
select value_json, updated_at from sync_cache
where cache_key = 'authored:bird:acct_primary:cursor';
```

Authored sync requires a persisted, non-null `sinceId` in `committed` state, or a resumable `pending-forward` state with a non-null `sinceId` and pagination token. If it is absent or invalid, skip authored sync and report the missing baseline; likes and bookmarks may still run. Keep `authored:xurl:acct_primary:cursor` intact as historical transport state. Birdclaw may seed missing transport cursors from archive data, but this scheduled task requires the saved bird cursor rather than risking a full-history scan.

Never use `--until-id`, reset/delete a cursor, supply an arbitrary `--since-id`, or backfill authored history in this task.

## Refreshes

Run each surface independently and inspect JSON `partial`, `error`, and cursor metadata even when the process exits successfully:

```bash
birdclaw --json sync authored --account transitive_bs --mode bird --limit 100 --max-pages 5
birdclaw --json sync likes --account transitive_bs --mode bird --limit 100 --all --max-pages 5 --early-stop --refresh
birdclaw --json sync bookmarks --account transitive_bs --mode bird --limit 100 --all --max-pages 5 --early-stop --refresh
```

An authored page cap can leave a safe `pending-forward` cursor; report it as partial and let the next run resume. Run likes and bookmarks even if authored sync fails or is skipped. Preserve each surface's progress and failures separately.

Use profile metadata ingested by these bird refreshes and compare local `profile_snapshots` before/after the run. Do not perform the old paid `/2/users/me` lookup or re-fetch old authored posts solely to force a profile snapshot. If the bird payload does not refresh the requested profile fields, report them as unavailable or unchanged in the local observations; retain each source's verification labels instead of treating labels from different transports as equivalent.

## Verification and report

Run a database integrity check after the refreshes. Confirm the bird authored cursor never moved backward; a committed cursor should cover the latest authored item observed through bird, while pending progress must retain its baseline and resume token. Leave the xurl cursor untouched.

Use run-start timestamps and Birdclaw metadata to distinguish new authored items from observations/updates. Classify standalone posts, replies, quote posts/quoted replies, and reposts without double-counting. Report likes/bookmarks as observed counts when `tweet_collections` has no first-seen timestamp; exact new counts are then unavailable. Include distinct observed/updated tweet IDs and refreshed profile IDs, detected personal profile changes, integrity, and cursor state.

Report per-surface transport/page counts and any errors. No `xurl` calls means no paid X API reads in this procedure; do not infer an exact monetary charge or model cost when billing data is unavailable.

Preserve the scheduled task's existing bookmark-to-Notion follow-on and its approval state. Run it only when its existing prerequisites and authorization allow it; report a blocked or failed Notion step separately from a successful Birdclaw sync. This transport update does not authorize retrying a previously rejected disclosure or Notion write.
