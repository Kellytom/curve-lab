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

// The doubles, in the registry's order: a record whose name begins "double-", with stored
// points to cut. The uid list is derived from the data, never typed.
export function doublesOf(curves) {
  return (curves || []).filter((curve) =>
    /^double-/i.test(curve.name || "") && Array.isArray(curve.path) && curve.path.length > 3);
}
