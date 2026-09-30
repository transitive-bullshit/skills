---
name: social-posting
description: "Travis Fischer's personal social posting workflow: launch game plans, scheduled posts, and cross-posting across Threads, Bluesky, LinkedIn, Instagram and TikTok through Postiz, using his X posts as the guide. Use for any social post, launch plan, posting schedule, backfill of past projects, or social results check, even when the user only says 'post this' or 'plan the launch'."
---

# Social posting

Travis builds and launches a lot of projects. X is where he puts the care: he drafts and posts there by hand, usually first. Every other platform is a lightweight bet for reach. The agent writes, schedules and measures those posts through Postiz, with no approval step.

| Channel | Account | Who posts | How |
| --- | --- | --- | --- |
| X | [@transitive_bs](https://x.com/transitive_bs) | Travis, by hand (Typefully) | Agent may suggest drafts; never posts |
| YouTube | Travis's channel | Travis, by hand | Agent prepares the package; never uploads |
| Threads | [@transitive_bullshit](https://www.threads.com/@transitive_bullshit) | Agent via Postiz | Launches; [`x-mirror`](../x-mirror/SKILL.md) mirrors his other X posts |
| Bluesky | [@transitivebullsh.it](https://bsky.app/profile/transitivebullsh.it) | Agent via Postiz | Same as Threads |
| LinkedIn | [fisch2](https://www.linkedin.com/in/fisch2) (personal) | Agent via Postiz | Launches, businesslike framing |
| Instagram | [@transitive_bullshit](https://www.instagram.com/transitive_bullshit) | Agent via Postiz | Video launches (Reels) |
| TikTok | [@transitive.bs](https://www.tiktok.com/@transitive.bs) | Agent via Postiz | Video launches |

Schedule Postiz posts directly and report what went out. Save questions for X and YouTube, the only channels where Travis confirms the details himself.

## Every post is new on its platform

Each platform sees a piece of content once. A repeated or near-identical post on the same account reads as spam and reflects badly on Travis's personal brand, and on LinkedIn it's especially costly. Returning to a topic is fine when it's a deliberate part of the plan: a new angle, new media, and new copy, spaced days apart, like a throwback or a second-shot clip.

Before scheduling anything, check each target channel for the same content, both **scheduled** and **already published**:

- **Scheduled and Postiz-published:** `postiz posts:list` over the past month and the coming weeks. Match on the project, the media and the opening line, not just the exact text. This includes text-only copies of his X posts that `x-mirror` queued.
- **Published outside Postiz:** Travis also posts by hand (Slow It Down went to Instagram and TikTok manually), and Postiz can't see those posts.
  - Bluesky: read his recent posts from the public API, `curl -s "https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?actor=transitivebullsh.it&limit=50"`.
  - Threads, Instagram, TikTok and LinkedIn: check his profile pages in the browser.

If the same content is already there, skip that channel, or replace the queued post, and say which in the report. Never create a second copy to be safe.

## 1. Gather context

Read before writing anything. The sources differ in how much of Travis they carry:

- **His X posts come first.** They're where he drafts and refines the framing, and they're his voice. Find the launch post, his self-replies in its thread, and other recent posts about the project: `xurl search "from:transitive_bs <project terms>"`, or `xurl read <post-url>` for a known post. For older history use the local archive through the `birdclaw` skill. Compare their engagement (`public_metrics`: impressions, likes, bookmarks): the angle that did best on X usually leads everywhere else, even when it isn't the announcement post.
- **The project repo:** README, `AGENTS.md`, docs. Use them for facts: what it is, how it was made, costs, credits, links.
- **The Notion Projects entry** backs his website ([Projects database](https://app.notion.com/p/3c5edb27f12480a69a16d7c2f8a1f078); the `personal-notion-projects` skill documents it). Sometimes it's his most refined telling of the story. Sometimes it's an AI-assisted derivative of the README. Use it for extra context and facts, not as a voice sample.
- **The public write-up** at `https://www.transitivebullsh.it/projects/<slug>` and the YouTube video, when they exist. These are what posts link to.
- **What's already out** on each channel, scheduled or published, as described in [Every post is new on its platform](#every-post-is-new-on-its-platform).

This step is done when you can state the project's hook, the X angle that performed best, two or three concrete facts (tools, cost, time, what's surprising), its credits, its canonical links, and what each channel already has for it.

## 2. Write each platform's version

Adapt, don't copy. Every platform gets the same core claim and facts, framed for its audience, and no two posts share the same copy. Read [voice and platforms](references/voice-and-platforms.md) for Travis's voice, the do's and don'ts, and each platform's framing, limits and examples.

For story structure (the hook, the stakes, a payoff that lands), use the [storytelling](../storytelling/SKILL.md) skill, especially for LinkedIn and anything longer than a few lines.

Finish with an **unslop pass**. Apply the rules of the `unslop` skill (it's manual-invoke only, so read its SKILL.md rather than invoking it): cut puffery and AI vocabulary, no em dashes, no chatbot phrasing. Then check the draft still sounds like his X posts.

Write each draft to `social/drafts/<platform>.md` in the project repo. It's local working state: make sure `social/drafts/` is in the repo's `.gitignore` and never commit it. Postiz is the record of what went out. Check each draft against its platform's character limit.

## 3. Launch game plan

Use this for a new project launch, or a backfilled one (see below).

1. **Check X and YouTube.** Confirm whether Travis has posted the X launch and the YouTube video, and link them in your report. If he hasn't, say so and offer draft suggestions for X, but never post there. A launch usually goes out on X first; the other platforms follow within a day or two.
2. **Prepare media.**
   - Use the clean master, never a file downloaded back from another platform. Instagram penalizes watermarked reposts.
   - Keep uploads under 300 MB, the Instagram and Bluesky API limit. Re-encode if needed (1080p H.264, audio copied).
   - Make the first frame the poster, since platforms often use it as the default cover.
   - TikTok's feed and profile grid are 9:16, so make a vertical cover there. Keep the face and title inside the middle 3:4, which is what the profile grid shows.
   - Instagram fits a Reel's cover to the video's shape: for a 16:9 video, use the 16:9 poster.
   - Check the soundtrack's rights before TikTok and Instagram. Both match audio and can mute or pull a post, and TikTok Business accounts are limited to TikTok's commercial music library. Original or Suno-generated audio is fine. For a licensed or commercial track, schedule anyway and flag it in the report, or skip those two channels if the video depends on the track.
3. **Pick the channels.** Video launches go to all five. A text or link project goes to Threads, Bluesky and LinkedIn; add Instagram only if there's a strong visual.
   - One launch post per project per channel. If one is already queued, replace it with `posts:delete` and a new post in the same slot, or keep it and skip that channel. Say which in the report.
   - If `x-mirror` already queued text-only copies of the launch, keep the published ones. Delete queued mirrors that would land within a day of the launch post, and say so.
4. **Schedule through Postiz.** Follow [Postiz mechanics](references/postiz.md) for uploads, per-platform settings and gotchas. The defaults:
   - Real links, never short links: `--no-shortLink`. Link the write-up in every post except TikTok, where links aren't clickable. It's also how `x-mirror` recognizes a launch. When there's a live product, link it first, then the write-up.
   - Staggered slots in US daytime (roughly 14:00–19:00 UTC), one platform per slot.
   - LinkedIn on a weekday morning ET (around 13:00 UTC).
   - **Natural times.** Vary every slot by a random offset of up to about 45 minutes, and avoid round times like :00, :15 or :30. Space platforms unevenly. Evenly spaced posts at round times read as automated.
   - At least 3.5 hours from other Postiz posts on the same channel. A launch is the main post of the day there.
   - Set the AI-generated labels wherever the platform offers them.
5. **Verify and report.** Run `postiz posts:list` and confirm every post is `QUEUE` with the right time and settings. Report a table: platform, UTC time, Travis's local time, and the framing used. Also report anything he has to do by hand, like Instagram's AI label and the X and YouTube items.

## Other workflows

- **His non-launch X posts** go to Bluesky and Threads through the [`x-mirror`](../x-mirror/SKILL.md) skill, which runs twice a day. It skips anything linking to a `transitivebullsh.it/projects/...` write-up, because launches belong to this workflow. So always include the write-up link in launch posts.
- **Backfilling past projects:** run the launch game plan for one past project per platform per week, interleaved with new launches. Frame it as a throwback or "behind the build" post, with fresh copy and a different cut or cover than the original. Spam filters punish bursts, and TikTok caps a creator at about 15 posts a day.
- **Backfilling Bluesky and Threads from X:** take his top-performing X posts (the 90th percentile and up by likes) since a start date he names, from the local archive (`~/.birdclaw/birdclaw.sqlite`, his top-level posts only). Mirror them strongest-first with `x-mirror --only <ids> --include-launches --gap-hours 8-15 --window 12-4`. That spaces them a random 8–15 hours apart per channel, between 8am and midnight ET, at irregular minutes and clear of launch posts. Launch videos that did well on X belong in this set.
- **A second shot at exposure:**
  - Postiz Plugs already handle Bluesky (repost at 5 likes) and Threads and Bluesky (a reply linking his projects page at 50 likes).
  - On the other platforms, don't repost the same video. Schedule a new post 3–5 days later with a different hook or clip.
- **Results:** pull `postiz analytics:post <id>` about 24 hours and 7 days after posting, and `postiz analytics:platform <integration-id>` for trends. Summarize what worked per platform and per framing. Bluesky reports no views, and LinkedIn personal-post analytics are often empty, so link clicks are the one comparable number.
