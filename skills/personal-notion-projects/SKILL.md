---
name: personal-notion-projects
description: Explicitly invoked workflow for adding project drafts to Travis Fischer's personal Notion CMS and, when separately requested, syncing human-approved content to his personal website.
---

# Personal Notion Projects

Use only when Travis explicitly invokes `$personal-notion-projects` or asks to use **Personal Notion Projects**. The default command is **add a project**. This skill captures a concise project story for human review; publication is a separate human decision.

## Command: add <project>

### 1. Establish the source and destination

Read the project's current README, its referenced screenshots, relevant implementation/decision records, and current brand guidance. Inspect the working implementation when claims conflict. Use earlier prototypes and creation conversations to recover meaningful choices, rejected directions, and lessons. Read representative writing from Travis's existing Notion projects or posts to match his voice. Use current personal strategy guidance when available; don't invent goals or make every project serve the same theme.

Fetch the Projects database and current schema before writing:

- [Projects database](https://app.notion.com/p/3c5edb27f12480a69a16d7c2f8a1f078)
- Data source: `collection://6ffedb27-f124-8259-8a40-075b8e5a4993`
- Parent: [TransitiveBullsh.it](https://app.notion.com/p/78fc5a4b88d74b0e824e29407e9f1ec1)

Check for an existing entry by project name, slug, and website before creating a duplicate. A request to update an existing entry means fetch it first and preserve the human's edits and publication choices. These IDs identify Travis's CMS; verify the live schema rather than copying historical field assumptions.

### 2. Write a distilled story

Start with **why**: the problem, curiosity, or motivating question. Explain the project in plain language before discussing implementation. Use first person in Travis's voice: direct, curious, opinionated, occasionally playful, and technically precise. Keep it concise—usually a few short paragraphs per section, with media doing some of the explaining.

Use native Notion headings and adapt the structure to the project:

- **Motivation:** what question or problem prompted it, why it matters, and what the experiment actually explores.
- **Experience:** what someone can do; distinguish different audiences or journeys when that distinction is interesting.
- **Creation process:** the main tools and collaboration loop, options tried, choices made, and rejected approaches with their reasons.
- **Key decisions and lessons:** specific insights supported by examples; include architecture only to explain an interesting tradeoff or behavior.
- **Results or artifacts:** real output, demonstrations, contributions, or a meaningful before/after.

Combine or omit sections that add no insight. Avoid a development diary, exhaustive stack inventory, generic marketing claims, or repeating the same lesson. Give technical details enough context to explain why they matter. Separate observed results from intentions and speculation. Copy no private credentials, invitation tokens, customer information, or unpublished third-party material into a public-facing story.

### 3. Support the story with media

Use the README's selected screenshots as the first source for the product preview. Include a small selection of earlier development images when they reveal a decision, not merely because they exist. Preserve authentic source assets; label prototypes, demo data, and actual production output clearly. Captions should explain what the visual demonstrates or why the direction changed.

Use a short video for motion, sound, or interactions that still images cannot communicate. Capture actual behavior and include sound when relevant. Prefer real public contributions; if only one example exists, include that one rather than fabricating more. Match the project's visual identity and Travis's stated personal strategy when selecting evidence.

**Host embedded assets in Notion.** Upload images, GIFs, audio, video clips, attachments, and the cover to Notion's own file storage. Importing a remote file into Notion storage is fine; an external URL embed is not an upload. Two exceptions may stay externally hosted: YouTube video embeds, and videos over 30 MB that are already on R2 at `https://assets.cultural-alignment.com/…`, such as a project's backed-up share cut. Embed those by their R2 URL instead of adding another copy to Notion. A smaller video, or one that isn't on R2 yet, is uploaded as usual.

Use the project's approved social/share image as the cover when available. Verify it is a native uploaded file, not an external cover pointing at a project server, GitHub, or an expiring signed URL. Prefer current Notion connector upload tools; use the Notion CLI/API for native cover uploads when necessary. Upload and attach through the same integration when file-upload IDs are scoped to the uploading integration. Never substitute hotlinks if uploading is blocked; report the specific missing asset.

### 4. Link sparingly

Use inline descriptive anchor text. Link an external source when it explains a central concept, credits an important inspiration, or supports a substantive claim. Link another project or article by Travis when the relationship adds context to this story. Prefer its canonical public website URL; otherwise retain a resolvable Notion page link and identify unpublished references for review. Read the destination before claiming a connection. Keep links selective rather than turning the story into a bibliography or promotional cross-link list.

### 5. Save a reviewable draft

Populate the live schema's relevant fields: `Name`, a concise `Description`, stable `Slug`, `Website`, `Source`, existing `Tags`, and `Author`. Use a launch `Tweet` only when one exists. The Projects Author field is people-based; resolve Travis's connected identity rather than writing an author string. System fields such as Last Updated are read-only.

For a new entry, set **Public=false**, **Featured=false**, and leave **Published empty**. Published is a date, not a checkbox. Travis manually reviews the story, decides whether to feature it, marks it Public, and sets its publication date. Do not publish the Notion page or change site-sharing settings as part of drafting. A database's Public property is the website's content-selection flag, not Notion's sharing control.

Fetch the finished page and verify its database parent, metadata, headings, links, media, native uploaded cover, and draft flags. Report the page link and any material omissions. Completion means a complete Notion draft awaiting human review; no repository sync, commit, push, or deployment is implied.

## Command: sync approved content

Only when Travis separately requests importing or deploying human-approved content, read [Website publication workflow](references/website-publication.md). It documents the manual path from Notion approval through `pnpm content:sync`, Git, Vercel, and production verification. Merely invoking this skill to add a project does not authorize that path.
