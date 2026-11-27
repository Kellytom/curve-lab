/**
 * quintic-guides.ts — 100 six-point control curves for the Inkscape work.
 *
 * A quintic Bézier has six control points. This script makes 100 of them from
 * ten families, ten members each, with every coordinate an integer on a
 * 120 × 120 grid so nothing is lost to a decimal.
 *
 *   node scripts/quintic-guides.ts
 *
 * Writes:
 *   workbench/quintic-guides.json    the record: uid, family, the six points
 *   workbench/quintic-guides.svg     a sheet: the control polygon and the curve
 *
 * The model is y-up (the house rule). SVG is y-down, so every y is flipped once,
 * at the point of writing: ySvg = PAPER_HEIGHT − y. The flip is there and only
 * there; nothing else sees a y-down coordinate.
 *
 * The curve is drawn as a cubic chain because SVG has no degree-5 primitive.
 * Each member carries the measured worst deviation of that chain from the true
 * quintic, in grid units, so the drawing never claims more than it shows.
 */

import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";

type Point = [number, number];
type Curve = {
  uid: string;
  group: "math" | "ornament";
  family: string;
  name: string;
  points: Point[];
  note: string;
  fitError: number;
};
type Options = { error: number; spans: number };

const ROOT = path.resolve(import.meta.dirname, "..");
const OUT_JSON = path.join(ROOT, "workbench", "quintic-guides.json");
const OUT_SVG = path.join(ROOT, "workbench", "quintic-guides.svg");
const OUT_PATHS = path.join(ROOT, "workbench", "quintic-guides-paths.svg");
const OUT_ORN_SVG = path.join(ROOT, "workbench", "quintic-guides-ornament.svg");
const OUT_ORN_PATHS = path.join(ROOT, "workbench", "quintic-guides-ornament-paths.svg");

const W = 120;
const H = 120;
const PAPER = 1500;

/* ---------- the maths: Bernstein, de Casteljau, cubic chain ---------- */

const binomial5 = [1, 5, 10, 10, 5, 1];

function bernstein(points: Point[], t: number): Point {
  const u = 1 - t;
  let x = 0;
  let y = 0;
  for (let i = 0; i < 6; i += 1) {
    const w = binomial5[i] * u ** (5 - i) * t ** i;
    x += w * points[i][0];
    y += w * points[i][1];
  }
  return [x, y];
}

/** One sub-curve of a quintic on [0, 1] after splitting at t — exact. */
function splitAt(points: Point[], t: number): [Point[], Point[]] {
  const left: Point[] = [];
  const right: Point[] = [];
  let row: Point[] = points;
  for (let depth = 0; depth < 6; depth += 1) {
    left.push(row[0]);
    right.unshift(row[row.length - 1]);
    const next: Point[] = [];
    for (let i = 0; i < row.length - 1; i += 1) {
      next.push([
        row[i][0] + (row[i + 1][0] - row[i][0]) * t,
        row[i][1] + (row[i + 1][1] - row[i][1]) * t,
      ]);
    }
    row = next;
  }
  return [left, right];
}

/** The cubic Bézier controls from the curve's values at 0, 1/3, 2/3, 1. */
const lagrange = [
  [1, 0, 0, 0],
  [-5 / 6, 3, -3 / 2, 1 / 3],
  [1 / 3, -3 / 2, 3, -5 / 6],
  [0, 0, 0, 1],
];

function cubicThrough(f: (t: number) => Point): Point[] {
  const values = [0, 1 / 3, 2 / 3, 1].map(f);
  const controls: Point[] = [];
  for (let k = 0; k < 4; k += 1) {
    let x = 0;
    let y = 0;
    for (let j = 0; j < 4; j += 1) {
      x += lagrange[k][j] * values[j][0];
      y += lagrange[k][j] * values[j][1];
    }
    controls.push([x, y]);
  }
  return controls;
}

/** The whole quintic as spans cubics, each span exact at four stations. */
function cubicChain(points: Point[], spans: number): Point[][] {
  const out: Point[][] = [];
  for (let s = 0; s < spans; s += 1) {
    const t0 = s / spans;
    const t1 = (s + 1) / spans;
    const piece = subCurve(points, t0, t1);
    out.push(cubicThrough((u) => bernstein(piece, u)));
  }
  return out;
}

/** The exact sub-quintic of `points` over [t0, t1]. */
function subCurve(points: Point[], t0: number, t1: number): Point[] {
  const [, afterStart] = splitAt(points, t0);
  const dt = (t1 - t0) / (1 - t0);
  const [middle] = splitAt(afterStart, dt);
  return middle;
}

function maxError(points: Point[], spans: number, samples = 200): number {
  const chain = cubicChain(points, spans);
  let worst = 0;
  for (let k = 0; k <= samples; k += 1) {
    const t = k / samples;
    const truth = bernstein(points, t);
    const s = Math.min(spans - 1, Math.floor(t * spans));
    const u = t * spans - s;
    const c = chain[s];
    const v = 1 - u;
    let x = 0;
    let y = 0;
    for (let i = 0; i < 4; i += 1) {
      const w = [1, 3, 3, 1][i] * v ** (3 - i) * u ** i;
      x += w * c[i][0];
      y += w * c[i][1];
    }
    worst = Math.max(worst, Math.hypot(x - truth[0], y - truth[1]));
  }
  return worst;
}

/** How many times the drawn curve crosses itself (sampled polyline count). */
function selfCrossings(points: Point[], samples = 240): number {
  const pts = Array.from({ length: samples + 1 }, (_, k) => bernstein(points, k / samples));
  let count = 0;
  const orient = (a: Point, b: Point, c: Point) =>
    Math.sign((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]));
  for (let i = 0; i < pts.length - 1; i += 1) {
    for (let j = i + 2; j < pts.length - 1; j += 1) {
      if (i === 0 && j === pts.length - 2) continue;
      const a = pts[i];
      const b = pts[i + 1];
      const c = pts[j];
      const d = pts[j + 1];
      if (orient(a, b, c) !== orient(a, b, d) && orient(c, d, a) !== orient(c, d, b)) count += 1;
    }
  }
  return count;
}

/* ---------- the hundred curves ---------- */
/* ---------- classic curves, fitted by a quintic ---------- */

type Point5 = (t: number) => Point;

/** Bernstein basis values at t, degree 5. */
function basis(t: number): number[] {
  const u = 1 - t;
  return binomial5.map((c, i) => c * u ** (5 - i) * t ** i);
}

/** Solve a 6×6 system by Gauss-Jordan with partial pivoting. */
function solve6(m: number[][], v: number[]): number[] {
  const a = m.map((row, i) => [...row, v[i]]);
  for (let col = 0; col < 6; col += 1) {
    let piv = col;
    for (let r = col + 1; r < 6; r += 1) if (Math.abs(a[r][col]) > Math.abs(a[piv][col])) piv = r;
    [a[col], a[piv]] = [a[piv], a[col]];
    const d = a[col][col] || 1e-12;
    for (let r = 0; r < 6; r += 1) {
      if (r === col) continue;
      const f = a[r][col] / d;
      for (let c = col; c <= 6; c += 1) a[r][c] -= f * a[col][c];
    }
  }
  return a.map((row, i) => row[6] / (row[i] || 1e-12));
}

/** The least-squares quintic through a sampled classic, rounded to integers. */
function fitQuintic(target: Point5, samples = 41): Point[] {
  const a = Array.from({ length: 6 }, () => new Array<number>(6).fill(0));
  const bx = new Array<number>(6).fill(0);
  const by = new Array<number>(6).fill(0);
  for (let k = 0; k <= samples; k += 1) {
    const b = basis(k / samples);
    const p = target(k / samples);
    for (let i = 0; i < 6; i += 1) {
      bx[i] += b[i] * p[0];
      by[i] += b[i] * p[1];
      for (let j = 0; j < 6; j += 1) a[i][j] += b[i] * b[j];
    }
  }
  const sx = solve6(a, bx);
  const sy = solve6(a, by);
  return sx.map((x, i) => [Math.round(x), Math.round(sy[i])] as Point);
}

/** Worst distance, in grid units, between the fitted quintic and its target. */
function fitError(points: Point[], target: Point5, samples = 200): number {
  let worst = 0;
  for (let k = 0; k <= samples; k += 1) {
    const t = k / samples;
    const p = bernstein(points, t);
    const q = target(t);
    worst = Math.max(worst, Math.hypot(p[0] - q[0], p[1] - q[1]));
  }
  return worst;
}

type Family = {
  family: string;
  name: string;
  note: string;
  group?: "math" | "ornament";
  /** either a classic to fit, or six points already chosen */
  target?: (k: number) => Point5;
  given?: (k: number) => Point[];
};

const families: Family[] = [
  {
    family: "parabola",
    name: "parabola",
    note: "y = 4t(1 − t): the classic arch; a quintic holds a quadratic exactly",
    target: (k) => (t) => [W * t, (40 + 5 * k) * 4 * t * (1 - t)],
  },
  {
    family: "bowl",
    name: "parabola, mirrored",
    note: "the same parabola turned over",
    target: (k) => (t) => [W * t, -(40 + 5 * k) * 4 * t * (1 - t)],
  },
  {
    family: "s-curve",
    name: "cubic S",
    note: "y = (2t − 1)³: one inflection, at the middle",
    target: (k) => (t) => [W * t, (14 + 4 * k) * (2 * t - 1) ** 3],
  },
  {
    family: "c-curve",
    name: "C: half a circle",
    note: "a 180° circular arc opening right; sampled, so fitted and not exact",
    target: (k) => (t) => {
      const r = 34 + 3 * k;
      const th = -Math.PI / 2 + Math.PI * t;
      return [34 + r * Math.cos(th), r * Math.sin(th)];
    },
  },
  {
    family: "hyperbola",
    name: "hyperbola",
    note: "y = a / x on one branch; sampled, so fitted and not exact",
    target: (k) => (t) => {
      const x = 20 + 100 * t;
      return [x, (400 + 80 * k) / x];
    },
  },
  {
    family: "cusp",
    name: "cusp (semicubical parabola)",
    note: "(u², u³) about the midpoint: a sharp cusp in the middle of the cell",
    target: (k) => (t) => {
      const u = 2 * t - 1;
      return [60 + 60 * u * u, (25 + 5 * k) * u ** 3];
    },
  },
  {
    family: "wave",
    name: "sine wave",
    note: "one full period; sampled, so fitted and not exact",
    target: (k) => (t) => [W * t, (10 + 3 * k) * Math.sin(2 * Math.PI * (t - 0.5))],
  },
  {
    family: "loop",
    name: "loop",
    note: "six points chosen so the curve crosses itself once, at about 39°",
    given: (k) => [[0, 0], [95 + 2 * k, 70 + 3 * k], [15, 95 + 3 * k], [10, 5], [90 - 2 * k, -8 - 2 * k], [W, 0]],
  },
  {
    family: "flattened-arch",
    name: "flattened arch",
    note: "y = 1 − (2t − 1)⁴: a quartic arch, flat on top",
    target: (k) => (t) => [W * t, (30 + 4 * k) * (1 - (2 * t - 1) ** 4)],
  },
  {
    family: "rise",
    name: "tangent rise",
    note: "y = t + t³: starts along the chord, then lifts; a cubic, exact",
    target: (k) => (t) => [W * t, (40 + 5 * k) * (t + 0.5 * t ** 3) / 1.5],
  },
];

/* ---------- the ornament canon: Roman, Greek, French ---------- */

/**
 * Classical design curves. Most are not polynomials — a volute is a spiral and
 * a moulding is a pair of arcs — so these are sampled and fitted, and each one
 * carries its measured error. They are shapes to test the workflow on, not
 * claims of exact construction.
 */
const ornamentFamilies: Family[] = [
  {
    family: "cyma-recta",
    group: "ornament",
    name: "cyma recta (Roman S-moulding)",
    note: "smoothstep profile: convex below, concave above; the classic Roman crown moulding",
    target: (k) => (t) => [W * t, (40 + 4 * k) * t * t * (3 - 2 * t)],
  },
  {
    family: "cyma-reversa",
    group: "ornament",
    name: "cyma reversa",
    note: "the same profile turned over: concave below, convex above",
    target: (k) => (t) => [W * t, (40 + 4 * k) * (1 - t * t * (3 - 2 * t))],
  },
  {
    family: "echinus",
    group: "ornament",
    name: "echinus (Roman quarter round)",
    note: "a quarter ellipse, the ovolo of a capital; sampled, so fitted",
    target: (k) => (t) => {
      const th = (Math.PI / 2) * t;
      return [W * (1 - Math.cos(th)), (34 + 4 * k) * Math.sin(th)];
    },
  },
  {
    family: "volute",
    group: "ornament",
    name: "volute quarter turn (Ionic)",
    note: "a logarithmic spiral over 90°; a volute is a spiral, so this is fitted, not exact",
    target: (k) => (t) => {
      const r0 = 6 + k;
      const r = r0 * Math.exp((1.1 + 0.05 * k) * (Math.PI / 2) * t);
      const th = (Math.PI / 2) * t;
      return [16 + r * Math.cos(th), r * Math.sin(th)];
    },
  },
  {
    family: "ogee-arch",
    group: "ornament",
    name: "ogee arch (pointed)",
    note: "two arcs meeting at a point: the apex is a corner, not a smooth top; fitted",
    target: (k) => (t) => [W * t, (34 + 4 * k) * (1 - Math.abs(2 * t - 1) ** 1.6)],
  },
  {
    family: "rocaille",
    group: "ornament",
    name: "rocaille C-scroll (French)",
    note: "the asymmetric scroll of the Rococo: one lobe, one long tail; fitted",
    target: (k) => (t) => [W * t, (16 + 3 * k) * (t - 0.5 + 0.35 * Math.sin(2 * Math.PI * t))],
  },
  {
    family: "acanthus",
    group: "ornament",
    name: "acanthus lobe",
    note: "one leaf lobe with the side notches of the Corinthian leaf; fitted",
    target: (k) => (t) => [W * t, (26 + 4 * k) * Math.sin(Math.PI * t) * (1 + 0.06 * Math.sin(3 * Math.PI * t))],
  },
  {
    family: "arabesque",
    group: "ornament",
    name: "arabesque vine",
    note: "a wave whose amplitude grows along the run; fitted",
    target: (k) => (t) => [W * t, (14 + 3 * k) * t * Math.sin(2 * Math.PI * t)],
  },
  {
    family: "trefoil",
    group: "ornament",
    name: "trefoil lobe",
    note: "two lobes inside one span; a true trefoil is three arcs, not one polynomial, so this is fitted",
    target: (k) => (t) => [W * t, (18 + 3 * k) * Math.sin(2 * Math.PI * t) * Math.sin(Math.PI * t)],
  },
  {
    family: "vitruvian-scroll",
    group: "ornament",
    name: "Vitruvian scroll",
    note: "a decaying wave, the running scroll of a frieze; fitted",
    target: (k) => (t) => [W * t, (22 + 4 * k) * Math.sin(2 * Math.PI * t) * Math.exp(-1.5 * t)],
  },
];

function build(group: "math" | "ornament"): Curve[] {
  const curves: Curve[] = [];
  for (const f of [...families, ...ornamentFamilies]) {
    if ((f.group ?? "math") !== group) continue;
    for (let k = 1; k <= 10; k += 1) {
      const target = f.target ? f.target(k) : undefined;
      const points = target ? fitQuintic(target) : f.given!(k);
      curves.push({
        uid: `q6-${f.family}-${String(k).padStart(2, "0")}`,
        group: f.group ?? "math",
        family: f.family,
        name: `${f.name} ${k}`,
        points,
        note: f.note,
        fitError: target ? +fitError(points, target).toFixed(4) : 0,
      });
    }
  }
  return curves;
}

/* ---------- the sheet ---------- */

function sheet(curves: Curve[], heading: string, subtitle: string): string {
  const margin = 62;
  const header = 62;
  const footer = 46;
  const rows = 10;
  const cols = 10;
  const rowHeight = (PAPER - header - footer) / rows;
  const cellWidth = (PAPER - margin - 16) / cols;
  const worst = Math.max(...curves.map((c) => maxError(c.points, 6)));
  const parts: string[] = [];
  parts.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${PAPER}" height="${PAPER}" viewBox="0 0 ${PAPER} ${PAPER}">`);
  parts.push(`<rect width="${PAPER}" height="${PAPER}" fill="#fff"/>`);
  parts.push(`<g font-family="Helvetica, Arial, sans-serif" fill="#111">`);
  parts.push(`<text x="${margin}" y="30" font-size="22" font-weight="600">${heading}</text>`);
  parts.push(`<text x="${margin}" y="52" font-size="13" fill="#555">${subtitle}</text>`);
  parts.push(`<g transform="translate(${margin},${PAPER - 22})" font-size="13" fill="#444">`);
  parts.push(`<circle cx="4" cy="-4" r="4" fill="#c0392b"/><text x="16" y="0">control point</text>`);
  parts.push(`<line x1="130" y1="-4" x2="170" y2="-4" stroke="#b9c6d6" stroke-width="1.5" stroke-dasharray="3 3"/><text x="180" y="0">control polygon</text>`);
  parts.push(`<line x1="330" y1="-4" x2="370" y2="-4" stroke="#123" stroke-width="1.7"/><text x="380" y="0">curve, drawn as a 6-span cubic chain (worst deviation ${worst.toFixed(3)} grid units)</text>`);
  parts.push(`</g>`);

  curves.forEach((curve, index) => {
    const row = Math.floor(index / cols);
    const col = index % cols;
    const cellX = margin + col * cellWidth;
    const cellY = header + row * rowHeight;

    const xs = curve.points.map((p) => p[0]);
    const ys = curve.points.map((p) => p[1]);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);
    const pad = 10;
    const scale = Math.min(
      (cellWidth - 2 * pad) / Math.max(1, maxX - minX),
      (rowHeight - 26 - 2 * pad) / Math.max(1, maxY - minY),
    );
    const offsetX = cellX + pad + ((cellWidth - 2 * pad) - (maxX - minX) * scale) / 2;
    const offsetY = cellY + 22 + pad + ((rowHeight - 26 - 2 * pad) - (maxY - minY) * scale) / 2;
    // y is flipped here and only here: model y-up, SVG y-down.
    const plot = (p: Point) => `${(offsetX + (p[0] - minX) * scale).toFixed(2)},${(offsetY + (maxY - p[1]) * scale).toFixed(2)}`;

    parts.push(`<g id="${curve.uid}">`);
    if (col === 0) {
      parts.push(`<text x="8" y="${(cellY + rowHeight / 2).toFixed(1)}" font-size="12" fill="#444">${curve.family}</text>`);
    }
    parts.push(`<text x="${(cellX + 4).toFixed(1)}" y="${(cellY + 14).toFixed(1)}" font-size="9" fill="#777">${curve.uid.replace("q6-", "")}</text>`);
    parts.push(
      `<polyline points="${curve.points.map(plot).join(" ")}" fill="none" stroke="#b9c6d6" stroke-width="1" stroke-dasharray="3 3"/>`,
    );
    const chain = cubicChain(curve.points, 6);
    const d = chain
      .map((c, i) => (i === 0 ? `M ${plot(c[0])} ` : "") + `C ${plot(c[1])} ${plot(c[2])} ${plot(c[3])}`)
      .join(" ");
    parts.push(`<path d="${d}" fill="none" stroke="#123" stroke-width="1.7"/>`);
    for (const p of curve.points) {
      const [x, y] = plot(p).split(",");
      parts.push(`<circle cx="${x}" cy="${y}" r="2.1" fill="#c0392b"/>`);
    }
    parts.push(`</g>`);
  });

  parts.push(`</g>`);
  parts.push(`</svg>`);
  return parts.join("\n");
}

/**
 * A clean sheet for the extension: one path per curve, six nodes each, no dots
 * and no drawn curve. This is the file to open and test against.
 */
function guidePaths(curves: Curve[], heading: string): string {
  const cols = 5;
  const rows = Math.ceil(curves.length / cols);
  const cell = 260;
  const width = cols * cell;
  const height = rows * cell + 60;
  const parts = [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">`,
    `<rect width="${width}" height="${height}" fill="#fff"/>`,
    `<text x="20" y="30" font-family="Helvetica, Arial, sans-serif" font-size="20" font-weight="600">${heading}</text>`,
  ];
  curves.forEach((curve, index) => {
    const cx = (index % cols) * cell;
    const cy = 60 + Math.floor(index / cols) * cell;
    const xs = curve.points.map((p) => p[0]);
    const ys = curve.points.map((p) => p[1]);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);
    const pad = 18;
    const top = 22;
    const s = Math.min(
      (cell - 2 * pad) / Math.max(1, maxX - minX),
      (cell - top - 2 * pad) / Math.max(1, maxY - minY),
    );
    const ox = cx + pad + ((cell - 2 * pad) - (maxX - minX) * s) / 2;
    const oy = cy + top + pad + ((cell - top - 2 * pad) - (maxY - minY) * s) / 2;
    // y is flipped here and only here: model y-up, SVG y-down.
    const pts = curve.points.map(([x, y]) => `${(ox + (x - minX) * s).toFixed(2)},${(oy + (maxY - y) * s).toFixed(2)}`);
    parts.push(`<g id="${curve.uid}">`);
    parts.push(
      `<text x="${cx + pad}" y="${cy + 14}" font-family="Helvetica, Arial, sans-serif" font-size="10" fill="#666">${curve.uid}</text>`,
    );
    parts.push(`<path d="M ${pts.join(" L ")}" fill="none" stroke="#8a9bb0" stroke-width="1.5" stroke-dasharray="4 4" inkscape:label="${curve.uid}" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"/>`);
    parts.push(`</g>`);
  });
  parts.push(`</svg>`);
  return parts.join("\n");
}

/* ---------- the shared record: spans, frame, joins ---------- */

const cross2 = (a: Point, b: Point) => a[0] * b[1] - a[1] * b[0];
const dot2 = (a: Point, b: Point) => a[0] * b[0] + a[1] * b[1];

/**
 * The end frame of a span, measured from its six points.
 * Reversing the control points gives the other end the same formula.
 * kappa = (r' x r'') / |r'|^3 and dkappa/ds = (r' x r''')/|r'|^4
 *          - 3 (r' x r'')(r' . r'')/|r'|^6.
 */
function endFrame(pointsIn: Point[], atEnd: boolean) {
  const p = atEnd ? [...pointsIn].reverse() : pointsIn;
  const d1: Point = [5 * (p[1][0] - p[0][0]), 5 * (p[1][1] - p[0][1])];
  const d2: Point = [20 * (p[2][0] - 2 * p[1][0] + p[0][0]), 20 * (p[2][1] - 2 * p[1][1] + p[0][1])];
  const d3: Point = [60 * (p[3][0] - 3 * p[2][0] + 3 * p[1][0] - p[0][0]), 60 * (p[3][1] - 3 * p[2][1] + 3 * p[1][1] - p[0][1])];
  const n = Math.hypot(d1[0], d1[1]);
  // The reversed list walks the curve backwards, so its signed curvature and
  // its curvature rate are the negative of the forward ones. Both ends are
  // reported along the forward parameter, so a join compares like with like.
  const sign = atEnd ? -1 : 1;
  const kappa = sign * (cross2(d1, d2) / n ** 3);
  const rate = sign * (cross2(d1, d3) / n ** 4 - (3 * cross2(d1, d2) * dot2(d1, d2)) / n ** 6);
  const forward: Point = atEnd
    ? [pointsIn[5][0] - pointsIn[4][0], pointsIn[5][1] - pointsIn[4][1]]
    : [pointsIn[1][0] - pointsIn[0][0], pointsIn[1][1] - pointsIn[0][1]];
  return {
    p: p[0],
    tangent: forward,
    kappa: +kappa.toFixed(6),
    rate: +rate.toFixed(6),
  };
}

/** One curve as the shared format says it must be written. */
function toRecord(c: Curve, selfCrossingsCount: number, chainError: number) {
  return {
    uid: c.uid,
    group: c.group,
    family: c.family,
    name: c.name,
    note: c.note,
    closed: false,
    winding: null,
    fitError: c.fitError,
    selfCrossings: selfCrossingsCount,
    cubicChain: { spans: 6, worstError: +chainError.toFixed(4) },
    spans: [
      {
        uid: `${c.uid}:0`,
        kind: "quintic" as const,
        points: c.points,
        weights: null,
        frame: { start: endFrame(c.points, false), end: endFrame(c.points, true) },
      },
    ],
    joins: [],
  };
}

/* ---------- run ---------- */
const mathCurves = build("math");
const ornamentCurves = build("ornament");
const curves = [...mathCurves, ...ornamentCurves];
if (mathCurves.length !== 100) throw new Error(`expected 100 math curves, built ${mathCurves.length}`);
if (ornamentCurves.length !== 100) throw new Error(`expected 100 ornament curves, built ${ornamentCurves.length}`);
for (const c of curves) {
  if (c.points.length !== 6) throw new Error(`${c.uid} has ${c.points.length} points, not 6`);
  for (const [x, y] of c.points) {
    if (!Number.isInteger(x) || !Number.isInteger(y)) throw new Error(`${c.uid} has a non-integer point`);
  }
}

const withError = curves.map((c) => ({
  ...c,
  selfCrossings: selfCrossings(c.points),
  approximation: { spans: 6, worstError: +maxError(c.points, 6).toFixed(4) },
}));
const worst = Math.max(...withError.map((c) => c.approximation.worstError));
const loopFamily = withError.filter((c) => c.family === "loop");
const loopsThatDoNotLoop = loopFamily.filter((c) => c.selfCrossings === 0).length;

mkdirSync(path.dirname(OUT_JSON), { recursive: true });
writeFileSync(
  OUT_JSON,
  `${JSON.stringify(
    {
      format: "curve-lab.quintic/1",
      degree: 5,
      order: ["P0", "P1", "P2", "P3", "P4", "P5"],
      axes: {
        x: "right",
        y: "up",
        units: "grid",
        extent: [
          Math.min(...withError.flatMap((c) => c.points.map((p) => p[0]))),
          Math.max(...withError.flatMap((c) => c.points.map((p) => p[0]))),
          Math.min(...withError.flatMap((c) => c.points.map((p) => p[1]))),
          Math.max(...withError.flatMap((c) => c.points.map((p) => p[1]))),
        ],
      },
      note: "Six integer control points per span, y-up. Fullness alpha moves P1..P4 toward the chord. The cubic chain is a display approximation; the six points are the exact object, and frame is measured from them.",
      count: withError.length,
      worstApproximationError: +worst.toFixed(4),
      curves: withError.map((c) => toRecord(c, c.selfCrossings, c.approximation.worstError)),
    },
    null,
    1,
  )}\n`,
);
writeFileSync(
  OUT_SVG,
  `${sheet(mathCurves, "Fig. QG1 — 100 six-point control curves (quintic Bézier), grid 120 × 120", "x right, y up, grid units. Ten classic families, ten members each. Six integer control points per curve; the JSON beside this file is the exact record.")}\n`,
);
writeFileSync(
  OUT_PATHS,
  `${guidePaths(mathCurves, "Fig. QG2 — 100 six-node guides, one path each, for the Quintic from Guide extension")}\n`,
);
writeFileSync(
  OUT_ORN_SVG,
  `${sheet(ornamentCurves, "Fig. QG3 — 100 ornament canon curves (Roman, Greek, French), six points each", "x right, y up, grid units. Ten classical design families, ten members each. These are sampled and fitted, so each carries its measured error; the six points are still the exact object.")}\n`,
);
writeFileSync(
  OUT_ORN_PATHS,
  `${guidePaths(ornamentCurves, "Fig. QG4 — 100 six-node ornament guides, one path each, for the Quintic from Guide extension")}\n`,
);
console.log(`wrote ${withError.length} curves`);
console.log(`worst cubic-chain deviation: ${worst.toFixed(4)} grid units (6 spans)`);
console.log(`families: ${[...new Set(withError.map((c) => c.family))].join(", ")}`);
console.log(`loop family self-crossings: ${loopFamily.map((c) => c.selfCrossings).join(", ")}`);
if (loopsThatDoNotLoop > 0) throw new Error(`${loopsThatDoNotLoop} loop curves do not cross themselves`);
