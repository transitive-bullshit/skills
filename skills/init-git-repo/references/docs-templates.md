# Docs templates

Three files with three audiences. Use lowercase `readme.md` and `contributing.md`, keep AGENTS.md uppercase, and match whatever casing an existing repo already uses.

- **`readme.md`** sells the project to developers.
- **`contributing.md`** helps someone run and change it.
- **AGENTS.md** gets a fresh agent productive quickly.

Don't duplicate content across them. Link instead.

## readme.md: developer-facing marketing

Keep it short. It should pitch, show, and link, and it must not turn into a manual. If the project has a published write-up (a project page or blog post), mirror its structure and wording. Choose tracked images/GIFs or stable hosted URLs under the [asset policy](../SKILL.md#2-decide-the-asset-and-large-file-policy).

```markdown
# <Project Name>

> <One-line hook>

[![<Project Name>](<hero image path or URL>)](<project URL>)

**[▶ <Primary call to action: watch / try / read>](<project URL>)**

<Two sentences: what it is and how it was made. One line that frames the repo, e.g. "This repo is the whole working directory behind it.">

## <Why: the motivation, in the author's voice>

## <What: the concept or features, with a visual>

## How it was made

<The pipeline or architecture in 5–10 bullets, tools used, and optionally tried-and-discarded and lessons learned.>

## License

The code is [MIT](license) © [Travis Fischer](https://x.com/transitive_bs). <Any rights notes for non-code content.>

---

Want to run it, change it, or see where everything lives? See [contributing.md](contributing.md).
```

## contributing.md: the technical detail

Include:

- **Setup:** toolchain, the one-line install, optional groups, system dependencies, and `.env.example`.
- **The main workflow:** a copy-pasteable command sequence, with a comment on what each step produces, what it costs, and what's safe to re-run.
- **Where each step lives:** a table of step, code, and output.
- **The common task** people will actually do (for example "redo a single shot"), as numbered steps.
- **Tests and CI:** what they cover, and that they're offline.
- **Repo map:** a short tree.
- **What's not in the repo, on purpose:** each category and the reason (copyright, regenerable, third-party), plus where the showcase copies live.

## AGENTS.md: a minimal jumping-off point

Write the file you'd want as a capable agent arriving without context. Aim for about 30–50 lines covering the project structure and the 80/20 facts. Prefer stable guidance (where things live, what's generated, what costs money) over implementation details that drift (counts, versions, line numbers, per-item settings). Point to `contributing.md` and the subsystem READMEs rather than repeating them. Never create a CLAUDE.md.

```markdown
# AGENTS.md

<What this is, in one line, with the published URL. Whether it's a package, an app, or a working directory of scripts.> See `contributing.md` for setup and commands.

## Mental model

<The pipeline or architecture as one flow: inputs → key files → outputs → feedback loop.>

## Edit sources, not outputs

- <Which files are the sources of truth, which are generated, and how to regenerate them. Mention it if a test enforces this.>

## Costs and side effects

- <Anything that spends money (paid APIs), touches production or public systems, or can't be undone: ask first. Idempotency and receipts.>
- <Keys come from `.env` (see `.env.example`); never print them.>

## Not in git

- <What a fresh clone lacks (media, data, weights), what must never be committed (copyrighted or private material), and where hosted copies live.>
- <`readme.md` is marketing; technical docs go in `contributing.md`.>

## Conventions that held up

- <The 3–5 hard-won rules or gotchas that would otherwise be rediscovered expensively.>

## Checks

<The test command, what CI runs, and any environment caveat, e.g. "`uv sync` prunes `.venv`".>
```
