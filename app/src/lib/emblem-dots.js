// The figure desk, dot-plot level: sacred emblems as plotted exact stations.
//
// The operator's direction, 2026-11-23: "make an algorithmic only attempt,
// no cubic beziers. you can just plot the dots… use what you have available
// from the whole repo." So this module only *computes stations* — every one
// an exact rational number, carried as a [numerator, denominator] pair of
// BigInts — and the page plots them with the house figure engine
// (app/src/lib/plot-figure.js). No cubic Bezier is drawn anywhere on the page.
//
// Symmetry rule (the hearts lesson): an emblem is designed as one chain and
// mirrored — reflection across an axis keeps every length, so exactness
// survives the mirror.

function gcd(a, b) {
  while (b) [a, b] = [b, a % b];
  return a < 0n ? -a : a;
}

/** A rational number [num, den], both BigInt, lowest terms, den > 0. */
export function fr(n, d = 1n) {
  if (d === 0n) throw new Error("fraction with denominator 0");
  if (d < 0n) [n, d] = [-n, -d];
  const g = gcd(n, d) || 1n;
  return [n / g, d / g];
}

export const fAdd = (a, b) => fr(a[0] * b[1] + b[0] * a[1], a[1] * b[1]);
export const fSub = (a, b) => fr(a[0] * b[1] - b[0] * a[1], a[1] * b[1]);
export const fMul = (a, b) => fr(a[0] * b[0], a[1] * b[1]);
export const fNeg = (a) => fr(-a[0], a[1]);
export const fDiv = (a, b) => fr(a[0] * b[1], a[1] * b[0]);
export const fNum = (a) => Number(a[0]) / Number(a[1]);

const rat = (x) => (typeof x === "object" ? x : fr(BigInt(x)));
const TWO = fr(2n);

/** A station: a point whose two coordinates are exact rationals. */
const st = (x, y) => ({ x, y });
export const mirrorX = (s) => st(fNeg(s.x), s.y);
export const mirrorY = (s) => st(s.x, fNeg(s.y));

/** Unit circle from the east point: x=(1−t²)/(1+t²), y=2t/(1+t²).
 *  t = [num, den] as raw BigInts; rational t gives rational points,
 *  no trigonometry anywhere. */
export function unitCircle([tn, td]) {
  const x2 = tn * tn;
  const y2 = td * td;
  const denom = x2 + y2;
  return [fr(y2 - x2, denom), fr(2n * tn * td, denom)];
}

/** A full rational ring, all stations rational: the east half for t in
 *  [−1,1] (bottom to top), then its mirror, top back to bottom. */
export function rationalRing(cx, cy, r, n = 24) {
  const R = rat(r);
  const east = [];
  for (let i = -n; i <= n; i += 1) {
    const [ux, uy] = unitCircle([BigInt(i), BigInt(n)]);
    east.push(st(fAdd(rat(cx), fMul(R, ux)), fAdd(rat(cy), fMul(R, uy))));
  }
  const reflect = (s) => st(fSub(fMul(rat(cx), TWO), s.x), s.y);
  return east.concat(east.slice(1, -1).reverse().map(reflect));
}

/** The ichthys: two mirrored parabola arcs.
 *  Upper: y = flare·(1 − (x/nose)²) from the nose x=−nose out past the
 *  crossing at x=+nose to the tail tip; the lower arc is its mirror across
 *  the axis, so both cross exactly at (nose, 0) and the crossed tails come
 *  free. The eye is a single station. */
export function fishStations({ flare = 40, tail = 80, nose = 66, n = 28 } = {}) {
  const upper = [];
  for (let i = 0; i <= n; i += 1) {
    const x = fAdd(rat(-nose), fMul(rat(nose + tail), fr(BigInt(i), BigInt(n))));
    const q = fDiv(x, rat(nose));
    const y = fMul(rat(flare), fSub(fr(1n), fMul(q, q)));
    upper.push(st(x, y));
  }
  return { upper, lower: upper.map(mirrorY), eye: st(fr(-30n), fr(8n)),
           crossing: st(fr(66n), fr(0n)) };
}

/** The heart: two open chains that meet at the two true cusps — the
 *  cleavage at (0, 50) and the point at (0, −62). The right chain is a
 *  rational arc (circle centre (30,50), r=30: west point, over the top, to
 *  the east point) plus a bowed straight side
 *      y = −62 + (28/15)x + (1/300)·x(60−x),
 *  which ends at (60, 50) with slope 31/15, so the point at the bottom is
 *  sharp. The left chain is the mirror. */
export function heartStations({ n = 20, m = 8 } = {}) {
  const C = { x: fr(30n), y: fr(50n) };
  const R = fr(30n);
  const lobe = [];
  for (let i = 0; i <= n; i += 1) {
    const [ux, uy] = unitCircle([BigInt(i), BigInt(n)]);
    // west-based param: x = Cx − r·ux, y = Cy + r·uy  (t: 0 = west, 1 = top)
    lobe.push(st(fSub(C.x, fMul(R, ux)), fAdd(C.y, fMul(R, uy))));
  }
  for (let i = n - 1; i >= 0; i -= 1) {
    const [ux, uy] = unitCircle([BigInt(i), BigInt(n)]);
    // east-based param: x = Cx + r·ux, y = Cy + r·uy  (t: 1 = top, 0 = east)
    lobe.push(st(fAdd(C.x, fMul(R, ux)), fAdd(C.y, fMul(R, uy))));
  }
  const side = [];
  for (let j = 1; j <= m; j += 1) {
    const x = fMul(fr(60n), fSub(fr(1n), fr(BigInt(j), BigInt(m))));
    const term = fMul(x, fSub(fr(60n), x));            // x(60−x)
    const y = fAdd(fAdd(fr(-62n), fMul(x, fr(28n, 15n))), fDiv(term, fr(300n)));
    side.push(st(x, y));
  }
  const right = lobe.concat(side);
  return { right, left: right.map(mirrorX), cusps: [st(fr(0n), fr(50n)), st(fr(0n), fr(-62n))] };
}

/** Straight strokes, dotted: the Latin cross and the chi-rho's stem and X. */
export function segmentStations(x1, y1, x2, y2, n = 8) {
  const out = [];
  for (let i = 0; i <= n; i += 1) {
    const t = fr(BigInt(i), BigInt(n));
    out.push(st(fAdd(rat(x1), fMul(t, fSub(rat(x2), rat(x1)))),
                fAdd(rat(y1), fMul(t, fSub(rat(y2), rat(y1))))));
  }
  return out;
}

export function crossStations() {
  return {
    vertical: segmentStations(0, -80, 0, 90, 10),
    horizontal: segmentStations(-45, 35, 45, 35, 8),
  };
}

export function chiRhoStations(n = 24) {
  return {
    stem: segmentStations(0, -80, 0, 30, 10),
    bowl: rationalRing(0, 52, 26, n),
    xLeft: segmentStations(-26, 26, 26, 78, 6),
    xRight: segmentStations(26, 26, -26, 78, 6),
  };
}

/** The engine plots plain [x, y] floats; this is the only exit from the
 *  exact record, and it is a read, never a write. */
export const toFloat = (stations) => stations.map((s) => [fNum(s.x), fNum(s.y)]);
