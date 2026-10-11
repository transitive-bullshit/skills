---
name: find-skills
description: Discover, compare, install or update agent skills when the user explicitly seeks skills or asks to extend their skill collection. Use for skill-discovery requests, not ordinary how-to or implementation questions.
---

# Find Skills

Find the smallest useful addition to the user’s existing skills. A search result
is a lead; inspect its source and overlap before recommending it.

## Discover and compare

1. Read the installed catalog and the canonical skills checkout from
   `~/.local/state/agent-env/environment.json`. Check whether an existing skill
   already covers the request, including explicit-only skills and plugins.
2. Start with official maintainers, relevant practitioners and the user’s trusted
   authors. Matt Pocock (`mattpocock/skills`) and David Zhang (`dzhng/skills`) are
   trusted regardless of star count. Use the user’s
   [AI Skills list](https://app.notion.com/p/transitive-bs/AI-Skills-3c1edb27f12480c1b076e637a6b156e5)
   when accessible. Search [skills.sh](https://skills.sh/) or use
   `npx skills find <query> --owner <owner>` for discovery when useful.
3. Inspect the actual skill and its linked resources. Verify author track record,
   recency, license, dependencies, invocation scope and whether it adds a new job
   or duplicates an installed skill. Adoption counts are context, not a quality
   threshold; cite primary sources for the claims behind the recommendation.
4. Present a concise shortlist: source, concrete benefit, overlap/replacement,
   maintenance cost and recommendation. Prefer keeping the current skill when
   the addition has no clear benefit. State when authoritative evidence is missing.

## Install or update when authorized

Use the Git checkouts recorded in `environment.json` and read their `AGENTS.md`
files. Import through the canonical skills repository rather than running a
third-party installer against global skill directories.

1. Compare upstream in a temporary checkout. Record exact commits, source paths
   and licenses; preserve current files, local edits and attribution. Inspect
   resources and resolve duplicate names or nested skill roots.
2. Add or update the effective skill under `skills/` and its provenance and
   profile membership in `skills.json`, following the repository’s current
   conventions. Preserve invocation policy unless the user changes it.
3. Read `python3 scripts/skillset.py --help`, run the required repository checks,
   then use its apply workflow and the existing profile to update shared links.
   Review the dry run before applying; do not overwrite unmanaged content.
4. Finish with `agent-env doctor` from the configured dotfiles checkout and
   report the installed revision, relevant local adjustments and any real drift.

`npx skills add -g`, bulk `npx skills update`, and upstream install scripts can
overwrite managed links or local changes. Use the canonical manifest and shared
installer for these writes. Discovery-only requests end with recommendations;
an explicit install/update request already authorizes its in-scope work.

If nothing suitable exists, say so and complete the underlying task directly
when requested. Propose a new personal skill only when recurring demand warrants
its maintenance cost.
