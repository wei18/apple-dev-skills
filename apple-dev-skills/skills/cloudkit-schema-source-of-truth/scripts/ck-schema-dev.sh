#!/usr/bin/env bash
#
# ck-schema-dev.sh — export, validate, and deploy the CloudKit Development
# schema. See ../SKILL.md for the full workflow, live-run gotchas, and the
# Production-promotion safety gate (Console-only, user-owned) — this script
# never touches Production.
#
# Usage: scripts/ck-schema-dev.sh
# Requires secrets/.env (gitignored) exporting:
#   CK_MANAGEMENT_TOKEN, CK_TEAM_ID, CK_CONTAINER_ID
#
set -euo pipefail

# Always clear the token from cktool's keychain store, even on failure.
trap 'xcrun cktool remove-token --type management --force' EXIT

# Load credentials for this shell session only.
set -a; source secrets/.env; set +a

# 1. Authenticate cktool for this session (positional arg — see gotcha 1 in SKILL.md).
xcrun cktool save-token --type management --force "$CK_MANAGEMENT_TOKEN"

# 2. Export the live Development schema to the committed source-of-truth file.
#    Seed step first: run a debug build once so the app's JIT schema provisions
#    the Development container, THEN export.
xcrun cktool export-schema \
  --team-id "$CK_TEAM_ID" --container-id "$CK_CONTAINER_ID" \
  --environment development > cloudkit/myapp.ckdb

# 3. Pre-flight: validate the committed .ckdb against the live container before importing.
xcrun cktool validate-schema \
  --team-id "$CK_TEAM_ID" --container-id "$CK_CONTAINER_ID" \
  --environment development --file cloudkit/myapp.ckdb

# 4. Deploy to Development — freely runnable and reversible.
xcrun cktool import-schema \
  --team-id "$CK_TEAM_ID" --container-id "$CK_CONTAINER_ID" \
  --environment development --file cloudkit/myapp.ckdb

# 5. Token cleanup happens via the trap above, even if a step failed midway.
