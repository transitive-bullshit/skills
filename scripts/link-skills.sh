#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
skills_dir="${repo_root}/skills"
global_skills_dir="${AGENTS_SKILLS_DIR:-${HOME}/.agents/skills}"

mkdir -p "${global_skills_dir}"

linked_count=0

for skill_dir in "${skills_dir}"/*; do
  [[ -d "${skill_dir}" && -f "${skill_dir}/SKILL.md" ]] || continue

  skill_name="${skill_dir##*/}"
  target="${global_skills_dir}/${skill_name}"

  if [[ -e "${target}" && ! -L "${target}" ]]; then
    printf 'Cannot link %s: %s already exists and is not a symlink.\n' "${skill_name}" "${target}" >&2
    exit 1
  fi

  ln -sfn "${skill_dir}" "${target}"
  printf 'Linked %s -> %s\n' "${target}" "${skill_dir}"
  linked_count=$((linked_count + 1))
done

if ((linked_count == 0)); then
  printf 'No skills found in %s.\n' "${skills_dir}" >&2
  exit 1
fi
