#!/usr/bin/env python3
"""Consistency gate: make README's SSOT claim enforceable across two plugins.

Checks
  1. Each <plugin>/skills/<dir>/ has a SKILL.md whose frontmatter name == <dir>.
  2. README.md Catalog contains every first-party skill (both plugins, 32) AND the
     five aggregated external plugin names (missing-direction only; extra kebab
     tokens are tolerated by design — Catalog prose legitimately names other things).
  3. Counts present: the values 20/12/5 each appear among the Catalog's "(N)" group
     headers (set membership, not per-header association); the Install one-liner
     comments and each plugin.json's "N first-party" are checked exactly.
  4. README.zh-Hant.md exists and its embedded src-sha == git hash-object README.md.
  5. All plugin/marketplace JSON parse; the two subdir plugin sources resolve to dirs;
     marketplace.json lists exactly the 7 plugins (2 local + 5 externals).
  6. The `git checkout v<semver>` pin in both READMEs' Install section ==
     marketplace.json metadata.version (drifted silently before: v1.2.0 → #17).
  7. Each SKILL.md frontmatter description <= DESC_MAX chars (descriptions are
     always-on context for every consumer session; keeps Lens-3 compression durable).
Stdlib only.
"""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = {"apple-dev-skills": 20, "collaboration-skills": 12}
EXTERNALS = {"apple-skills", "swiftui-expert", "swiftui-pro", "caveman", "ponytail"}
DESC_MAX = 800  # current max is 795 (github-contribution-workflow); cap future growth
errors: list[str] = []
def fail(m): errors.append(m)

def fm_field(p: Path, field: str):
    t = p.read_text(encoding="utf-8")
    if not t.startswith("---"): return None
    end = t.find("\n---", 3)
    if end == -1: return None
    m = re.search(rf"^{field}:\s*(.+?)\s*$", t[3:end], re.MULTILINE)
    return m.group(1).strip() if m else None

# 1. skill dirs + frontmatter
all_skills: set[str] = set()
for plugin, expected in PLUGINS.items():
    sdir = ROOT / plugin / "skills"
    dirs = sorted(p.name for p in sdir.iterdir() if p.is_dir()) if sdir.is_dir() else []
    if len(dirs) != expected:
        fail(f"[skill] {plugin}/skills has {len(dirs)} dirs, expected {expected}")
    for name in dirs:
        all_skills.add(name)
        md = sdir / name / "SKILL.md"
        if not md.is_file(): fail(f"[skill] {plugin}/{name}: no SKILL.md"); continue
        fn = fm_field(md, "name")
        if fn != name: fail(f"[skill] {plugin}/{name}: frontmatter name={fn!r} != dir")
        # 7. description length budget
        desc = fm_field(md, "description")
        if desc is None: fail(f"[skill] {plugin}/{name}: no frontmatter description")
        elif len(desc) > DESC_MAX:
            fail(f"[skill] {plugin}/{name}: description {len(desc)} chars > {DESC_MAX}")

# helper: scope README Catalog section
def scoped(text: str, *markers: str) -> str:
    for mk in markers:
        i = text.find(mk)
        if i == -1: continue
        m = re.search(r"^## ", text[i + len(mk):], re.MULTILINE)
        return text[i : i + len(mk) + m.start() if m else len(text)]
    return ""

# 2 + 3. README catalog
readme = (ROOT / "README.md").read_text(encoding="utf-8")
sec = scoped(readme, "## Catalog", "## catalog")
if not sec:
    fail("[readme] no '## Catalog' section")
else:
    tokens = set(re.findall(r"`([a-z0-9][a-z0-9-]+)`", sec))
    missing = (all_skills | EXTERNALS) - tokens
    if missing: fail(f"[readme] Catalog missing: {sorted(missing)}")
    g = [int(x) for x in re.findall(r"\((\d+)\)", sec)]
    for required in (*PLUGINS.values(), len(EXTERNALS)):
        if required not in g:
            fail(f"[readme] Catalog counts {sorted(g)} must include {sorted((*PLUGINS.values(), len(EXTERNALS)))}")
            break

# plugin.json counts
for plugin, expected in PLUGINS.items():
    pj = ROOT / plugin / ".claude-plugin" / "plugin.json"
    try: d = json.loads(pj.read_text(encoding="utf-8"))
    except Exception as e: fail(f"[manifest] {plugin}/plugin.json invalid: {e}"); continue
    for c in re.findall(r"(\d+)\s+first-party", d.get("description", "")):
        if int(c) != expected: fail(f"[manifest] {plugin} says '{c} first-party', expected {expected}")

# 3b. Install one-liner comments (outside the Catalog section, so scoped() misses them)
for plugin, n in re.findall(r"/plugin install (\S+?)@apple-dev-skills\s+#\s*(\d+)\b", readme):
    if plugin in PLUGINS and int(n) != PLUGINS[plugin]:
        fail(f"[readme] Install comment says '{n}' for {plugin}, expected {PLUGINS[plugin]}")

# 4. zh-Hant freshness
zh = ROOT / "README.zh-Hant.md"
if not zh.is_file():
    fail("[zh] README.zh-Hant.md missing — run `mise run readme-zh`")
else:
    m = re.search(r"src-sha:\s*([0-9a-f]+)", zh.read_text(encoding="utf-8"))
    cur = subprocess.run(["git", "hash-object", "README.md"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    if not m: fail("[zh] no embedded src-sha")
    elif m.group(1) != cur: fail("[zh] stale — run `mise run readme-zh` (src-sha != README.md)")

# 5. marketplace JSON + subdir sources
mp = ROOT / ".claude-plugin" / "marketplace.json"
try:
    d = json.loads(mp.read_text(encoding="utf-8"))
    for p in d.get("plugins", []):
        src = p.get("source")
        if isinstance(src, str) and src.startswith("./"):
            if not (ROOT / src).is_dir(): fail(f"[marketplace] source {src} not a dir")
    names = {p.get("name") for p in d.get("plugins", [])}
    expected_names = set(PLUGINS) | EXTERNALS
    if names != expected_names:
        fail(f"[marketplace] plugin set mismatch — missing: {sorted(expected_names - names)}, extra: {sorted(names - expected_names)}")
    # 6. README Install pin == marketplace metadata.version
    mp_version = d.get("metadata", {}).get("version", "")
    for readme_name in ("README.md", "README.zh-Hant.md"):
        text = (ROOT / readme_name).read_text(encoding="utf-8") if (ROOT / readme_name).is_file() else ""
        pins = re.findall(r"git checkout v(\d+\.\d+\.\d+)", text)
        if not pins:
            fail(f"[readme] {readme_name}: no 'git checkout v<semver>' pin found")
        for pin in pins:
            if pin != mp_version:
                fail(f"[readme] {readme_name}: Install pin v{pin} != marketplace metadata.version {mp_version} — run `mise run bump`")
except Exception as e:
    fail(f"[marketplace] invalid: {e}")

if errors:
    print(f"FAIL — {len(errors)} error(s):", file=sys.stderr)
    for e in errors: print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"OK — 2 plugins ({'/'.join(map(str, PLUGINS.values()))}), catalog + counts + zh-Hant consistent.")
