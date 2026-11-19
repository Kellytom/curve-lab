#!/bin/sh
# "Where is my phone": make the phone make a noise, three ways, best first.
#
#   scripts/where-is-my-phone.sh          # uses ~/.config/curve-lab/phone
#   scripts/where-is-my-phone.sh +1...    # an explicit number, for one call
#
# 1. A Shortcuts shortcut named "Where is my Phone" if it exists — that is the
#    proper way: Find My plays a sound on the device.
# 2. Otherwise a short message to the number; a linked iPhone rings.
# 3. Otherwise the browser's Find My page, which is a human step, not a ding.
#
# The number lives in ~/.config/curve-lab/phone (mode 600), never in the repo:
# a personal number in a public repository is a leak waiting to happen.
set -u
NUMBER="${1:-}"
if [ -z "$NUMBER" ]; then
  NUMBER=$(cat "$HOME/.config/curve-lab/phone" 2>/dev/null | tr -d '[:space:]')
fi
if [ -z "$NUMBER" ]; then
  echo "no number: put one in ~/.config/curve-lab/phone, or pass it as the first argument" >&2
  exit 2
fi

if command -v shortcuts >/dev/null 2>&1; then
  if shortcuts list 2>/dev/null | grep -qx "Where is my Phone"; then
    echo "running the Shortcuts shortcut: Where is my Phone"
    shortcuts run "Where is my Phone" && exit 0
    echo "the shortcut failed; trying a message" >&2
  fi
fi

echo "sending a short message to $NUMBER"
osascript <<APPLESCRIPT
tell application "Messages"
  set targetService to 1st account whose service type = iMessage
  set targetBuddy to participant "$NUMBER" of targetService
  send "ding — where is my phone?" to targetBuddy
end tell
APPLESCRIPT
if [ $? -eq 0 ]; then
  echo "sent"
  exit 0
fi

echo "message failed; opening Find My in the browser instead" >&2
open "https://www.icloud.com/find"
