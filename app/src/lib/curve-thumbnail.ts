// The card-sized picture of a curve, from its speed rows — one drawing rule
// for every gallery that shows curves.
//
// The curve is sampled at 33 exact stations (the polynomial integrated from
// the rows, coefficient-wise), joined by Catmull-Rom cubic spans (the house
// rule — never straight segments between stations), and flipped to SVG's
// y-down only here. The stroke is a fraction of the curve's own extent: a
// fixed width fattens a 0.4-unit curve into a blob and thins a 40-unit one.

import { curvePolynomials, evaluate, fr } from "./measure.ts";
import { plainNumber } from "./plain-number.js";
import { catmullRomD } from "./svg.ts";

export function curveThumbnail(
  speedX: Array<number | string>,
  speedY: Array<number | string>,
  height = 130,
): string {
  const { x, y } = curvePolynomials(speedX, speedY);
  const num = (a: { n: bigint; d: bigint }): number => Number(a.n) / Number(a.d);
  const pts: Array<[number, number]> = [];
  for (let k = 0; k <= 32; k += 1) {
    const t = fr(BigInt(k), 32n);
    pts.push([num(evaluate(x, t)), num(evaluate(y, t))]);
  }
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
  for (const [px, py] of pts) {
    x0 = Math.min(x0, px); x1 = Math.max(x1, px);
    y0 = Math.min(y0, py); y1 = Math.max(y1, py);
  }
  const w = x1 - x0 || 1;
  const h = y1 - y0 || 1;
  const pad = Math.max(w, h) * 0.08;
  const flipped: Array<[number, number]> = pts.map(([px, py]) => [px, y1 - py]);
  const d = catmullRomD(flipped, 2);
  const view = `${plainNumber(x0 - pad)} ${plainNumber(-pad)} ${plainNumber(w + 2 * pad)} ${plainNumber(h + 2 * pad)}`;
  const stroke = Math.max(w, h) / 55;
  return `<svg viewBox="${view}" width="100%" height="${height}" preserveAspectRatio="xMidYMid meet" role="img"><path d="${d}" fill="none" stroke="#3b2d1c" stroke-width="${plainNumber(stroke)}" stroke-linecap="round"/></svg>`;
}
