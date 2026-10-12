# Working here

Skills in `skills/` are the editable source of truth. Keep adopted files and their attribution intact unless intentionally changing them; `skills.json` records provenance and profile membership. Add new skills to that manifest. Use `scripts/skillset.py --help` for installation and checks.

Instructions in `routines/` are read in place by scheduled Claude routines. They aren't skills: keep them out of `skills.json`, and update the routine prompts in `~/.claude/scheduled-tasks/` if you move them.

When importing or updating a skill, preserve local edits, inspect its resources, and resolve duplicate names or nested skill roots before installation. Use a temporary checkout for upstream comparisons; install from this repo rather than letting an upstream installer overwrite its links.

Run `pnpm test` after changes. Installer tests run independently with `python3 -m unittest discover -s tests`. Keep READMEs short and practical, with a copyable agent setup prompt; put operational exceptions in `docs/setup.md`.
