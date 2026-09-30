---
name: x-mirror
description: "Travis Fischer's personal X mirror: schedules his new top-level X posts and threads (@transitive_bs) on Bluesky and Threads through Postiz. Use when asked to mirror, cross-post or sync recent X posts to Bluesky or Threads, or when the scheduled x-mirror task runs."
---

# x-mirror

X is Travis's primary channel; Bluesky and Threads follow it with no extra work from him. This skill schedules his recent X posts on both through Postiz, with no confirmation step. Project launches are handled by the [social-posting](../social-posting/SKILL.md) skill instead.

Run it:

```bash
python3 ~/.agents/skills/x-mirror/x_mirror.py            # mirror posts from the last 48 h
python3 ~/.agents/skills/x-mirror/x_mirror.py --dry-run  # show the plan only
python3 ~/.agents/skills/x-mirror/x_mirror.py --lookback-hours 168   # one-off backfill of a week

# spaced-out backfill of specific posts, in the order given: about one a day per channel, in US daytime
python3 ~/.agents/skills/x-mirror/x_mirror.py --only ID1 ID2 ... --include-launches --gap-hours 20 --window 13-23
```

`--only` fetches the given posts directly at any age. Threads older than X search's 7-day window come from the local birdclaw archive. `--include-launches` also mirrors project-launch posts, for a deliberate backfill of posts that did well on X.

It prints one line per decision (`posted`, `skip`, `wait`, or `plan` in a dry run). Report those lines as they are.

## Rules the script enforces

- **Only new top-level posts and his own threads.** Replies to other people and reposts are never mirrored. A thread (his chain of replies to himself) is mirrored as a thread. Polls are skipped.
- **No X links on Bluesky or Threads.** People use them to get away from X. When a post quotes or links an X post, the script handles it per platform:
  - One of Travis's own posts: the link is swapped for the matching post on that platform (its mirror, or a launch post with the same opening line).
  - A match that isn't live yet: the post waits for the next run.
  - Anyone else's post, or an own post with no match: the post is skipped on that platform.
- **Project launches are left to the [social-posting](../social-posting/SKILL.md) workflow.** A post is skipped when it, or one of his replies under it, links to `transitivebullsh.it/projects/...`, or when a Postiz launch post on that channel already has the same link or opening line.
- **Nothing posts twice on a platform.** A post is also skipped when its opening line is already in any Postiz post on that channel, or already published on his Bluesky profile (read from the public API, which catches posts made outside Postiz). Threads has no public read API, so posts made there by hand aren't checked.
- **Text stays as written.** t.co links are expanded and X media links dropped. `@handles` lose the `@` on Threads so they can't tag the wrong person. Text over the limit (Bluesky 300, Threads 500) becomes extra thread posts rather than being cut.
- **Media is carried over.** Photos (up to 4) or the first video are re-uploaded to Postiz.
- **Timing is best effort.** The earliest slot at least 3.5 h from other Postiz posts on that channel (launch posts are the main post of the day) and 45 min from other mirrors. If there is no such slot in 36 h, it posts soon anyway.
- **Posts must be at least 1 h old** (X's edit window, and time to finish a thread). Younger ones wait for the next run.
- **Real links only** (`shortLink: false`). Mirrors carry the Postiz tag `x-mirror`.

State lives in `~/.local/state/x-mirror/state.json`: each X post is mirrored or skipped once. Delete an entry to retry it.

## When it fails

`x-mirror failed: ...` on stderr, with exit code 1.

- **Auth errors:** `xurl auth status` and `postiz auth:status` show which CLI lost its session. Tell Travis rather than re-authenticating.
- **Anything else:** report the message. Don't hand-post the missing mirrors; the next run retries anything not recorded in state.
