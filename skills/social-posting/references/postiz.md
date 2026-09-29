# Postiz mechanics

The `postiz` CLI is installed and authenticated globally (`postiz auth:status` checks). The official `postiz` skill documents every command. This file records the choices and gotchas specific to Travis's setup.

## Channels

Look up integration IDs at runtime rather than hard-coding them: `postiz integrations:list`, matched by `identifier`.

| identifier             | Platform                    |
| ---------------------- | --------------------------- |
| `threads`              | Threads                     |
| `bluesky`              | Bluesky                     |
| `linkedin`             | LinkedIn (personal profile) |
| `instagram-standalone` | Instagram                   |
| `tiktok-business`      | TikTok                      |

X and YouTube are deliberately not connected, so a Postiz key can never post there.

Run `postiz integrations:settings <id>` before a platform's first post in a session. Honor the `rules` and field descriptions it returns: settings that don't apply are silently dropped, so this is the only place a mistake shows up.

## Posting

1. **Upload each media file once:** `postiz upload <file>`, then reuse the returned `.path` for every channel. Raw paths and external URLs are rejected.
2. **Create one post per channel** with its own text, time and settings:

   ```bash
   postiz posts:create -c "$(cat social/drafts/threads.md)" -m "$VIDEO_PATH" \
     -s 2026-10-01T18:00:00Z -t schedule --no-shortLink -i <threads-id>
   ```

   - `--no-shortLink` keeps real URLs. The CLI shortens links by default.
   - `-t schedule` queues the post. Travis doesn't review Postiz posts, so don't create drafts for approval.
   - For threads, or media on individual thread posts, use `--json` with one `value` entry per post. The official `postiz` skill has examples.

3. **Verify:** run `postiz posts:list --startDate … --endDate …` and check each post's `state` (`QUEUE`), `publishDate` and `settings`. The list doesn't show media. To check an attachment, open the post in the Postiz UI (Calendar → list view). The video is the small tile under the text.

## Per-platform settings

- **TikTok** needs the full settings block. `DIRECT_POST` publishes; `UPLOAD` only drops the video in the TikTok app's inbox:

  ```json
  {
    "title": "<project name>",
    "privacy_level": "PUBLIC_TO_EVERYONE",
    "duet": false,
    "stitch": false,
    "comment": true,
    "autoAddMusic": "no",
    "brand_content_toggle": false,
    "brand_organic_toggle": false,
    "content_posting_method": "DIRECT_POST",
    "video_made_with_ai": true
  }
  ```

  TikTok often returns no post ID at first. If `analytics:post` says `{"missing": true}`, run `postiz posts:missing <id>`, then `postiz posts:connect <id> --release-id <tiktok-id>`.

- **Instagram:** `{"post_type":"post"}`. A video becomes a Reel. Postiz has no AI-label setting, so Travis toggles "AI info" in the app.
- **Threads, Bluesky, LinkedIn:** no settings. LinkedIn allows one video per post.

## Limits and gotchas

- **Size:** Instagram and Bluesky reject uploads over about 300 MB through the API, so re-encode large masters. For example: `ffmpeg -i in.mp4 -c:v libx264 -preset medium -crf 19 -maxrate 9M -bufsize 18M -pix_fmt yuv420p -c:a copy -movflags +faststart out.mp4`.
- **Text:** Bluesky 300 characters, Threads 500, LinkedIn 3,000, Instagram and TikTok 2,200. Bluesky counts the full URL.
- **Editing in the UI:** closing the post editor shows "Are you sure… all data will be lost". That only discards unsaved edits; the saved post stays.
- **Tags:** tags passed to `posts:create` that don't already exist in Postiz are silently dropped.
- **Plan:** the Standard plan has 5 channels, and all five are in use. Adding Mastodon or Reddit means upgrading to Team. Threads' fediverse sharing already puts his Threads posts on Mastodon.

## Plugs (account-wide automations)

These are set once in the Postiz UI (Plugs), not per post. Current configuration:

| Channel | Plug | Trigger | Action |
| --- | --- | --- | --- |
| Bluesky | Auto Repost | 5 likes, within a week | Reposts the post |
| Bluesky | Auto plug | 50 likes | Replies with a link to https://www.transitivebullsh.it/projects |
| Threads | Auto plug | 50 likes | Same reply, lowercase |

Instagram, TikTok and LinkedIn have no plugs. Avoid the editor's "Repeat Post Every…" option: it re-publishes identical content.
