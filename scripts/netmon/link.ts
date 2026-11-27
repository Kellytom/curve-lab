/**
 * The Wi-Fi link as the Mac reports it: signal, noise, rate and channel.
 *
 * `airport -I` is the one built-in command that answers this on macOS 12
 * without sudo. On a mesh or extender network the channel changes when the Mac
 * moves to another access point, so the channel is what a drop is grouped by.
 */
import { execFile } from "node:child_process";

const AIRPORT =
  "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport";

export type LinkState = {
  ssid: string | null;
  /** Blank on some drivers; kept so a machine that reports it gets it logged. */
  bssid: string | null;
  /** Signal strength in dBm; -55 is good, -80 is weak. */
  rssi: number | null;
  /** Noise floor in dBm. */
  noise: number | null;
  /** Last transmit rate in Mbit/s. */
  txRate: number | null;
  /** For example "149,80": channel 149, 80 MHz wide. */
  channel: string | null;
};

export const NO_LINK: LinkState = {
  ssid: null,
  bssid: null,
  rssi: null,
  noise: null,
  txRate: null,
  channel: null,
};

export function parseAirport(text: string): LinkState {
  const fields = new Map<string, string>();
  for (const line of text.split("\n")) {
    const at = line.indexOf(":");
    if (at < 0) continue;
    fields.set(line.slice(0, at).trim(), line.slice(at + 1).trim());
  }

  const asNumber = (key: string): number | null => {
    const raw = fields.get(key);
    if (!raw) return null;
    const value = Number(raw);
    return Number.isFinite(value) ? value : null;
  };
  const asText = (key: string): string | null => fields.get(key) || null;

  return {
    ssid: asText("SSID"),
    bssid: asText("BSSID"),
    rssi: asNumber("agrCtlRSSI"),
    noise: asNumber("agrCtlNoise"),
    txRate: asNumber("lastTxRate"),
    channel: asText("channel"),
  };
}

/** Never throws: a missing or slow airport leaves the link fields empty. */
export function readLink(timeoutMs = 3000): Promise<LinkState> {
  return new Promise((resolve) => {
    execFile(AIRPORT, ["-I"], { timeout: timeoutMs }, (error, stdout) => {
      if (error || !stdout) return resolve({ ...NO_LINK });
      resolve(parseAirport(stdout));
    });
  });
}
