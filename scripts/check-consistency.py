#!/usr/bin/env python3
"""Consistency gate: make README's SSOT claim enforceable across two plugins.

Checks
  1. Each <plugin>/skills/<dir>/ has a SKILL.md whose frontmatter name == <dir>.
  2. README.md Catalog contains every first-party skill (both plugins, 40), every agent,
     AND the seven aggregated external plugin names (missing-direction only; extra kebab
     tokens are tolerated by design — Catalog prose legitimately names other things).
  3. Counts present: the values 28/12/7 each appear among the Catalog's "(N)" group
     headers (set membership, not per-header association); the Install one-liner
     comments and each plugin.json's "N first-party" are checked exactly.
  4. Each README mirror (see mirrors.py for the current list) exists and its
     embedded src-sha == git hash-object README.md.
  5. All plugin/marketplace JSON parse; the two subdir plugin sources resolve to dirs;
     marketplace.json lists exactly the 9 plugins (2 local + 7 externals).
  6. The `"ref": "v<semver>"` marketplace pin in README.md and every mirror ==
     marketplace.json top-level version (drifted silently before as a
     `git checkout v<semver>` string: v1.2.0 → #17).
  7. Each SKILL.md frontmatter description <= DESC_MAX chars (descriptions are
     always-on context for every consumer session; keeps Lens-3 compression durable).
  8. Each plugin's `.claude-plugin/plugin.json` "version" == the corresponding
     marketplace.json plugins[] entry "version" (the pair bump-version.py maintains).
  9. Each README mirror's own Catalog-equivalent section (scripts/mirrors.py) covers
     the same first-party skills, every agent + externals as README.md's Catalog (mirrors check 2;
     count regex also accepts full-width parens, since mirrors are hand-typed).
  10. Each SKILL.md frontmatter description that is not quoted must not contain
      ": " or start with a YAML indicator character (PR #42: an unquoted value
      containing ": " breaks strict YAML parsers). A block scalar (`description: >`)
      is exempt: everything after the indicator is literal text. Indented continuation
      lines count as part of the value; a value that opens a quote must close it, with
      nothing after the closing quote but an optional ` # comment`.
  11. Every skill or agent named in the Catalog's journey anchor list (above the tables)
      exists — rule 2 only checks the missing direction, so a rename would leave a
      dead pointer there while the tables below stayed correct.
  12. Each first-party plugin's marketplace.json description leading number
      (e.g. "28 first-party Apple/Swift skills") == the PLUGINS constant below.
  13. README.md's "install only the N first-party skills" sentence (flat-install
      caveat) has N == sum(PLUGINS.values()).
  14. <plugin>/agents/ is flat. Each <file>.md there has frontmatter name == <file>; its
      description passes the rule 7 + 10 checks with AGENT_DESC_MAX as the limit; every
      `${CLAUDE_PLUGIN_ROOT}/<path>` its body points to exists in that plugin, with no
      `..` segment; the unbraced `$CLAUDE_PLUGIN_ROOT` form does not appear. Rules 7/10
      are a quoting heuristic, not a YAML parser; `claude plugin validate` parses it.
Stdlib only.
"""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path

from mirrors import MIRRORS

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = {"apple-dev-skills": 28, "collaboration-skills": 12}
EXTERNALS = {"apple-skills", "swiftui-expert", "swiftui-pro", "caveman", "ponytail", "i-have-adhd", "xcode-build-skill"}
DESC_MAX = 800  # ceiling on frontmatter description length; which skill is currently
                # longest shifts as skills are added — don't hardcode a name here
AGENT_DESC_MAX = 400  # an agent description sits in the Agent tool's roster in every session
errors: list[str] = []
def fail(m): errors.append(m)

BLOCK_SCALAR = "\x00block\x00"  # internal marker: value came from a YAML block scalar

def fm_field(p: Path, field: str):
    """Raw frontmatter value, quotes intact. Block scalars (`>`/`|`) come back as
    the folded text with a BLOCK marker so callers can tell them from a bare `>`."""
    t = p.read_text(encoding="utf-8")
    if not t.startswith("---"): return None
    end = t.find("\n---", 3)
    if end == -1: return None
    fm = t[3:end]
    # [ \t]*, not \s*: \s would cross the newline, so an empty `field:` would capture the
    # next line as its value.
    m = re.search(rf"^{field}:[ \t]*(.*?)[ \t]*$", fm, re.MULTILINE)
    if not m: return None
    head = m.group(1).strip()
    # The value continues on the indented lines that follow (a block scalar's body, or
    # a multi-line plain / quoted scalar) up to the next non-indented line.
    body = []
    for ln in fm[m.end():].splitlines():
        if ln.strip() and not ln.startswith((" ", "\t")): break
        body.append(ln.strip())
    cont = " ".join(x for x in body if x)
    if head and head[0] in "|>":
        return BLOCK_SCALAR + cont
    # Plain / quoted scalars fold line breaks into spaces: return the whole value, so
    # rule 10 also sees a continuation line (e.g. one containing ': ').
    return " ".join(x for x in (head, cont) if x)

def closing_quote(v: str):
    """Index of the quote that closes v's opening quote, or None if it never closes.
    Double-quoted: a backslash escapes the next char. Single-quoted: '' is a literal '."""
    q, i = v[0], 1
    while i < len(v):
        if q == '"' and v[i] == "\\": i += 2; continue
        if v[i] == q:
            if q == "'" and v[i + 1:i + 2] == "'": i += 2; continue
            return i
        i += 1
    return None

def unquote(v: str) -> str:
    """name/description are legitimately bare or quoted YAML: strip matching outer quotes."""
    return v[1:-1] if len(v) >= 2 and v[0] in "'\"" and v[-1] == v[0] else v

def check_description(label: str, md: Path, max_len: int) -> None:
    """Rules 7 + 10 (and rule 14 for agents): description present, within max_len,
    and quoted wherever strict YAML needs it."""
    desc = fm_field(md, "description")
    # A block scalar (`description: >`) is already YAML-safe: everything after the
    # indicator is literal text, so `: ` and indicator characters need no quoting.
    block = bool(desc) and desc.startswith(BLOCK_SCALAR)
    if block: desc = desc[len(BLOCK_SCALAR):]
    if not desc:
        fail(f"{label}: no frontmatter description"); return
    opens_quote = not block and desc[0] in "'\""
    quoted = False
    if opens_quote:
        close = closing_quote(desc)
        if close is None:
            fail(f"{label}: description opens a {desc[0]} quote that "
                 f"never closes — breaks YAML parsing")
        elif re.fullmatch(r"(\s+#.*)?\s*", desc[close + 1:]):
            # A ` # comment` after the closing quote is legal YAML. Strip it only
            # here, once the quote has closed — never on an unquoted value, where
            # ` #` silently truncates (checked below).
            desc, quoted = desc[:close + 1], True
        else:
            fail(f"{label}: description has text after its closing "
                 f"{desc[0]} quote (unescaped quote inside, or a partly quoted value) "
                 f"— breaks YAML parsing")
    # 7. Length counts the value a consumer actually sees (quotes stripped), matching
    # check-skills.py's parse_front() — otherwise a quoted description that needs
    # quoting only because of a ': ' or indicator gets penalized twice for it.
    shown = desc[1:-1] if quoted else desc
    if not shown.strip():
        fail(f"{label}: no frontmatter description"); return
    desc_len = len(shown)
    if desc_len > max_len:
        fail(f"{label}: description {desc_len} chars > {max_len}")
    # 10. description must survive a strict YAML parse — fm_field() returns the
    # raw value (quotes intact, not stripped), so check quoting directly on it.
    # A value that opens a quote was fully checked by closing_quote() above (an
    # unescaped quote inside closes it early and leaves trailing text).
    if not block and not opens_quote:
        if ": " in desc or desc[0] in "[]{}&*>|#%@`!":
            fail(f"{label}: description must be quoted (contains ': ' or a YAML indicator)")
        if " #" in desc:
            fail(f"{label}: description must be quoted "
                 f"(contains ' #' — starts a YAML comment, silently truncating the value)")
        if desc.startswith("- "):
            fail(f"{label}: description must be quoted "
                 f"(starts with '- ' — a YAML block-sequence indicator)")
        if desc.endswith(":"):
            fail(f"{label}: description must be quoted "
                 f"(ends with ':' — a YAML mapping-value indicator)")

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
        if unquote(fn or "") != name: fail(f"[skill] {plugin}/{name}: frontmatter name={fn!r} != dir")
        check_description(f"[skill] {plugin}/{name}", md, DESC_MAX)

# 14. agents/*.md: name == file stem, bounded description, plugin-root pointers resolve
all_agents: set[str] = set()
for plugin in PLUGINS:
    adir = ROOT / plugin / "agents"
    for md in sorted(adir.rglob("*.md")):
        rel = md.relative_to(adir)
        if len(rel.parts) > 1:
            # Claude Code loads agents/ recursively; the catalog keeps it flat so that
            # name == file stem stays the one naming rule.
            fail(f"[agent] {plugin}/agents/{rel}: agents/ must be flat — move it to agents/{md.name}")
            continue
        all_agents.add(md.stem)
        fn = fm_field(md, "name")
        if unquote(fn or "") != md.stem: fail(f"[agent] {plugin}/{md.name}: frontmatter name={fn!r} != file stem")
        check_description(f"[agent] {plugin}/{md.name}", md, AGENT_DESC_MAX)
        body = md.read_text(encoding="utf-8")
        if re.search(r"\$CLAUDE_PLUGIN_ROOT\b", body):
            fail(f"[agent] {plugin}/{md.name}: write ${{CLAUDE_PLUGIN_ROOT}} with braces — "
                 f"Claude Code does not substitute $CLAUDE_PLUGIN_ROOT")
        for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)", body):
            if ".." in ref.split("/"):
                fail(f"[agent] {plugin}/{md.name}: pointer {ref} leaves the plugin ('..')")
            # The path pattern also matches a sentence-ending period after the path.
            elif not (ROOT / plugin / ref.rstrip(".")).exists():
                fail(f"[agent] {plugin}/{md.name}: points to missing {ref}")

catalog_names = all_skills | all_agents | EXTERNALS

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
    missing = catalog_names - tokens
    if missing: fail(f"[readme] Catalog missing: {sorted(missing)}")
    g = [int(x) for x in re.findall(r"\((\d+)\)", sec)]
    for required in (*PLUGINS.values(), len(EXTERNALS)):
        if required not in g:
            fail(f"[readme] Catalog counts {sorted(g)} must include {sorted((*PLUGINS.values(), len(EXTERNALS)))}")
            break
    # 11. The journey anchor list sits above the tables, so rule 2's "nothing is
    # missing" direction can't see a stale name in it — a renamed skill would
    # leave a dead pointer here while the tables below stayed correct.
    anchors = scoped(sec, "## Catalog").split("###")[0]
    stale = {t for t in re.findall(r"`([a-z0-9][a-z0-9-]+)`", anchors)} - catalog_names
    if stale: fail(f"[readme] Catalog anchor list names no such skill or agent: {sorted(stale)}")

# 9. Each mirror's own Catalog-equivalent section — same token coverage check as
# above, mirrored: mirrors are hand-typed so a translator can silently drop/mistype
# a skill token without README.md or the src-sha check (rule 4) ever noticing.
for mirror_name, heading in MIRRORS.items():
    mirror_path = ROOT / mirror_name
    if not mirror_path.is_file():
        continue  # rule 4 below already flags a missing mirror
    m_sec = scoped(mirror_path.read_text(encoding="utf-8"), heading)
    if not m_sec:
        fail(f"[{mirror_name}] no '{heading}' section")
        continue
    m_tokens = set(re.findall(r"`([a-z0-9][a-z0-9-]+)`", m_sec))
    m_missing = catalog_names - m_tokens
    if m_missing: fail(f"[{mirror_name}] {heading} missing: {sorted(m_missing)}")
    mg = [int(x) for x in re.findall(r"[\(（](\d+)[\)）]", m_sec)]
    for required in (*PLUGINS.values(), len(EXTERNALS)):
        if required not in mg:
            fail(f"[{mirror_name}] {heading} counts {sorted(mg)} must include {sorted((*PLUGINS.values(), len(EXTERNALS)))}")
            break

# plugin.json counts
plugin_json_versions: dict[str, str] = {}
for plugin, expected in PLUGINS.items():
    pj = ROOT / plugin / ".claude-plugin" / "plugin.json"
    try: d = json.loads(pj.read_text(encoding="utf-8"))
    except Exception as e: fail(f"[manifest] {plugin}/plugin.json invalid: {e}"); continue
    for c in re.findall(r"(\d+)\s+first-party", d.get("description", "")):
        if int(c) != expected: fail(f"[manifest] {plugin} says '{c} first-party', expected {expected}")
    plugin_json_versions[plugin] = d.get("version")

# 3b. Install one-liner comments (outside the Catalog section, so scoped() misses them)
for plugin, n in re.findall(r"/plugin install (\S+?)@apple-dev-skills\s+#\s*(\d+)\b", readme):
    if plugin in PLUGINS and int(n) != PLUGINS[plugin]:
        fail(f"[readme] Install comment says '{n}' for {plugin}, expected {PLUGINS[plugin]}")

# 13. "install only the N first-party skills" flat-install caveat == sum(PLUGINS.values())
total_first_party = sum(PLUGINS.values())
m = re.search(r"install only the (\d+) first-party skills", readme)
if not m:
    fail("[readme] no 'install only the N first-party skills' sentence found")
elif int(m.group(1)) != total_first_party:
    fail(f"[readme] 'install only the {m.group(1)} first-party skills' != {total_first_party}")

# 4. Mirror freshness
MIRROR_TASK = {  # mirror filename -> its `mise run <task>` regenerator (scripts/*.mise.toml)
    "README.zh-Hant.md": "readme-zh",
    "README.zh-Hans.md": "readme-zh-hans",
    "README.ja.md": "readme-ja",
}
for mirror_name in MIRRORS:
    task = MIRROR_TASK.get(mirror_name, "readme-zh")
    mirror = ROOT / mirror_name
    if not mirror.is_file():
        fail(f"[{mirror_name}] missing — run `mise run {task}`")
        continue
    m = re.search(r"src-sha:\s*([0-9a-f]+)", mirror.read_text(encoding="utf-8"))
    cur = subprocess.run(["git", "hash-object", "README.md"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.strip()
    if not m: fail(f"[{mirror_name}] no embedded src-sha")
    elif m.group(1) != cur: fail(f"[{mirror_name}] stale (src-sha != README.md) — hand-mirror the changed "
                                 f"lines + re-stamp src-sha (CONTRIBUTING §README mirrors)")

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
    # 12. marketplace.json plugins[].description leading count == PLUGINS constant
    for p in d.get("plugins", []):
        name = p.get("name")
        if name not in PLUGINS: continue
        expected = PLUGINS[name]
        counts = [int(c) for c in re.findall(r"(\d+)\s+first-party", p.get("description", ""))]
        if not counts:
            fail(f"[marketplace] {name} description has no 'N first-party' count")
        elif any(c != expected for c in counts):
            fail(f"[marketplace] {name} description says '{counts} first-party', expected {expected}")
    # 8. plugin.json version == marketplace.json plugins[].version (pair bump-version.py maintains)
    mp_versions = {p.get("name"): p.get("version") for p in d.get("plugins", [])}
    for plugin in PLUGINS:
        pj_v, mp_v = plugin_json_versions.get(plugin), mp_versions.get(plugin)
        if pj_v is None or mp_v is None:
            fail(f"[manifest] {plugin} version missing — plugin.json={pj_v!r}, marketplace.json={mp_v!r}")
        elif pj_v != mp_v:
            fail(f"[manifest] {plugin} plugin.json version {pj_v!r} != marketplace.json plugins[].version {mp_v!r} — run `mise run bump`")
    # 6. README marketplace-pin == marketplace top-level version
    mp_version = d.get("version", "")
    for readme_name in ("README.md", *MIRRORS):
        text = (ROOT / readme_name).read_text(encoding="utf-8") if (ROOT / readme_name).is_file() else ""
        pins = re.findall(r'"ref":\s*"v(\d+\.\d+\.\d+)"', text)
        if not pins:
            fail(f'[readme] {readme_name}: no \'"ref": "v<semver>"\' pin found')
        for pin in pins:
            if pin != mp_version:
                fail(f"[readme] {readme_name}: Install pin v{pin} != marketplace.json version {mp_version} — run `mise run bump`")
except Exception as e:
    fail(f"[marketplace] invalid: {e}")

if errors:
    print(f"FAIL — {len(errors)} error(s):", file=sys.stderr)
    for e in errors: print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"OK — 2 plugins ({'/'.join(map(str, PLUGINS.values()))}), {len(all_agents)} agent(s), catalog + counts + "
      f"{len(MIRRORS)} README mirror(s) ({'/'.join(MIRRORS)}) consistent.")
