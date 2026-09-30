# Website publication workflow

Read this only when asked to explain, sync, or deploy approved CMS content. Draft creation ends in Notion; human publication approval and a request to sync/deploy are separate steps. Reuse authorization already given in the conversation without repeatedly asking for it.

## Source of truth

- Local repository: `~/dev/modules/personal-site`
- GitHub: `https://github.com/transitive-bullshit/personal-site`
- Production: `https://www.transitivebullsh.it`
- Read that repository's `AGENTS.md`, `docs/content-sync.md`, `docs/verification.md`, and `package.json` before execution. Those files govern current behavior; details below were verified on 2026-09-28.

The site renders committed snapshots. Editing Notion does not immediately update production, and builds do not automatically sync Notion.

```text
Notion draft
  → Travis reviews, marks Public, and chooses Published date / Featured
  → explicitly run pnpm content:sync in personal-site
  → review generated content + media, run repository checks
  → commit generated files and push approved changes to main
  → Vercel builds and completes the production deployment
  → verify the resulting page on the production domain
```

## Approval and import

Verify the intended entry's current Notion state. **Public=true is the actual importer inclusion gate.** Published is date metadata (optional for projects), and Featured controls homepage selection. Neither substitutes for Public or human approval. Leave all three decisions to Travis; never flip them to make a sync include a draft. Existing approved publication state need not be reconfirmed without a reason.

For projects, the schema is available from the Projects data source linked in SKILL.md. Blog Posts use database `f917892e0b8c4dbeb1743620de57a0ec`, data source `bb51e17f-99ae-4f07-97a8-4c9af77a85ec`; fetch its current schema for article work.

Inspect the checkout, branch, and existing changes. Use the configured credentials without exposing them. Run the smallest appropriate normal import from the personal-site repository:

```sh
pnpm content:sync --only projects
```

Use `--only articles` for blog posts, or `pnpm content:sync` when both collections are in scope. Selection is collection-wide, not restricted to a single page; inspect all resulting changes. Read the sync guide before using repair or migration flags. A dry run validates discovery but does not prove media import succeeds. Fast mode can omit new images, so it is not a complete import for a new illustrated project.

## Review and Git

The normal sync writes `content/snapshot.json` and `public/search-index.json`. It also copies media from Notion into immutable R2 storage for durable website delivery. Notion-hosted source media and R2-hosted website copies are intentional, separate stages; leave the Notion page's media in Notion. Large videos already on R2 are embedded by URL instead (see SKILL.md). Since personal-site `4943570` (2026-09-29), the sync keeps MP4, WebM, and MOV files on the owned origin `https://assets.cultural-alignment.com` as remote originals. It range-reads them for dimensions and a first-frame poster and uploads only the poster, so no second copy is made. The rules are in `docs/content-sync.md`.

Review both generated files together, warnings, routes, unexpected removals, and fallback content. A nonzero sync exit may still have written partial results; resolve the failure rather than assuming nothing changed or publishing an incomplete import. Run the current repository's required content-sync checks and inspect representative rendered pages, including new images/video. Restart an already-running local dev server after sync because it loads the snapshot at startup. Repair content in Notion or the importer, not by hand-editing generated JSON.

When committing and deploying are authorized, commit the reviewed snapshot and search index together, preserving unrelated work. Push approved changes to `main` through the repository's current workflow, without force-pushing. A request only to sync locally does not authorize a push.

## Deployment and production check

A push is not proof of publication. Identify the Vercel production deployment for the pushed commit and wait for it to finish successfully. Then inspect the canonical production route:

- Project: `/projects/<slug>`
- Blog post: `/<slug>`

Confirm the expected content version, cover, images, playable media/sound, and important links. Check discovery in the relevant project/writing index; check homepage placement only if Featured was approved. Verify the production domain rather than treating a preview URL or successful local build as the final result.

Report the live URL and verified deployment/commit when complete. If sync, push, deployment, or production verification is blocked, state the last completed stage and the exact remaining issue. Never call content live while Vercel is pending or the production page is unverified.
