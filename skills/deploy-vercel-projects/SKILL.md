---
name: deploy-vercel-projects
description: 'Deploy and configure Vercel projects from verified docs. Use when deploying to Vercel, editing vercel.json, giving Vercel dashboard or project-settings steps, setting up Web Analytics or Speed Insights, or shipping prebuilt or locally built output.'
---

# Deploy Vercel Projects

Vercel's dashboard, CLI, and build pipeline change often, and remembered details come out confidently wrong. Ground every Vercel-specific claim in the current docs or the live project.

## Rules

- **Verify dashboard paths and setting names.** Confirm them in the docs or through the Vercel API/MCP before giving them, or say you're unsure. Remembered paths have been wrong in practice, e.g. Ignored Build Step placed under Settings → Git; it is under Settings → Build and Deployment.
- **Read docs as Markdown sections.** A docs page is ~850 KB as HTML and still 15–30 KB as Markdown. Append `.md` to the docs URL (`https://vercel.com/docs/cli/deploy.md`) or send `Accept: text/markdown`, list headings with `grep -n '^#'`, and print only the section you need.
- **Analytics needs a Vercel-run build.** Web Analytics and Speed Insights routes are attached only to deployments Vercel builds itself. The tell: on a `vercel deploy --prebuilt` deployment the analytics script returns 404 and no data arrives. In the v2 `@vercel/analytics` and `@vercel/speed-insights` packages the script path is project-specific and reaches the page only through `VERCEL_OBSERVABILITY_CLIENT_CONFIG`, which Vercel injects into builds it runs. For a site built locally, upload the built output with a trivial Vercel build step that writes that config into the page. Worked example: `scripts/deploy.ts` and `scripts/vercel-analytics.mjs` in `transitive-bullshit/murmuration` (private; local checkout `~/dev/modules/murmuration`).
- **`vercel rm <project-name>` removes the whole project** unless `--safe` is passed. To remove one deployment, pass its full deployment URL.
- **`"git": { "deploymentEnabled": false }`** in `vercel.json` stops Git-triggered deployments for every branch.
