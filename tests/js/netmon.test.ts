/**
 * The monitor's parsers and roll-ups. No network is touched: the fixtures are
 * one good and one failed `networkQuality -c` run, and the Wi-Fi text is the
 * real `airport -I` output from this Mac (BSSID blank, as the driver reports it).
 */
import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import { parseAirport } from "../../scripts/netmon/link.ts";
import { parseNetworkQuality } from "../../scripts/netmon/speed.ts";
import { duration, pairDrops, speedsAround, stats } from "../../scripts/netmon/analysis.ts";

const fixture = (name: string): string =>
  readFileSync(new URL(`../fixtures/netmon/${name}`, import.meta.url), "utf8");

test("a good networkQuality run reports downlink in Mbit/s from bits per second", () => {
  const sample = parseNetworkQuality(fixture("good.json"));
  // 39,800,000 bits/s = 39.8 Mbit/s; 11,500,000 = 11.5.
  assert.equal(sample.downMbps, 39.8);
  assert.equal(sample.upMbps, 11.5);
  assert.equal(sample.responsiveness, 812);
  assert.equal(sample.error, null);
  assert.equal(sample.raw.downBitsPerSecond, 39800000);
});

test("1,000,000 bits per second is 1 Mbit/s, never 8 Mbit/s", () => {
  // The unit guard. On 2026-11-27 the first reading of `netstat -ib` summed
  // three en0 rows (link, IPv6, IPv4) that carry the same counters, tripling
  // the bytes, and the field briefly looked like bytes/s. The corrected run —
  // 42.15 MB in 17.5 s = 2.41 MB/s average — matches a 24.85 Mbit/s peak, so
  // the reader divides by 1e6 and must not multiply by 8.
  const sample = parseNetworkQuality(JSON.stringify({ dl_throughput: 1_000_000 }));
  assert.equal(sample.downMbps, 1);
});

test("a failed run keeps its rate and names Apple's error", () => {
  const sample = parseNetworkQuality(fixture("failed.json"));
  assert.equal(sample.error, "NSURLErrorDomain/-1001");
  // 1,117,305 bits/s: the 6 Mbit/s link had already fallen when the run gave up.
  assert.equal(sample.downMbps, 1.1);
  assert.equal(sample.upMbps, 0);
  assert.equal(sample.responsiveness, 27);
});

test("unreadable output is a sample with an error, not a crash", () => {
  const sample = parseNetworkQuality("not json");
  assert.match(String(sample.error), /unparseable/);
  assert.equal(sample.downMbps, null);
});

test("airport -I text gives signal, channel and rate, and a blank BSSID is null", () => {
  const text = [
    "     agrCtlRSSI: -53",
    "    agrCtlNoise: -90",
    "          state: running",
    "     lastTxRate: 867",
    "          BSSID:",
    "           SSID: NETGEAR",
    "        channel: 149,80",
  ].join("\n");
  const link = parseAirport(text);
  assert.equal(link.rssi, -53);
  assert.equal(link.noise, -90);
  assert.equal(link.txRate, 867);
  assert.equal(link.ssid, "NETGEAR");
  assert.equal(link.bssid, null);
  assert.equal(link.channel, "149,80");
});

test("drops pair start with end, an open drop stays open, and order does not matter", () => {
  const drops = pairDrops([
    { ts: 300, type: "drop-end" },
    { ts: 100, type: "drop-start", error: "ENOTFOUND" },
    { ts: 400, type: "drop-start", error: "ETIMEDOUT" },
  ]);
  assert.equal(drops.length, 2);
  assert.deepEqual(drops[0], { start: 100, end: 300, error: "ENOTFOUND" });
  assert.deepEqual(drops[1], { start: 400, end: null, error: "ETIMEDOUT" });
});

test("stats give median, p10, lowest and highest", () => {
  const found = stats([40, 6, 39, 41, 10]);
  assert.equal(found?.count, 5);
  assert.equal(found?.median, 39);
  assert.equal(found?.min, 6);
  assert.equal(found?.max, 41);
  assert.equal(stats([]), null);
});

test("the nearest speed sample before and after a drop is found inside the window", () => {
  const samples = [
    { ts: 100, downMbps: 40 },
    { ts: 900, downMbps: 6 },
    { ts: 5000, downMbps: 41 },
  ];
  const around = speedsAround(samples, 1000, 2000);
  assert.equal(around.before?.downMbps, 6);
  assert.equal(around.after, null);
  assert.equal(speedsAround(samples, 4000, 2000).after?.downMbps, 41);
});

test("durations read as seconds, minutes and hours", () => {
  assert.equal(duration(42), "42 s");
  assert.equal(duration(380), "6 min 20 s");
  assert.equal(duration(3900), "1 h 05 min");
});

test("sample.ts runs, writes one speed row, and keeps the state it found", () => {
  // End to end through the manual path, with a fake networkQuality so the test
  // never touches the network. It also proves the file is valid TypeScript that
  // Node can run — `node --check` does not strip types, so this is the check.
  const dir = mkdtempSync(path.join(tmpdir(), "netmon-"));
  const fake = path.join(dir, "networkQuality");
  writeFileSync(fake, `#!/bin/sh\ncat <<'EOF'\n${fixture("good.json")}\nEOF\n`, { mode: 0o755 });
  writeFileSync(path.join(dir, "state.json"), JSON.stringify({ reachable: true, lastSpeedDown: 1 }));

  const sampleScript = fileURLToPath(new URL("../../scripts/netmon/sample.ts", import.meta.url));
  const result = spawnSync(process.execPath, [sampleScript], {
    env: { ...process.env, NETMON_DIR: dir, NETMON_NETWORKQUALITY: fake },
    encoding: "utf8",
    timeout: 20_000,
  });

  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /down 39\.8 Mbit\/s/);

  const rows = readFileSync(path.join(dir, "speed.jsonl"), "utf8").trim().split("\n").map((line) => JSON.parse(line));
  assert.equal(rows.length, 1);
  assert.equal(rows[0].reason, "manual");
  assert.equal(rows[0].downMbps, 39.8);

  const state = JSON.parse(readFileSync(path.join(dir, "state.json"), "utf8"));
  assert.equal(state.reachable, true, "the daemon's reachability survives a manual sample");
  assert.equal(state.lastSpeedDown, 39.8);
});
