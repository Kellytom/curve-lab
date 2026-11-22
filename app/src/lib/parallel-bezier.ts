// Fitted cubic-Bézier parallel rails, after Levien's parallel Béziers.
//
// TypeScript port of `curve_lab/parallel_bezier.py`. The exact offset of a
// cubic Bézier is an analytic curve of degree ten — not tractable to work
// with. Levien's 2022 method fits a cubic-Bézier chain to the true parallel
// and subdivides until the error is acceptable. This module is the house
// implementation of that option, not a line-by-line port of the article's
// area/moment solver:
//
// - sample the exact normal offset of each source cubic;
// - fit a cubic chain with the house adaptive fitter (`bezier.ts`);
// - report the maximum error against the dense exact offset;
// - flag the intervals where |d · kappa| >= 1, where the rail folds.
//
// Reference: Raph Levien, "Parallel curves of cubic Béziers", 2022-09-09.
// Output is cubic Bézier spans (p0, c1, c2, p3, s0, s1), SVG-friendly, and
// comparable directly with the exact PH rail. It is always a fitted option;
// never call it exact.

import { cubicAt, fitInterval, spanError, type Point, type Span } from "./bezier.ts";

export interface SourceSpan { p0: Point; c1: Point; c2: Point; p3: Point }

function cubicDeriv(span: SourceSpan, t: number): Point {
  const u = 1.0 - t;
  const [x0, y0] = span.p0, [x1, y1] = span.c1;
  const [x2, y2] = span.c2, [x3, y3] = span.p3;
  const a = 3.0 * u * u, b = 6.0 * u * t, c = 3.0 * t * t;
  return [a * (x1 - x0) + b * (x2 - x1) + c * (x3 - x2),
          a * (y1 - y0) + b * (y2 - y1) + c * (y3 - y2)];
}

function cubicCurvature(span: SourceSpan, t: number): number {
  const [dx, dy] = cubicDeriv(span, t);
  const u = 1.0 - t;
  const [x0, y0] = span.p0, [x1, y1] = span.c1;
  const [x2, y2] = span.c2, [x3, y3] = span.p3;
  const ddx = 6.0 * u * (x2 - 2.0 * x1 + x0) + 6.0 * t * (x3 - 2.0 * x2 + x1);
  const ddy = 6.0 * u * (y2 - 2.0 * y1 + y0) + 6.0 * t * (y3 - 2.0 * y2 + y1);
  const den = (dx * dx + dy * dy) ** 1.5;
  if (den < 1e-15) return 0.0;
  return (dx * ddy - dy * ddx) / den;
}

/** The exact normal offset of the source cubic at t: left normal. */
export function offsetPoint(span: SourceSpan, t: number, distance: number): Point {
  const [x, y] = cubicAt(span as Span, t);
  const [dx, dy] = cubicDeriv(span, t);
  const length = Math.hypot(dx, dy);
  if (length < 1e-15) return [x, y];
  return [x - distance * dy / length, y + distance * dx / length];
}

export function offsetTangent(span: SourceSpan, t: number): number {
  const [dx, dy] = cubicDeriv(span, t);
  return Math.atan2(dy, dx);
}

export function cuspRanges(span: SourceSpan, distance: number, steps = 96):
  Array<[number, number]> {
  const out: Array<[number, number]> = [];
  let opened: number | null = null;
  for (let i = 0; i <= steps; i += 1) {
    const t = i / steps;
    const folded = Math.abs(distance * cubicCurvature(span, t)) >= 1.0;
    if (folded && opened === null) opened = t;
    else if (!folded && opened !== null) { out.push([opened, t]); opened = null; }
  }
  if (opened !== null) out.push([opened, 1.0]);
  return out;
}

/** Fit a cubic chain to an exact offset given as point/tangent callables —
 * opened up so a source that is not a cubic (a degree-7 PH curve, say) can be
 * fitted from its exact offset instead of from a cubic approximation of the
 * source. */
export function fitOffset(point: (t: number) => Point, tangent: (t: number) => number,
                          tol = 0.01, maxSpans = 64) {
  const fitted = fitInterval(0.0, 1.0, point, tangent, tol, maxSpans);
  const errors = fitted.map((span) => spanError(span as Span, point));
  return {
    spans: fitted,
    error_max: errors.length ? Math.max(...errors) : 0.0,
    clamped: fitted.filter((span) => span.clamped).length,
  };
}

/** Fit one source cubic's normal offset with a cubic chain. */
export function fitSpanOffset(span: SourceSpan, distance: number, tol = 0.01, maxSpans = 64) {
  const fitted = fitOffset(
    (t) => offsetPoint(span, t, distance),
    (t) => offsetTangent(span, t),
    tol, maxSpans);
  return { ...fitted, cusps: cuspRanges(span, distance) };
}

/** Fit a cubic chain's normal offset; one source span at a time. Returns all
 * fitted spans, the worst error, the cusp intervals (source-span index plus
 * t range), and the clamped count. */
export function fitChainOffset(spans: SourceSpan[], distance: number, tol = 0.01, maxSpans = 64) {
  const allSpans: Span[] = [];
  let error = 0.0, clamped = 0;
  const cusps: Array<{ span: number; ranges: Array<[number, number]> }> = [];
  spans.forEach((span, index) => {
    const item = fitSpanOffset(span, distance, tol, maxSpans);
    allSpans.push(...item.spans);
    error = Math.max(error, item.error_max);
    clamped += item.clamped;
    if (item.cusps.length) cusps.push({ span: index, ranges: item.cusps });
  });
  return { spans: allSpans, error_max: error, cusps, clamped, tol };
}
