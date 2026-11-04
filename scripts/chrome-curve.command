#!/bin/sh
# Curve-lab browser: a stripped second Chrome.
#
# Fresh profile, no extensions, no session restore, no sync. Opens the workbench
# pages straight from the local server. Quitting it does not touch your main
# Chrome, and it costs a few hundred MB instead of several GB.
#
#   scripts/chrome-curve.command                 # default page set
#   scripts/chrome-curve.command catenary.html   # one page (bare name)
#
# Double-click it in Finder, or drag it to the Dock, to relaunch after a reboot.

set -eu

ROOT="/Users/thomaskelly/developer/curve-lab"
PROFILE="${TMPDIR:-/tmp}/chrome-curve"
PORT=8003
BASE="http://127.0.0.1:${PORT}"

# Pages opened on launch. Bare names are resolved by scripts/serve.py.
DEFAULT_PAGES="workbench/workbench.html workbench/pythagorean-families.html"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || { echo "Chrome not found at $CHROME" >&2; exit 1; }

# 1. Server: start only if it is not already answering, and never in the
#    foreground (serve.py blocks in serve_forever on a free port).
if ! curl -sf -o /dev/null --max-time 2 "$BASE/"; then
  echo "starting serve.py on :$PORT"
  ( cd "$ROOT" && .venv/bin/python scripts/serve.py \
      >"${TMPDIR:-/tmp}/curve-lab-serve.log" 2>&1 & )
  i=0
  while [ "$i" -lt 20 ]; do
    curl -sf -o /dev/null --max-time 1 "$BASE/" && break
    i=$((i + 1)); sleep 0.25
  done
fi

code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 "$BASE/" || true)
case "$code" in
  200|30*) ;;
  *) echo "server not answering on $BASE (got '${code:-none}')" >&2; exit 1 ;;
esac

# 2. Pages: arguments, or the default set.
if [ "$#" -gt 0 ]; then
  PAGES="$*"
else
  PAGES="$DEFAULT_PAGES"
fi

set -- # reused for the URL list
for p in $PAGES; do
  case "$p" in
    http://*|https://*|file://*) set -- "$@" "$p" ;;
    *) set -- "$@" "$BASE/${p#/}" ;;
  esac
done

# 3. Launch. A distinct --user-data-dir is what makes this a separate instance
#    with no extensions and no restored tabs.
exec "$CHROME" \
  --user-data-dir="$PROFILE" \
  --no-first-run \
  --no-default-browser-check \
  --disable-sync \
  --disable-extensions \
  --disable-background-networking \
  --disable-component-update \
  "$@"
