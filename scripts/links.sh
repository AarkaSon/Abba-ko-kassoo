#!/usr/bin/env bash
# ULTRON — SO-01: emit raw GitHub download links for tracked deliverables.
# Usage:  bash scripts/links.sh [path-filter]
# Verifies each file is COMMITTED and PUSHED before emitting a link (an
# unpushed file 404s).
set -uo pipefail
BR="arena/019fa790-abba-ko-kassoo"
BASE="https://github.com/AarkaSon/Abba-ko-kassoo/raw/${BR}"
FILTER="${1:-results/}"

git fetch -q origin "$BR" 2>/dev/null
if [ "$(git rev-parse HEAD)" != "$(git rev-parse FETCH_HEAD 2>/dev/null)" ]; then
  echo "!! WARNING: local HEAD differs from remote — PUSH before sharing links." >&2
fi

printf '| File | Direct download link |\n|---|---|\n'
git ls-files "$FILTER" | grep -vE '\.gitkeep$' | while read -r f; do
  printf '| `%s` | %s/%s |\n' "$(basename "$f")" "$BASE" "$f"
done
