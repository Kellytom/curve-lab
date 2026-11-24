// Cutting a curve's legs off at rational fractions of its parameter.
//
// The operator, 2026-11-24: "cutting the legs off the curves using rational fractions of t".
// A stored curve is a list of stations in parameter order; t = 0 is the first station and t = 1
// the last (for a record with branches, each branch has its own 0 … 1, so the same cut applies to
// every branch). The cut is given as two fractions, t0 and t1, typed as p/q; the stations between
// them are kept, the legs outside are dropped, and the two cut points are placed exactly at the
// fractions by interpolating the one segment they fall on.
//
// Nothing here invents a curve: the kept stations are the record's own, and the two new endpoints
// lie on the segment between stations, which the record already says is approximate there.

export class FractionError extends Error {}

const integer = (text) => /^\d+$/.test(String(text).trim());

// "1/4" or "3" — a decimal is refused on purpose: the cut is a rational fraction of t.
export function parseFraction(text) {
  const raw = String(text ?? "").trim();
  if (!raw) throw new FractionError("type a fraction, p/q");
  const parts = raw.split("/");
  if (parts.length > 2 || !parts.every(integer)) {
    throw new FractionError(`${raw} is not a whole-number fraction; write p/q, like 1/4`);
  }
  const p = Number(parts[0]);
  const q = parts.length === 2 ? Number(parts[1]) : 1;
  if (q === 0) throw new FractionError("the denominator cannot be zero");
  if (p > q) throw new FractionError(`${raw} is past the end; t runs from 0 to 1`);
  return { p, q, value: p / q, text: q === 1 ? String(p) : `${p}/${q}` };
}

export function parseRange(fromText, toText) {
  const from = parseFraction(fromText);
  const to = parseFraction(toText);
  if (!(from.value < to.value)) {
    throw new FractionError(`the front cut ${from.text} must come before the back cut ${to.text}`);
  }
  return { from, to };
}

const at = (point, fraction) => point[0] + (point[1] - point[0]) * fraction;

// The segment a fraction falls on, and the exact point there.
function pointAt(points, fraction) {
  const last = points.length - 1;
  const x = fraction * last;
  const i = Math.min(last - 1, Math.floor(x));
  const f = x - i;
  const a = points[i];
  const b = points[i + 1];
  return [at([a[0], b[0]], f), at([a[1], b[1]], f)];
}

// One run: the kept stations with exact endpoints, and the two legs that were dropped.
export function trimRun(points, from, to) {
  if (!Array.isArray(points) || points.length < 2) return null;
  const last = points.length - 1;
  const kept = [];
  for (let i = 0; i <= last; i += 1) {
    const t = i / last;
    if (t > from.value && t < to.value) kept.push([points[i][0], points[i][1]]);
  }
  const start = pointAt(points, from.value);
  const end = pointAt(points, to.value);
  const head = points.slice(0, Math.floor(from.value * last) + 1).map((p) => [p[0], p[1]]);
  head.push(start);
  const tail = [[...end]];
  for (let i = Math.ceil(to.value * last); i <= last; i += 1) tail.push([points[i][0], points[i][1]]);
  return {
    kept: [start, ...kept, end],
    head, tail,
    keptStations: kept.length + 2,
    droppedStations: head.length + tail.length - 2,
  };
}

// The whole record: every branch is trimmed by the same fractions.
export function trimRecord(record, from, to) {
  const branches = Array.isArray(record.branches) && record.branches.length
    ? record.branches
    : [record.path];
  const runs = branches.map((branch) => trimRun(branch, from, to)).filter(Boolean);
  if (!runs.length) return null;
  const kept = runs.map((run) => run.kept);
  return {
    branches: kept,
    path: kept.flat(),
    head: runs.map((run) => run.head).flat(),
    tail: runs.map((run) => run.tail).flat(),
    keptStations: runs.reduce((sum, run) => sum + run.keptStations, 0),
    droppedStations: runs.reduce((sum, run) => sum + run.droppedStations, 0),
  };
}

// The exact point at a fraction on the record's first run, for the readout: the cut lands on a
// rational parameter, and its coordinates are printed from the stored segment, not re-sampled.
export function pointAtFraction(record, fraction) {
  const points = Array.isArray(record.branches) && record.branches.length
    ? record.branches[0] : record.path;
  return points ? pointAt(points, fraction.value) : null;
}
