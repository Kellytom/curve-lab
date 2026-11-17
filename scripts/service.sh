#!/bin/sh
# Run the Astro app and the tunnel as login services, so they start at login,
# restart when they fall over, and do not belong to any one terminal session.
#
#   scripts/service.sh install     # write two LaunchAgents, start both
#   scripts/service.sh status      # loaded? running? what URL?
#   scripts/service.sh url         # the current phone URL (also copies it)
#   scripts/service.sh restart app # kick the app only (the phone URL survives)
#   scripts/service.sh restart tunnel   # new tunnel, new URL
#   scripts/service.sh restart     # kick both
#   scripts/service.sh uninstall   # stop and remove the agents
#
# Logs: /tmp/curve-lab-app.log and /tmp/curve-lab-tunnel.log (cleared on reboot).
# The tunnel is the QUICK kind: it needs no domain, and its URL changes when the
# tunnel process restarts. A named tunnel (docs/TUNNEL.md) replaces the tunnel
# agent later and gives one permanent hostname.

set -eu

REPO="/Users/thomaskelly/developer/curve-lab"
APP="$REPO/app"
CF="${CLOUDFLARED:-$HOME/bin/cloudflared}"
AGENTS="$HOME/Library/LaunchAgents"
APP_LABEL="com.curvelab.app"
TUNNEL_LABEL="com.curvelab.tunnel"
APP_PLIST="$AGENTS/$APP_LABEL.plist"
TUNNEL_PLIST="$AGENTS/$TUNNEL_LABEL.plist"
APP_LOG="/tmp/curve-lab-app.log"
TUNNEL_LOG="/tmp/curve-lab-tunnel.log"
UID_NUM=$(id -u)
DOMAIN="gui/$UID_NUM"

app_plist() {
  cat <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$APP_LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/npm</string><string>run</string><string>dev</string>
    <string>--</string><string>--host</string>
  </array>
  <key>WorkingDirectory</key><string>$APP</string>
  <key>EnvironmentVariables</key><dict>
    <key>PATH</key><string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>CURVE_LAB_ROOT</key><string>$REPO</string>
    <key>HOME</key><string>$HOME</string>
  </dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ThrottleInterval</key><integer>10</integer>
  <key>StandardOutPath</key><string>$APP_LOG</string>
  <key>StandardErrorPath</key><string>$APP_LOG</string>
</dict></plist>
PLIST
}

tunnel_plist() {
  cat <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$TUNNEL_LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$CF</string><string>tunnel</string><string>--url</string>
    <string>http://localhost:4321</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ThrottleInterval</key><integer>10</integer>
  <key>StandardOutPath</key><string>$TUNNEL_LOG</string>
  <key>StandardErrorPath</key><string>$TUNNEL_LOG</string>
</dict></plist>
PLIST
}

loaded() {
  launchctl print "$DOMAIN/$1" >/dev/null 2>&1
}

quick_url() {
  # The newest quick-tunnel address in the log.
  grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' "$TUNNEL_LOG" 2>/dev/null | tail -1
}

start_one() {
  label="$1"; plist="$2"
  launchctl bootout "$DOMAIN/$label" >/dev/null 2>&1 || true
  launchctl bootstrap "$DOMAIN" "$plist"
  launchctl enable "$DOMAIN/$label" >/dev/null 2>&1 || true
}

stop_one() {
  label="$1"
  launchctl bootout "$DOMAIN/$label" >/dev/null 2>&1 || true
}

case "${1:-status}" in
  install)
    [ -x "$CF" ] || { echo "cloudflared missing at $CF" >&2; exit 1; }
    mkdir -p "$AGENTS"
    : >"$APP_LOG"; : >"$TUNNEL_LOG"
    app_plist >"$APP_PLIST"
    tunnel_plist >"$TUNNEL_PLIST"
    start_one "$APP_LABEL" "$APP_PLIST"
    start_one "$TUNNEL_LABEL" "$TUNNEL_PLIST"
    echo "installed: $APP_LABEL, $TUNNEL_LABEL"
    sleep 10
    exec "$0" status
    ;;
  uninstall)
    stop_one "$APP_LABEL"
    stop_one "$TUNNEL_LABEL"
    rm -f "$APP_PLIST" "$TUNNEL_PLIST"
    echo "removed both agents and their plists"
    ;;
  restart)
    case "${2:-all}" in
      app)    targets="$APP_LABEL" ;;
      tunnel) targets="$TUNNEL_LABEL" ;;
      all)    targets="$APP_LABEL $TUNNEL_LABEL" ;;
      *)      echo "use: $0 restart [app|tunnel|all]" >&2; exit 2 ;;
    esac
    for label in $targets; do
      if loaded "$label"; then
        launchctl kickstart -k "$DOMAIN/$label"
        echo "restarted $label"
      else
        echo "$label is not installed; run $0 install" >&2
      fi
    done
    sleep 8
    exec "$0" status
    ;;
  url)
    found=$(quick_url)
    if [ -z "$found" ]; then
      echo "no quick-tunnel URL in $TUNNEL_LOG yet; try $0 status" >&2
      exit 1
    fi
    printf '%s' "$found" | pbcopy 2>/dev/null || true
    echo "$found   (copied)"
    ;;
  status)
    for pair in "$APP_LABEL:app" "$TUNNEL_LABEL:tunnel"; do
      label=${pair%%:*}; name=${pair##*:}
      if loaded "$label"; then
        state=$(launchctl print "$DOMAIN/$label" | awk '/state =/{print $3; exit}')
        pid=$(launchctl print "$DOMAIN/$label" | awk '/pid =/{print $3; exit}')
        echo "$name: loaded, state ${state:-?}, pid ${pid:-none}"
      else
        echo "$name: not loaded"
      fi
    done
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://localhost:4321/ || true)
    echo "local  http://localhost:4321 → ${code:-000}"
    found=$(quick_url)
    if [ -n "$found" ]; then
      host=${found#https://}
      remote=$(curl -s -o /dev/null -w '%{http_code}' --max-time 12 "$found/" || true)
      echo "phone  $found → ${remote:-000}"
      if [ "${remote:-000}" != "200" ]; then
        # A name looked up before Cloudflare created it is negatively cached by
        # this Mac, so curl says "could not resolve" while the tunnel is fine.
        # Pin the address to tell those two apart.
        ip=$(host "$host" 2>/dev/null | awk '/has address/{print $4; exit}')
        if [ -n "$ip" ]; then
          pinned=$(curl -s -o /dev/null -w '%{http_code}' --max-time 12 \
            --resolve "$host:443:$ip" "$found/" || true)
          if [ "${pinned:-000}" = "200" ]; then
            echo "       tunnel is healthy ($ip answers 200)."
            echo "       this Mac's DNS cache is stale; the phone will resolve it."
            echo "       to clear it here: sudo killall -HUP mDNSResponder"
          else
            echo "       (502: app not up yet; 530/1033: tunnel not connected)"
          fi
        else
          echo "       (502: app not up yet; 530/1033: tunnel not connected)"
        fi
      fi
    fi
    ;;
  log)
    echo "--- app ---"; tail -20 "$APP_LOG"
    echo "--- tunnel ---"; tail -20 "$TUNNEL_LOG"
    ;;
  *)
    echo "use: $0 install|status|url|restart [app|tunnel|all]|uninstall|log" >&2
    exit 2
    ;;
esac
