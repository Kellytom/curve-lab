// The glue sandbox: a connector between two curves whose end slopes differ.
//
// A cubic with its two inner control points placed along the two end directions cannot have
// the wrong slope: the ends are exact by construction. Slopes are entered as fractions
// ("3/4", "-7/24", "2"), so every direction is a pair of whole numbers, and a handle given as a
// percentage is a fraction with denominator 100. The control points printed are exact fractions;
// the picture is drawn from them in floating point and says so.

const gcd = (a, b) => (b ? gcd(b, a % b) : Math.abs(a));

export function frac(n, d = 1) {
  if (!Number.isFinite(n) || !Number.isFinite(d) || d === 0) return null;
  const sign = d < 0 ? -1 : 1;
  const g = gcd(Math.abs(n), Math.abs(d)) || 1;
  return { n: (sign * n) / g, d: Math.abs(d) / g };
}

export const fracText = (f) => (!f ? "—" : f.d === 1 ? `${f.n}` : `${f.n}/${f.d}`);
export const fracValue = (f) => (f ? f.n / f.d : NaN);

// "3/4" or "-7/24" or "2" -> a reduced fraction
export function parseSlope(text) {
  const clean = String(text || "").trim().replace(/\s+/g, "");
  const match = /^([+-]?\d+)(?:\/([+-]?\d+))?$/.exec(clean);
  if (!match) return null;
  const n = Number(match[1]);
  const d = match[2] === undefined ? 1 : Number(match[2]);
  return d === 0 ? null : frac(n, d);
}

// a slope as a direction pair: slope = rise / run, so the direction is (run, rise)
export function direction(slope) {
  if (!slope) return null;
  return { x: slope.d, y: slope.n };
}

// A direction pair normalised to unit length. When the pair is a p-triple (its hypotenuse is
// whole — 4:3 gives 5, 24:-7 gives 25) the unit direction is rational and exact; otherwise it
// is divided by the squared length and is a float, which the sandbox says.
export function unitDirection(slope) {
  if (!slope) return null;
  const x = slope.d, y = slope.n;
  const l2 = x * x + y * y;
  const root = Math.round(Math.sqrt(l2));
  if (root * root === l2 && root > 0) return { x: x / root, y: y / root, exact: true };
  return { x: x / l2, y: y / l2, exact: false };
}

// exact control points for a G1 cubic join. p0 and p3 are points, h0 and h1 are handle
// lengths as fractions of the chord; returns fractions.
export function controls(p0, p3, slope0, slope1, h0, h1) {
  const d0 = direction(slope0);
  const d1 = direction(slope1);
  if (!d0 || !d1) return null;
  const chord = Math.hypot(p3.x - p0.x, p3.y - p0.y);
  // a handle may be given as a fraction (exact) or a plain number
  const size = (value) => (value && typeof value === "object" ? fracValue(value) : Number(value));
  const H0 = chord * size(h0);
  const H1 = chord * size(h1);
  const u0 = unitDirection(slope0);
  const u1 = unitDirection(slope1);
  return [
    p0,
    { x: p0.x + H0 * u0.x, y: p0.y + H0 * u0.y },
    { x: p3.x - H1 * u1.x, y: p3.y - H1 * u1.y },
    p3,
  ];
}

// the derivative of a cubic at t (Bezier), for checking the ends
export function derivative(p, t) {
  const mt = 1 - t;
  return {
    x: 3 * mt * mt * (p[1].x - p[0].x) + 6 * mt * t * (p[2].x - p[1].x) + 3 * t * t * (p[3].x - p[2].x),
    y: 3 * mt * mt * (p[1].y - p[0].y) + 6 * mt * t * (p[2].y - p[1].y) + 3 * t * t * (p[3].y - p[2].y),
  };
}

// the slope the drawn curve actually leaves with, as a float ratio
export const slopeAt = (p, t) => {
  const d = derivative(p, t);
  return Math.abs(d.x) < 1e-12 ? Infinity : d.y / d.x;
};

export function cubicPoints(p, n = 240) {
  const out = [];
  for (let i = 0; i <= n; i += 1) {
    const t = i / n;
    const mt = 1 - t;
    out.push({
      x: mt ** 3 * p[0].x + 3 * mt ** 2 * t * p[1].x + 3 * mt * t ** 2 * p[2].x + t ** 3 * p[3].x,
      y: mt ** 3 * p[0].y + 3 * mt ** 2 * t * p[1].y + 3 * mt * t ** 2 * p[2].y + t ** 3 * p[3].y,
    });
  }
  return out;
}

// where the cubic crosses itself, if it loops
export function crossings(points) {
  const hits = [];
  const cross = (a, b, c, d) => {
    const rx = b.x - a.x, ry = b.y - a.y;
    const qx = d.x - c.x, qy = d.y - c.y;
    const den = rx * qy - ry * qx;
    if (Math.abs(den) < 1e-12) return null;
    const t = ((c.x - a.x) * qy - (c.y - a.y) * qx) / den;
    const u = ((c.x - a.x) * ry - (c.y - a.y) * rx) / den;
    if (t <= 1e-6 || t >= 1 - 1e-6 || u <= 1e-6 || u >= 1 - 1e-6) return null;
    return { x: a.x + t * rx, y: a.y + t * ry };
  };
  for (let i = 0; i < points.length - 1; i += 2) {
    for (let j = i + 3; j < points.length - 1; j += 2) {
      const hit = cross(points[i], points[i + 1], points[j], points[j + 1]);
      if (hit) hits.push(hit);
    }
  }
  return hits;
}
