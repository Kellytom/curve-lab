#!/bin/sh
# Every address this app answers on, right now. The LAN address changes with the DHCP
# lease; the app itself needs no change, because every link is relative.
PORT="${PORT:-4321}"
HOSTS=$(ifconfig 2>/dev/null | awk '/inet /{print $2}' | grep -v '^127\.')
printf 'localhost   http://127.0.0.1:%s/\n' "$PORT"
for host in $HOSTS; do
  printf 'network     http://%s:%s/\n' "$host" "$PORT"
done
