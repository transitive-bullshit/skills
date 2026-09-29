# TypeScript and JavaScript repos: the user's conventions

Most of the user's projects are TypeScript, and they share one setup. The files in `templates/` are the shared baseline, taken from the user's most recent repos in `~/dev/modules`. The license and `.editorconfig` are identical across those repos. The other files are the common starting point that each project then extends (see "Extending the baseline" below), and `test.yml` is the common core of the recent workflows. Trust these templates, and the most recently active repos, over `~/dev/modules/ts-template` and `next-starter-2026`, which lag behind. When in doubt, compare against two or three of the most recently committed repos in `~/dev/modules`.

## Files every TS/JS repo gets

| Template | Destination | Notes |
| --- | --- | --- |
| `templates/common/license` | `license` | MIT, Travis Fischer. Update the year. |
| `templates/common/editorconfig` | `.editorconfig` |  |
| `templates/common/gitignore` | `.gitignore` | The shared base. Append project-specific sections at the end. |
| `templates/typescript/package.json` | `package.json` | Fill in the placeholders; see below. |
| `templates/typescript/pnpm-workspace.yaml` | `pnpm-workspace.yaml` | Build allowlist, pre/post scripts, and a 1-day minimum release age (the user's own config is exempt). |
| `templates/typescript/tsconfig.node.json` | `tsconfig.json` | Node, libraries, CLIs, and scripts. It extends `@fisch0920/config/tsconfig-node`. |
| `templates/typescript/tsconfig.next.json` | `tsconfig.json` | Next.js and React apps. It extends `@fisch0920/config/tsconfig-react`. |
| `templates/typescript/oxlint.config.ts` | `oxlint.config.ts` | Extends `@fisch0920/config/oxlint`. Project rules go in `rules`. |
| `templates/typescript/oxfmt.config.ts` | `oxfmt.config.ts` | Re-exports `@fisch0920/config/oxfmt`. |
| `templates/typescript/test.yml` | `.github/workflows/test.yml` | pnpm plus Node, with actions pinned to commit SHAs plus version comments; refresh them with `npx actions-up -y`. It has no build step: add `- run: pnpm build` after `pnpm test` only when `package.json` has a `build` script, because pnpm fails on a missing script. |
| `templates/typescript/AGENTS.md` | `AGENTS.md` | The shared conventions block. Add the project's 80/20 below it. |

Doc files are lowercase: `readme.md`, `license`, `contributing.md`. AGENTS.md stays uppercase.

## package.json conventions

- **Required fields:** `name`, `version` (`0.0.0`), `private: true` (unless it's published), `description`, `license: MIT`, `author`, `repository` (`https://github.com/transitive-bullshit/<repo>`), `type: module`, `engines.node: ">=24"`, and `packageManager: pnpm@<current>`.
- **Scripts:**
  - `test` runs `run-s test:*`, over `test:format` (`oxfmt --check`), `test:lint` (`oxlint`), `test:types` (`tsc --noEmit`), and `test:unit` (`vitest run`, only when tests exist).
  - Plus `lint`, `typecheck`, and `fix` (`run-s fix:*`), over `fix:format` and `fix:lint`.
  - Add `build` only when there's something to build. Apps also add a `pnpm build` step to CI; libraries build from `posttest` instead.
- **Pre-commit hook:** `simple-git-hooks` runs `lint-staged`, which runs oxfmt and `oxlint --fix` on staged `*.{ts,tsx}`.
- **Tooling devDependencies:**
  - `@fisch0920/config` (shared tsconfig, oxlint, oxfmt, and ts-reset)
  - TypeScript 7
  - `oxlint` with `oxlint-tsgolint` (type-aware lint)
  - `oxfmt`
  - `npm-run-all2`
  - `simple-git-hooks` and `lint-staged`
  - `tsx` for scripts
  - `vitest`
  - `@types/node`

  Add them with `pnpm add -D <pkg>` so they resolve to current versions; the template's versions are only a floor. Set `packageManager` from `pnpm --version`.

- **Libraries** (published to npm): drop `private`, and add `files`, `exports`, `sideEffects: false`, and `publishConfig.access: public`. Build with `tsdown` (`build`, `dev: tsdown --watch`), with `posttest: run-s build` so `pnpm test` also builds (pnpm runs pre and post scripts because of `enablePrePostScripts`). Release with `release-it`, with a `prerelease: run-s test` script. `~/dev/modules/config` is a current example.
- **Next.js apps:**
  - Use `tsconfig.next.json`.
  - Scripts: `dev: portless run next dev --hostname 127.0.0.1`, `build: next build`, `start: next start`, and `test:types: next typegen && tsc --noEmit`. Add `- run: pnpm build` to `test.yml`.
  - Dev dependencies: `@types/react`, `@types/react-dom`, `portless`, and Tailwind v4 (`tailwindcss`, `@tailwindcss/postcss`).
  - Check a recent app such as `personal-site` or `buy-me-some-tokens` for current details.

## Extending the baseline

These are the ways recent repos extend the baseline files:

- **`oxfmt.config.ts`:** to skip generated or data files, spread the shared config and extend its ignores: `import config from '@fisch0920/config/oxfmt'`, then `export default { ...config, ignorePatterns: [...(config.ignorePatterns ?? []), 'content/snapshot.json'] }`.
- **`oxlint.config.ts`:** project rules go in `rules`. With none, `export { default } from '@fisch0920/config/oxlint'` works too.
- **`pnpm-workspace.yaml`:** give dependencies whose install scripts must run an `allowBuilds` entry (`'@swc/core': true`), or set `false` for ones that shouldn't run. `patchedDependencies` also goes here.
- **`tsconfig.json`:** narrow `include` to the real source dirs (for example `["src", "test", "*.config.ts"]`), and exclude local work, cache, or report dirs.
- **`test.yml`:** add project needs as steps (`sudo apt-get install -y ffmpeg`, `pnpm db:migrate`), plus `services` (Postgres) and test-only `env` with dummy values, never real secrets.

## Code conventions (these go in AGENTS.md)

- ESM only.
- No semicolons; oxfmt decides the formatting.
- `ky` for HTTP, and `zod` for anything external.
- Keep `pnpm test` green.

## Verify

Run each `run:` step of `test.yml` locally, in order, exactly as CI does: `pnpm install --frozen-lockfile --strict-peer-dependencies`, `pnpm test`, and `pnpm build` if the workflow has that step. Then do it again from a fresh clone in a temp dir. Run `npx actions-up -y` so the workflow's actions are current and SHA-pinned. Keep `.env` out of git and list variable names in `.env.example`. For Node 20+, `node --env-file=.env` loads it; Next.js reads `.env.local`.
