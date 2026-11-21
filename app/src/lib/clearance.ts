// Clearance and crossings: does the ink keep its distance?
//
// TypeScript port of `curve_lab/clearance.py` — the rule: two strokes keep at
// least `clearance` between their edges and cross nowhere except at a contact
// the caller declares. Two engineering decisions carry over unchanged:
//
// **Flattening has a bound.** A cubic becomes a polyline within `tol` of the
// curve, so a measured minimum can be up to 2·tol smaller than the true one;
// a gap inside that band is a *warning*, and a failure is claimed only below
// `clearance - 2*tol`.
//
// **Instances own their ink.** Groups are compared by `instance`, so a
// ribbon's own two rails are never measured against each other.

export type Point = [number, number];

export interface Span { p0: Point; c1: Point; c2: Point; p3: Point }
export interface Group { name: string; instance: string; role: string; spans: Span[] }
export interface Contact {
  point: Point;
  radius: number;
  waivesClearance: boolean;
  allows: (point: Point, a: string, b: string) => boolean;
}

const EPS = 1e-12;

function mid(p: Point, q: Point): Point {
  return [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2];
}

/** De Casteljau split at t = 0.5, returning the two halves as spans. */
export function split(span: Span): [Span, Span] {
  const { p0, c1, c2, p3 } = span;
  const m01 = mid(p0, c1), m12 = mid(c1, c2), m23 = mid(c2, p3);
  const a = mid(m01, m12), b = mid(m12, m23);
  const centre = mid(a, b);
  return [
    { p0, c1: m01, c2: a, p3: centre },
    { p0: centre, c1: b, c2: m23, p3 },
  ];
}

/** How far the control points stray from the chord: a conservative bound. */
export function flatness(span: Span): number {
  const { p0, c1, c2, p3 } = span;
  const dx = p3[0] - p0[0], dy = p3[1] - p0[1];
  const chord = Math.hypot(dx, dy);
  if (chord <= EPS) {
    return Math.max(Math.hypot(p0[0] - c1[0], p0[1] - c1[1]),
                    Math.hypot(p0[0] - c2[0], p0[1] - c2[1]),
                    Math.hypot(p0[0] - p3[0], p0[1] - p3[1]));
  }
  let worst = 0.0;
  for (const point of [c1, c2]) {
    const cross = Math.abs(dx * (point[1] - p0[1]) - dy * (point[0] - p0[0]));
    worst = Math.max(worst, cross / chord);
  }
  return worst;
}

/** A polyline within `tol` of the curve, as points in design space. */
export function flatten(spans: Span[], tol = 0.05, maxDepth = 18): Point[] {
  if (tol <= 0) throw new Error("flattening tolerance must be positive");
  if (!spans.length) return [];
  const points: Point[] = [[...spans[0].p0] as Point];
  const stack: Array<[Span, number]> = [];
  for (let i = spans.length - 1; i >= 0; i -= 1) stack.push([spans[i], 0]);
  while (stack.length) {
    const [span, depth] = stack.pop()!;
    if (depth >= maxDepth || flatness(span) <= tol) {
      points.push([...span.p3] as Point);
    } else {
      const [left, right] = split(span);
      stack.push([right, depth + 1]);
      stack.push([left, depth + 1]);
    }
  }
  return points;
}

function dot(ax: number, ay: number, bx: number, by: number): number {
  return ax * bx + ay * by;
}

const dist = (p: Point, q: Point) => Math.hypot(p[0] - q[0], p[1] - q[1]);

/** Closest points between two segments, as (distance, pointA, pointB) —
 * Ericson, *Real-Time Collision Detection* §5.1.9, with parallel and
 * degenerate segments handled explicitly. */
export function segmentDistance(p1: Point, q1: Point, p2: Point, q2: Point):
  [number, Point, Point] {
  const d1x = q1[0] - p1[0], d1y = q1[1] - p1[1];
  const d2x = q2[0] - p2[0], d2y = q2[1] - p2[1];
  const rx = p1[0] - p2[0], ry = p1[1] - p2[1];
  const a = dot(d1x, d1y, d1x, d1y);
  const e = dot(d2x, d2y, d2x, d2y);
  const f = dot(d2x, d2y, rx, ry);
  let s = 0.0, t = 0.0;
  if (a <= EPS && e <= EPS) {
    s = 0.0; t = 0.0;
  } else if (a <= EPS) {
    s = 0.0;
    t = Math.min(1.0, Math.max(0.0, f / e));
  } else {
    const c = dot(d1x, d1y, rx, ry);
    if (e <= EPS) {
      t = 0.0;
      s = Math.min(1.0, Math.max(0.0, -c / a));
    } else {
      const b = dot(d1x, d1y, d2x, d2y);
      const denom = a * e - b * b;
      s = denom <= EPS ? 0.0 : Math.min(1.0, Math.max(0.0, (b * f - c * e) / denom));
      t = (b * s + f) / e;
      if (t < 0.0) {
        t = 0.0;
        s = Math.min(1.0, Math.max(0.0, -c / a));
      } else if (t > 1.0) {
        t = 1.0;
        s = Math.min(1.0, Math.max(0.0, (b - c) / a));
      }
    }
  }
  const pa: Point = [p1[0] + d1x * s, p1[1] + d1y * s];
  const pb: Point = [p2[0] + d2x * t, p2[1] + d2y * t];
  return [dist(pa, pb), pa, pb];
}

/** The intersection point of two segments, or null. */
export function segmentHit(p1: Point, q1: Point, p2: Point, q2: Point, eps = 1e-9): Point | null {
  const r: Point = [q1[0] - p1[0], q1[1] - p1[1]];
  const s: Point = [q2[0] - p2[0], q2[1] - p2[1]];
  const denom = r[0] * s[1] - r[1] * s[0];
  const qp: Point = [p2[0] - p1[0], p2[1] - p1[1]];
  if (Math.abs(denom) <= eps) {
    if (Math.abs(qp[0] * r[1] - qp[1] * r[0]) > eps) return null;
    const rr = dot(r[0], r[1], r[0], r[1]);
    if (rr <= eps) return null;
    const t0 = dot(qp[0], qp[1], r[0], r[1]) / rr;
    const t1 = t0 + dot(s[0], s[1], r[0], r[1]) / rr;
    const lo = Math.max(0.0, Math.min(t0, t1)), hi = Math.min(1.0, Math.max(t0, t1));
    if (hi < lo - eps) return null;
    const t = (lo + hi) / 2.0;
    return [p1[0] + r[0] * t, p1[1] + r[1] * t];
  }
  const t = (qp[0] * s[1] - qp[1] * s[0]) / denom;
  const u = (qp[0] * r[1] - qp[1] * r[0]) / denom;
  if (-eps <= t && t <= 1 + eps && -eps <= u && u <= 1 + eps) {
    return [p1[0] + r[0] * t, p1[1] + r[1] * t];
  }
  return null;
}

/** Lower bound on the gap between two boxes, for cheap rejection. */
export function bboxGap(a: [number, number, number, number], b: [number, number, number, number]): number {
  const dx = Math.max(0.0, b[0] - a[2], a[0] - b[2]);
  const dy = Math.max(0.0, b[1] - a[3], a[1] - b[3]);
  return Math.hypot(dx, dy);
}

export class Ink {
  readonly instance: string;
  readonly segments: Array<[Point, Point, string]> = [];
  readonly points: Point[] = [];

  constructor(instance: string) { this.instance = instance; }

  add(group: Group, tol: number): void {
    const points = flatten(group.spans, tol);
    this.points.push(...points);
    for (let i = 0; i + 1 < points.length; i += 1) {
      if (dist(points[i], points[i + 1]) > EPS) {
        this.segments.push([points[i], points[i + 1], group.name]);
      }
    }
  }

  get bbox(): [number, number, number, number] {
    const xs = this.points.map((p) => p[0]);
    const ys = this.points.map((p) => p[1]);
    return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
  }

  gap(other: Ink): [number, Point, Point, string] {
    let best: [number, Point, Point, string] = [Infinity, [0, 0], [0, 0], ""];
    for (const [a0, a1, name] of this.segments) {
      for (const [b0, b1] of other.segments) {
        const [distance, pa, pb] = segmentDistance(a0, a1, b0, b1);
        if (distance < best[0]) best = [distance, pa, pb, name];
      }
    }
    return best;
  }

  near(point: Point, radius: number): boolean {
    return this.segments.some(([a0, a1]) => segmentDistance(a0, a1, point, point)[0] <= radius);
  }

  crossings(other: Ink): Array<[Point, string]> {
    const hits: Array<[Point, string]> = [];
    for (const [a0, a1, name] of this.segments) {
      for (const [b0, b1] of other.segments) {
        const hit = segmentHit(a0, a1, b0, b1);
        if (hit !== null) hits.push([hit, name]);
      }
    }
    return hits;
  }
}

export function instances(groups: Group[], tol: number,
                          roles: string[] = ["rail", "cap"]): Record<string, Ink> {
  const ink: Record<string, Ink> = {};
  for (const group of groups) {
    if (!roles.includes(group.role)) continue;
    const key = group.instance || "";
    if (!ink[key]) ink[key] = new Ink(key);
    ink[key].add(group, tol);
  }
  const kept: Record<string, Ink> = {};
  for (const [name, item] of Object.entries(ink)) if (item.segments.length) kept[name] = item;
  return kept;
}

export function measure(groups: Group[], clearance = 5.0, tol = 0.05,
                        contacts: Contact[] = [], roles: string[] = ["rail", "cap"]) {
  if (clearance <= 0) throw new Error("clearance must be positive");
  if (tol <= 0) throw new Error("tolerance must be positive");
  const ink = instances(groups, tol, roles);
  const names = Object.keys(ink);
  const margin = 2.0 * tol;
  const violations: any[] = [], warnings: any[] = [], crossings: any[] = [], merged: any[] = [];
  let best: any = null;
  for (let i = 0; i < names.length; i += 1) {
    const aName = names[i], a = ink[aName];
    for (const bName of names.slice(i + 1)) {
      const b = ink[bName];
      const [distance, pa, pb, group] = a.gap(b);
      const at: Point = [(pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2];
      const entry = { distance, a: aName, b: bName, group, at };
      if (best === null || distance < best.distance) {
        best = { distance, a: aName, b: bName, group, at };
      }
      if (distance < clearance - margin) {
        if (contacts.some((c) => c.waivesClearance && c.allows(c.point, aName, bName)
            && a.near(c.point, c.radius) && b.near(c.point, c.radius))) {
          (entry as any).merged = true;
          merged.push(entry);
        } else {
          (entry as any).shortfall = clearance - margin - distance;
          violations.push(entry);
        }
      } else if (distance < clearance + margin) {
        warnings.push(entry);
      }
      if (bboxGap(a.bbox, b.bbox) > 1e-9) continue;
      for (const [point, name] of a.crossings(b)) {
        const allowed = contacts.some((c) => c.allows(point, aName, bName));
        crossings.push({ at: point, a: aName, b: bName, group: name, allowed });
      }
    }
  }
  const disallowed = crossings.filter((c) => !c.allowed);
  return {
    ok: !violations.length && !disallowed.length,
    clearance, tolerance: tol, margin,
    min: best, violations, warnings, crossings, disallowed, merged,
  };
}
