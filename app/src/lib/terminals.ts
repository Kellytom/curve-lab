// How an open ribbon ends: butt, point, arc, round and taper.
//
// TypeScript port of `curve_lab/terminals.py` — the cap vocabulary and the
// geometry that closes a ribbon's cross-section. A terminal is geometry, not a
// stroke hint: it adds the few spans that bridge the rail ends, so the end
// shape survives export to a tool that ignores stroke-linecap. The frame is
// the package's: y up, millimetres, control points in the design plane; the
// SVG writer flips y once, at output.
//
// Cap limit: 120 degrees, a project choice (see junction.md). `butt`, `point`,
// `arc` and `round` are caps; `taper`, `bulb` and `cone` are tapers.

import type { Point } from "./bezier.js";

export const TERMINALS = ["butt", "point", "arc", "round", "taper", "bulb", "cone"] as const;
export type TerminalKind = typeof TERMINALS[number];
export const ARC_RADIUS = 5.0;
export const TAPER_FACTOR = 4.0;

export interface Rail { spans: SpanDict[] }
export interface SpanDict { p0: Point; c1: Point; c2: Point; p3: Point; s0?: number; s1?: number; clamped?: boolean }

export function checkTerminal(kind: string): TerminalKind {
  if (!TERMINALS.includes(kind as TerminalKind)) {
    throw new Error(`unknown terminal ${JSON.stringify(kind)}; expected one of ${TERMINALS.join(", ")}`);
  }
  return kind as TerminalKind;
}

/** How far the end reaches past the rail ends, in millimetres. */
export function terminalExtension(kind: string, width: number): number {
  checkTerminal(kind);
  const half = width / 2.0;
  if (kind === "butt") return 0.0;
  if (kind === "point" || kind === "round") return half;
  if (kind === "arc") {
    const radius = Math.max(ARC_RADIUS, half);
    return radius - Math.sqrt(radius * radius - half * half);
  }
  return TAPER_FACTOR * half;
}

/** The half-width fraction at t: 0 at the tip, ½ at the full-width join. */
export function widthLaw(kind: string): (t: number) => number {
  if (kind === "bulb") return (t) => 0.5 * (t * (3 - 3 * t + t * t) + 12 * t * t * (1 - t) ** 3);
  if (kind === "cone") return (t) => 0.5 * (1 - (1 - t) ** 3);
  throw new Error(`${JSON.stringify(kind)} has no width law`);
}

function unit(dx: number, dy: number): Point {
  const length = Math.hypot(dx, dy);
  if (length < 1e-9) throw new Error("terminal tangent is degenerate");
  return [dx / length, dy / length];
}

/** The rail's end point and the outward unit tangent there. */
export function railEnd(spans: SpanDict[], end: string): [Point, Point] {
  if (end !== "start" && end !== "end") throw new Error(`end must be 'start' or 'end', got ${JSON.stringify(end)}`);
  let span: SpanDict, dx: number, dy: number;
  if (end === "end") {
    span = spans[spans.length - 1];
    const point = span.p3;
    dx = point[0] - span.c2[0]; dy = point[1] - span.c2[1];
    if (Math.hypot(dx, dy) < 1e-9) { dx = point[0] - span.p0[0]; dy = point[1] - span.p0[1]; }
    return [[point[0], point[1]], unit(dx, dy)];
  }
  span = spans[0];
  const point = span.p0;
  dx = point[0] - span.c1[0]; dy = point[1] - span.c1[1];
  if (Math.hypot(dx, dy) < 1e-9) { dx = point[0] - span.p3[0]; dy = point[1] - span.p3[1]; }
  return [[point[0], point[1]], unit(dx, dy)];
}

function asSpan(p0: Point, p3: Point, c1: Point, c2: Point): SpanDict {
  return {
    p0: [p0[0], p0[1]], c1: [c1[0], c1[1]],
    c2: [c2[0], c2[1]], p3: [p3[0], p3[1]],
  };
}

function straight(p0: Point, p3: Point): SpanDict {
  const a: Point = [(p3[0] - p0[0]) / 3.0, (p3[1] - p0[1]) / 3.0];
  return asSpan(p0, p3, [p0[0] + a[0], p0[1] + a[1]], [p3[0] - a[0], p3[1] - a[1]]);
}

/** One cubic whose midpoint sits `sagitta` past the chord and whose ends
 * leave along `outward`, so it joins the rails without a kink. */
function dome(pPos: Point, pNeg: Point, outward: Point, sagitta: number): SpanDict {
  const pull = 4.0 / 3.0 * sagitta;
  const c1: Point = [pPos[0] + outward[0] * pull, pPos[1] + outward[1] * pull];
  const c2: Point = [pNeg[0] + outward[0] * pull, pNeg[1] + outward[1] * pull];
  return asSpan(pPos, pNeg, c1, c2);
}

/** A smooth cubic chain through points, endpoints gently clamped. */
function catmull(points: Point[]): SpanDict[] {
  const pts: Point[] = [points[0], ...points, points[points.length - 1]];
  const spans: SpanDict[] = [];
  for (let i = 1; i + 2 < pts.length; i += 1) {
    const [p0, p1, p2, p3] = [pts[i - 1], pts[i], pts[i + 1], pts[i + 2]];
    const c1: Point = [p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0];
    const c2: Point = [p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0];
    spans.push(asSpan(p1, p2, c1, c2));
  }
  return spans;
}

/** Two rails from the ribbon ends to a point, on a width law. */
function lawSpans(pPos: Point, pNeg: Point, mid: Point, outward: Point,
                  side: Point, half: number, length: number,
                  law: (t: number) => number): SpanDict[] {
  const plus: Point[] = [], minus: Point[] = [];
  const steps = 8;
  for (let i = 0; i <= steps; i += 1) {
    const u = i / steps;
    const centre: Point = [mid[0] + outward[0] * length * u, mid[1] + outward[1] * length * u];
    const width = 2.0 * half * law(1.0 - u);
    plus.push([centre[0] + side[0] * width, centre[1] + side[1] * width]);
    minus.push([centre[0] - side[0] * width, centre[1] - side[1] * width]);
  }
  plus[0] = pPos; minus[0] = pNeg;
  return [...catmull(plus), ...catmull(minus).reverse()];
}

/** Spans that close one ribbon end, running from the +half rail to the −half.
 * `railPos`/`railNeg` are the built rails at ±width/2, so the cap starts on
 * the real rail ends. `butt` returns no spans: the blunt end is the rails
 * stopping. */
export function terminalSpans(railPos: Rail, railNeg: Rail, kind: string,
                              end = "end", radius = ARC_RADIUS,
                              taper = TAPER_FACTOR): SpanDict[] {
  checkTerminal(kind);
  if (kind === "butt") return [];
  const [pPos, tPos] = railEnd(railPos.spans, end);
  const [pNeg, tNeg] = railEnd(railNeg.spans, end);
  const half = Math.hypot(pPos[0] - pNeg[0], pPos[1] - pNeg[1]) / 2.0;
  if (half <= 1e-9) throw new Error("a terminal needs a ribbon with a width");
  const mid: Point = [(pPos[0] + pNeg[0]) / 2.0, (pPos[1] + pNeg[1]) / 2.0];
  const outward = unit(tPos[0] + tNeg[0], tPos[1] + tNeg[1]);

  if (kind === "point") {
    const apex: Point = [mid[0] + outward[0] * half, mid[1] + outward[1] * half];
    return [straight(pPos, apex), straight(apex, pNeg)];
  }
  if (kind === "bulb" || kind === "cone") {
    const length = taper * half;
    const side = unit(pPos[0] - pNeg[0], pPos[1] - pNeg[1]);
    return lawSpans(pPos, pNeg, mid, outward, side, half, length, widthLaw(kind));
  }
  if (kind === "taper") {
    const length = taper * half;
    const apex: Point = [mid[0] + outward[0] * length, mid[1] + outward[1] * length];
    const shoulder = length * 0.5, waist = length * 0.25;
    return [
      asSpan(pPos, apex,
             [pPos[0] + outward[0] * shoulder, pPos[1] + outward[1] * shoulder],
             [apex[0] - outward[0] * waist, apex[1] - outward[1] * waist]),
      asSpan(apex, pNeg,
             [apex[0] - outward[0] * waist, apex[1] - outward[1] * waist],
             [pNeg[0] + outward[0] * shoulder, pNeg[1] + outward[1] * shoulder]),
    ];
  }
  let sagitta: number;
  if (kind === "arc") {
    const r = Math.max(radius, half);
    sagitta = r - Math.sqrt(r * r - half * half);
  } else {
    sagitta = half;  // round: a semicircle, whose radius is the half width
  }
  return [dome(pPos, pNeg, outward, sagitta)];
}

export interface ConeResult {
  spans: SpanDict[];
  tip: Point;
  centres: { pos: Point; neg: Point };
  radius: number;
  half: number;
  outward: Point;
  tangents: { base: Point; tip_pos: Point; tip_neg: Point };
  shift: { pos: number; neg: number };
  axisTwist: number;
}

/** The two-arc cone terminal: R = 2 x the half width, meeting at the tip.
 * NOT the same as kind="cone" (a width law): this is a construction. One
 * circular arc leaves each rail end, both of radius R = 2 x half, each tangent
 * to its rail at the base, and the two meet at a point on the centreline. The
 * two 60-degree turns make 120 degrees - the cap limit, a pointed cone, not a
 * cap. Symmetric mode snaps the rail ends to the centreline and squares the
 * cap's axis; shift and axisTwist say how far each had to move, zero when they
 * were already symmetric. */
export function coneTerminal(railPos: Rail, railNeg: Rail, end = "end",
                             symmetric = false, centre?: Point,
                             tangent?: Point): ConeResult {
  const [pPosBase, tPos0] = railEnd(railPos.spans, end);
  const [pNegBase, tNeg0] = railEnd(railNeg.spans, end);
  const span = Math.hypot(pPosBase[0] - pNegBase[0], pPosBase[1] - pNegBase[1]);
  let half = span / 2.0;
  if (half <= 1e-9) throw new Error("a cone terminal needs a ribbon with a width");
  let mid: Point = [(pPosBase[0] + pNegBase[0]) / 2.0, (pPosBase[1] + pNegBase[1]) / 2.0];
  const outwardBase = unit(tPos0[0] + tNeg0[0], tPos0[1] + tNeg0[1]);
  let side = unit(pPosBase[0] - pNegBase[0], pPosBase[1] - pNegBase[1]);
  const shift = { pos: 0.0, neg: 0.0 };
  if (centre != null) mid = [centre[0], centre[1]];
  let outward = outwardBase;
  const along = outward[0] * side[0] + outward[1] * side[1];
  const squared: Point = [outward[0] - side[0] * along, outward[1] - side[1] * along];
  if (Math.hypot(squared[0], squared[1]) < 1e-12) {
    throw new Error("a cone terminal needs the two rails to leave the same way");
  }
  let axisTwist = Math.abs(90.0 - Math.acos(Math.max(-1.0, Math.min(1.0, Math.abs(along)))) * 180.0 / Math.PI);
  outward = unit(squared[0], squared[1]);
  let pPos: Point = [pPosBase[0], pPosBase[1]];
  let pNeg: Point = [pNegBase[0], pNegBase[1]];
  if (symmetric) {
    if (tangent !== undefined) {
      outward = unit(tangent[0], tangent[1]);
      axisTwist = Math.abs(Math.acos(Math.max(-1.0, Math.min(1.0,
        outwardBase[0] * outward[0] + outwardBase[1] * outward[1]))) * 180.0 / Math.PI);
    }
    side = [-outward[1], outward[0]];
    if (side[0] * (pPos[0] - pNeg[0]) + side[1] * (pPos[1] - pNeg[1]) < 0) {
      side = [outward[1], -outward[0]];
    }
    half = Math.abs((pPos[0] - pNeg[0]) * side[0] + (pPos[1] - pNeg[1]) * side[1]) / 2.0;
    if (half <= 1e-9) throw new Error("a symmetric cone terminal needs a width across its axis");
    const targetPos: Point = [mid[0] + side[0] * half, mid[1] + side[1] * half];
    const targetNeg: Point = [mid[0] - side[0] * half, mid[1] - side[1] * half];
    shift.pos = Math.hypot(pPos[0] - targetPos[0], pPos[1] - targetPos[1]);
    shift.neg = Math.hypot(pNeg[0] - targetNeg[0], pNeg[1] - targetNeg[1]);
    pPos = targetPos;
    pNeg = targetNeg;
  }
  const radius = 2.0 * half;
  const tip: Point = [mid[0] + outward[0] * Math.sqrt(3.0) * half,
                      mid[1] + outward[1] * Math.sqrt(3.0) * half];
  const centrePos: Point = [...pNeg] as Point;
  const centreNeg: Point = [...pPos] as Point;
  const reach = (4.0 / 3.0) * Math.tan(15.0 * Math.PI / 180.0) * radius;
  const arc = (start: Point, finish: Point, at: Point,
               tAtStart: Point, tAtFinish: Point): SpanDict =>
    asSpan(start, finish,
           [start[0] + tAtStart[0] * reach, start[1] + tAtStart[1] * reach],
           [finish[0] - tAtFinish[0] * reach, finish[1] - tAtFinish[1] * reach]);
  const toTipPos = unit(tip[0] - pPos[0], tip[1] - pPos[1]);
  const leaveTip = unit(pNeg[0] - tip[0], pNeg[1] - tip[1]);
  const tangentPos = outward;
  const tangentNeg: Point = [-outward[0], -outward[1]];
  const perpendicularInto = (radiusVector: Point, travelHint: Point): Point => {
    let candidate = unit(-radiusVector[1], radiusVector[0]);
    if (candidate[0] * travelHint[0] + candidate[1] * travelHint[1] < 0) {
      candidate = unit(radiusVector[1], -radiusVector[0]);
    }
    return candidate;
  };
  const tipTangentPos = perpendicularInto([tip[0] - centrePos[0], tip[1] - centrePos[1]], toTipPos);
  const tipTangentNeg = perpendicularInto([tip[0] - centreNeg[0], tip[1] - centreNeg[1]], leaveTip);
  const spans = [
    arc(pPos, tip, centrePos, tangentPos, tipTangentPos),
    arc(tip, pNeg, centreNeg, tipTangentNeg, tangentNeg),
  ];
  return { spans, tip, centres: { pos: centrePos, neg: centreNeg }, radius, half,
           outward, tangents: { base: outward, tip_pos: tipTangentPos, tip_neg: tipTangentNeg },
           shift, axisTwist };
}
