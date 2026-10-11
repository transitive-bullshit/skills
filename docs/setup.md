# Setup notes

Requires Python 3.11+. The CLI help and `skills.json` define the supported commands and profiles. Full machine setup is owned by the sibling [dotfiles repo](https://github.com/transitive-bullshit/dotfiles).

- `mac` installs the core and desktop groups; `cloud` installs core; `current` adds the selected personal, social, archive, and discovery workflows. Optional groups are explicit profile entries in `skills.json`.
- `apply` reuses the installed profile unless one is supplied. It links both Agents/Codex and Claude by default. Cloud setup selects Codex only.
- First adoption uses `--adopt`: conflicts and the old skills.sh lock move into a private backup under `~/.local/state/agent-env/backups`. `restore --backup <id>` reverses that installation if its targets have not changed since.
- `doctor` fails on missing, wrong, obsolete, or unexpected skill installations and missing required commands. Editing a linked skill is normal Git work, not drift.
- `check` validates all profiles, provenance, names, and skill roots. Additions must have manifest entries. Keep experimental downloads outside agent discovery directories until imported.
- Upstream skills have a pinned commit, pristine snapshot under `provenance/upstream/`, and a local patch under `provenance/patches/`. `python3 scripts/upstream.py check` verifies hashes and reconstructs each effective skill from its snapshot plus patch. After intentional local edits, run `python3 scripts/upstream.py record <name>` and review the patch.
- To refresh upstream, use a temporary checkout, compare the recorded commit with upstream HEAD, replace the pristine snapshot and license, reconcile the existing patch in `skills/<name>`, update the manifest source commit/path, and run `upstream.py record <name>`. Preserve local invocation policy and resources. Run `pnpm test`, apply the environment, and finish with `agent-env doctor`.
- Derived skills declare a `derivation.lock` in the manifest. Their source lock records versioned upstream snapshots, personal inputs, and reviewed output hashes. `upstream.py check` verifies them; `record <name>` checks frozen inputs before recording authored output changes. Follow the skill's derivation reference when updating sources; synthesis is reviewed, not automatic.
- `provenance/history/2026-10-11-before.tar.gz` preserves the complete pre-curation skills, original provenance, and unmanaged good-css. Its JSON receipt records the archive hash. Unknown historical upstream revisions remain unknown; refreshed revisions are explicit.
- Preserve upstream licenses. Retrieved license files describe upstream at migration time; they do not establish the unknown historical snapshot revision. Records marked `unresolved` need investigation before public redistribution.

System and marketplace-managed skills remain owned by their hosts, including Claude desktop's session cache at `~/.claude/skills/synced/`. This installer manages standalone user skills only.
