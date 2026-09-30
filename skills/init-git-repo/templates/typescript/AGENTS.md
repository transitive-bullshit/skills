# Project: <name>

<One line on what this is, with its URL if published. See `contributing.md` for setup and commands.>

## Conventions

- use `pnpm`
- use modern TypeScript (ESM only, no CommonJS)
- no semicolons; oxfmt formats (`pnpm fix:format`) and oxlint lints (`pnpm fix:lint`)
- `pnpm test` runs format, lint, types, and unit tests; keep it green
- use `ky` as a wrapper around `fetch` for HTTP requests
- use `zod` to validate external data
- for local development, use `pnpm dev` and the Portless URL it prints (apps only)

<Then only the project-specific 80/20 from references/docs-templates.md: mental model, sources vs. outputs, costs and side effects, what's not in git.>
