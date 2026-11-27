/**
 * What happened to the internet, in plain text.
 *
 *   node scripts/netmon/report.ts            last 24 hours
 *   node scripts/netmon/report.ts --hours 72 --under 15
 *
 * It answers one question at a time: did the link lose capacity, or did the
 * link keep its capacity and the name look-up / provider fail above it?
 */
import { readJsonl } from "./log.ts";
import { EVENT_LOG, PROBE_LOG, SPEED_LOG, STATE_FILE } from "./paths.ts";
import { duration, pairDrops, speedsAround, stats, type SpeedRow } from "./analysis.ts";
import { readFileSync } from "node:fs";

const argv = process.argv.slice(2);
function option(name: string, fallback: number): number {
  const at = argv.indexOf(name);
  if (at >= 0 && argv[at + 1]) {
    const value = Number(argv[at + 1]);
    if (Number.isFinite(value)) return value;
  }
  return fallback;
}

const hours = option("--hours", 24);
const under = option("--under", 20);
const limit = option("--limit", 12);
const since = Date.now() - hours * 3600_000;

function pad(value: string | number, width: number): string {
  return String(value).padStart(width);
}

function clock(ts: number): string {
  const date = new Date(ts);
  const two = (value: number): string => String(value).padStart(2, "0");
  return `${two(date.getHours())}:${two(date.getMinutes())}:${two(date.getSeconds())}`;
}

function dayClock(ts: number): string {
  const date = new Date(ts);
  return `${date.getMonth() + 1}/${date.getDate()} ${clock(ts)}`;
}

function mbps(value: number | null | undefined): string {
  return typeof value === "number" ? value.toFixed(1) : "—";
}

function linkLabel(link: SpeedRow["link"]): string {
  if (!link) return "link unknown";
  const ssid = link.ssid ?? "—";
  const channel = link.channel ? `ch ${link.channel.split(",")[0]}` : "ch —";
  const rssi = typeof link.rssi === "number" ? `${link.rssi} dBm` : "— dBm";
  return `${ssid} / ${channel} / ${rssi}`;
}

const speeds = readJsonl(SPEED_LOG).filter((row) => row.type === "speed" && Number(row.ts) >= since) as SpeedRow[];
const probes = readJsonl(PROBE_LOG).filter((row) => row.type === "probe" && Number(row.ts) >= since);
// Pairing needs the start of a drop that began before the window, so read the
// whole event file and keep the drops that end inside the window.
const events = readJsonl(EVENT_LOG);
const drops = pairDrops(events).filter((drop) => (drop.end ?? Date.now()) >= since);

console.log(
  `Internet monitor — last ${hours} h (${dayClock(since)} → ${dayClock(Date.now())})`,
);

if (speeds.length === 0 && probes.length === 0) {
  console.log("No samples yet. Is the daemon running?  launchctl list | grep local.netmon");
  process.exit(0);
}

// ---- speed ---------------------------------------------------------------
const down = stats(speeds.map((row) => Number(row.downMbps)).filter((value) => Number.isFinite(value)));
const up = stats(speeds.map((row) => Number(row.upMbps)).filter((value) => Number.isFinite(value)));
const early = speeds.filter((row) => row.error).length;

console.log("");
console.log(`Speed test (Apple networkQuality), ${speeds.length} sample${speeds.length === 1 ? "" : "s"}`);
if (down) {
  console.log(
    `  downlink   median ${down.median.toFixed(1)}   lowest ${down.min.toFixed(1)}   p10 ${down.p10.toFixed(1)}   highest ${down.max.toFixed(1)}   Mbit/s`,
  );
}
if (up) console.log(`  uplink     median ${up.median.toFixed(1)}   lowest ${up.min.toFixed(1)}   Mbit/s`);
console.log(`  ${speeds.length - early} ran to the end; ${early} ended early (the rate reached is kept)`);

const low = speeds.filter((row) => typeof row.downMbps === "number" && row.downMbps < under);
if (low.length > 0) {
  console.log("");
  console.log(`Below ${under} Mbit/s — ${low.length} of ${speeds.length} samples`);
  for (const row of low.slice(0, limit)) {
    const why = row.error ? `  ended early (${row.error})` : "";
    console.log(`  ${clock(row.ts)}   ${pad(mbps(row.downMbps), 5)}   ${linkLabel(row.link)}${why}`);
  }
  if (low.length > limit) console.log(`  … and ${low.length - limit} more`);
}

// ---- opencode reachability ----------------------------------------------
const failed = probes.filter((row) => !row.ok).length;
const lostSeconds = drops.reduce(
  (total, drop) => total + ((drop.end ?? Date.now()) - drop.start) / 1000,
  0,
);

console.log("");
console.log(`OpenCode (opencode.ai): ${probes.length} probes, ${failed} failed, ${drops.length} drop${drops.length === 1 ? "" : "s"}, ${duration(lostSeconds)} lost`);
for (const drop of drops.slice(-limit)) {
  const end = drop.end ?? Date.now();
  const around = speedsAround(speeds, drop.start);
  const before = around.before ? mbps(around.before.downMbps) : "—";
  const after = around.after ? mbps(around.after.downMbps) : "—";
  const state = `${clock(drop.start)} → ${drop.end ? clock(drop.end) : "now"}`;
  console.log(
    `  ${state}  ${pad(duration((end - drop.start) / 1000), 9)}  speed before ${before}, after ${after} Mbit/s   ${drop.error ?? ""}`,
  );
}

// ---- the channel is the repeater evidence --------------------------------
const byNetwork = new Map<string, SpeedRow[]>();
for (const row of speeds) {
  const ssid = row.link?.ssid ?? "?";
  const channel = row.link?.channel ? `ch ${String(row.link.channel).split(",")[0]}` : "ch —";
  const key = `${ssid} · ${channel}`;
  const list = byNetwork.get(key) ?? [];
  list.push(row);
  byNetwork.set(key, list);
}
if (byNetwork.size > 1 || !byNetwork.has("? · ch —")) {
  console.log("");
  console.log("By network and channel (a move between access points changes this key)");
  for (const [key, rows] of [...byNetwork].sort()) {
    const values = rows.map((row) => Number(row.downMbps)).filter((value) => Number.isFinite(value));
    const found = stats(values);
    if (!found) continue;
    console.log(
      `  ${key.padEnd(28)} ${pad(rows.length, 4)} samples   median ${found.median.toFixed(1)}   lowest ${found.min.toFixed(1)}   Mbit/s`,
    );
  }
}

// ---- the Mac changing network is a cause, not a symptom ------------------
const moves = events.filter((row) => row.type === "network-change");
if (moves.length > 0) {
  console.log("");
  console.log(`Network changes: ${moves.length}`);
  for (const move of moves.slice(-limit)) {
    const from = move.from ?? {};
    const to = move.to ?? {};
    const where = (link: Record<string, any>): string =>
      `${link.ssid ?? "?"}${link.channel ? ` ch ${String(link.channel).split(",")[0]}` : ""}`;
    console.log(`  ${clock(move.ts)}   ${where(from)} → ${where(to)}`);
  }
}

// ---- the reading ---------------------------------------------------------
if (drops.length > 0) {
  const withLowSpeed = drops.filter((drop) => {
    const around = speedsAround(speeds, drop.start);
    const values = [around.before?.downMbps, around.after?.downMbps].filter(
      (value): value is number => typeof value === "number",
    );
    return values.some((value) => value < under);
  }).length;

  console.log("");
  if (withLowSpeed >= Math.ceil(drops.length / 2)) {
    console.log(
      `Reading: ${withLowSpeed} of ${drops.length} drops had a speed sample under ${under} Mbit/s within 30 min — the link lost capacity.`,
    );
  } else {
    console.log(
      `Reading: ${drops.length - withLowSpeed} of ${drops.length} drops kept ${under}+ Mbit/s nearby — the failure was above the link (DNS or the provider), not the radio.`,
    );
  }
}

try {
  const state = JSON.parse(readFileSync(STATE_FILE, "utf8"));
  const age = Math.round((Date.now() - Number(state.updated)) / 1000);
  console.log("");
  console.log(
    `Now: ${state.reachable ? "reachable" : "down"}${state.lastSpeedDown ? `, last speed ${mbps(state.lastSpeedDown)} Mbit/s` : ""} (state written ${duration(age)} ago)`,
  );
} catch {
  // no state file yet; the rest of the report still stands
}
