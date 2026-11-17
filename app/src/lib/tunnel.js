// The tunnel's current quick address, read from the log cloudflared writes.
//
// A quick tunnel takes a new name each time its process starts, so the address
// is not a setting: it is whatever the running process last announced. Parsing
// the log keeps one source — the process itself — and lets the hub print it.

import { existsSync, readFileSync, statSync } from "node:fs";

export const TUNNEL_LOG = "/tmp/curve-lab-tunnel.log";
const QUICK = /https:\/\/[a-z0-9-]+\.trycloudflare\.com/g;

// The last address in the log wins: a restarted tunnel appends a new banner.
export function latestTunnelUrl(text) {
  if (!text) return null;
  const found = text.match(QUICK);
  return found ? found[found.length - 1] : null;
}

export function tunnelInfo(logPath = TUNNEL_LOG) {
  if (!existsSync(logPath)) return { url: null, logPath, updated: null };
  try {
    const url = latestTunnelUrl(readFileSync(logPath, "utf8"));
    return { url, logPath, updated: statSync(logPath).mtime };
  } catch {
    return { url: null, logPath, updated: null };
  }
}
