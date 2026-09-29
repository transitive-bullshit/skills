---
name: init-git-repo
description: "Turn a local project into a clean, shareable Git repo that follows the user's conventions. Covers: an audit and cleanup (large files, secrets, private or copyrighted material, local paths); the baseline files (license, .editorconfig, .gitignore base); a deliberate large-file policy (ignore, host on R2, or Git LFS); lockfiles plus the user's TypeScript setup (pnpm, @fisch0920/config, oxlint, oxfmt); a minimal offline GitHub Actions test.yml pinned with actions-up; and readme.md (marketing), contributing.md (technical), and AGENTS.md. Use when initializing, publishing, or open-sourcing a local workspace, or when setting up a new TypeScript or JavaScript repo."
---

# Initialize a shareable Git repo

The goal is a repo that a stranger or a fresh agent can clone, understand in a minute, and reproduce. It should contain no private data, no derived bulk, and nothing the user doesn't have the right to share. Work in the phases below. Nothing leaves the machine until the user asks for a commit or a push.

## 1. Inventory

- Run `scripts/audit.sh <project-dir>`. It shows sizes by directory, the largest files, what `git add` would stage, any secret patterns, and absolute local paths. It prints file names only, never values.
- Classify everything by category:
  - **source:** code, prompts, configs, docs, small curated data
  - **derived:** builds, renders, caches, generated media, logs
  - **third-party:** vendored checkouts, model weights, virtualenvs, `node_modules`
  - **private:** secrets, personal data, local paths
  - **not ours:** copyrighted material the user doesn't own
- Check the git state:
  - Loose objects left by an earlier `git add` in a repo with no commits: run `git gc --prune=now`.
  - An existing remote and branch: check them before assuming a fresh start.
  - Files that came from another project, such as that project's own `.gitignore` entries: remove them.
- If the project is already published, find its live URL and hosted media. For the user's site, projects live at `https://www.transitivebullsh.it/projects/<slug>` (from the Notion Projects CMS), with media on R2 at `https://assets.cultural-alignment.com/personal-site/media/<hash>.<ext>`. Parse them from the live page's HTML. The README reuses them instead of committing media.

## 2. Decide the large-file policy per category, not per file

| What | Where it goes |
| --- | --- |
| Derived or regenerable | `.gitignore`. If it's expensive to regenerate, back it up outside git (an R2 prefix or a release asset), and commit the inputs that produce it (prompts, configs, receipts). |
| Showcase media for docs | Host it on R2 or the project's site, and link it. |
| Third-party code, weights, environments | `.gitignore`. Document how to fetch or rebuild them. |
| Private or copyrighted material | Never committed, LFS included. |
| Integral source binaries | Commit directly if small (under ~1 MB) and rarely changing. Use Git LFS only for large binaries the project can't be rebuilt without. |

GitHub rejects files over 100 MB and warns over 50 MB. LFS on a public repo spends quota on every clone, and pushed objects are hard to purge, so LFS is the exception.

## 3. Add the baseline files and the .gitignore

- **Every repo, in any language,** gets the user's common `license` (MIT, update the year), `.editorconfig`, and `.gitignore` base from `templates/common/`. The `.editorconfig` sets 2-space indents everywhere, so append each other language's convention (for Python, a `[*.py]` section with `indent_size = 4`).
- **Doc files are lowercase:** `readme.md`, `license`, `contributing.md`. AGENTS.md stays uppercase. Keep whatever casing an existing repo already uses.
- **The .gitignore:**
  - Start from the common base, which is the user's standard across projects (its Next.js and Vercel sections included), so keep it whole.
  - Append project-specific sections in this order: environments and third-party checkouts, private and copyrighted material, derived outputs by directory, and last, a safety net that blocks media by extension. A deliberate exception is `git add -f`.
  - Drop only entries copied from another project's own additions.
- **Anchor top-level directories with a leading `/`.** A bare `audio/` also matches `video/audio/`.
- **Verify the result:**
  - Read `git add -n .` for the exact file list, count, and total size.
  - Use `git check-ignore -v <path>` to explain any surprise.
  - Confirm that every file the docs link to is tracked.

## 4. Audit privacy and security

- **Secrets:** check for keys, tokens, private keys, `.env` files, and credentials embedded in notebooks, logs, receipts, or saved API responses. Keys stay in the environment. `.env.example` lists names and a one-line purpose for each, never values.
- **Absolute local paths** (`/Users/<name>`, `/home/<name>`): make them relative where they affect behavior (configs, scripts), not only to hide them.
- **Text you don't own:** check docs and data for copyrighted text (lyrics, scripts, book text), not just media files.
- **Report** anything legally or personally sensitive to the user rather than silently deciding its fate.

## 5. Make it reproducible (the 80/20)

- **TypeScript or JavaScript:** follow the user's conventions in `references/typescript.md`. That means pnpm, `@fisch0920/config` for tsconfig, oxlint, and oxfmt, the standard `package.json` scripts and git hooks, and the canonical files in `templates/typescript/`. Most of the user's projects are TypeScript.
- **Other ecosystems get one manifest and lockfile each, with modern defaults.** See `references/reproducibility.md`. For Python that's uv (`pyproject.toml`, `uv.lock`, `.python-version`); for Rust, `Cargo.lock` plus `rust-toolchain.toml`; for Go, `go.mod` and `go.sum`.
- **Derive dependencies from what the code actually imports,** at the installed versions. Pin git dependencies to a commit.
- **Keep the default install light.** Put heavy or optional stacks (ML frameworks, experiments, tooling for abandoned approaches) in optional groups.
- **Document what isn't in git:** system dependencies (`brew`/`apt`), required environment variables, and any input files.
- **Verify in isolation:**
  - Install from the lockfile into a temporary environment and run a smoke path.
  - Never sync or prune the user's existing environment. With uv, `uv sync` removes unlisted packages, so point `UV_PROJECT_ENVIRONMENT` at a temp dir. `uv run` also installs into the project env, so run checks against the temp env too.
  - After the first local commit, `git clone` into a temp dir and run install plus tests. That's the real self-containment check.
- **Fix portability issues** you find along the way, such as absolute paths and machine-specific configs.

## 6. Add minimal CI

- **One workflow, `.github/workflows/test.yml`** (named `Test`, run on push), in this order: checkout, toolchain setup, install from the lockfile (core only), cheap checks (compile, typecheck, or build), tests. For TypeScript, use `templates/typescript/test.yml`.
- **If no tests exist, add two to four offline smoke tests.** They should exercise real code paths on committed data, for example "the committed generated file matches its generator".
- **Keep it safe and cheap:**
  - No secrets, external API calls, or paid services.
  - Set `timeout-minutes` and `permissions: contents: read`.
- **Pin actions with `npx actions-up -y`** after writing or editing a workflow. It updates every action to its latest release and pins it to a commit SHA with a version comment, which is the user's convention. `--dry-run` previews the changes. When it reports a breaking (major-version) update, read that action's release notes and confirm that the workflow's inputs and triggers still behave the same.

## 7. Write the docs

- **`readme.md` is a developer-facing marketing asset.**
  - Open with the pitch, then the project URL (the live site or published write-up), prominently.
  - Put featured images up top, hosted rather than committed.
  - Follow with a concise why, what, and how it was made. If a published write-up exists, mirror its wording.
  - No setup instructions or repo internals.
  - End with a short License section, linking the author to `https://x.com/transitive_bs`, then a link to `contributing.md`.
  - GitHub renders external images inline but not external video or audio, so link those.
- **`contributing.md` holds the technical detail:**
  - setup and commands
  - where things live
  - how to do the common task
  - tests and CI
  - what's deliberately not in the repo, and why
- **AGENTS.md is a minimal jumping-off point for future agents.** Never write a CLAUDE.md. See `references/docs-templates.md`. TypeScript repos start from the conventions block in `templates/typescript/AGENTS.md`.

## 8. Commit and push, when asked

- **Last checks before committing:** staged file count and size, no media, `.env`, or secret matches in the stage, and passing tests.
- **Check `git ls-remote origin` first.** An empty remote takes a first commit on the default branch. A remote that already has commits (a GitHub-created README or license, say) gets integrated, never force-pushed over.
- **Follow the environment's commit-attribution rules.** After pushing, check the CI run once.

## Report

Summarize:

- what's tracked and what's deliberately excluded, and why
- the reproducibility setup and how it was verified
- CI
- decisions left for the user, such as backups of expensive generated assets or legally sensitive files
