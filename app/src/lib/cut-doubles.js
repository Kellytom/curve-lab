// Cutting a double-wonk at its cusp.
//
// The doubles are wonk curves cut where they cross y = x and mirrored back, so each one carries
// a seam of cusps: the tangent arrives and leaves in nearly opposite directions. Some of those
// shapes read as an animal or a person (the operator, 2026-11-23: "too anthropomorphic or
// zoomorphic. many of them i want to cut at the big blue dot").
//
// A cut at a cusp splits the closed path into two open arcs. The long one is the figure; the
// short one is the lobe the cusp closes, and dropping it is the cut. Nothing here is a curve
// family: the kept arcs are the stored points, in order, and the plate says sampled.

// The plate's own cusp rule, on the source stations (before any smoothing): the angle between
// the station before and after turns by more than 165 degrees.
export const CUSP_ANGLE = 165;

export function cuspsOf(points) {
  const out = [];
  for (let i = 1; i < points.length - 1; i += 1) {
    const a = points[i - 1], b = points[i], c = points[i + 1];
    const v1 = [b[0] - a[0], b[1] - a[1]];
    const v2 = [c[0] - b[0], c[1] - b[1]];
    const l1 = Math.hypot(v1[0], v1[1]) || 1;
    const l2 = Math.hypot(v2[0], v2[1]) || 1;
    const dot = (v1[0] * v2[0] + v1[1] * v2[1]) / (l1 * l2);
    const angle = (Math.acos(Math.max(-1, Math.min(1, dot))) * 180) / Math.PI;
    if (angle > CUSP_ANGLE) out.push({ index: i, point: [b[0], b[1]], angle });
  }
  return out;
}

const arcLength = (points) => {
  let total = 0;
  for (let i = 1; i < points.length; i += 1) {
    total += Math.hypot(points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]);
  }
  return total;
};

// The two arcs a cusp index separates, with the cusp station kept at both ends so the cut
// point is on both pieces and the readout can name it.
export function arcsAt(points, index) {
  const at = Math.max(1, Math.min(points.length - 2, Number(index)));
  const head = points.slice(0, at + 1);
  const tail = points.slice(at);
  return { head, tail, headLength: arcLength(head), tailLength: arcLength(tail) };
}

// Which arc to keep: "long" drops the lobe the cusp closes; "short" is offered because the
// operator may want the other side of the same dot.
export function cutAt(points, index, keep = "long") {
  const arcs = arcsAt(points, index);
  const long = arcs.headLength >= arcs.tailLength;
  const chosen = keep === "short" ? !long : long;
  const kept = chosen ? arcs.head : arcs.tail;
  const dropped = chosen ? arcs.tail : arcs.head;
  return {
    points: kept,
    dropped,
    cusp: points[Math.max(1, Math.min(points.length - 2, Number(index)))],
    keptLength: chosen ? arcs.headLength : arcs.tailLength,
    droppedLength: chosen ? arcs.tailLength : arcs.headLength,
  };
}

// Which cut the form asks for, and the runs it keeps. `dot` is the operator's cut: at a
// numbered blue dot, on the stored points. The line cut is the other mode; it must never be
// what a dot choice shows — the operator, 2026-11-23: "does not cut at the dotted line. it
// cuts at 1 and 2 the blue dots, remember? algorithmically, not looking at the plot and
// cutting it in half."
export function previewCut(points, mode = "dot", cuspIndex = 0, keep = "long") {
  if (mode === "top" || mode === "bottom") {
    const runs = lineRuns(points, mode);
    return { mode, side: mode, runs, cusps: cuspsOf(points),
             kept: null, dropped: null, angle: null, cusp: null };
  }
  const cusps = cuspsOf(points);
  const cusp = cusps[Number(cuspIndex) || 0];
  if (!cusp) return { mode: "dot", runs: [], cusps, kept: null, dropped: null,
                      angle: null, cusp: null };
  const cut = cutAt(points, cusp.index, keep);
  return {
    mode: "dot", runs: [cut.points], cusps,
    cusp: Number(cuspIndex) || 0, angle: cusp.angle,
    kept: cut.keptLength, dropped: cut.droppedLength,
  };
}

// The record's own turn, exactly as the plate applies it: the desk turns clockwise on screen,
// so the model turns the other way. Kept here as a function so the check can compare it with
// the plate's `turn`; a desk that draws the stored points unturned is 45 degrees off for the
// doubles, which is how the operator saw it (2026-11-23).
export function turnPoints(points, degrees) {
  if (!degrees) return points;
  const a = (-degrees * Math.PI) / 180;
  const c = Math.cos(a), s = Math.sin(a);
  return points.map(([x, y]) => [x * c - y * s, x * s + y * c]);
}

// The horizontal cut: the line through the middle of the drawn curve, and the runs it
// separates. The operator, 2026-11-23: "add a line and two more curves cut from the original:
// the top half and the bottom half ... as curves not closed shapes." A side may hold more than
// one run (a tulip has two petals above its line), so the answer is a list of open runs, not
// one closed shape and not one long path with chords.
export function lineY(points) {
  const ys = points.map((point) => point[1]);
  return (Math.min(...ys) + Math.max(...ys)) / 2;
}

export function lineRuns(points, side = "top", at = lineY(points)) {
  const runs = [];
  let run = [points[0]];
  for (let i = 1; i < points.length; i += 1) {
    const a = points[i - 1], b = points[i];
    const da = a[1] - at, db = b[1] - at;
    if ((da >= 0) !== (db >= 0) && da !== db) {
      const t = da / (da - db);
      const crossing = [a[0] + (b[0] - a[0]) * t, at];
      run.push(crossing);
      runs.push(run);
      run = [crossing, b];
    } else {
      run.push(b);
    }
  }
  runs.push(run);

  const keep = side === "bottom" ? -1 : 1;
  return runs
    .map((pointsOfRun) => ({
      points: pointsOfRun,
      length: arcLength(pointsOfRun),
      mean: pointsOfRun.reduce((sum, point) => sum + point[1], 0) / pointsOfRun.length,
    }))
    .filter((entry) => keep * (entry.mean - at) >= -1e-9 && entry.points.length > 2)
    .sort((a, b) => b.length - a.length)
    .map((entry) => entry.points);
}

// points to cut. The uid list is derived from the data, never typed.
export function doublesOf(curves) {
  return (curves || []).filter((curve) =>
    /^double-/i.test(curve.name || "") && Array.isArray(curve.path) && curve.path.length > 3);
}
