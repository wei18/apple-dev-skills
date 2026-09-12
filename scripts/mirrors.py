"""Single source of truth for this repo's README mirrors (SSOT is README.md).

Each entry maps a mirror file to the heading text that opens its localized
Catalog-equivalent section (used by check-consistency.py rule 9 to scope the
coverage check, mirroring rule 2's scoping of README.md's own "## Catalog").

check-consistency.py and bump-version.py loop over this mapping instead of
hardcoding a filename — but adding a new language mirror still touches four
places, not just this file: this MIRRORS dict, check-consistency.py's
MIRROR_TASK (mirror filename -> its regenerator task), scripts/gen-readme-zh.sh's
locale case statement, and .mise.toml's per-locale `readme-*` task definition.
"""
MIRRORS = {
    "README.zh-Hant.md": "## 目錄",
    "README.zh-Hans.md": "## 目录",
    "README.ja.md": "## カタログ",
}
