// The tunnel's current quick address, read from the log cloudflared writes.
//
// A quick tunnel takes a new name each time its process starts, so the address
// is not a setting: it is whatever the running process last announced. Parsing
// the log keeps one source — the process itself — and lets the hub print it.

import { existsSync, readFileSync, statSync } from "node:fs";
import { networkInterfaces } from "node:os";

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

// The LAN addresses this Mac answers on, so a phone at home has a way in that
// does not depend on the tunnel's name surviving a restart.
export function lanUrls(port = 4321) {
  const urls = [];
  for (const [name, addresses] of Object.entries(networkInterfaces())) {
    if (name.startsWith("lo") || name.startsWith("utun") || name.startsWith("awdl")) continue;
    for (const address of addresses || []) {
      if (address.family === "IPv4" && !address.internal) {
        urls.push(`http://${address.address}:${port}`);
      }
    }
  }
  return urls;
}
