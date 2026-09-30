#!/usr/bin/env bash
# Pre-publish audit for a local project: sizes, large files, what git would commit, secret-like patterns, local paths.
# Read-only. Prints file names only, never secret values.
# usage: audit.sh [project-dir=.] [large-file-MB=10]
set -uo pipefail
DIR="${1:-.}"; LARGE_MB="${2:-10}"
cd "$DIR" || { echo "no such directory: $DIR" >&2; exit 1; }
hr() { printf '\n== %s\n' "$1"; }
none_if_empty() { if [ -n "$1" ]; then printf '%s\n' "$1"; else echo "(none)"; fi; }
IS_GIT=0; git rev-parse --is-inside-work-tree >/dev/null 2>&1 && IS_GIT=1
LIST=$(mktemp); trap 'rm -f "$LIST"' EXIT

hr "Sizes by top-level entry"
du -sh -- * .[!.]* 2>/dev/null | sort -h | tail -25

hr "Files over ${LARGE_MB} MB (outside .git, node_modules, virtualenvs, build dirs)"
big=$(find . \( -path ./.git -o -name node_modules -o -name '.venv*' -o -name target -o -name .next \) -prune -o \
        -type f -size +"${LARGE_MB}"M -print 2>/dev/null | while IFS= read -r f; do
        st="untracked"
        if [ "$IS_GIT" = 1 ]; then if git check-ignore -q "$f"; then st="ignored"; else st="WOULD-COMMIT"; fi; fi
        printf '%8s  %-12s  %s\n' "$(du -h "$f" | cut -f1)" "$st" "$f"
      done | sort -k2,2r -k1,1hr | head -60)
none_if_empty "$big"

# the files a commit would contain: already tracked + what `git add .` would add (or every file, outside git)
if [ "$IS_GIT" = 1 ]; then
  { git -c core.quotePath=false ls-files; git -c core.quotePath=false add -n . 2>/dev/null | sed "s/^add '//; s/'$//"; } | sort -u > "$LIST"
else
  find . \( -path ./.git -o -name node_modules -o -name '.venv*' \) -prune -o -type f -print | sed 's#^\./##' | sort > "$LIST"
fi

hr "What a commit would contain"
n=$(grep -c . "$LIST" || true)
kb=$(tr '\n' '\0' < "$LIST" | xargs -0 du -ck 2>/dev/null | tail -1 | cut -f1)
echo "${n} files, ~$(( ${kb:-0} / 1024 )) MB"
echo "largest:"
tr '\n' '\0' < "$LIST" | xargs -0 ls -l 2>/dev/null | sort -k5 -rn | head -10 | awk '{ printf "  %10.1f KB  %s\n", $5 / 1024, $NF }'

hr "Media, archives, weights, or binaries a commit would contain"
none_if_empty "$(grep -iE '\.(wav|mp3|m4a|flac|aiff?|mp4|mov|webm|mkv|avi|png|jpe?g|webp|gif|psd|tiff?|zip|tar|t?gz|7z|rar|pt|pth|ckpt|safetensors|onnx|bin|h5|parquet|sqlite3?|db)$' "$LIST" | head -40)"

hr "Env files a commit would contain"
none_if_empty "$(grep -E '(^|/)\.env($|\.)' "$LIST" | grep -v '\.env\.example$')"

hr "Secret-like patterns (file: pattern; values not shown)"
hits=""
while IFS='|' read -r name rx; do
  [ -z "$name" ] && continue
  files=$(tr '\n' '\0' < "$LIST" | xargs -0 grep -IliE -e "$rx" 2>/dev/null | head -20)
  [ -n "$files" ] && hits="${hits}$(printf '%s\n' "$files" | sed "s/\$/: $name/")"$'\n'
done <<'EOF'
aws-access-key|AKIA[0-9A-Z]{16}
private-key|-----BEGIN [A-Z ]*PRIVATE KEY-----
github-token|gh[pousr]_[A-Za-z0-9]{36,}
slack-token|xox[baprs]-[A-Za-z0-9-]{10,}
openai-or-anthropic-key|sk-(ant-|proj-)?[A-Za-z0-9_-]{20,}
notion-token|(ntn|secret)_[A-Za-z0-9]{30,}
google-api-key|AIza[0-9A-Za-z_-]{35}
bearer-token|[Bb]earer [A-Za-z0-9._-]{30,}
key-assignment|(api[_-]?key|secret|token|passw(or)?d)["']?[[:space:]]*[:=][[:space:]]*["'][A-Za-z0-9/+_.-]{16,}["']
EOF
none_if_empty "$(printf '%s' "$hits" | sed '/^$/d')"

hr "Absolute home-directory paths ($HOME)"
none_if_empty "$(tr '\n' '\0' < "$LIST" | xargs -0 grep -IlF -e "$HOME" 2>/dev/null | head -30)"

if [ "$IS_GIT" = 1 ]; then
  hr "Git state"
  echo "branch: $(git branch --show-current 2>/dev/null)"
  git remote -v | head -2
  git count-objects -vH | grep -E '^(count|size|size-pack|garbage):'
  git rev-parse -q --verify HEAD >/dev/null || echo "no commits yet: if 'size' is large, run 'git gc --prune=now' before the first commit"
fi
