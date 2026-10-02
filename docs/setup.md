# Setup notes

Requires Python 3.11+. The CLI help and `skills.json` define the supported commands and profiles. Full machine setup is owned by the sibling [dotfiles repo](https://github.com/transitive-bullshit/dotfiles).

- `mac` installs the core and desktop groups; `cloud` installs core; `current` preserves the original MacBook selection. Optional groups are explicit profile entries in `skills.json`.
- `apply` reuses the installed profile unless one is supplied. It links both Agents/Codex and Claude by default. Cloud setup selects Codex only.
- First adoption uses `--adopt`: conflicts and the old skills.sh lock move into a private backup under `~/.local/state/agent-env/backups`. `restore --backup <id>` reverses that installation if its targets have not changed since.
- `doctor` fails on missing, wrong, obsolete, or unexpected skill installations and missing required commands. Editing a linked skill is normal Git work, not drift.
- `check` validates all profiles, provenance, names, and skill roots. Additions must have manifest entries. Keep experimental downloads outside agent discovery directories until imported.
- Update upstream skills separately from machine sync. Use the recorded source to compare a temporary upstream checkout with your effective files. The imported snapshots may include local edits and lack exact upstream commits; do not overwrite them or invent a baseline commit.
- Preserve upstream licenses. Retrieved license files describe upstream at migration time; they do not establish the unknown historical snapshot revision. Records marked `unresolved` need investigation before public redistribution.

System and marketplace-managed skills remain owned by their hosts. This installer manages standalone user skills only.
