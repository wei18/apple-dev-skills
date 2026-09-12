#!/usr/bin/env python3
"""Bump release versions across every surface the gate checks, in one shot.

Surfaces (previously a 4-file manual dance, see v1.3.1 / PR #16):
  --marketplace X.Y.Z  -> marketplace.json metadata.version
                          + `"ref": "vX.Y.Z"` marketplace pin in README.md AND every
                            mirror in scripts/mirrors.py
                          + re-stamp each mirror's src-sha (pin line is hand-mirrored;
                            no full mirror regeneration needed for this one-line change)
  --apple X.Y.Z        -> apple-dev-skills/.claude-plugin/plugin.json version
                          + its marketplace.json plugins[] entry version
  --collab X.Y.Z       -> same pair for collaboration-skills

Edits are targeted text substitutions (never a JSON load->dump round-trip, which
would reflow the hand-formatted single-line objects into a noise diff).
Ends by running check-consistency.py. Tag `vX.Y.Z` manually after the PR merges.

Usage: mise run bump -- --marketplace 1.4.0 --collab 1.4.0
Stdlib only.
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path

from mirrors import MIRRORS

ROOT = Path(__file__).resolve().parent.parent
MP = ROOT / ".claude-plugin" / "marketplace.json"
SEMVER = r"\d+\.\d+\.\d+"


def die(msg: str):
    print(f"ERROR: {msg}", file=sys.stderr); sys.exit(1)


def sub_once(text: str, pattern: str, repl: str, where: str) -> str:
    new, n = re.subn(pattern, repl, text, count=1, flags=re.DOTALL)
    if n != 1: die(f"pattern not found in {where}: {pattern}")
    return new


def set_plugin_version(plugin_dir: str, version: str):
    pj = ROOT / plugin_dir / ".claude-plugin" / "plugin.json"
    pj.write_text(sub_once(pj.read_text(encoding="utf-8"),
                           r'("version"\s*:\s*")' + SEMVER + r'(")',
                           rf"\g<1>{version}\g<2>", str(pj)), encoding="utf-8")
    mp_text = MP.read_text(encoding="utf-8")
    MP.write_text(sub_once(mp_text,
                           rf'("name"\s*:\s*"{plugin_dir}"[^}}]*?"version"\s*:\s*")' + SEMVER + r'(")',
                           rf"\g<1>{version}\g<2>", f"marketplace plugins[{plugin_dir}]"),
                  encoding="utf-8")
    print(f"  {plugin_dir}: -> {version} (plugin.json + marketplace entry)")


def precheck_marketplace_mirrors():
    """Refuse to bump `--marketplace` while any mirror is already stale — otherwise the
    re-stamp in set_marketplace_version() just re-freshens a src-sha that was never an
    honest mirror of README.md (regression: bump-version.py --marketplace silently
    launders a stale mirror into a green gate, see check-consistency.py rule 4).

    Called before ANY file is written (not just before the marketplace edits) so a
    multi-flag bump (e.g. --apple + --marketplace) can't die here after --apple's
    plugin.json + marketplace.json edits are already on disk — a non-atomic partial bump."""
    pre_sha = subprocess.run(["git", "hash-object", "README.md"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.strip()
    for mirror_name in MIRRORS:
        mirror = ROOT / mirror_name
        m = re.search(r"<!-- src-sha: ([0-9a-f]+) -->", mirror.read_text(encoding="utf-8"))
        if not m or m.group(1) != pre_sha:
            die(f"{mirror_name} src-sha is stale vs README.md — run `mise run readme-zh` first, then re-run bump")


def set_marketplace_version(version: str):
    MP.write_text(sub_once(MP.read_text(encoding="utf-8"),
                           r'("metadata"\s*:\s*\{[^}]*?"version"\s*:\s*")' + SEMVER + r'(")',
                           rf"\g<1>{version}\g<2>", "marketplace metadata"), encoding="utf-8")
    for name in ("README.md", *MIRRORS):
        p = ROOT / name
        text, n = re.subn(r'"ref":\s*"v' + SEMVER + r'"', f'"ref": "v{version}"',
                          p.read_text(encoding="utf-8"))
        if n == 0: die(f'no \'"ref": "v<semver>"\' pin in {name}')
        p.write_text(text, encoding="utf-8")
    sha = subprocess.run(["git", "hash-object", "README.md"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.strip()
    for mirror_name in MIRRORS:
        mirror = ROOT / mirror_name
        mirror.write_text(sub_once(mirror.read_text(encoding="utf-8"),
                               r"(<!-- src-sha: )[0-9a-f]+( -->)", rf"\g<1>{sha}\g<2>",
                               f"{mirror_name} src-sha"), encoding="utf-8")
    print(f"  marketplace metadata + README pins: -> {version} (mirror src-sha re-stamped)")


def main():
    sys.stdout.reconfigure(line_buffering=True)  # keep our lines ordered before the gate subprocess's
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--marketplace", metavar="X.Y.Z")
    ap.add_argument("--apple", metavar="X.Y.Z")
    ap.add_argument("--collab", metavar="X.Y.Z")
    args = ap.parse_args()
    if not (args.marketplace or args.apple or args.collab):
        ap.error("nothing to bump — pass at least one of --marketplace/--apple/--collab")
    for v in (args.marketplace, args.apple, args.collab):
        if v and not re.fullmatch(SEMVER, v): die(f"not a semver: {v}")

    if args.marketplace: precheck_marketplace_mirrors()  # before any write — see docstring

    if args.apple: set_plugin_version("apple-dev-skills", args.apple)
    if args.collab: set_plugin_version("collaboration-skills", args.collab)
    if args.marketplace: set_marketplace_version(args.marketplace)

    json.loads(MP.read_text(encoding="utf-8"))  # still valid JSON after text edits
    print("running gate...")
    sys.exit(subprocess.run([sys.executable, str(ROOT / "scripts" / "check-consistency.py")]).returncode)


if __name__ == "__main__":
    main()
