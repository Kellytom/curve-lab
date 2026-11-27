/**
 * One speed test, now, by hand.
 *
 *   ~/node24/bin/node scripts/netmon/sample.ts
 *
 * The daemon already does this at start-up, every six hours and 15 s into a
 * drop. This is for the moment the operator wants a reading without waiting for
 * one of those. It writes the same row, with `reason: "manual"`.
 */
import { appendJsonl, writeJson } from "./log.ts";
import { readLink } from "./link.ts";
import { runNetworkQuality } from "./speed.ts";
import { STATE_FILE, SPEED_LOG } from "./paths.ts";
import { readFileSync } from "node:fs";

const sample = await runNetworkQuality();
const link = await readLink();
const ts = Date.now();

appendJsonl(SPEED_LOG, { ts, type: "speed", reason: "manual", ...sample, link });

let previous: Record<string, unknown> = {};
try {
  previous = JSON.parse(readFileSync(STATE_FILE, "utf8"));
} catch {
  // the daemon may not have written it yet
}
writeJson(STATE_FILE, { ...previous, updated: ts, lastSpeedAt: ts, lastSpeedDown: sample.downMbps, link });

const down = sample.downMbps === null ? "—" : `${sample.downMbps.toFixed(1)} Mbit/s`;
const up = sample.upMbps === null ? "—" : `${sample.upMbps.toFixed(1)} Mbit/s`;
const where = link.ssid ? `${link.ssid}, ch ${String(link.channel ?? "—").split(",")[0]}, ${link.rssi ?? "—"} dBm` : "link unknown";
console.log(`down ${down}, up ${up}, ${sample.seconds} s, ${where}${sample.error ? ` (ended early: ${sample.error})` : ""}`);
