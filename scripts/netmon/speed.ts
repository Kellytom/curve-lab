/**
 * One run of Apple's own capacity test, `networkQuality`.
 *
 * This is the measurement that answers "40 mb to 6": it is the same tool
 * macOS uses in System Settings, run with `-c` for JSON and `-s` so upload and
 * download are timed one after the other instead of competing for the link.
 *
 * Units, measured on 2026-11-27: `dl_throughput` is **bits per second**, so
 * Mbps = value / 1,000,000. The check that settled it: a run read 24,853,812
 * and moved 42.15 MB across en0 in 17.5 s. That is 2.41 MB/s averaged over the
 * whole run including the idle upload phase; 24.85 Mbps is 3.11 MB/s, just
 * above the average, which is what a peak looks like. (The first attempt at
 * this arithmetic read `netstat -ib` wrongly: it prints three en0 rows — link,
 * IPv6, IPv4 — with identical counters, and summing them triples the bytes.)
 *
 * A second check: an 89 Mbit/s run on a link whose transmit rate was 117 Mbit/s
 * is ordinary; the same number read as bytes/s would be 715 Mbit/s, which that
 * radio cannot do.
 */
import { execFile } from "node:child_process";

export type SpeedSample = {
  downMbps: number | null;
  upMbps: number | null;
  /** Apple's responsiveness score: round trips per minute under load. */
  responsiveness: number | null;
  /** Set when networkQuality itself gave up, for example "NSURLErrorDomain/-1001". */
  error: string | null;
  /** How long the whole run took. */
  seconds: number;
  /** The raw values, so a future reader can re-check the unit. */
  raw: { downBitsPerSecond: number | null; upBitsPerSecond: number | null };
};

const BITS_PER_SECOND_TO_MBPS = 1 / 1_000_000;
/** Overridable so the tests can run a fixture through the real code path. */
const BINARY = process.env.NETMON_NETWORKQUALITY ?? "/usr/bin/networkQuality";

export function parseNetworkQuality(text: string): SpeedSample {
  let raw: Record<string, unknown>;
  try {
    raw = JSON.parse(text) as Record<string, unknown>;
  } catch {
    return {
      downMbps: null,
      upMbps: null,
      responsiveness: null,
      error: "unparseable networkQuality output",
      seconds: 0,
      raw: { downBitsPerSecond: null, upBitsPerSecond: null },
    };
  }

  const number = (value: unknown): number | null =>
    typeof value === "number" && Number.isFinite(value) ? value : null;

  const down = number(raw.dl_throughput);
  const up = number(raw.ul_throughput);
  const responsiveness =
    number(raw.responsiveness) ?? number(raw.dl_responsiveness) ?? number(raw.ul_responsiveness);

  const code = number(raw.error_code);
  const domain = typeof raw.error_domain === "string" ? raw.error_domain : "error";
  const error = code !== null && code !== 0 ? `${domain}/${code}` : null;

  const round = (value: number | null): number | null =>
    value === null ? null : Math.round(value * BITS_PER_SECOND_TO_MBPS * 10) / 10;

  return {
    downMbps: round(down),
    upMbps: round(up),
    responsiveness,
    error,
    seconds: 0,
    raw: { downBitsPerSecond: down, upBitsPerSecond: up },
  };
}

/** Never rejects: a failed test is a sample with an `error`, not a crash. */
export function runNetworkQuality(timeoutMs = 240_000): Promise<SpeedSample> {
  const started = performance.now();
  return new Promise((resolve) => {
    execFile(
      BINARY,
      ["-s", "-c"],
      { timeout: timeoutMs, maxBuffer: 8 << 20 },
      (error, stdout) => {
        const seconds = Math.round(performance.now() - started) / 1000;
        const sample = parseNetworkQuality(stdout ?? "");
        if (error && !sample.error) {
          sample.error = error.killed ? `killed after ${timeoutMs} ms` : error.message;
        }
        resolve({ ...sample, seconds });
      },
    );
  });
}
