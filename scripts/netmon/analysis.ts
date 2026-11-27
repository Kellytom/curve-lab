/**
 * The arithmetic the report does, kept apart from the printing so a test can
 * call it without a terminal or a log file.
 */

export type Drop = {
  start: number;
  /** null means the drop had not ended when the window closed. */
  end: number | null;
  error: string | null;
};

export type SpeedRow = {
  ts: number;
  downMbps?: number | null;
  upMbps?: number | null;
  error?: string | null;
  link?: { ssid?: string | null; channel?: string | null; rssi?: number | null } | null;
};

export function pairDrops(events: Record<string, any>[]): Drop[] {
  const drops: Drop[] = [];
  const ordered = [...events].sort((a, b) => Number(a.ts) - Number(b.ts));
  for (const event of ordered) {
    if (event.type === "drop-start") {
      drops.push({ start: Number(event.ts), end: null, error: event.error ?? null });
      continue;
    }
    if (event.type === "drop-end") {
      const open = [...drops].reverse().find((drop) => drop.end === null);
      if (open) open.end = Number(event.ts);
    }
  }
  return drops;
}

export function stats(values: number[]): { count: number; median: number; p10: number; min: number; max: number } | null {
  const sorted = values.filter((value) => Number.isFinite(value)).sort((a, b) => a - b);
  if (sorted.length === 0) return null;
  const at = (share: number): number => sorted[Math.min(sorted.length - 1, Math.floor(share * (sorted.length - 1)))];
  return {
    count: sorted.length,
    median: at(0.5),
    p10: at(0.1),
    min: sorted[0],
    max: sorted[sorted.length - 1],
  };
}

export function speedsAround(
  samples: SpeedRow[],
  ts: number,
  withinMs = 30 * 60_000,
): { before: SpeedRow | null; after: SpeedRow | null } {
  let before: SpeedRow | null = null;
  let after: SpeedRow | null = null;
  for (const sample of samples) {
    if (sample.ts <= ts && ts - sample.ts <= withinMs) {
      if (before === null || sample.ts > before.ts) before = sample;
    }
    if (sample.ts >= ts && sample.ts - ts <= withinMs) {
      if (after === null || sample.ts < after.ts) after = sample;
    }
  }
  return { before, after };
}

/** "42 s", "6 min 20 s", "1 h 05 min" — a duration a reader can parse at a glance. */
export function duration(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)} s`;
  const minutes = Math.floor(seconds / 60);
  const rest = Math.round(seconds % 60);
  if (minutes < 60) return rest ? `${minutes} min ${rest} s` : `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  return `${hours} h ${String(minutes % 60).padStart(2, "0")} min`;
}
