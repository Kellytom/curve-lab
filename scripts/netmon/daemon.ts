/**
 * netmon — the always-on monitor.
 *
 * Two jobs, one process:
 *   1. every 10 s, resolve `opencode.ai` and open TCP 443. That is the layer the
 *      operator's "getaddrinfo ENOTFOUND" failure sits in.
 *   2. on a timer (10 min by default), run Apple's `networkQuality` and log the
 *      capacity, responsiveness and the Wi-Fi channel it ran on.
 *
 * It also runs a speed test 15 s into a drop, so a drop has a throughput number
 * beside it instead of only a timestamp. Keeping the two together is the whole
 * point: "the link kept 40 Mbit/s but DNS died" and "the link fell to 6 Mbit/s"
 * are different faults and the report must say which one happened.
 *
 * Every value goes to ~/.local/share/netmon/*.jsonl, outside the repo.
 */
import { execFile } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, unlinkSync, writeFileSync } from "node:fs";
import path from "node:path";
import { appendJsonl, pruneJsonl, readJsonl, writeJson } from "./log.ts";
import { readLink, type LinkState } from "./link.ts";
import { probeHost } from "./probe.ts";
import { runNetworkQuality } from "./speed.ts";
import { EVENT_LOG, LOG_DIR, PROBE_LOG, SPEED_LOG, STATE_FILE } from "./paths.ts";

const PROBE_MS = Number(process.env.NETMON_PROBE_MS ?? 10_000);
// Apple's test is not cheap: one run measured 580 MB (151 down, 430 up) at
// 36/155 Mbit/s on 2026-11-27. A six-hourly baseline plus one test per drop is
// what keeps the daily volume sane; NETMON_SPEED_MS changes it.
const SPEED_MS = Number(process.env.NETMON_SPEED_MS ?? 6 * 3600_000);
const DROP_COOLDOWN_MS = 10 * 60_000;
const HOST = process.env.NETMON_HOST ?? "opencode.ai";
const NOTIFY = process.env.NETMON_NOTIFY !== "0";
const KEEP_DAYS = Number(process.env.NETMON_KEEP_DAYS ?? 30);
const LOCK = path.join(LOG_DIR, "daemon.lock");

let reachable: boolean | null = null;
let dropStartedAt: number | null = null;
let lastOkAt: number | null = null;
let lastLink: LinkState | null = null;
let lastSpeedAt = 0;
let lastSpeedDown: number | null = null;
let speedRunning = false;
let probing = false;
let lastNotifyAt = 0;

function notify(text: string): void {
  if (!NOTIFY) return;
  // A flapping link can cross the line many times a minute; one alert per
  // five minutes is enough to bring the operator to the report.
  if (Date.now() - lastNotifyAt < 5 * 60_000) return;
  lastNotifyAt = Date.now();
  const escaped = text.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
  execFile(
    "/usr/bin/osascript",
    ["-e", `display notification "${escaped}" with title "Internet monitor"`],
    () => {},
  );
}

function writeState(): void {
  writeJson(STATE_FILE, {
    updated: Date.now(),
    pid: process.pid,
    host: HOST,
    reachable,
    lastOkAt,
    dropStartedAt,
    lastSpeedAt: lastSpeedAt || null,
    lastSpeedDown,
  });
}

function takeLock(): boolean {
  try {
    if (existsSync(LOCK)) {
      const pid = Number(readFileSync(LOCK, "utf8").trim());
      if (pid && pid !== process.pid) {
        try {
          process.kill(pid, 0);
          return false; // a live daemon already holds it
        } catch {
          // stale lock: the pid is gone
        }
      }
    }
    writeFileSync(LOCK, String(process.pid));
    return true;
  } catch {
    return true;
  }
}

async function speedTick(reason: "timer" | "start" | "drop"): Promise<void> {
  if (speedRunning) return;
  // A flapping link can start many drops; one measurement every 10 minutes is
  // enough, and each run moves hundreds of megabytes.
  if (reason === "drop" && Date.now() - lastSpeedAt < DROP_COOLDOWN_MS) return;
  speedRunning = true;
  try {
    const sample = await runNetworkQuality();
    const link = await readLink();
    lastSpeedAt = Date.now();
    lastSpeedDown = sample.downMbps;
    appendJsonl(SPEED_LOG, { ts: lastSpeedAt, type: "speed", reason, host: HOST, ...sample, link });
  } catch (error) {
    appendJsonl(EVENT_LOG, { ts: Date.now(), type: "error", where: "speed", error: String(error) });
  } finally {
    speedRunning = false;
    writeState();
  }
}

async function probeTick(): Promise<void> {
  if (probing) return;
  probing = true;
  try {
    const ts = Date.now();
    const [reach, link] = await Promise.all([probeHost(HOST), readLink()]);
    appendJsonl(PROBE_LOG, {
      ts,
      type: "probe",
      ok: reach.ok,
      dnsMs: reach.dnsMs,
      tcpMs: reach.tcpMs,
      address: reach.address,
      error: reach.error,
      link,
    });

    if (lastLink && (lastLink.ssid !== link.ssid || lastLink.channel !== link.channel)) {
      appendJsonl(EVENT_LOG, {
        ts,
        type: "network-change",
        from: { ssid: lastLink.ssid, channel: lastLink.channel, rssi: lastLink.rssi },
        to: { ssid: link.ssid, channel: link.channel, rssi: link.rssi },
      });
    }
    lastLink = link;

    if (reach.ok) {
      lastOkAt = ts;
      if (reachable === false && dropStartedAt !== null) {
        const seconds = (ts - dropStartedAt) / 1000;
        appendJsonl(EVENT_LOG, { ts, type: "drop-end", started: dropStartedAt, seconds, link });
        notify(`OpenCode is reachable again after ${Math.round(seconds)} s`);
        dropStartedAt = null;
      }
      reachable = true;
    } else {
      if (reachable !== false) {
        dropStartedAt = ts;
        appendJsonl(EVENT_LOG, { ts, type: "drop-start", error: reach.error, link });
        notify(`OpenCode unreachable: ${reach.error ?? "probe failed"}`);
        // A single failed lookup is not proof of a drop; measure 15 s in.
        const startedAt = ts;
        setTimeout(() => {
          if (reachable === false && dropStartedAt === startedAt) void speedTick("drop");
        }, 15_000);
      }
      reachable = false;
    }
    writeState();
  } catch (error) {
    appendJsonl(EVENT_LOG, { ts: Date.now(), type: "error", where: "probe", error: String(error) });
  } finally {
    probing = false;
  }
}

async function probeLoop(): Promise<void> {
  await probeTick();
  setTimeout(probeLoop, PROBE_MS);
}

async function speedLoop(): Promise<void> {
  await speedTick("timer");
  setTimeout(speedLoop, SPEED_MS);
}

function prune(): void {
  const before = Date.now() - KEEP_DAYS * 24 * 3600_000;
  for (const file of [PROBE_LOG, SPEED_LOG, EVENT_LOG]) {
    try {
      pruneJsonl(file, before);
    } catch (error) {
      appendJsonl(EVENT_LOG, { ts: Date.now(), type: "error", where: "prune", error: String(error) });
    }
  }
}

function stop(): void {
  appendJsonl(EVENT_LOG, { ts: Date.now(), type: "stop", pid: process.pid });
  try {
    unlinkSync(LOCK);
  } catch {
    // already gone
  }
  process.exit(0);
}

mkdirSync(LOG_DIR, { recursive: true });

if (!takeLock()) {
  process.exit(0);
}

appendJsonl(EVENT_LOG, {
  ts: Date.now(),
  type: "start",
  pid: process.pid,
  host: HOST,
  probeMs: PROBE_MS,
  speedMs: SPEED_MS,
});
writeState();
process.on("SIGTERM", stop);
process.on("SIGINT", stop);

void probeLoop();
// A baseline soon after boot, but not after every crash-restart: if a sample is
// already newer than the baseline interval, the timer will produce the next one.
const recent = readJsonl(SPEED_LOG).some(
  (row) => row.type === "speed" && Date.now() - Number(row.ts) < SPEED_MS,
);
if (!recent) setTimeout(() => void speedTick("start"), 20_000);
setTimeout(speedLoop, SPEED_MS);
prune();
setInterval(prune, 24 * 3600_000);
