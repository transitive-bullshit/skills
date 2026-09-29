#!/usr/bin/env python3
"""Mirror new top-level X posts and threads from @transitive_bs to Bluesky and Threads through Postiz.

usage: x_mirror.py [--dry-run] [--lookback-hours 48] [--only X_POST_ID ...]

What gets mirrored: original top-level posts, plus the thread Travis continues under one (his own chain of replies
to himself), as a thread. Replies to other people and reposts are never mirrored; the X API query excludes them and
the thread chain only follows his replies to his own posts. Polls are skipped. A post is skipped when it belongs to a
project launch (it or one of his replies under it links to transitivebullsh.it/projects/...), since launch-social
handles those, or when the same link or opening line already appears in a Postiz launch post on that channel.

X links don't cross over: people use Bluesky and Threads to get away from X. When a post quotes or links an X post,
the link is swapped for the matching post on that platform if it's one of Travis's own (his mirror of it, or a launch
post with the same opening line), and the post waits for the next run if that match isn't live yet. A post that
quotes or links anyone else's X post, or an own post with no match, is skipped on that platform.

Text is otherwise mirrored as written: t.co links expanded, X media links dropped, and anything over a platform's
limit split into more thread posts rather than cut. Images and videos are re-uploaded to Postiz. Each mirror is
scheduled at the earliest slot at least 3.5 h from any other Postiz post on that channel (launch posts) and 45 min
from other mirrors, falling back to "soon" when the next 36 h have no such slot. Mirrors carry the Postiz tag
"x-mirror".

State (which X posts were mirrored, skipped or are pending, and why) lives in ~/.local/state/x-mirror/state.json.
Needs the `xurl` and `postiz` CLIs, both already authenticated.
"""
import argparse, datetime as dt, html, json, pathlib, re, subprocess, sys, tempfile, urllib.request

HANDLE = "transitive_bs"
CHANNELS = {"bluesky": 300, "threads": 500}  # Postiz provider identifier -> max characters per post
STATE = pathlib.Path.home() / ".local/state/x-mirror/state.json"
TAG = {"value": "x-mirror", "label": "X mirror"}
LAUNCH_GAP, MIRROR_GAP = dt.timedelta(hours=3.5), dt.timedelta(minutes=45)
STEP, HORIZON = dt.timedelta(minutes=15), dt.timedelta(hours=36)
MIN_AGE = dt.timedelta(minutes=60)  # X allows edits for an hour, and threads get finished; mirror the settled version
UTC = dt.timezone.utc
FIELDS = ("tweet.fields=created_at,note_tweet,entities,attachments,conversation_id,referenced_tweets,author_id"
          "&expansions=attachments.media_keys&media.fields=type,url,variants")
X_STATUS = re.compile(r"https?://(?:www\.|mobile\.)?(?:x|twitter)\.com/\w+/status/(\d+)[^\s]*")


def cli_json(*cmd):
    """Run a CLI and parse the JSON it prints (postiz prefixes its JSON with status lines)."""
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode:
        raise RuntimeError(f"{' '.join(cmd[:2])} failed: {(out.stderr or out.stdout).strip()[:400]}")
    lines = out.stdout.splitlines()
    for k, line in enumerate(lines):
        if line.lstrip().startswith(("{", "[")):
            return json.loads("\n".join(lines[k:]))
    raise RuntimeError(f"{' '.join(cmd[:2])} printed no JSON: {out.stdout.strip()[:400]}")


def iso(t): return t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
def parse_time(s): return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
def norm(s): return re.sub(r"\W+", " ", s.lower()).strip()
def refs(post, kind): return [r["id"] for r in post.get("referenced_tweets", []) if r["type"] == kind]


def load_state():
    return json.loads(STATE.read_text()) if STATE.exists() else {"posts": {}}


def save_state(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def x_text(post):
    """The post's full text with t.co links expanded and X media links removed, plus its non-X outbound links.
    A quoted post's link is kept (or added) so it can be swapped for the matching post on each platform."""
    note = post.get("note_tweet")
    text, ents = (note["text"], note.get("entities", {})) if note else (post["text"], post.get("entities", {}))
    links = []
    for u in ents.get("urls", []):
        url = u.get("unwound_url") or u.get("expanded_url") or u["url"]
        if u.get("media_key") or re.match(r"https?://(x|twitter)\.com/\w+/status/\d+/(photo|video)/", url):
            url = ""
        elif not re.match(r"https?://(www\.|mobile\.)?(x|twitter)\.com/", url):
            links.append(url)
        text = text.replace(u["url"], url)
    text = html.unescape(text)
    quoted = refs(post, "quoted")
    if quoted and f"/status/{quoted[0]}" not in text:
        text += f"\n\nhttps://x.com/i/status/{quoted[0]}"
    text = re.sub(r"[ \t]{2,}", " ", re.sub(r"[ \t]+\n", "\n", text)).strip()
    return re.sub(r"\n{3,}", "\n\n", text), links


def x_refs(text):
    """X post ids that a mirrored text quotes or links."""
    return list(dict.fromkeys(m.group(1) for m in X_STATUS.finditer(text)))


def _pieces(block, limit):
    """Break one paragraph into pieces of at most `limit` characters: by sentence, then by word."""
    if len(block) <= limit:
        return [block]
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", block) if s]
    if len(sentences) > 1:
        return [p for s in sentences for p in _pieces(s, limit)]
    out, cur = [], ""
    for word in block.split(" "):
        while len(word) > limit:  # a single overlong token
            out, word = out + ([cur] if cur else []) + [word[:limit]], word[limit:]
            cur = ""
        if cur and len(cur) + 1 + len(word) > limit:
            out.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}" if cur else word
    return out + ([cur] if cur else [])


def split(text, limit):
    """Split text into posts of at most `limit` characters, keeping paragraphs together where they fit."""
    chunks, cur = [], ""
    for para in [p.strip() for p in text.split("\n\n") if p.strip()]:
        for k, piece in enumerate(_pieces(para, limit)):
            sep = " " if k else "\n\n"
            if cur and len(cur) + len(sep) + len(piece) <= limit:
                cur += sep + piece
            else:
                if cur:
                    chunks.append(cur)
                cur = piece
    return chunks + ([cur] if cur else [])


def for_channel(text, channel):
    if channel == "threads":  # an X @handle could tag a different person on Threads
        text = re.sub(r"(?<![\w@/])@(\w{1,15})\b", r"\1", text)
    return split(text, CHANNELS[channel]) or [""]


def self_thread(root, replies):
    """Travis's thread under `root`: the chain of his replies to his own posts, in order."""
    chain, tail = [root], root["id"]
    for r in sorted(replies, key=lambda p: p["created_at"]):
        if tail in refs(r, "replied_to"):
            chain.append(r)
            tail = r["id"]
    return chain


def media_files(post, media_by_key, tmp):
    """Download a post's media: its first video if it has one (Bluesky takes a single video), else up to 4 photos."""
    items = [media_by_key[k] for k in post.get("attachments", {}).get("media_keys", []) if k in media_by_key]
    videos = [m for m in items if m["type"] in ("video", "animated_gif")]
    items = videos[:1] if videos else [m for m in items if m["type"] == "photo"][:4]
    files = []
    for k, m in enumerate(items):
        if m["type"] == "photo":
            url = m["url"]
        else:
            mp4s = [v for v in m.get("variants", []) if v.get("content_type") == "video/mp4"]
            url = max(mp4s, key=lambda v: v.get("bit_rate", 0))["url"]
        path = pathlib.Path(tmp) / f"{post['id']}_{k}{'.jpg' if m['type'] == 'photo' else '.mp4'}"
        urllib.request.urlretrieve(url, path)
        files.append(path)
    return files


def pick_slot(now, launch_times, mirror_times):
    t = (now + dt.timedelta(minutes=10)).replace(second=0, microsecond=0)
    t += dt.timedelta(minutes=-t.minute % 5)
    fallback = t
    while t < now + HORIZON:
        if all(abs(t - l) >= LAUNCH_GAP for l in launch_times) and all(abs(t - m) >= MIRROR_GAP for m in mirror_times):
            return t
        t += STEP
    return fallback


def bluesky_published(handle):
    """His recent Bluesky posts as (normalized text, raw text + link targets), read from the public API. This sees
    posts made outside Postiz too. Returns [] if the API can't be reached; the Postiz queue check still applies."""
    url = f"https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?actor={handle}&limit=100&filter=posts_no_replies"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            feed = json.load(r).get("feed", [])
    except Exception:
        return []
    out = []
    for item in feed:
        post = item.get("post", {})
        if post.get("author", {}).get("handle") != handle:
            continue  # a repost of someone else
        text = post.get("record", {}).get("text", "")
        ext = json.dumps(post.get("embed", {})) + json.dumps(post.get("record", {}).get("facets", []))
        out.append((norm(text), text + " " + ext))
    return out


class Queue:
    """Postiz posts within three weeks either side of now, by channel, with which ones are mirrors."""

    def __init__(self, now, mirror_ids):
        posts = cli_json("postiz", "posts:list", "--startDate", iso(now - dt.timedelta(days=21)),
                         "--endDate", iso(now + dt.timedelta(days=21)))
        posts = posts.get("posts", posts) if isinstance(posts, dict) else posts
        self.by_id = {p["id"]: p for p in posts if not p.get("deletedAt")}
        self.by_channel = {}
        for p in self.by_id.values():
            p["_norm"] = norm(p.get("content", ""))
            p["_mirror"] = p["id"] in mirror_ids or "x-mirror" in json.dumps(p.get("tags", [])).lower()
            p["_time"] = parse_time(p["publishDate"])
            self.by_channel.setdefault(p.get("integration", {}).get("providerIdentifier"), []).append(p)

    def launches(self, channel): return [p for p in self.by_channel.get(channel, []) if not p["_mirror"]]

    def add(self, channel, slot, text):
        self.by_channel.setdefault(channel, []).append(
            {"_time": slot, "_norm": norm(text), "content": text, "_mirror": True, "id": None})

    def slot(self, now, channel):
        posts = self.by_channel.get(channel, [])
        return pick_slot(now, [p["_time"] for p in posts if not p["_mirror"]],
                         [p["_time"] for p in posts if p["_mirror"]])


def resolve_x_refs(ids, channel, lookup, state, queue):
    """Map quoted/linked X posts to their `channel` equivalents: ({x_id: url}, None), or ({}, ("wait"|"skip", why))."""
    urls = {}
    for xid in ids:
        post = lookup.get(xid)
        if not post:
            return {}, ("skip", f"quotes or links an X post that can't be read ({xid})")
        if post.get("author_id") != state["user_id"]:
            return {}, ("skip", f"quotes or links @{post.get('_username', 'someone')}'s X post; X links don't cross over")
        entry = next((e for k, e in state["posts"].items() if k == xid or xid in e.get("thread_ids", [])), {})
        postiz_id = entry.get("mirrored", {}).get(channel, {}).get("postiz_id")
        match = queue.by_id.get(postiz_id) if postiz_id else None
        if not match:  # his launch post on this channel with the same opening line
            first = norm(x_text(post)[0].split("\n")[0])
            match = next((p for p in queue.launches(channel) if len(first) >= 20 and first in p["_norm"]), None)
        if not match:
            return {}, ("skip", f"quotes or links his X post {xid}, which has no {channel} version")
        if not match.get("releaseURL"):
            return {}, ("wait", f"quotes his X post {xid}; its {channel} version isn't live yet")
        urls[xid] = match["releaseURL"]
    return urls, None


def create_post(channel, cid, slot, parts, tmp, name):
    body = {"type": "schedule", "date": iso(slot), "shortLink": False, "tags": [TAG],
            "posts": [{"integration": {"id": cid}, "value": parts, "settings": {"__type": channel}}]}
    spec = pathlib.Path(tmp) / f"{name}_{channel}.json"
    for attempt in range(2):
        spec.write_text(json.dumps(body, ensure_ascii=False))
        try:
            return cli_json("postiz", "posts:create", "--json", str(spec))[0]["postId"]
        except RuntimeError as e:
            if attempt or "tag" not in str(e).lower():
                raise
            body["tags"] = []  # tags are a nicety; never let them block the post


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="show the plan; upload and schedule nothing")
    ap.add_argument("--lookback-hours", type=float, default=48)
    ap.add_argument("--only", nargs="*", help="limit to these X post ids")
    args = ap.parse_args()

    state, now = load_state(), dt.datetime.now(UTC)
    if "user_id" not in state:
        state["user_id"] = cli_json("xurl", f"/2/users/by/username/{HANDLE}")["data"]["id"]
    since = iso(now - dt.timedelta(hours=args.lookback_hours))
    res = cli_json("xurl", f"/2/users/{state['user_id']}/tweets?max_results=50&exclude=retweets,replies"
                           f"&start_time={since}&{FIELDS}")
    # The timeline's exclude=replies still lets his thread continuations through; they ride along with their root.
    roots = sorted((p for p in res.get("data", []) if not refs(p, "replied_to")), key=lambda p: p["created_at"])
    media_by_key = {m["media_key"]: m for m in res.get("includes", {}).get("media", [])}

    listed = [i for i in cli_json("postiz", "integrations:list") if not i.get("disabled")]
    integrations = {i["identifier"]: i["id"] for i in listed}
    profiles = {i["identifier"]: i.get("profile") for i in listed}
    channels = {c: integrations[c] for c in CHANNELS if c in integrations}
    mirror_ids = {v["postiz_id"] for p in state["posts"].values() for v in p.get("mirrored", {}).values()}
    queue = Queue(now, mirror_ids)
    published = {"bluesky": bluesky_published(profiles["bluesky"])} if profiles.get("bluesky") else {}

    report = []
    with tempfile.TemporaryDirectory() as tmp:
        for root in roots:
            pid = root["id"]
            entry = state["posts"].get(pid)
            if (args.only and pid not in args.only) or (entry and not entry.get("pending")):
                continue
            todo = [c for c in channels if not entry or c in entry["pending"]]
            x_url = f"https://x.com/{HANDLE}/status/{pid}"
            first = x_text(root)[0].split("\n")[0]
            if now - parse_time(root["created_at"]) < MIN_AGE:
                report.append(f"wait   {x_url} (under an hour old; next run)")
                continue
            if root.get("attachments", {}).get("poll_ids"):
                state["posts"][pid] = {"x_url": x_url, "skipped": "poll"}
                report.append(f"skip   {x_url} (poll)")
                continue
            # His own posts in the conversation: the thread to mirror, and a project-launch signal.
            conv = cli_json("xurl", f"/2/tweets/search/recent?query=conversation_id:{pid}%20from:{HANDLE}"
                                    f"&max_results=50&{FIELDS}")
            media_by_key.update({m["media_key"]: m for m in conv.get("includes", {}).get("media", [])})
            own = conv.get("data", [])
            thread = self_thread(root, [p for p in own if p["id"] != pid])
            all_links = [l for p in [root] + own for l in x_text(p)[1]]
            if any("transitivebullsh.it/projects/" in l for l in all_links):
                state["posts"][pid] = {"x_url": x_url, "skipped": "project launch (handled by launch-social)"}
                report.append(f"skip   {x_url} (project launch: {first[:50]!r})")
                continue
            texts = [x_text(p)[0] for p in thread]
            ref_ids = list(dict.fromkeys(i for t in texts for i in x_refs(t)))
            lookup = {}
            if ref_ids:
                got = cli_json("xurl", f"/2/tweets?ids={','.join(ref_ids)}&tweet.fields=author_id,note_tweet,entities"
                                       f"&expansions=author_id&user.fields=username")
                names = {u["id"]: u["username"] for u in got.get("includes", {}).get("users", [])}
                lookup = {p["id"]: {**p, "_username": names.get(p.get("author_id"), "")} for p in got.get("data", [])}
            uploads, done = None, {}
            for channel in todo:
                cid = channels[channel]
                # Same link as a launch post, or the same opening line as any post, means it's already covered.
                if any(any(l in p.get("content", "") for l in all_links) for p in queue.launches(channel)) or \
                        (len(norm(first)) >= 20 and any(norm(first) in p["_norm"] for p in queue.by_channel.get(channel, []))):
                    done[channel] = {"skipped": "already in Postiz"}
                    report.append(f"skip   {x_url} on {channel} (already in Postiz)")
                    continue
                # Posted on the platform outside Postiz (by hand): same opening line already on his profile.
                if len(norm(first)) >= 20 and any(norm(first) in n for n, _ in published.get(channel, [])):
                    done[channel] = {"skipped": f"already published on {channel}"}
                    report.append(f"skip   {x_url} on {channel} (already published on {channel})")
                    continue
                urls, problem = resolve_x_refs(ref_ids, channel, lookup, state, queue)
                if problem:
                    kind, why = problem
                    done[channel] = {"pending" if kind == "wait" else "skipped": why}
                    report.append(f"{kind:<6} {x_url} on {channel} ({why})")
                    continue
                swapped = [X_STATUS.sub(lambda m: urls.get(m.group(1), m.group(0)), t) for t in texts]
                chunked = [for_channel(t, channel) for t in swapped]
                n_parts = sum(len(c) for c in chunked)
                desc = (f"{len(thread)}-post X thread -> {n_parts} {channel} posts" if len(thread) > 1
                        else f"{n_parts} post(s)") + (f", {len(urls)} X link(s) swapped for {channel} posts" if urls else "")
                slot = queue.slot(now, channel)
                if args.dry_run:
                    n_media = sum(len(p.get("attachments", {}).get("media_keys", [])) for p in thread)
                    report.append(f"plan   {x_url} -> {channel} at {iso(slot)}: {desc}, {n_media} media: {first[:60]!r}")
                else:
                    if uploads is None:
                        uploads = [[{"id": u["id"], "path": u["path"]}
                                    for u in (cli_json("postiz", "upload", str(f))
                                              for f in media_files(p, media_by_key, tmp))] for p in thread]
                    parts = [{"content": c, "image": uploads[i] if k == 0 else []}
                             for i, chunks in enumerate(chunked) for k, c in enumerate(chunks)]
                    postiz_id = create_post(channel, cid, slot, parts, tmp, pid)
                    done[channel] = {"postiz_id": postiz_id, "date": iso(slot), "parts": n_parts}
                    report.append(f"posted {x_url} -> {channel} at {iso(slot)}: {desc}")
                queue.add(channel, slot, swapped[0])
            if not args.dry_run:
                entry = state["posts"].get(pid) or {"x_url": x_url, "text": first[:120]}
                entry.update(thread_ids=[p["id"] for p in thread], checked_at=iso(now))
                entry.setdefault("mirrored", {}).update({c: v for c, v in done.items() if "postiz_id" in v})
                skipped = {c: v["skipped"] for c, v in done.items() if "skipped" in v}
                if skipped:
                    prev = entry.get("skipped")
                    entry["skipped"] = {**prev, **skipped} if isinstance(prev, dict) else skipped
                entry["pending"] = {c: v["pending"] for c, v in done.items() if "pending" in v}
                if not entry["pending"]:
                    entry.pop("pending")
                state["posts"][pid] = entry
                save_state(state)
    if not args.dry_run:
        save_state(state)
    print("\n".join(report) or f"No new top-level X posts from @{HANDLE} in the last {args.lookback_hours:g} h.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"x-mirror failed: {e}", file=sys.stderr)
        sys.exit(1)
