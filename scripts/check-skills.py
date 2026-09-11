#!/usr/bin/env python3
"""Skill-format gate: official Agent Skills / Claude Code rules + this catalog's own conventions.
Exits 1 on any BLOCKER. Usage: python3 check-skills.py <repo-root> [--md out.md]"""
import os, re, sys, glob, json

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
PLUGINS = {"apple-dev-skills": "apple-dev-skills/skills", "collaboration-skills": "collaboration-skills/skills"}
OFFICIAL_KEYS = {"name","description","when_to_use","argument-hint","arguments","disable-model-invocation",
                 "user-invocable","allowed-tools","disallowed-tools","model","effort","context","agent","background","paths",
                 "shell","hooks","license","metadata","compatibility","version"}
SECTIONS = ["When to invoke","Scope","Rationale","Deviation considerations","Common Mistakes",
            "Review Checklist|Verification checklist","Related skills"]
FIRST_PERSON = re.compile(r"\b(I can|I help|I will|I'll|I provide|we can|we help)\b", re.I)
PATHS_HINT = re.compile(r"(\*\.swift|any file matching|automatically during .* dispatch|invoke automatically|any `?\S*View\S*\.swift)", re.I)

def parse_front(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m: return None, text
    fm = {}
    cur = None
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if km:
            cur = km.group(1); fm[cur] = km.group(2)
        elif cur and line.startswith((" ", "\t")):
            fm[cur] += " " + line.strip()
    for k, v in fm.items():
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"): v = v[1:-1]
        if v in (">", "|", ">-", "|-"): v = ""
        fm[k] = v
    return fm, m.group(2)

def is_quoted_example(body, start, end):
    """True if body[start:end] sits inside a "..." span on its own line — i.e. it's
    prose illustrating what a pointer instruction *would* look like, not a real
    in-body pointer this skill relies on (e.g. skill-authoring-patterns quoting
    `references/synchronization.md` as an example instruction to write)."""
    line_start = body.rfind("\n", 0, start) + 1
    line_end = body.find("\n", end)
    if line_end == -1: line_end = len(body)
    before = body[line_start:start]
    after = body[end:line_end]
    return bool(re.search(r'"[^"]*$', before)) and bool(re.search(r'^[^"]*"', after))

skills = {}
for plugin, sub in PLUGINS.items():
    for d in sorted(glob.glob(os.path.join(ROOT, sub, "*"))):
        if os.path.isfile(os.path.join(d, "SKILL.md")):
            skills[os.path.basename(d)] = (plugin, d)

findings = []   # (severity, skill, rule, detail)
matrix = {}
def add(sev, skill, rule, detail): findings.append((sev, skill, rule, detail))

for name, (plugin, d) in skills.items():
    path = os.path.join(d, "SKILL.md")
    text = open(path, encoding="utf-8").read()
    fm, body = parse_front(text)
    if fm is None:
        add("BLOCKER", name, "frontmatter", "no YAML frontmatter"); continue
    # --- official name rules
    n = fm.get("name","")
    if n != name: add("BLOCKER", name, "name==dir", f"name={n!r}")
    if len(n) > 64: add("BLOCKER", name, "name<=64", f"{len(n)} chars")
    if not re.fullmatch(r"[a-z0-9-]+", n): add("BLOCKER", name, "name charset", n)
    # Claude Code itself doesn't enforce this — only the claude.ai upload path
    # (and package_skill.py) hard-errors on "anthropic"/"claude" in `name`.
    if re.search(r"anthropic|claude", n):
        add("MINOR", name, "name reserved word", f"{n} (only blocks the claude.ai upload path, not Claude Code)")
    # --- official description rules
    desc = fm.get("description","")
    if not desc: add("BLOCKER", name, "description empty", "")
    L = len(desc) + len(fm.get("when_to_use",""))
    if len(desc) > 1024: add("BLOCKER", name, "description<=1024 (API)", f"{len(desc)}")
    if L > 1536: add("BLOCKER", name, "description+when_to_use<=1536 (Claude Code listing)", f"{L}")
    if len(desc) > 800:  add("MAJOR",   name, "description<=800 (repo gate)", f"{len(desc)}")
    if re.search(r"<[a-zA-Z/][^>]*>", desc): add("BLOCKER", name, "description XML tag", desc[:80])
    if FIRST_PERSON.search(desc): add("MAJOR", name, "description first person", FIRST_PERSON.search(desc).group(0))
    if not re.search(r"\b(when|use for|query|invoke)\b", desc, re.I): add("MAJOR", name, "description lacks trigger phrase", desc[:80])
    # --- unknown frontmatter keys
    for k in fm:
        if k not in OFFICIAL_KEYS: add("MAJOR", name, "unknown frontmatter key", k)
    if fm.get("context") == "fork" and "agent" not in fm: add("MINOR", name, "context: fork without agent", "defaults to general-purpose")
    if "agent" in fm and fm.get("context") != "fork": add("MAJOR", name, "agent without context: fork", "")
    # --- body length
    nlines = body.count("\n") + 1
    if nlines > 500: add("MAJOR", name, "body>500 lines", f"{nlines}")
    words = len(body.split())
    # --- section matrix (catalog convention; informational)
    heads = re.findall(r"^##\s+(.+?)\s*$", body, re.M)
    present = {s: any(re.fullmatch(alt, h.strip(), re.I) for h in heads for alt in s.split("|")) for s in SECTIONS}
    matrix[name] = (plugin, L, nlines, words, present)
    # --- references/ pointers must exist (skip prose that merely quotes an example
    # pointer instruction rather than relying on one — see is_quoted_example())
    seen_refs = set()
    for m in re.finditer(r"`?(references/[\w./-]+\.md)`?", body):
        ref = m.group(1)
        if ref in seen_refs: continue
        if is_quoted_example(body, m.start(1), m.end(1)): continue
        seen_refs.add(ref)
        if not os.path.isfile(os.path.join(d, ref)): add("BLOCKER", name, "dangling references/ pointer", ref)
    if os.path.isdir(os.path.join(d, "references")):
        for f in os.listdir(os.path.join(d, "references")):
            if f.endswith(".md") and f"references/{f}" not in body: add("MINOR", name, "references/ file never pointed to", f)
    # --- cross-skill references
    for tok in set(re.findall(r"`([a-z0-9-]+(?::[a-z0-9-]+)?)`", body)):
        if ":" in tok:
            pl, sk = tok.split(":", 1)
            if pl in PLUGINS and sk not in skills: add("BLOCKER", name, "broken plugin:skill ref", tok)
            if pl in PLUGINS and sk in skills and skills[sk][0] != pl: add("BLOCKER", name, "ref to wrong plugin", tok)
        elif tok in skills and tok != name:
            # A line listing three or more skill names is an enumeration
            # (naming conventions, catalogues), not a cross-reference pointer.
            line = next((l for l in body.splitlines() if f"`{tok}`" in l), "")
            enumeration = sum(1 for s2 in skills if f"`{s2}`" in line) >= 3
            if skills[tok][0] != plugin and not enumeration: add("MAJOR", name, "bare cross-plugin ref (dangling if other plugin not installed)", f"{tok} -> use {skills[tok][0]}:{tok}")
    # --- prose triggers that official `paths:` could replace
    m = PATHS_HINT.search(desc + "\n" + body[:1500])
    if m and "paths" not in fm: add("MINOR", name, "prose file-trigger; candidate for paths:", m.group(0))
    # --- description summarizing workflow (heuristic: numbered steps / arrows)
    if re.search(r"(→.*→|Step ?1|\b1\)\s.*\b2\)\s)", desc): add("MINOR", name, "description may summarize workflow", desc[:80])

sev_order = {"BLOCKER":0,"MAJOR":1,"MINOR":2}
findings.sort(key=lambda f:(sev_order[f[0]], f[1], f[2]))
out = []
out.append(f"# Skill gate report — {len(skills)} skills\n")
counts = {s: sum(1 for f in findings if f[0]==s) for s in sev_order}
out.append(f"BLOCKER {counts['BLOCKER']} · MAJOR {counts['MAJOR']} · MINOR {counts['MINOR']}\n")
out.append("## Findings\n\n| sev | skill | rule | detail |\n|---|---|---|---|")
for s, n, r, dt in findings:
    dt = dt.replace("|", "&#124;")
    out.append(f"| {s} | {n} | {r} | {dt} |")
out.append("\n## Section matrix (catalog convention; ✓ present)\n")
out.append("| skill | plugin | desc len | lines | words | " + " | ".join(SECTIONS) + " |")
out.append("|---|---|---|---|---|" + "---|"*len(SECTIONS))
for n,(pl,L,nl,w,pr) in matrix.items():
    out.append(f"| {n} | {pl.split('-')[0]} | {L} | {nl} | {w} | " + " | ".join("✓" if pr[s] else "·" for s in SECTIONS) + " |")
missing = {s: [n for n,v in matrix.items() if not v[4][s]] for s in SECTIONS}
out.append("\n## Missing-section totals\n")
for s, lst in missing.items(): out.append(f"- {s}: {len(lst)}/{len(matrix)} missing")
report = "\n".join(out)
if "--md" in sys.argv: open(sys.argv[sys.argv.index("--md")+1], "w").write(report)
print(report if "--md" not in sys.argv else f"wrote report; {counts}")

if counts["BLOCKER"] > 0:
    sys.exit(1)
