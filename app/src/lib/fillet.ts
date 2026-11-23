// Junctions, starting with the circular fillet.
//
// The port of curve_lab/fillet.py's first half — `corner_fillet` and
// `arc_segment`, the part provable with a ruler. `fillet_span` (the span-level
// fillet) stays in Python for now; it is the next row and is labelled so.
//
// The construction every CAD sketcher uses: for an interior angle θ at the
// corner, the arc touches each edge at T = r / tan(θ/2) from the corner, its
// centre sits on the bisector at r / sin(θ/2), and the arc turns through π − θ.
// It is G1 — curvature steps to 1/r at each touch point — and the report says
// so instead of pretending otherwise. Coordinates: design units, y up.

export type Point = [number, number];

export class FilletError extends Error {}

const EPS = 1e-9;

function unit(dx: number, dy: number): Point {
  const length = Math.hypot(dx, dy);
  if (length <= EPS) {
    throw new FilletError("corner has a zero-length edge");
  }
  return [dx / length, dy / length];
}

export type Span = { p0: Point; c1: Point; c2: Point; p3: Point };

export type Fillet = {
  start: Point;
  end: Point;
  centre: Point;
  radius: number;
  angle: number;
  tangent: number;
  trim: [number, number];
  spans: Span[];
  sweep: number;
  length: number;
};

/** A tangent arc at `corner` between the edges `corner → a` and `corner → c`. */
export function cornerFillet(
  a: Point, corner: Point, c: Point, radius: number, segments = 2,
): Fillet {
  if (!(radius > 0)) {
    throw new FilletError("fillet radius must be positive");
  }
  if (segments < 1) {
    throw new FilletError("a fillet needs at least one span");
  }

  const [cornerX, cornerY] = [Number(corner[0]), Number(corner[1])];
  const ax = a[0] - cornerX;
  const ay = a[1] - cornerY;
  const cx = c[0] - cornerX;
  const cy = c[1] - cornerY;
  const lengthA = Math.hypot(ax, ay);
  const lengthC = Math.hypot(cx, cy);
  const [ux, uy] = unit(ax, ay);
  const [vx, vy] = unit(cx, cy);

  const cosine = Math.max(-1, Math.min(1, ux * vx + uy * vy));
  const angle = Math.acos(cosine);
  if (angle <= 1e-6) {
    throw new FilletError("the edges are collinear; there is no corner to fillet");
  }
  if (angle >= Math.PI - 1e-6) {
    throw new FilletError("the edges double back; a fillet needs an interior angle");
  }

  const tangent = radius / Math.tan(angle / 2);
  if (tangent > Math.min(lengthA, lengthC)) {
    throw new FilletError(
      `radius ${radius} needs ${tangent.toPrecision(3)} along each edge, ` +
        `but the shorter edge is ${Math.min(lengthA, lengthC).toPrecision(3)}`,
    );
  }

  const start: Point = [cornerX + ux * tangent, cornerY + uy * tangent];
  const end: Point = [cornerX + vx * tangent, cornerY + vy * tangent];
  let [bx, by] = [ux + vx, uy + vy];
  if (Math.hypot(bx, by) <= EPS) {
    throw new FilletError("the bisector is undefined for these edges");
  }
  [bx, by] = unit(bx, by);
  const offset = radius / Math.sin(angle / 2);
  const centre: Point = [cornerX + bx * offset, cornerY + by * offset];

  const first = Math.atan2(start[1] - centre[1], start[0] - centre[0]);
  const last = Math.atan2(end[1] - centre[1], end[0] - centre[0]);
  let sweep = last - first;
  while (sweep > Math.PI) sweep -= 2 * Math.PI;
  while (sweep < -Math.PI) sweep += 2 * Math.PI;
  const expected = Math.PI - angle;
  if (Math.abs(Math.abs(sweep) - expected) > 1e-6) {
    // mirror-image corners sweep the other way; take the arc that matches
    sweep = -sweep;
  }

  const step = sweep / segments;
  const spans: Span[] = [];
  for (let index = 0; index < segments; index += 1) {
    const t0 = first + step * index;
    const t1 = t0 + step;
    const p0: Point = [centre[0] + radius * Math.cos(t0), centre[1] + radius * Math.sin(t0)];
    const p3: Point = [centre[0] + radius * Math.cos(t1), centre[1] + radius * Math.sin(t1)];
    const pull = (4 / 3) * Math.tan(step / 4) * radius;
    const c1: Point = [p0[0] - pull * Math.sin(t0), p0[1] + pull * Math.cos(t0)];
    const c2: Point = [p3[0] + pull * Math.sin(t1), p3[1] - pull * Math.cos(t1)];
    spans.push({ p0, c1, c2, p3 });
  }
  spans[0] = { ...spans[0], p0: start };
  spans[spans.length - 1] = { ...spans[spans.length - 1], p3: end };

  return {
    start,
    end,
    centre,
    radius,
    angle,
    tangent,
    trim: [tangent, tangent],
    spans,
    sweep,
    length: radius * expected,
  };
}

/** The fillet as a circular-arc clothoid segment, ready for a Design: kd = 0,
 * curvature ±1/r, length r·|sweep|, anchored at the arc's start tangent. The
 * joins are G1, not G2 — that is the fillet, stated plainly. */
export function arcSegment(fillet: Fillet): {
  anchor: { x: number; y: number; angle: number };
  segment: { kd: number; length: number; kappa0: number };
} {
  const { radius, sweep, start, centre } = fillet;
  if (!(radius > 0) || Math.abs(sweep) <= 0) {
    throw new FilletError("not a fillet");
  }
  const dx = start[0] - centre[0];
  const dy = start[1] - centre[1];
  const sign = sweep > 0 ? 1 : -1;
  const tx = -dy * sign;
  const ty = dx * sign;
  return {
    anchor: { x: start[0], y: start[1], angle: Math.atan2(ty, tx) },
    segment: { kd: 0, length: radius * Math.abs(sweep), kappa0: sign / radius },
  };
}
