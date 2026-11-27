// Candidates posted from Inkscape's round trip.
//
// A posted variant is a desk row whose record names the curve it came from in `base_uid`.
// It is not a registry curve until it is promoted, so the tune page cannot find it by uid;
// it finds it here, by that parent link, and shows it beside the spine's own variants
// (state/SCToDo-int.md, Immediate queue row 2).
//
// The row's data is the payload `inkscape/ph_variant.py` builds: the baked speed rows, the
// exact transform, and `candidate: true`. Nothing is inferred from the uid: `base_uid` is
// the only link, and a row without it is not a candidate of anything.

export type DeskRow = { name: string; data: string };

export type Candidate = {
  uid: string;
  name: string;
  baseUid: string;
  origin: string;
  variant: string;
  savedAt: string | null;
  rows: { speedX: number[]; speedY: number[] };
  transform: { degrees: number; exact: boolean } | null;
};

export function parseDeskRow(row: DeskRow): Record<string, unknown> {
  try {
    const data = JSON.parse(row.data);
    return data && typeof data === "object" ? (data as Record<string, unknown>) : {};
  } catch {
    return {};
  }
}

const numbers = (value: unknown): number[] =>
  Array.isArray(value) ? value.filter((item): item is number => typeof item === "number") : [];

const text = (value: unknown): string => (typeof value === "string" ? value : "");

// Every posted candidate whose parent is `spineUid`. A row that has become a registry record
// is dropped: it is listed as a curve from this spine, not twice.
export function candidatesFor(
  rows: DeskRow[],
  spineUid: string,
  recordUids: Iterable<string> = [],
): Candidate[] {
  const taken = new Set(recordUids);
  const found: Candidate[] = [];
  for (const row of rows) {
    const data = parseDeskRow(row);
    if (text(data.base_uid) !== spineUid) continue;
    if (taken.has(row.name)) continue;
    const speedX = numbers(data.speedX);
    const speedY = numbers(data.speedY);
    if (!speedX.length || speedX.length !== speedY.length) continue;
    const transform = data.transform && typeof data.transform === "object"
      ? (data.transform as Record<string, unknown>)
      : null;
    found.push({
      uid: row.name,
      name: text(data.curveName) || text(data.name) || row.name,
      baseUid: spineUid,
      origin: text(data.origin) || text(data.source) || "sandbox",
      variant: text(data.variant),
      savedAt: text(data.savedAt) || null,
      rows: { speedX, speedY },
      transform: transform
        ? { degrees: Number(transform.degrees) || 0, exact: transform.exact === true }
        : null,
    });
  }
  return found.sort((a, b) => a.uid.localeCompare(b.uid));
}
