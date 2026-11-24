// Crossing pairs of a polyline, counted once per segment pair.
//
// The TypeScript twin of `curve_lab/crossings.py`: a uniform grid over the segments, then the
// same strict-orientation test, so the answer is identical to the brute-force loop (the test
// compares them on random polylines).
//
// A pair is (i, j) with j >= i + 2 — adjacent segments share an endpoint by construction — and
// the meeting must be strictly inside both segments, so a vertex where the path merely touches
// does not count. Crossing pairs, not places: a triple point is three pairs.

export type Point = [number, number];

export type CrossingHit = { i: number; j: number; t1: number; t2: number; x: number; y: number };

const meeting = (points: Point[], i: number, j: number): Point | null => {
  const [ax, ay] = points[i];
  const [bx, by] = points[i + 1];
  const [cx, cy] = points[j];
  const [dx, dy] = points[j + 1];
  const denominator = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx);
  if (Math.abs(denominator) < 1e-12) return null;
  const s = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / denominator;
  const u = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / denominator;
  if (!(s > 0 && s < 1 && u > 0 && u < 1)) return null;
  return [ax + (bx - ax) * s, ay + (by - ay) * s];
};

// Every proper crossing, once per segment pair, with the pair's segment indices and the
// meeting point. The parameters are the segments' starts: t1 = i / segments.
export function crossingHits(points: Point[]): CrossingHit[] {
  const clean = points.map(([x, y]) => [Number(x), Number(y)] as Point);
  const segments = clean.length - 1;
  if (segments < 3) return [];

  const xs = clean.map((point) => point[0]);
  const ys = clean.map((point) => point[1]);
  const width = Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)) || 1;
  const cell = width / Math.max(1, Math.sqrt(segments));
  const cellOf = (value: number, low: number): number => Math.floor((value - low) / cell);
  const x0 = Math.min(...xs);
  const y0 = Math.min(...ys);

  const buckets = new Map<string, number[]>();
  for (let i = 0; i < segments; i += 1) {
    const [ax, ay] = clean[i];
    const [bx, by] = clean[i + 1];
    const cx0 = cellOf(Math.min(ax, bx), x0);
    const cx1 = cellOf(Math.max(ax, bx), x0);
    const cy0 = cellOf(Math.min(ay, by), y0);
    const cy1 = cellOf(Math.max(ay, by), y0);
    for (let cx = cx0; cx <= cx1; cx += 1) {
      for (let cy = cy0; cy <= cy1; cy += 1) {
        const key = `${cx},${cy}`;
        const list = buckets.get(key);
        if (list) list.push(i);
        else buckets.set(key, [i]);
      }
    }
  }

  const seen = new Set<string>();
  const hits: CrossingHit[] = [];
  for (const ids of buckets.values()) {
    for (let a = 0; a < ids.length; a += 1) {
      const i = ids[a];
      for (let b = a + 1; b < ids.length; b += 1) {
        const j = ids[b];
        if (j - i < 2) continue;
        const key = `${i},${j}`;
        if (seen.has(key)) continue;
        seen.add(key);
        const point = meeting(clean, i, j);
        if (!point) continue;
        hits.push({
          i, j,
          t1: Math.round((i / segments) * 1e4) / 1e4,
          t2: Math.round((j / segments) * 1e4) / 1e4,
          x: Math.round(point[0] * 1e4) / 1e4,
          y: Math.round(point[1] * 1e4) / 1e4,
        });
      }
    }
  }
  return hits;
}

export function crossingPairs(points: Point[]): number {
  return crossingHits(points).length;
}
