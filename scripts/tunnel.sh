#!/bin/sh
# curve-lab tunnel: one stable hostname for the Astro app, from Cloudflare.
#
#   scripts/tunnel.sh start    # run the tunnel in the background
#   scripts/tunnel.sh stop     # stop it
#   scripts/tunnel.sh status    # is it up, and does the hostname answer?
#   scripts/tunnel.sh log       # the last 40 lines
#
# The tunnel itself is created once, by hand; docs/TUNNEL.md walks through it.
# The app is NOT started here — start it first (`cd app && npm run dev`) or the
# tunnel has nothing to serve.

set -eu

NAME="${TUNNEL_NAME:-curve-lab}"
CF="${CLOUDFLARED:-$HOME/bin/cloudflared}"
CONFIG="${TUNNEL_CONFIG:-$HOME/.cloudflared/config.yml}"
LOG="${TUNNEL_LOG:-/tmp/curve-lab-tunnel.log}"

if [ ! -x "$CF" ]; then
  echo "cloudflared not found at $CF (set CLOUDFLARED=... to point at it)" >&2
  exit 1
fi
if [ ! -f "$CONFIG" ]; then
  echo "no config at $CONFIG — see docs/TUNNEL.md, one-time setup" >&2
  exit 1
fi

hostname() {
  # The first hostname in the ingress list.
  sed -n 's/^[[:space:]]*-[[:space:]]*hostname:[[:space:]]*//p' "$CONFIG" | head -1
}

running() {
  pgrep -f "cloudflared.*tunnel.*run.*$NAME" >/dev/null 2>&1
}

case "${1:-status}" in
  start)
    if running; then
      echo "already running (pid $(pgrep -f "cloudflared.*tunnel.*run.*$NAME" | head -1))"
      exit 0
    fi
    echo "starting $NAME; log → $LOG"
    nohup "$CF" tunnel --config "$CONFIG" run "$NAME" >>"$LOG" 2>&1 &
    sleep 3
    if running; then
      echo "up: https://$(hostname)"
    else
      echo "failed to start; last lines:" >&2
      tail -20 "$LOG" >&2
      exit 1
    fi
    ;;
  stop)
    if running; then
      pkill -f "cloudflared.*tunnel.*run.*$NAME"
      echo "stopped"
    else
      echo "not running"
    fi
    ;;
  status)
    if running; then
      echo "running (pid $(pgrep -f "cloudflared.*tunnel.*run.*$NAME" | head -1))"
    else
      echo "not running"
    fi
    if [ -n "$(hostname)" ]; then
      code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 8 "https://$(hostname)" || echo 000)
      echo "https://$(hostname) → $code"
      [ "$code" = "200" ] || echo "  (000/5xx: the app may be down, or the Mac asleep)"
    fi
    ;;
  log)
    tail -40 "$LOG"
    ;;
  *)
    echo "use: $0 start|stop|status|log" >&2
    exit 2
    ;;
esac
