#!/usr/bin/env bash
# The push gate: the three checks that must pass before a push leaves.
#
#   scripts/prepush.sh
#
# It stops at the first failure and exits non-zero, so a red push is caught
# before it leaves the machine. Run it from the repository root, with the Node
# 24 bin directory on PATH.
set -euo pipefail

cd "$(dirname "$0")/.."

step() { printf '\n=== %s ===\n' "$1"; }

step "python suite (--full)"
.venv/bin/python scripts/test.py --full

step "no imaginaries"
.venv/bin/python scripts/check_no_imaginaries.py

step "recheck"
.venv/bin/python scripts/recheck.py

step "app check"
npm --prefix app run check

printf '\nprepush: all three checks passed\n'
