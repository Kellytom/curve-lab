#!/bin/sh
# Count the code that is ours, by language and area.
#
#     sh scripts/code_count.sh
#
# Excluded on purpose: .venv, node_modules, site, vendor/ and the vendored
# focus-math/repos copy of spiro. None of those are ours to change, and
# counting them makes the trend invisible.
set -eu
cd "$(dirname "$0")/.." || exit 1

row() {
  label=$1
  ext=$2
  shift 2
  files=$(find "$@" \
    -not -path "*/.venv/*" -not -path "*/node_modules/*" \
    -not -path "*/site/*" -not -path "*/vendor/*" \
    -not -path "*/focus-math/repos/*" \
    -name "*.$ext" -print 2>/dev/null | wc -l | tr -d ' ')
  lines=$(find "$@" \
    -not -path "*/.venv/*" -not -path "*/node_modules/*" \
    -not -path "*/site/*" -not -path "*/vendor/*" \
    -not -path "*/focus-math/repos/*" \
    -name "*.$ext" -print0 2>/dev/null | xargs -0 cat 2>/dev/null \
    | wc -l | tr -d ' ')
  printf '%-22s %4s files %7s lines\n' "$label" "$files" "$lines"
}

echo "ours, by language and area"
row "python: engine"  py curve_lab
row "python: scripts" py scripts
row "python: tests"   py tests
row "python: web"     py web
row "js: workbench"   js workbench
row "js: scripts"     js scripts
row "js: tests/js"    js tests/js
