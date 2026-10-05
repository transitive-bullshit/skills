#!/usr/bin/env python3
"""Mirror new top-level X posts and threads from @transitive_bs to Bluesky and Threads through Postiz.

usage: x_mirror.py [--dry-run] [--lookback-hours 48] [--only X_POST_ID ...]
       x_mirror.py --only ID ... --include-launches --gap-hours 20 --window 13-23   (a spaced-out backfill)

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

Posts, threads, media and quoted posts start in the local birdclaw archive (~/.birdclaw/birdclaw.sqlite), which a
separate bird-backed job keeps in sync. Missing quoted/linked posts or video mp4s try bird, then public FxTwitter,
then paid xurl. A paid fallback prints a note explaining the cheaper-source failures.

State (which X posts were mirrored, skipped or are pending, and why) lives in ~/.local/state/x-mirror/state.json.
Needs the `postiz` CLI, already authenticated, and the birdclaw archive.
"""
import argparse, datetime as dt, html, json, pathlib, random, re, sqlite3, subprocess, sys, tempfile, urllib.request

HANDLE = "transitive_bs"
CHANNELS = {"bluesky": 300, "threads": 500}  # Postiz provider identifier -> max characters per post
STATE = pathlib.Path.home() / ".local/state/x-mirror/state.json"
TAG = {"value": "x-mirror", "label": "X mirror"}
LAUNCH_GAP, MIRROR_GAP = dt.timedelta(hours=3.5), dt.timedelta(minutes=45)
STEP, HORIZON = dt.timedelta(minutes=15), dt.timedelta(hours=36)
MIN_AGE = dt.timedelta(minutes=60)  # X allows edits for an hour, and threads get finished; mirror the settled version
UTC = dt.timezone.utc
BIRDCLAW_DB = pathlib.Path.home() / ".birdclaw/birdclaw.sqlite"  # local X archive, synced by a separate job
STALE_SYNC = dt.timedelta(hours=26)  # birdclaw syncs every 12 h; say so when it's fallen well behind
MEDIA_TYPES = {"image": "photo", "photo": "photo", "video": "video", "gif": "animated_gif", "animated_gif": "animated_gif"}
X_STATUS = re.compile(r"https?://(?:www\.|mobile\.)?(?:x|twitter)\.com/\w+/status/(\d+)[^\s]*")


def cli_json(*cmd, timeout=None):
    """Run a CLI and parse the JSON it prints (postiz prefixes its JSON with status lines)."""
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
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


class Archive:
    """The local birdclaw archive, read-only. Rows come back shaped like X API v2 posts (the raw API payload birdclaw
    keeps where it has one), and their media lands in `media_by_key`."""
    SELECT = """select t.*, p.handle, (select r.payload_json from tweet_revisions r where r.root_tweet_id = t.id
        order by r.observed_at desc limit 1) payload
        from tweets t left join profiles p on p.id = t.author_profile_id"""
    LIVE = "t.deleted_at is null and t.superseded_at is null"

    def __init__(self):
        if not BIRDCLAW_DB.exists():
            raise RuntimeError(f"no birdclaw archive at {BIRDCLAW_DB}")
        self.con = sqlite3.connect(f"file:{BIRDCLAW_DB}?mode=ro", uri=True)
        self.con.row_factory = sqlite3.Row
        self.media_by_key = {}

    def user_id(self, handle):
        row = self.con.execute("select id from profiles where lower(handle) = lower(?)", (handle,)).fetchone()
        if not row:
            raise RuntimeError(f"@{handle} isn't in the birdclaw archive")
        return row["id"].removeprefix("profile_user_")

    def last_sync(self):
        """When birdclaw last pulled his authored posts from X, or None if it never has."""
        row = self.con.execute("select updated_at from sync_cache where cache_key like 'authored:%:cursor'"
                               " order by updated_at desc limit 1").fetchone()
        return parse_time(row["updated_at"]) if row else None

    def posts(self, where, params=(), order="t.created_at"):
        sql = f"{self.SELECT} where {self.LIVE} and ({where}) order by {order}"
        return [self._post(r) for r in self.con.execute(sql, params)]

    def by_ids(self, ids):
        return self.posts(f"t.id in ({','.join('?' * len(ids))})", ids) if ids else []

    def roots(self, user_id, since):
        """His top-level posts since `since`, oldest first; reposts left out."""
        posts = self.posts("t.author_profile_id = ? and t.created_at >= ? and t.reply_to_id is null",
                           (f"profile_user_{user_id}", since.strftime("%Y-%m-%dT%H:%M:%S.000Z")))
        return [p for p in posts if not refs(p, "retweeted") and not p["text"].startswith("RT @")]

    def own_in_conversation(self, root, user_id):
        """His posts under `root`: the self-reply chain (his thread) plus his other replies in the conversation."""
        author = f"profile_user_{user_id}"
        chain = [r[0] for r in self.con.execute(f"""with recursive chain(id) as (select ? union all
            select t.id from tweets t join chain c on t.reply_to_id = c.id where t.author_profile_id = ? and {self.LIVE})
            select id from chain where id != ?""", (root["id"], author, root["id"]))]
        conv = [r[0] for r in self.con.execute(f"""select t.id from tweets t join tweet_revisions r on r.root_tweet_id = t.id
            where t.author_profile_id = ? and t.created_at > ? and t.id != ? and {self.LIVE}
            and json_extract(r.payload_json, '$.conversation_id') = ?""", (author, root["created_at"], root["id"], root["id"]))]
        return self.by_ids(list(dict.fromkeys(chain + conv)))

    def _post(self, row):
        raw = json.loads(row["payload"] or "{}")
        snake = lambda urls: [{**u, "expanded_url": u.get("expanded_url") or u.get("expandedUrl"),
                               "unwound_url": u.get("unwound_url") or u.get("unwoundUrl")} for u in urls]
        entities = raw.get("entities") or json.loads(row["entities_json"] or "{}")
        post = {"id": row["id"], "created_at": row["created_at"], "text": row["text"],
                "author_id": raw.get("author_id") or row["author_profile_id"].removeprefix("profile_user_"),
                "_username": row["handle"] or "", "entities": {**entities, "urls": snake(entities.get("urls", []))},
                "referenced_tweets": raw.get("referenced_tweets") or
                    ([{"type": "replied_to", "id": row["reply_to_id"]}] if row["reply_to_id"] else []) +
                    ([{"type": "quoted", "id": row["quoted_tweet_id"]}] if row["quoted_tweet_id"] else [])}
        if row["note_tweet_json"]:  # a long post's full text
            note = json.loads(row["note_tweet_json"])
            ents = note.get("entities") or {}
            post["note_tweet"] = {"text": note["text"], "entities": {**ents, "urls": snake(ents.get("urls", []))}}
        keys = []
        for k, m in enumerate(json.loads(row["media_json"] or "[]")):
            key = f"{row['id']}_{k}"
            self.media_by_key[key] = {"type": MEDIA_TYPES.get(m.get("type"), m.get("type")), "url": m.get("url"),
                                      "variants": [{"url": v["url"], "content_type": v.get("contentType") or v.get("content_type"),
                                                    "bit_rate": v.get("bitRate") or v.get("bit_rate") or 0}
                                                   for v in m.get("variants", [])]}
            keys.append(key)
        post["attachments"] = {**raw.get("attachments", {}), "media_keys": keys}
        return post


class MediaUnavailable(RuntimeError):
    """A post's video can't be downloaded yet; the post waits for a later run."""


def mp4s(variants): return [v for v in variants if v.get("content_type") == "video/mp4"]


def normalize_x_post(payload, post_id):
    """Adapt bird, FxTwitter, or X API data to the shape used by the archive reader."""
    if not isinstance(payload, dict):
        raise ValueError("API response is not an object")
    if payload.get("code", 200) != 200:
        raise ValueError(f"API code {payload['code']}")
    data = payload.get("data")
    post = next((p for p in data if isinstance(p, dict) and str(p.get("id")) == post_id), {}) if isinstance(data, list) else \
        payload.get("status") or payload.get("tweet") or data or payload
    if not isinstance(post, dict) or str(post.get("id")) != post_id:
        raise ValueError("requested post unavailable")
    author = post.get("author") or {}
    author_id = post.get("author_id") or post.get("authorId") or author.get("id")
    if not author_id:
        raise ValueError("post author ID unavailable")
    includes = payload.get("includes") or {}
    names = {str(u["id"]): u["username"] for u in includes.get("users", [])}
    username = author.get("username") or author.get("screen_name") or names.get(str(author_id), "")
    media = post.get("media") or []
    if isinstance(media, dict):
        media = media.get("all") or media.get("photos", []) + media.get("videos", [])
    if not media:
        keys = (post.get("attachments") or {}).get("media_keys", [])
        media = [m for m in includes.get("media", []) if m.get("media_key") in keys]
    normalized_media = []
    for m in media:
        kind = MEDIA_TYPES.get(m.get("type"), m.get("type"))
        variants = [{"url": v["url"], "content_type": v.get("content_type") or v.get("contentType"),
                     "bit_rate": v.get("bit_rate") or v.get("bitRate") or v.get("bitrate") or 0}
                    for v in m.get("variants", []) if v.get("url")]
        video_url = m.get("videoUrl") or m.get("video_url")
        if not video_url and kind in ("video", "animated_gif") and ".mp4" in (m.get("url") or ""):
            video_url = m["url"]
        if video_url and not mp4s(variants):
            variants.append({"url": video_url, "content_type": "video/mp4", "bit_rate": 0})
        normalized_media.append({"type": kind, "url": m.get("url"), "variants": variants})
    return {**post, "id": post_id, "author_id": str(author_id), "_username": username,
            "created_at": post.get("created_at") or post.get("createdAt"), "_media": normalized_media}


def fxtwitter_post(post_id):
    request = urllib.request.Request(f"https://api.fxtwitter.com/2/status/{post_id}",
                                     headers={"User-Agent": "personal-x-mirror/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def read_x_posts(ids, require_video=False):
    """Fill known archive gaps in cost order; batch only the unresolved paid reads."""
    ids = list(dict.fromkeys(str(i) for i in ids))
    if any(not re.fullmatch(r"\d+", i) for i in ids):
        raise ValueError("X post IDs must be numeric")
    found, failures = {}, {i: [] for i in ids}

    def accept(payload, post_id):
        post = normalize_x_post(payload, post_id)
        videos = [m for m in post["_media"] if m["type"] in ("video", "animated_gif")]
        if require_video and (not videos or not mp4s(videos[0]["variants"])):
            raise ValueError("video mp4 unavailable")
        found[post_id] = post

    for post_id in ids:
        for source, read in [("bird", lambda: cli_json("bird", "--timeout", "30000", "read", post_id,
                                                       "--json", timeout=45)),
                             ("FxTwitter", lambda: fxtwitter_post(post_id))]:
            try:
                accept(read(), post_id)
                break
            except (RuntimeError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as e:
                failures[post_id].append(f"{source}: {str(e)[:140]}")
    missing = [i for i in ids if i not in found]
    for start in range(0, len(missing), 100):
        batch = missing[start:start + 100]
        for post_id in batch:
            print(f"note   paid xurl fallback for X post {post_id} ({'; '.join(failures[post_id])})")
        try:
            got = cli_json("xurl", f"/2/tweets?ids={','.join(batch)}&tweet.fields=author_id,note_tweet,entities"
                                  "&expansions=author_id,attachments.media_keys&user.fields=username&media.fields=type,variants",
                           timeout=45)
            for post_id in batch:
                try:
                    accept(got, post_id)
                except (ValueError, KeyError, TypeError):
                    pass
        except (RuntimeError, OSError, ValueError, subprocess.SubprocessError):
            pass
    return {i: found.get(i) for i in ids}


def lookup_x_posts(archive, ids):
    """Return complete local references before asking any live transport."""
    lookup = {p["id"]: p for p in archive.by_ids(ids)}
    missing = [i for i in ids if i not in lookup]
    if missing:
        lookup.update(read_x_posts(missing))
    return lookup


def x_video_variants(post_id):
    """Try cheaper live sources first for a video the archive stored without mp4 variants."""
    post = read_x_posts([post_id], require_video=True)[post_id]
    if not post:
        raise MediaUnavailable(f"video variants unavailable for X post {post_id} after bird, FxTwitter, and xurl")
    videos = [m for m in post["_media"] if m.get("type") in ("video", "animated_gif")]
    return mp4s(videos[0].get("variants", [])) if videos else []


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
            variants = mp4s(m.get("variants", [])) or x_video_variants(post["id"])
            if not variants:
                raise MediaUnavailable(f"no mp4 for the video in X post {post['id']}")
            url = max(variants, key=lambda v: v.get("bit_rate", 0))["url"]
        path = pathlib.Path(tmp) / f"{post['id']}_{k}{'.jpg' if m['type'] == 'photo' else '.mp4'}"
        urllib.request.urlretrieve(url, path)
        files.append(path)
    return files


JITTER_MIN = 45  # up to this many minutes of random offset, so posting times look human rather than scheduled


def pick_slot(now, launch_times, mirror_times, mirror_gap=(MIRROR_GAP, MIRROR_GAP), window=None, horizon=HORIZON):
    """A natural-looking slot: clear of launch posts (LAUNCH_GAP) and of other mirrors by a gap drawn at random from
    the mirror_gap range, optionally only within a window of UTC hours (start, end), then nudged by a random offset
    that never lands on a round five-minute mark. Falls back to the first allowed slot when nothing fits."""
    gap = mirror_gap[0] + (mirror_gap[1] - mirror_gap[0]) * random.random()
    # Mirrors go out in order: start after the last queued mirror plus this post's gap, never ahead of it.
    t = max([now + dt.timedelta(minutes=10)] + [m + gap for m in mirror_times]).replace(second=0, microsecond=0)
    t += dt.timedelta(minutes=-t.minute % 5)
    def in_window(t):  # UTC hours [start, end), wrapping past midnight when start > end (e.g. 12-4)
        if not window:
            return True
        start, end = window
        return start <= t.hour < end if start < end else (t.hour >= start or t.hour < end)
    ok = lambda t: in_window(t) and all(abs(t - l) >= LAUNCH_GAP for l in launch_times) and \
        all(abs(t - m) >= gap for m in mirror_times)
    fallback = None
    while t < now + horizon:
        if in_window(t):
            fallback = fallback or t
            if ok(t):
                for _ in range(10):  # jitter within the rules, off the round five-minute marks
                    j = t + dt.timedelta(minutes=random.randint(1, JITTER_MIN))
                    if j.minute % 5 and ok(j):
                        return j
                return t
        t += STEP
    return fallback or t


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

    def add(self, channel, slot, text, postiz_id=None):
        post = {"_time": slot, "_norm": norm(text), "content": text, "_mirror": True, "id": postiz_id}
        self.by_channel.setdefault(channel, []).append(post)
        if postiz_id:  # visible to later posts in this run, e.g. a quote waiting for it to go live
            self.by_id[postiz_id] = post

    def slot(self, now, channel, **kw):
        posts = self.by_channel.get(channel, [])
        return pick_slot(now, [p["_time"] for p in posts if not p["_mirror"]],
                         [p["_time"] for p in posts if p["_mirror"]], **kw)


def resolve_x_refs(ids, channel, lookup, state, queue):
    """Map quoted/linked X posts to their `channel` equivalents: ({x_id: url}, None), or ({}, ("wait"|"skip", why))."""
    urls = {}
    for xid in ids:
        post = lookup.get(xid)
        if post is None:  # all read sources failed; try again next run
            return {}, ("wait", f"quotes or links X post {xid}, unavailable from Birdclaw, bird, FxTwitter, and xurl")
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
    ap.add_argument("--only", nargs="*", help="limit to these X post ids (fetched directly, any age)")
    ap.add_argument("--include-launches", action="store_true",
                    help="mirror project-launch posts too (for a deliberate backfill of posts that did well on X)")
    ap.add_argument("--gap-hours", default="0.75",
                    help="hours between mirrors on a channel: a minimum (0.75, the default) or a random range (8-15) "
                         "to spread a backfill out")
    ap.add_argument("--window", help="only schedule within these UTC hours, e.g. 12-4 for 8am to midnight ET")
    args = ap.parse_args()

    state, now, archive = load_state(), dt.datetime.now(UTC), Archive()
    if "user_id" not in state:
        state["user_id"] = archive.user_id(HANDLE)
    run_opts = {"include_launches": args.include_launches, "gap_hours": args.gap_hours, "window": args.window}

    def slot_kw_for(opts):
        window = tuple(int(h) for h in opts["window"].split("-")) if opts.get("window") else None
        lo, _, hi = str(opts["gap_hours"]).partition("-")
        gap = (dt.timedelta(hours=float(lo)), dt.timedelta(hours=float(hi or lo)))
        return {"mirror_gap": gap, "window": window,
                "horizon": HORIZON if gap[1] <= dt.timedelta(hours=1) and not window else dt.timedelta(days=21)}
    report = []
    synced = archive.last_sync()
    if not synced or now - synced > STALE_SYNC:
        ago = f"{(now - synced).total_seconds() / 3600:.0f} h ago" if synced else "never"
        report.append(f"note   birdclaw last synced @{HANDLE}'s posts {ago}; newer X posts wait for its next sync")
    if args.only:  # specific posts, any age; a backfill goes out in the order given (e.g. strongest first)
        roots = sorted((p for p in archive.by_ids(args.only) if not refs(p, "replied_to")),
                       key=lambda p: args.only.index(p["id"]))
        found = {p["id"] for p in archive.by_ids(args.only)}
        report += [f"skip   https://x.com/{HANDLE}/status/{i} (not in the birdclaw archive)" for i in args.only if i not in found]
    else:
        roots = archive.roots(state["user_id"], now - dt.timedelta(hours=args.lookback_hours))
        pending = [k for k, e in state["posts"].items() if e.get("pending") and k not in {p["id"] for p in roots}]
        roots += archive.by_ids(pending)  # retry waiting posts from earlier runs, whatever their age
    media_by_key = archive.media_by_key

    listed = [i for i in cli_json("postiz", "integrations:list") if not i.get("disabled")]
    integrations = {i["identifier"]: i["id"] for i in listed}
    profiles = {i["identifier"]: i.get("profile") for i in listed}
    channels = {c: integrations[c] for c in CHANNELS if c in integrations}
    mirror_ids = {v["postiz_id"] for p in state["posts"].values() for v in p.get("mirrored", {}).values()}
    queue = Queue(now, mirror_ids)
    published = {"bluesky": bluesky_published(profiles["bluesky"])} if profiles.get("bluesky") else {}

    with tempfile.TemporaryDirectory() as tmp:
        for root in roots:
            pid = root["id"]
            entry = state["posts"].get(pid)
            if (args.only and pid not in args.only) or (entry and not entry.get("pending")):
                continue
            todo = [c for c in channels if not entry or c in entry["pending"]]
            opts = (entry or {}).get("opts") or run_opts
            slot_kw = slot_kw_for(opts)
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
            own = archive.own_in_conversation(root, state["user_id"])
            thread = self_thread(root, [p for p in own if p["id"] != pid])
            all_links = [l for p in [root] + own for l in x_text(p)[1]]
            if not opts.get("include_launches") and any("transitivebullsh.it/projects/" in l for l in all_links):
                state["posts"][pid] = {"x_url": x_url, "skipped": "project launch (handled by launch-social)"}
                report.append(f"skip   {x_url} (project launch: {first[:50]!r})")
                continue
            texts = [x_text(p)[0] for p in thread]
            ref_ids = list(dict.fromkeys(i for t in texts for i in x_refs(t)))
            lookup = lookup_x_posts(archive, ref_ids)
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
                slot = queue.slot(now, channel, **slot_kw)
                if args.dry_run:
                    n_media = sum(len(p.get("attachments", {}).get("media_keys", [])) for p in thread)
                    report.append(f"plan   {x_url} -> {channel} at {iso(slot)}: {desc}, {n_media} media: {first[:60]!r}")
                else:
                    if uploads is None:
                        try:
                            uploads = [[{"id": u["id"], "path": u["path"]}
                                        for u in (cli_json("postiz", "upload", str(f))
                                                  for f in media_files(p, media_by_key, tmp))] for p in thread]
                        except MediaUnavailable as e:
                            uploads = e
                    if isinstance(uploads, MediaUnavailable):  # wait for a later run rather than mirror without it
                        done[channel] = {"pending": str(uploads)}
                        report.append(f"wait   {x_url} on {channel} ({uploads})")
                        continue
                    parts = [{"content": c, "image": uploads[i] if k == 0 else []}
                             for i, chunks in enumerate(chunked) for k, c in enumerate(chunks)]
                    postiz_id = create_post(channel, cid, slot, parts, tmp, pid)
                    done[channel] = {"postiz_id": postiz_id, "date": iso(slot), "parts": n_parts}
                    report.append(f"posted {x_url} -> {channel} at {iso(slot)}: {desc}")
                queue.add(channel, slot, swapped[0], done.get(channel, {}).get("postiz_id"))
            if not args.dry_run:
                entry = state["posts"].get(pid) or {"x_url": x_url, "text": first[:120]}
                entry.update(thread_ids=[p["id"] for p in thread], checked_at=iso(now))
                entry.setdefault("mirrored", {}).update({c: v for c, v in done.items() if "postiz_id" in v})
                skipped = {c: v["skipped"] for c, v in done.items() if "skipped" in v}
                if skipped:
                    prev = entry.get("skipped")
                    entry["skipped"] = {**prev, **skipped} if isinstance(prev, dict) else skipped
                entry["pending"] = {c: v["pending"] for c, v in done.items() if "pending" in v}
                if entry["pending"]:
                    entry["opts"] = opts
                else:
                    entry.pop("pending")
                    entry.pop("opts", None)
                state["posts"][pid] = entry
                save_state(state)
    if not args.dry_run:
        save_state(state)
    if all(line.startswith("note") for line in report):
        report.append(f"No new top-level X posts from @{HANDLE} in the last {args.lookback_hours:g} h.")
    print("\n".join(report))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"x-mirror failed: {e}", file=sys.stderr)
        sys.exit(1)
