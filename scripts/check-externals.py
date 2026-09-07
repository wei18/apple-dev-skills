#!/usr/bin/env python3
"""Opt-in drift detector for aggregated externals.

`check-consistency.py` only checks that this repo's own JSON/README stay
internally consistent — it never looks upstream. But this catalog installs
each external at *the author's latest*, and the MIT/no-overlap check that
qualified it happens once, at listing time (see CONTRIBUTING.md #1). An
external's license, archive status, manifest, or skill count can all move
after that (`caveman` already grew from 1 skill to 20 and split its license
per-directory — a human happened to notice on a later read-through).

This script makes "does the listing condition still hold" a command instead
of something that only gets checked when someone happens to look:

  1. Read every aggregated external out of `.claude-plugin/marketplace.json`.
  2. For each, ask GitHub (via `gh api`) whether the repo still exists /
     is archived, its repo-level license SPDX id, whether its
     `.claude-plugin/plugin.json` manifest still exists, and how many
     `SKILL.md` files its plugin provides (scoped to the git-subdir `path`
     for a subdir source).
  3. Diff that against the committed snapshot (`.claude-plugin/externals-snapshot.json`).
     Any field that changed is printed and the script exits 1. A clean match
     exits 0.
  4. `--update` writes the freshly probed data as the new snapshot instead of
     diffing — run it after a reviewed, deliberate change (including right
     after adding a new external, so its baseline gets recorded).

This needs `gh` + network, so it is deliberately NOT wired into lefthook's
pre-commit or the consistency GitHub Actions workflow — both must work
offline. Run it by hand: `mise run check-externals` (or `-- --update`).

Stdlib only.
"""
from __future__ import annotations
import argparse, json, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
SNAPSHOT = ROOT / ".claude-plugin" / "externals-snapshot.json"
FIELDS = ("repo", "path", "archived", "license", "manifest_present", "skill_count")
AUTH_HINTS = ("not logged into", "auth login", "authentication required")


def die(msg: str, code: int = 1):
    print(msg, file=sys.stderr)
    sys.exit(code)


def gh_json(*args: str):
    try:
        r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=30)
    except FileNotFoundError:
        die("gh CLI not found on PATH — install it (https://cli.github.com) to run check-externals.")
    if r.returncode != 0:
        stderr = r.stderr.strip()
        if any(h in stderr.lower() for h in AUTH_HINTS):
            die("gh is not authenticated — run `gh auth login` first, then re-run check-externals.")
        die(f"gh call failed: gh {' '.join(args)}\n{stderr}")
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        die(f"gh returned non-JSON output for: gh {' '.join(args)}\n{r.stdout[:500]}")


def parse_repo_url(url: str) -> str:
    m = re.search(r"github\.com/([^/]+/[^/]+?)(?:\.git)?/?$", url)
    if not m:
        die(f"[check-externals] cannot parse owner/repo from url: {url}")
    return m.group(1)


def external_entries(mp: dict) -> list[tuple[str, str, str | None]]:
    """(plugin name, owner/repo, git-subdir path or None) for every aggregated
    external — a first-party plugin's source is a plain './...' string, so it's
    skipped here."""
    out = []
    for p in mp.get("plugins", []):
        src = p.get("source")
        if not isinstance(src, dict):
            continue
        kind = src.get("source")
        if kind == "github":
            out.append((p["name"], src["repo"], None))
        elif kind == "git-subdir":
            out.append((p["name"], parse_repo_url(src["url"]), src.get("path")))
        else:
            die(f"[check-externals] {p.get('name')}: unrecognized source shape {src!r}")
    return out


def probe(repo: str, path: str | None) -> dict:
    info = gh_json("api", f"repos/{repo}", "--jq", "{archived: .archived, license: .license.spdx_id}")
    tree = gh_json("api", f"repos/{repo}/git/trees/HEAD?recursive=1", "--jq", "[.tree[].path]")
    prefix = f"{path}/" if path else ""
    manifest_present = f"{prefix}.claude-plugin/plugin.json" in tree
    skills_prefix = f"{prefix}skills/"
    skill_count = sum(1 for t in tree if t.startswith(skills_prefix) and t.endswith("/SKILL.md"))
    return {
        "repo": repo,
        "path": path,
        "archived": info.get("archived"),
        "license": info.get("license"),
        "manifest_present": manifest_present,
        "skill_count": skill_count,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--update", action="store_true",
                     help="write freshly probed data as the new snapshot instead of diffing")
    args = ap.parse_args()

    if shutil.which("gh") is None:
        die("gh CLI not found on PATH — install it (https://cli.github.com) to run check-externals. "
            "This check needs network + gh and is intentionally not run in pre-commit or CI.")

    mp = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    entries = external_entries(mp)

    current = {}
    for name, repo, path in entries:
        loc = f"{repo}/{path}" if path else repo
        print(f"probing {name} ({loc}) ...", file=sys.stderr)
        current[name] = probe(repo, path)

    if args.update:
        SNAPSHOT.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"OK — snapshot updated: {SNAPSHOT.relative_to(ROOT)} — review the diff and commit it.")
        return

    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8")) if SNAPSHOT.is_file() else {}
    diffs: list[str] = []
    for name, data in current.items():
        if name not in snapshot:
            diffs.append(f"{name}: not in snapshot (new external) — run `mise run check-externals -- --update`")
            continue
        old = snapshot[name]
        for field in FIELDS:
            if old.get(field) != data.get(field):
                diffs.append(f"{name}.{field}: snapshot={old.get(field)!r} -> current={data.get(field)!r}")
    for name in snapshot:
        if name not in current:
            diffs.append(f"{name}: in snapshot but no longer listed in marketplace.json")

    if diffs:
        print(f"DRIFT — {len(diffs)} change(s) since the snapshot was taken:", file=sys.stderr)
        for d in diffs:
            print(f"  - {d}", file=sys.stderr)
        print("Review each change against CONTRIBUTING.md's aggregation requirements; if it's still "
              "acceptable, accept the new baseline with `mise run check-externals -- --update`.",
              file=sys.stderr)
        sys.exit(1)

    print(f"OK — {len(current)} aggregated externals match the recorded snapshot.")


if __name__ == "__main__":
    main()
