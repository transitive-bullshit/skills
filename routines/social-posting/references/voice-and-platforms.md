# Voice and platforms

## Travis's voice

His X posts are the reference. Read a few recent ones before drafting. The traits that carry across platforms:

- **Concise.** Short lines, line breaks between thoughts, and one idea per post. A one-line hook plus one line of substance often beats a paragraph.
- **Personality.** Casual and playful, with lowercase on X and Threads, "w/", stretched words ("sooooo", "ahoooo") and the occasional emoji. The humor comes from the project itself.
- **Honest about the process.** He names the tools (Opus 5.5, Claude Code, Suno, fal), the real cost ("~$300"), and what took work ("this video is _not_ one-shot"). Specific numbers beat adjectives.
- **Generous with credit.** He names the inspiration ("inspired by this dope hip hop classic") and links the source and the write-up ("open source", "behind the scenes breakdown").
- **Opinionated.** He takes a position ("AI safety has a branding problem") and lets the project argue it.

### Do

- Lead with the claim or hook he used on X, then adapt its register to the platform.
- Use concrete facts from the project: tools, cost, time, what surprised him.
- Link the canonical write-up (`https://www.transitivebullsh.it/projects/<slug>`), and the source repo when it's public.
- Keep his lowercase and casual register on Threads. Use sentence case on Bluesky and LinkedIn.
- Credit inspirations and collaborators by name.

### Don't

- Hype words and puffery: "excited to announce", "game-changer", "revolutionary", "I'm thrilled".
- AI filler and structure: "In today's fast-moving landscape", "Not just X, but Y", forced groups of three, em dashes. The unslop rules cover the full list.
- Engagement bait ("like and repost if…"), emoji walls, or emoji as bullet markers.
- X links on other platforms. People use Bluesky and Threads to get away from X: link the write-up, never a tweet.
- Claims the sources don't support. If a fact isn't in the repo, write-up or his posts, leave it out.

## Platforms

Limits come from Postiz's `integrations:settings` for each channel. Check them there, since they can change.

### Threads: close to his X voice

- 500 characters, clickable links (at most 5). Long text becomes a thread.
- Lowercase and casual is fine. Mirror the energy of his X post, not its exact words.
- Hashtags are unnecessary.
- Handles: X `@handles` don't map to Threads, so write names without the `@`.

### Bluesky: compact and link-first

- 300 characters including the full URL. The link card does the visual work.
- Sentence case with one crisp hook line. The audience is technical and wary of X culture.

### LinkedIn: businesslike tone and content

LinkedIn changes the framing, not just the tone. Lead with the idea or problem a professional audience cares about, then what he built, how, and what it shows. Use the storytelling skill's product/project pitch pattern: the audience's situation, the insight, what he built, proof, then the link.

- Up to 3,000 characters. Short paragraphs, and a bulleted "how it was made" list works well.
- Include the concrete numbers (cost, time, tools) and an honest "not one-shot" note: that's credibility here.
- End with the write-up and source links, then 3–4 broad hashtags (#AI #GenerativeAI #ClaudeCode).
- Skip the playful lowercase and stretched words.

### Instagram: visual-first

- Caption up to 2,200 characters. The first line is the hook, since the rest is folded.
- Links aren't clickable: write "Full breakdown at transitivebullsh.it" instead.
- 5–8 relevant hashtags at the end.
- Video posts become Reels. 9:16 is ideal, but 16:9 works (it's letterboxed).
- Postiz can't set Instagram's AI label. Tell Travis to toggle "AI info" in the app after it posts.

### TikTok: hook plus hashtags

- A short caption: the hook, one line of what it is, then 6–8 hashtags.
- Video only. Set `video_made_with_ai: true` and post publicly with `DIRECT_POST`; see the Postiz reference.
- Duets and stitches are unavailable for videos over 60 seconds, so set them false.

## Example: one launch across platforms

Slow It Down, an AI-made R&B music video. His X launch post:

> AI safety has a branding problem
>
> Sometimes you just gotta slow it down, baby
>
> Seriously, just give this video a chance. Regardless of your views on AI, I can guarantee you'll appreciate the vibes

His self-reply added the facts: about $300 with Opus 5.5 and Suno, "not one-shot", inspired by The-Dream's "Slow It Down", and the source and write-up links.

**Threads**, casual and close to X:

> ai safety has a branding problem
>
> sometimes you just gotta slow it down, baby 🎶
>
> made this ai music video w/ opus 5.5 + suno. it's not one-shot: ~$300 and a lot of back & forth, but the models did so much of the heavy lifting that i could finally express something like this
>
> inspired by one of my fav classic slow jams, The-Dream's "Slow It Down", then we took it our own way
>
> how it was made: https://www.transitivebullsh.it/projects/slow-it-down-ai-music-video

**Bluesky**, compact:

> AI safety has a branding problem.
>
> Sometimes you just gotta slow it down, baby 🎶
>
> An AI-made R&B slow jam about pacing the frontier, made with Opus 5.5 + Suno.
>
> How it was made: https://www.transitivebullsh.it/projects/slow-it-down-ai-music-video

**LinkedIn**, the same claim reframed as an idea about the industry (abridged):

> AI safety has a branding problem.
>
> The frontier labs say they want to "pace" AI development, because "slow" sounds like losing. Slowing down reads as weak, and racing reads as optimistic and inevitable. So I ran an experiment: could slowing down feel sexy instead?
>
> The result is "Slow It Down", an AI-made R&B music video set in Club Frontier. [...]
>
> A few notes on how it was made:
>
> • Claude Code with Opus 5.5 did nearly all of the production work [...]. My job was taste and feedback. • It cost about $300, mostly spent exploring directions before landing on one I liked. • It is not one-shot. [...]
>
> Full write-up on the process: https://www.transitivebullsh.it/projects/slow-it-down-ai-music-video
>
> #AI #AISafety #GenerativeAI #ClaudeCode
