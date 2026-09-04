#!/bin/sh
# Path C (flat, no plugin) for the WHOLE catalog: `npx skills` scans a repo for
# SKILL.md folders and never reads marketplace.json, so `npx skills add
# wei18/apple-dev-skills` yields only the first-party skills and silently skips
# the aggregated externals. This script walks marketplace.json (the SSOT) and
# adds every plugin source, externals included, from their authors' repos.
# Usage: scripts/install-flat.sh [--dry-run] [extra `npx skills add` flags, e.g. -g]
#   --dry-run may appear in any position; every other argument is forwarded.
set -eu

TOP="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -z "$TOP" ] || [ ! -f "$TOP/.claude-plugin/marketplace.json" ]; then
  echo "install-flat.sh reads this repo's marketplace.json, so it must run from inside a clone:" >&2
  echo "  git clone https://github.com/wei18/apple-dev-skills" >&2
  echo "  cd apple-dev-skills && scripts/install-flat.sh --dry-run" >&2
  exit 1
fi
cd "$TOP"

# Pull --dry-run out of any position, keeping the remaining args in "$@" (rotate-and-shift).
DRY=0
argc=$#
while [ "$argc" -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    *) set -- "$@" "$1" ;;
  esac
  shift
  argc=$((argc - 1))
done

# Quote one argument the way a shell would, so a dry-run line pastes back verbatim.
quote() {
  case "$1" in
    *[!A-Za-z0-9@%_+=:,./-]*) printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")" ;;
    *) printf '%s' "$1" ;;
  esac
}

# One argv, two consumers: print it (dry-run) or exec it (real run) — never two spellings.
install_one() {
  if [ "$DRY" -eq 1 ]; then
    sep=''
    for a in "$@"; do printf '%s' "$sep"; quote "$a"; sep=' '; done
    printf '\n'
  else
    "$@"
  fi
}

SOURCES="$(python3 - <<'PY'
import json
printed_self = False
for p in json.load(open(".claude-plugin/marketplace.json"))["plugins"]:
    s = p["source"]
    if isinstance(s, str):  # local subdir plugin -> one add of this repo covers all
        if not printed_self:
            print("wei18/apple-dev-skills")
            printed_self = True
    elif s.get("source") == "github":
        print(s["repo"])
    elif s.get("source") == "git-subdir":
        # `skills add` takes a subdirectory as a GitHub tree URL; printing the bare
        # url would name a different (whole-repo) install than the one that runs.
        ref = s.get("sha") or s.get("ref") or "main"
        print(f"{s['url'].rstrip('/')}/tree/{ref}/{s['path'].strip('/')}")
PY
)"

for src in $SOURCES; do
  install_one npx -y skills add "$src" --skill '*' -y "$@"
done
