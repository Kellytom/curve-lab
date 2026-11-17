#!/bin/sh
# Curve-lab browser: a stripped second Chrome, kept light.
#
# It opens one local page, workbench/tabs.html, listing only the tabs saved for
# the current focus; clicking one opens it. --save snapshots the tabs you have
# open now. First run, or --default, opens the two focus pages. Quitting it does
# not touch your main Chrome.
#
#   scripts/chrome-curve.command                 # the saved-tabs page, or the default pair
#   scripts/chrome-curve.command --save          # snapshot the open tabs
#   scripts/chrome-curve.command --saved         # open the saved-tabs page (explicit)
#   scripts/chrome-curve.command --default       # the default focus pair
#   scripts/chrome-curve.command book/index.html # one page (bare name)
#
# The snapshot is ~/.config/curve-lab/tabs.json, read and written by
# scripts/tabs.mjs through the light profile's debugging port (9224). A running
# instance started before this change must be relaunched once to expose the port.
#
# Double-click it in Finder, or drag it to the Dock, to relaunch after a reboot.

set -eu

ROOT="/Users/thomaskelly/developer/curve-lab"
PROFILE="${TMPDIR:-/tmp}/chrome-curve"
PORT=8003
BASE="http://127.0.0.1:${PORT}"
DEBUG_PORT=9224
NODE=$(command -v node || echo /usr/local/bin/node)

# The current focus pair: the lab and the book gallery, both on the local server.
DEFAULT_PAGES="workbench/square-frame.html book/index.html"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || { echo "Chrome not found at $CHROME" >&2; exit 1; }

SAVE=0
SAVED=0
DEFAULT=0
HAS_ARGS=0
PAGES=""
for arg in "$@"; do
  case "$arg" in
    --save) SAVE=1 ;;
    --saved) SAVED=1 ;;
    --default) DEFAULT=1 ;;
    --help|-h)
      sed -n '2,19p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    -*) echo "unknown option: $arg (try --help)" >&2; exit 2 ;;
    *) PAGES="$PAGES $arg"; HAS_ARGS=1 ;;
  esac
done

# A snapshot is taken from a running instance; no server or launch is needed.
if [ "$SAVE" = 1 ]; then
  exec "$NODE" "$ROOT/scripts/tabs.mjs" save
fi

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

# 2. Pages: arguments win; then the snapshot; then the default pair.
if [ "$HAS_ARGS" = 0 ]; then
  INDEX=""
  if [ "$SAVED" = 1 ]; then
    INDEX=$("$NODE" "$ROOT/scripts/tabs.mjs" index) || {
      echo "no saved-tabs page; run --save while the light browser is open" >&2
      exit 1
    }
  elif [ "$DEFAULT" = 0 ]; then
    INDEX=$("$NODE" "$ROOT/scripts/tabs.mjs" index 2>/dev/null) || INDEX=""
  fi
  if [ -n "$INDEX" ]; then
    PAGES="file://$INDEX"
  else
    PAGES="$DEFAULT_PAGES"
  fi
fi

set -- # reused for the URL list
for p in $PAGES; do
  case "$p" in
    http://*|https://*|file://*) set -- "$@" "$p" ;;
    *) set -- "$@" "$BASE/${p#/}" ;;
  esac
done

# 3. Launch. A distinct --user-data-dir is what makes this a separate instance
#    with no extensions. Only the chosen tabs are opened; the old session is not
#    restored, because a restored session is heavier than the focus set.
exec "$CHROME" \
  --user-data-dir="$PROFILE" \
  --no-first-run \
  --no-default-browser-check \
  --disable-sync \
  --disable-extensions \
  --disable-background-networking \
  --disable-component-update \
  --remote-debugging-port="$DEBUG_PORT" \
  "$@"
