#!/bin/sh
# Push the data exports to GitHub. The database itself stays local; these files
# rebuild it, so GitHub is the off-site copy.
set -eu
cd "$(dirname "$0")/.."
LOCK="state/.sync.lock"
mkdir "$LOCK" 2>/dev/null || exit 0
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT
git add workbench/curve-notes.json workbench/finder-stars.json workbench/starred.json workbench/operator-list.json
if git diff --cached --quiet; then exit 0; fi
git commit -q -m "data: sync $(date -u +%Y-%m-%dT%H:%MZ)"
git push -q origin main
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) synced" >> state/sync.log
