// The gothic desk's maths: find the parent's mirror, cut the middle out, and join the two arms
// into a pointed arch. Pure functions; the page and the save both read this file.
//
// The operator, 2026-11-23: "the curve is mirrored around an x axis already, so somewhere around
// t = .5 ... from there, move back a little for the first cut, and forward the same amount for
// the second cut." The cut is therefore a symmetric pair about the stored middle station, and
// the two outer arms are joined at the cut so the join is the apex.
//
// Only a mirror makes a point. A half-turn-only curve meets itself smoothly at the cut (180°),
// so it is measured, reported and refused rather than drawn as a point it is not.

import { turnPoints } from "./cut-doubles.js";
import { sides } from "./class-v.js";

export type Point = [number, number];

export type Axis = {
  id: string;
  label: string;
  reflect: (point: Point, center: Point) => Point;
};

export type MeasuredAxis = Axis & {
  center: Point;
  gap: number;
  maxGap?: number;
  measure: "pairs" | "nearest";
};

export type Bbox = {
  x0: number; x1: number; y0: number; y1: number;
  width: number; height: number; size: number;
};

export type IntegerHit = { x: number; y: number; miss: number; t: number; index: number };

export type Arch = {
  path: Point[];
  drawn: Point[];
  degrees: number;
  axis: string;
  axisLabel: string;
  gap: number;
  maxGap: number;
  measure: string;
  share: number;
  cutIndex: number;
  points: number;
  t: [number, number];
  tRequested: [number, number];
  q: number;
  mirrored: boolean;
  width: number;
  height: number;
  feetLevel: number;
  apexAngle: number;
  keptShare: number;
};

export type CutOptions = {
  share?: number;
  q?: number | null;
  axis?: MeasuredAxis | null;
  force?: boolean;
};

export type FigureOptions = {
  source?: Point[] | null;
  hits?: IntegerHit[];
  width?: number;
  height?: number;
  band?: boolean;
  label?: string;
};

export type RecordLike = {
  widthPct?: unknown;
  plus?: unknown;
  minus?: unknown;
  profile?: unknown;
};

export const MIRROR_GAP_LIMIT = 0.005; // share of the curve's own bounding diagonal
export const DEFAULT_SHARE = 0.1; // each side of the middle, as a share of the half
export const MIN_SHARE = 0.02;
export const MAX_SHARE = 0.35;

// The cut is a symmetric pair of exact parameter values: t = 1/2 - q and t = 1/2 + q. The menu
// offers the steps the operator will use; the percent of the half is only the echo (q = share/2).
export const DEFAULT_Q = 1 / 20;
export const CUT_STEPS = [
  { label: "1/40", q: 1 / 40 },
  { label: "1/25", q: 1 / 25 },
  { label: "1/20", q: 1 / 20 },
  { label: "1/16", q: 1 / 16 },
  { label: "1/12", q: 1 / 12 },
  { label: "1/10", q: 1 / 10 },
  { label: "1/8", q: 1 / 8 },
  { label: "1/6", q: 1 / 6 },
];

// The four rational mirrors. Each reflect(p, c) is the point p reflected across the line through
// c with that direction; no trigonometry, so a reflected point is exact in the parent's numbers.
const AXES: Axis[] = [
  { id: "vertical", label: "vertical", reflect: (p, c) => [2 * c[0] - p[0], p[1]] },
  { id: "horizontal", label: "horizontal", reflect: (p, c) => [p[0], 2 * c[1] - p[1]] },
  { id: "y=x", label: "y = x", reflect: (p, c) => [c[0] + p[1] - c[1], c[1] + p[0] - c[0]] },
  { id: "y=-x", label: "y = −x", reflect: (p, c) => [c[0] - (p[1] - c[1]), c[1] - (p[0] - c[0])] },
];

export function bboxOf(points: Point[]): Bbox {
  const xs = points.map((p) => p[0]);
  const ys = points.map((p) => p[1]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs);
  const y0 = Math.min(...ys), y1 = Math.max(...ys);
  return {
    x0, x1, y0, y1, width: x1 - x0, height: y1 - y0,
    size: Math.hypot(x1 - x0, y1 - y0) || 1,
  };
}

// The middle of the stored path: the midpoint of the two central stations. The symmetry axis
// passes through this point.
export function middleOf(points: Point[]): Point {
  const n = points.length;
  const lo = Math.floor((n - 1) / 2);
  const hi = Math.ceil((n - 1) / 2);
  return [(points[lo][0] + points[hi][0]) / 2, (points[lo][1] + points[hi][1]) / 2];
}

export function arcLength(points: Point[]): number {
  let total = 0;
  for (let i = 1; i < points.length; i += 1) {
    total += Math.hypot(points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]);
  }
  return total;
}

// Pair station i with station n-1-i, as a uniform sample in t does. Fast, and exact when the
// curve's own sampling is symmetric.
export function measureAxis(points: Point[], axis: Axis): MeasuredAxis {
  const n = points.length;
  const center = middleOf(points);
  const size = bboxOf(points).size;
  let sum = 0, max = 0;
  for (let i = 0; i < n; i += 1) {
    const r = axis.reflect(points[i], center);
    const q = points[n - 1 - i];
    const d = Math.hypot(r[0] - q[0], r[1] - q[1]);
    sum += d * d;
    if (d > max) max = d;
  }
  return { ...axis, center, gap: Math.sqrt(sum / n) / size, maxGap: max / size, measure: "pairs" };
}

// A path sampled unevenly in t can miss on the pair test; reflect a few stations and measure to
// the nearest station instead. This is the honest fallback, not the first choice.
function nearestGap(points: Point[], axis: MeasuredAxis): number {
  const n = points.length;
  const size = bboxOf(points).size;
  const step = Math.max(1, Math.floor(n / 48));
  let sum = 0, count = 0;
  for (let i = 0; i < n; i += step) {
    const r = axis.reflect(points[i], axis.center);
    let best = Infinity;
    for (let j = 0; j < n; j += 1) {
      const dx = points[j][0] - r[0], dy = points[j][1] - r[1];
      const d = dx * dx + dy * dy;
      if (d < best) best = d;
    }
    sum += Math.sqrt(best);
    count += 1;
  }
  return sum / (count || 1) / size;
}

// The best of the four rational mirrors, with its gap as a share of the curve's size.
export function bestAxis(points: Point[]): MeasuredAxis | null {
  if (!points || points.length < 12) return null;
  const measured = AXES.map((axis) => measureAxis(points, axis));
  measured.sort((a, b) => a.gap - b.gap);
  const best = measured[0];
  if (best.gap <= MIRROR_GAP_LIMIT) return best;
  let nearest: MeasuredAxis | null = null;
  for (const axis of measured) {
    const gap = nearestGap(points, axis);
    if (!nearest || gap < nearest.gap) nearest = { ...axis, gap, measure: "nearest" };
  }
  return nearest && nearest.gap < best.gap ? nearest : best;
}

const angleAt = (drawn: Point[], index: number): number => {
  const apex = drawn[index];
  const a = drawn[Math.max(0, index - 1)];
  const b = drawn[Math.min(drawn.length - 1, index + 1)];
  const v1 = [a[0] - apex[0], a[1] - apex[1]];
  const v2 = [b[0] - apex[0], b[1] - apex[1]];
  const l1 = Math.hypot(...v1) || 1, l2 = Math.hypot(...v2) || 1;
  const dot = (v1[0] * v2[0] + v1[1] * v2[1]) / (l1 * l2);
  return (Math.acos(Math.max(-1, Math.min(1, dot))) * 180) / Math.PI;
};

// The house's sampled hit rule (scripts/levien_integer.py `integer_hits`): a station within
// `tolerance` of a whole-number point is a hit. The tolerance is absolute in model units and is
// printed with the marks, so a hit is never claimed as exact.
export const HIT_TOLERANCE = 0.01;

export function integerHits(points: Point[], tolerance = HIT_TOLERANCE): IntegerHit[] {
  const found = new Map<string, IntegerHit>();
  const count = Math.max(1, points.length - 1);
  points.forEach(([x, y], index) => {
    const ix = Math.round(x);
    const iy = Math.round(y);
    const miss = Math.hypot(x - ix, y - iy);
    if (miss > tolerance) return;
    const key = `${ix},${iy}`;
    const hit = { x: ix, y: iy, miss, t: index / count, index };
    const previous = found.get(key);
    if (!previous || miss < previous.miss) found.set(key, hit);
  });
  return [...found.values()].sort((a, b) => a.t - b.t);
}

// A parameter as the fraction it is, for the readout; a station that is not a small fraction
// prints as a decimal rather than pretending.
export function asFraction(value: number, maxDenominator = 64): string {
  for (let denominator = 1; denominator <= maxDenominator; denominator += 1) {
    const numerator = Math.round(value * denominator);
    if (Math.abs(value - numerator / denominator) < 1e-9) {
      return denominator === 1 ? String(numerator) : `${numerator}/${denominator}`;
    }
  }
  return Number(value).toFixed(3);
}

// Cut the middle out and join the arms at the cut. The arm is mirrored about the vertical line
// through the cut point, so the apex lies on the axis and the two sides are equal by
// construction (the class V rule: "join on the axis; mirror, never rotate"). The parent's
// measured gap is carried for the readout, because it says how nearly the other arm agrees.
export function cutArch(points: Point[], {
  share = DEFAULT_SHARE, q = null, axis = null, force = false,
}: CutOptions = {}): Arch | null {
  if (!points || points.length < 12) return null;
  const ax = axis ?? bestAxis(points);
  if (!ax) return null;
  // A mirror makes the parent's two halves agree; the arch itself is one arm mirrored, so a
  // curve without a mirror can still be cut — the gap is carried and printed, never hidden.
  if (ax.gap > MIRROR_GAP_LIMIT && !force) return null;

  // q is the step in t each side of the middle; share is the same cut as a share of the half.
  const askedQ = q === null ? null : Number(q);
  const fromQ = askedQ !== null && Number.isFinite(askedQ) && askedQ > 0;
  const asked = fromQ ? 2 * (askedQ as number) : Number(share);
  const s = Math.min(MAX_SHARE, Math.max(MIN_SHARE,
    fromQ ? asked : (Number.isFinite(asked) && asked !== 0 ? asked : DEFAULT_SHARE)));
  const n = points.length;
  const mid = Math.floor(n / 2);
  const k = Math.max(1, Math.round(mid * s));
  const cutIndex = mid - k;
  if (cutIndex < 3) return null;

  const left = points.slice(0, cutIndex + 1); // foot -> apex
  const apex = left[left.length - 1];
  const moved: Point[] = left.map((p) => [p[0] - apex[0], p[1] - apex[1]]); // the cut is the origin
  const right: Point[] = moved.map(([x, y]) => [-x, y]); // the mirror through the apex
  const path: Point[] = moved.concat(right.slice().reverse().slice(1)); // foot -> apex -> foot

  // The feet are (+x, y) and (-x, y). If they lie above the cut, turn the arch half a turn so
  // the apex is the top; both turns are exact, so no general angle enters the record.
  const feetUp = moved[0][1] > 0;
  const degrees = feetUp ? 180 : 0;
  const drawn = turnPoints(path, degrees) as Point[];

  const b = bboxOf(drawn);
  const t1 = n > 1 ? cutIndex / (n - 1) : 0;
  return {
    path,
    drawn,
    degrees,
    axis: ax.id,
    axisLabel: ax.label,
    gap: ax.gap,
    maxGap: ax.maxGap ?? ax.gap,
    measure: ax.measure,
    share: s,
    cutIndex,
    points: n,
    // the parameter pair the cut sits at, in the record's own station parameter
    t: [t1, 1 - t1],
    // the exact pair that was asked for; the drawn cut is the nearest stored station
    tRequested: [0.5 - s / 2, 0.5 + s / 2],
    q: s / 2,
    mirrored: ax.gap <= MIRROR_GAP_LIMIT,
    width: b.width,
    height: b.height,
    feetLevel: Math.abs(drawn[0][1] - drawn[drawn.length - 1][1]) / b.size,
    apexAngle: angleAt(drawn, cutIndex),
    // the kept pair: the arm and its mirror, as a share of the parent's length
    keptShare: (2 * arcLength(left)) / (arcLength(points) || 1),
  };
}

// The character values the save and the preview both use: a zero in a record is the note
// migration's placeholder, not a choice, so it falls through to the preset.
export function characterOf(record: RecordLike | null | undefined): {
  widthPct: number; plus: number; minus: number; profile: string;
} {
  const real = (value: unknown, fallback: number): number => {
    const number = Number(value);
    return Number.isFinite(number) && number !== 0 ? number : fallback;
  };
  return {
    widthPct: real(record?.widthPct, 1.5),
    plus: real(record?.plus, 2.5),
    minus: real(record?.minus, 0.1),
    profile: typeof record?.profile === "string" && record.profile ? record.profile : "bow",
  };
}

const esc = (text: unknown): string => String(text).replace(/[&<>"]/g, (character) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[character] as string));

// One figure, two panels at one scale: the new arch above, the original below with its two cut
// points, the removed middle and the integer hits. The first paint and every redraw use this.
export function archFigure(arch: Arch | null, {
  source = null, hits = [], width = 660, height = 800, band = true, label = "",
}: FigureOptions = {}): string {
  if (!arch) return "";
  const W = width, H = height;
  const PAD = 34;
  const TITLE = 70;
  const LEGEND = 40;
  const PANEL = (H - 2 * TITLE - LEGEND) / 2;
  const topY = TITLE;
  const bottomY = TITLE + PANEL + TITLE;

  const archPts = arch.drawn;
  const sourcePts: Point[] | null = Array.isArray(source) && source.length > 2 ? source : null;
  const aBox = bboxOf(archPts);
  const sBox = sourcePts ? bboxOf(sourcePts) : aBox;
  // one scale for both panels, each centred on its own frame
  const k = Math.min(
    (W - 2 * PAD) / (aBox.width || 1), PANEL / (aBox.height || 1),
    (W - 2 * PAD) / (sBox.width || 1), PANEL / (sBox.height || 1));
  const mapFor = (originY: number, box: Bbox) => ([x, y]: Point): Point => [
    (W - box.width * k) / 2 + (x - box.x0) * k,
    originY + (PANEL - box.height * k) / 2 + (box.y1 - y) * k,
  ];
  const topPx = mapFor(topY, aBox);
  const bottomPx = mapFor(bottomY, sBox);
  const d = (list: Point[], px: (point: Point) => Point): string => list.map((p, i) =>
    `${i ? "L" : "M"}${px(p)[0].toFixed(1)},${px(p)[1].toFixed(1)}`).join("");
  const text = (x: number, y: number, value: string,
    options: { size?: number; fill?: string } = {}): string =>
    `<text x="${x.toFixed(1)}" y="${y.toFixed(1)}" font-family="ui-monospace,Menlo,monospace" ` +
    `font-size="${options.size || 13}" fill="${options.fill || "#5a4a36"}">${esc(value)}</text>`;

  const rails = band
    ? sides(archPts.map(([x, y]) => ({ x, y })), 1.5, 1.3) as
      { left: Array<{ x: number; y: number }>; right: Array<{ x: number; y: number }> } | null
    : null;
  const railSvg = rails
    ? `<path d="${d(rails.left.map((p) => [p.x, p.y] as Point), topPx)}" fill="none" stroke="#8d8d8d" stroke-width="1.1"/>` +
      `<path d="${d(rails.right.map((p) => [p.x, p.y] as Point), topPx)}" fill="none" stroke="#8d8d8d" stroke-width="1.1"/>`
    : "";
  const apex = topPx(archPts[arch.cutIndex]);

  const shortLabel = label && label.length > 28 ? `${label.slice(0, 27)}…` : label;
  const topLine1 = `the new arch${shortLabel ? ` · ${shortLabel}` : ""}`;
  const topLine2 = `cut ${Math.round(arch.share * 100)} % each side of the middle · t = ` +
    `${asFraction(arch.t[0])} … ${asFraction(arch.t[1])}`;
  const topLine3 = `apex ${arch.apexAngle.toFixed(1)}° · feet level ` +
    `${(arch.feetLevel * 100).toFixed(2)} %` +
    (arch.mirrored ? "" : ` · parent gap ${(arch.gap * 100).toFixed(2)} % (one arm mirrored)`);
  const bottomTitle1 = "the original";
  const bottomTitle2 = "red = the removed middle · gold = integer hit within " +
    `${HIT_TOLERANCE}${hits.length ? "" : " · none found"}`;
  let sourceSvg = "";
  let hitsSvg = "";
  if (sourcePts) {
    const n = sourcePts.length;
    const cutA = Math.max(0, Math.min(n - 1, arch.cutIndex));
    const cutB = Math.max(0, Math.min(n - 1, n - 1 - arch.cutIndex));
    const middle = Math.max(0, Math.min(n - 1, Math.floor((n - 1) / 2)));
    const removed = sourcePts.slice(Math.min(cutA, cutB), Math.max(cutA, cutB) + 1);
    sourceSvg =
      `<path d="${d(sourcePts, bottomPx)}" fill="none" stroke="#2b2b2b" stroke-width="1.6"/>` +
      (removed.length > 2
        ? `<path d="${d(removed, bottomPx)}" fill="none" stroke="#b03a2e" stroke-width="2.2" stroke-opacity="0.45"/>`
        : "") +
      [cutA, cutB].map((index) => {
        const [x, y] = bottomPx(sourcePts[index]);
        return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="4" fill="#b03a2e"/>`;
      }).join("") +
      (() => {
        const [x, y] = bottomPx(sourcePts[middle]);
        return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3.5" fill="#fffef9" stroke="#8a6d3b" stroke-width="1.6"/>`;
      })();
    hitsSvg = (hits.length ? hits : integerHits(sourcePts)).map((hit) => {
      const [x, y] = bottomPx([hit.x, hit.y]);
      const toLeft = x > W - 120;
      const labelX = toLeft ? x - 10 : x + 10;
      const anchor = toLeft ? "end" : "start";
      return `<g><circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3.6" fill="#8a6d3b"/>` +
        `<text x="${labelX.toFixed(1)}" y="${(y + 4).toFixed(1)}" text-anchor="${anchor}" ` +
        `font-family="ui-monospace,Menlo,monospace" font-size="12" fill="#6b5b46">` +
        `(${hit.x}, ${hit.y})</text></g>`;
    }).join("");
  }

  const legend = `<g font-family="ui-monospace,Menlo,monospace" font-size="15" fill="#5a4a36">
    <line x1="${PAD}" x2="${PAD + 26}" y1="${H - 14}" y2="${H - 14}" stroke="#2b2b2b" stroke-width="2"/>
    <text x="${PAD + 34}" y="${H - 9}">spine</text>
    <line x1="${PAD + 104}" x2="${PAD + 130}" y1="${H - 14}" y2="${H - 14}" stroke="#b03a2e" stroke-width="2.2" stroke-opacity="0.6"/>
    <text x="${PAD + 138}" y="${H - 9}">cut / removed</text>
    <circle cx="${PAD + 300}" cy="${H - 14}" r="4" fill="#8a6d3b"/>
    <text x="${PAD + 310}" y="${H - 9}">integer hit</text>
    <text x="${W - PAD}" y="${H - 9}" text-anchor="end">same scale</text>
  </g>`;

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="100%">
    <rect width="${W}" height="${H}" fill="#fffef9"/>
    ${text(PAD, 20, topLine1, { size: 15, fill: "#3f3a33" })}
    ${text(PAD, 39, topLine2, { size: 14, fill: "#5a4a36" })}
    ${text(PAD, 58, topLine3, { size: 14, fill: "#5a4a36" })}
    ${railSvg}
    <path d="${d(archPts, topPx)}" fill="none" stroke="#2b2b2b" stroke-width="1.8" stroke-linejoin="round"/>
    <circle cx="${apex[0].toFixed(1)}" cy="${apex[1].toFixed(1)}" r="4" fill="#8a6d3b"/>
    ${text(PAD, bottomY - 44, bottomTitle1, { size: 15, fill: "#3f3a33" })}
    ${text(PAD, bottomY - 24, bottomTitle2, { size: 13, fill: "#5a4a36" })}
    ${sourceSvg}${hitsSvg}
    ${legend}
  </svg>`;
}
