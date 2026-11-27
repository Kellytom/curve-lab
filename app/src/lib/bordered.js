// The illuminations: every curve in the registry, bordered by a curve.
//
// The inner curve has its own spec, stored by uid in workbench/curve-notes.json:
//
//   rotation    degrees, usually a multiple of 90; applied to the inner only
//   pieces      1, 2 or 4; 2 adds a vertical mirror, 4 adds the horizontal too
//   border_uid  the curve used for the border, when it is not the same one
//
// The frame rule is the lab's: the side is n x the motif, so n copies fill each
// edge. 9 by default, 5 for the curves whose loops make a wide border. The
// border's share of the figure is measured and printed, so a wide one is seen.

import { statSync } from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

import { repoRoot } from "./gallery.js";

const require = createRequire(import.meta.url);
// The plate maths lives at the repository root, not inside app/. A path
// relative to this file works in the source tree and breaks in the built
// server, where the chunk sits in app/dist/server/chunks: the require then
// looks for app/workbench/plate_math.js. Ask for the repo root instead.
const P = require(path.join(repoRoot(), "workbench", "plate_math.js"));

const SIZE = 900;
const PAD = 0.04;
const PER_SIDE = 9;
const PER_SIDE_FIVE = new Set(["c-0007", "c-0002"]);
const TOO_WIDE = 30;

// A border is a band: the motif repeats along the edge with its chord as the
// step, so a motif whose loops are taller than its chord tiles into a mesh and
// the centre disappears. Measured on c-0003: chord 14, amplitude 50. Turning it
// a quarter turn does not help (P.frame normalises each copy to its chord), so
// the motif is flattened to a stated share of the step before tiling.
const BAND_SHARE = 0.09;
// How much of the frame's side the central design takes: the subject, not a mark.
// The old rule scaled it to 1/perSide (one ninth), which read as a speck.
const CENTRAL_SHARE = 0.50;

// The curves the operator found colliding with their own border (2026-11-19).
// The aspect test catches the tall ones; these are the rest, where the loops
// are wide but still deeper than the step.

function pointsOf(record) {
  if (record.path) return record.path;
  return P.spine(record.speedX, record.speedY, 400).map((s) => [s.x, s.y]);
}

function rotatePoints(points, degrees) {
  const turn = (((Number(degrees) || 0) % 360) + 360) % 360;
  if (!turn) return points.map(([x, y]) => [x, y]);
  const exact = [90, 180, 270].includes(turn);
  const a = turn * Math.PI / 180;
  const c = exact ? Math.round(Math.cos(a)) : Math.cos(a);
  const s = exact ? Math.round(Math.sin(a)) : Math.sin(a);
  return points.map(([x, y]) => [x * c - y * s, x * s + y * c]);
}

function mirroredPieces(points, pieces) {
  const box = P.bbox(points);
  const cx = (box[0] + box[2]) / 2;
  const cy = (box[1] + box[3]) / 2;
  const out = [points];
  if (pieces >= 2) out.push(points.map(([x, y]) => [2 * cx - x, y]));
  if (pieces >= 4) {
    out.push(points.map(([x, y]) => [x, 2 * cy - y]));
    out.push(points.map(([x, y]) => [2 * cx - x, 2 * cy - y]));
  }
  return out;
}

// The mirror of a curve across the chord through its first and last station.
// The two feet lie on the chord, so they are fixed points of the reflection and
// the two halves share them exactly.
function reflectAcrossChord(points) {
  const a = points[0];
  const b = points[points.length - 1];
  const dx = b[0] - a[0];
  const dy = b[1] - a[1];
  const len2 = dx * dx + dy * dy;
  if (!len2) {
    // A closed curve: the chord is a point, so mirror across that point.
    return points.map(([x, y]) => [2 * a[0] - x, 2 * a[1] - y]);
  }
  return points.map(([x, y]) => {
    const t = ((x - a[0]) * dx + (y - a[1]) * dy) / len2;
    const px = a[0] + t * dx;
    const py = a[1] + t * dy;
    return [2 * px - x, 2 * py - y];
  });
}

function scaleAbout(points, factor) {
  return points.map(([x, y]) => [x * factor, y * factor]);
}

function moveToCentre(points, cx, cy) {
  const box = P.bbox(points);
  return points.map(([x, y]) => [x - (box[0] + box[2]) / 2 + cx, y - (box[1] + box[3]) / 2 + cy]);
}

// `turn` rotates the repeated motif before it is laid along the edges. The band
// is as wide as the motif's short side, so turning a tall curve a quarter turn
// thins the border without changing the side of the square.
// The motif with its amplitude limited to BAND_SHARE of its chord: the band a
// border needs. The inner curve is not touched.
function bandMotif(record) {
  const points = record.path || P.spine(record.speedX, record.speedY, 160).map((s) => [s.x, s.y]);
  const box = P.bbox(points);
  const width = box[2] - box[0];
  const height = box[3] - box[1];
  if (!width || !height) return record;
  // Only ever flatten: a motif already flatter than the share is left alone.
  const k = Math.min(1, (BAND_SHARE * width) / height);
  if (k === 1) return record;
  if (record.path) return { ...record, path: record.path.map(([x, y]) => [x, y * k]) };
  return { ...record, speedY: (record.speedY || []).map((v) => v * k) };
}

function frameBorder(record, perSide, turn = 0) {
  if (record.path) {
    const flat = bandMotif(record).path;
    const motif = turn ? rotatePoints(flat, turn) : flat;
    const xs = motif.map((p) => p[0]);
    const ys = motif.map((p) => p[1]);
    const unit = Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)) || 1;
    const side = perSide * unit;
    const spin = (pts, deg) => {
      const a = deg * Math.PI / 180;
      return pts.map(([x, y]) => [x * Math.cos(a) - y * Math.sin(a), x * Math.sin(a) + y * Math.cos(a)]);
    };
    const border = [];
    [[0, 0, 0], [side, 0, 90], [side, side, 180], [0, side, 270]].forEach(([ox, oy, deg]) => {
      for (let copy = 0; copy < perSide; copy += 1) {
        const moved = motif.map(([x, y]) => [x + copy * unit, y]);
        border.push(spin(moved, deg).map(([x, y]) => [x + ox, y + oy]));
      }
    });
    return { paths: border, fills: [] };
  }
  // A speed-row curve is turned by turning its velocity: (u, v) -> (-v, u).
  // That is what makes the four wide curves a border instead of a collision.
  const turned = turn === 90
    ? { ...record, speedX: (record.speedY || []).map((v) => -v), speedY: record.speedX }
    : record;
  const a = P.group(bandMotif(turned));
  const items = P.frame(a, null, perSide, perSide, 45, "a", false);
  const paths = items.flatMap((item) => item.paths);
  const fills = items
    .filter((item) => item.paths.length >= 3)
    .map((item) => {
      const band = [...item.paths[1], ...item.paths[2].slice().reverse()];
      band.push(band[0]);
      return band;
    });
  return { paths, fills };
}

// The paths the centre draws: the spine only, or the spine and its rails when
// the note turns the character offsets on.
function centralPaths(record, rotation) {
  if (record.offsets && record.speedX && record.speedY) {
    return {
      paths: P.group(record).paths.map((path) => rotatePoints(path, rotation)),
      offset: true,
      branched: false,
    };
  }
  // A multi-branch record is already whole (c-0416's four arms). Drawn as one path its jumps
  // become chords and fill as a blob, so every branch is its own path here.
  //
  // A rows record has no stored path, and branchesOf reads only paths: it returns []. Fall back
  // to the record's own speed rows. Without this the central design is empty and the figure
  // catches the error, drawing a bare half-curve — c-0022's "diamond" lost its mirror half
  // (2026-11-26).
  const stored = P.branchesOf ? P.branchesOf(record) : [];
  const branches = stored.length ? stored : [pointsOf(record)];
  return {
    paths: branches.map((path) => rotatePoints(path, rotation)),
    offset: false,
    branched: branches.length > 1,
  };
}

function marginPercent(border, central) {
  const fbox = P.bbox(border.flat());
  const cbox = P.bbox(central.flat());
  const margin = Math.min(cbox[0] - fbox[0], fbox[2] - cbox[2],
                          cbox[1] - fbox[1], fbox[3] - cbox[3]);
  const size = Math.max(fbox[2] - fbox[0], fbox[3] - fbox[1]) || 1;
  return Math.max(0, Math.round((margin / size) * 100));
}

export function figureFor(record, all, borderRecord) {
  const perSide = Number(record.perSide) || (PER_SIDE_FIVE.has(record.uid) ? 5 : PER_SIDE);
  const rotation = Number(record.rotation) || 0;
  const pieces = [1, 2, 4].includes(Number(record.pieces)) ? Number(record.pieces) : 1;

  const build = (borderTurn) => {
    const borderFrame = frameBorder(borderRecord || record, perSide,
      borderRecord ? 0 : (Number(record.borderTurn) || 0));
    let border = borderFrame.paths;
    let borderFills = borderFrame.fills;
    // The corner rule is a C/D treatment; A and B keep the old wrap.
    const applyCorner = record.variant === "C" || record.variant === "D";
    // The corner rule: a natural right angle turns the motif by the per-leg
    // residual; every other curve leaves the band where it is (the "stop").
    if (applyCorner && record.cornerRule === "corner" && Number(record.cornerGap)) {
      const a = (Number(record.cornerGap) * Math.PI) / 180;
      const turn = ([x, y]) => [x * Math.cos(a) - y * Math.sin(a), x * Math.sin(a) + y * Math.cos(a)];
      border = border.map((path) => path.map(turn));
      borderFills = borderFills.map((path) => path.map(turn));
    }
    if (applyCorner && record.cornerRule === "stop") {
      // Stop the band short of the corners with a plain cap: a 3% inset, not a
      // wrap into the corner.
      const box = P.bbox(border.flat());
      const sx = (box[0] + box[2]) / 2;
      const sy = (box[1] + box[3]) / 2;
      const inset = ([x, y]) => [sx + (x - sx) * 0.97, sy + (y - sy) * 0.97];
      border = border.map((path) => path.map(inset));
      borderFills = borderFills.map((path) => path.map(inset));
    }
    const fbox = P.bbox(border.flat());
    const cx = (fbox[0] + fbox[2]) / 2;
    const cy = (fbox[1] + fbox[3]) / 2;
    let central;
    let centralCount;
    let fills;
    if (pieces === 1) {
      const centralInfo = centralPaths(record, rotation);
      const half = centralInfo.paths;
      if (centralInfo.branched) {
        // branches are already whole: scale the set about its common centre, no mirror, no
        // fill. (Centring each branch on its own box would pile the arms on one point.)
        const target = CENTRAL_SHARE * (fbox[2] - fbox[0]);
        const bbox0 = P.bbox(half.flat());
        const size0 = Math.max(bbox0[2] - bbox0[0], bbox0[3] - bbox0[1]) || 1;
        const scale0 = target / size0;
        const mx = (bbox0[0] + bbox0[2]) / 2;
        const my = (bbox0[1] + bbox0[3]) / 2;
        central = half.map((path) =>
          path.map(([x, y]) => [(x - mx) * scale0 + cx, (y - my) * scale0 + cy]));
        centralCount = central.length;
        fills = [...borderFills];
      } else {
        const mirror = half.map((path) => reflectAcrossChord(path));
        const halves = [half, mirror];
        const bands = [];
        if (half.length >= 3) {
          const band = [...half[1], ...half[2].slice().reverse()];
          band.push(band[0]);
          const mirrorBand = [...mirror[1], ...mirror[2].slice().reverse()];
          mirrorBand.push(mirrorBand[0]);
          bands.push(band, mirrorBand);
        } else {
          const leaf = [...half[0], ...mirror[0].slice().reverse()];
          leaf.push(leaf[0]);
          bands.push(leaf);
        }
        const all = halves.flat();
        const pairBox = P.bbox(all.flat());
        const size = Math.max(pairBox[2] - pairBox[0], pairBox[3] - pairBox[1]) || 1;
        const target = CENTRAL_SHARE * (fbox[2] - fbox[0]);
        const scale = target / size;
        const scaledHalves = halves.map((h) => h.map((p) => scaleAbout(p, scale)));
        const scaledBands = bands.map((b) => scaleAbout(b, scale));
        const box = P.bbox(scaledHalves.flat().flat());
        const dx = cx - (box[0] + box[2]) / 2;
        const dy = cy - (box[1] + box[3]) / 2;
        const movedHalves = scaledHalves.map((h) => h.map((p) => p.map(([x, y]) => [x + dx, y + dy])));
        const movedBands = scaledBands.map((b) => b.map(([x, y]) => [x + dx, y + dy]));
        central = movedHalves.flat();
        centralCount = movedHalves.length;
        fills = [...movedBands, ...borderFills];
      }
    } else {
      const centralInfo = centralPaths(record, rotation);
      const innerPaths = centralInfo.paths;
      const ibox = P.bbox(innerPaths.flat());
      const size = Math.max(ibox[2] - ibox[0], ibox[3] - ibox[1]) || 1;
      const target = CENTRAL_SHARE * (fbox[2] - fbox[0]);
      if (centralInfo.branched) {
        // pieces of a branched record stay branches: tile nothing, draw the set once
        central = innerPaths.map((path) =>
          path.map(([x, y]) => [(x - (ibox[0] + ibox[2]) / 2) * (target / size) + cx,
            (y - (ibox[1] + ibox[3]) / 2) * (target / size) + cy]));
        centralCount = central.length;
        fills = [...borderFills];
      } else {
        central = mirroredPieces(scaleAbout(innerPaths[0], target / size), pieces)
          .map((line) => moveToCentre(line, cx, cy));
        centralCount = central.length;
        fills = borderFills;
      }
    }
    const margin = marginPercent(border, central);
    return {
      paths: [...central, ...border],
      perSide,
      margin,
      rotation,
      pieces,
      centralCount,
      fills,
      borderTurn,
      cornerRule: record.cornerRule || "stop",
      cornerGap: record.cornerGap ?? null,
      seam: record.seam || null,
      failed: false,
      tooWide: margin >= TOO_WIDE,
    };
  };

  try {
    const straight = build(0);
    const quarter = build(90);
    // Only a real gain pays for the change of look: five points of clearance.
    return quarter.margin >= straight.margin + 5 ? quarter : straight;
  } catch (error) {
    return {
      paths: [pointsOf(record)], perSide, margin: 0, rotation, pieces, centralCount: 1,
      fills: [], failed: true, reason: String(error.message || error),
    };
  }
}

function svgFrom(paths, label, fills = [], options = {}) {
  // A loop, not Math.min(...xs): with rails and fills a figure holds far more
  // points than a spread can take, and the illuminations page builds 238 of
  // them in one request — a spread there throws Maximum call stack size.
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const path of paths) {
    for (const [x, y] of path) {
      if (x < x0) x0 = x;
      if (x > x1) x1 = x;
      if (y < y0) y0 = y;
      if (y > y1) y1 = y;
    }
  }
  const w = x1 - x0 || 1, h = y1 - y0 || 1;
  const inner = SIZE * (1 - 2 * PAD);
  const k = inner / Math.max(w, h);
  const ox = (SIZE - w * k) / 2 - x0 * k;
  const oy = (SIZE + h * k) / 2 + y0 * k;
  const fillsSvg = fills.map((points) => {
    const d = points.map(([x, y], i) => `${i ? "L" : "M"}${(ox + x * k).toFixed(2)},${(oy - y * k).toFixed(2)}`).join("");
    return `<path d="${d}Z" fill="#e6d9b6" stroke="none" fill-rule="nonzero"/>`;
  }).join("");
  const central = Number(options.centralCount) || 0;
  const lines = paths.map((points, index) => {
    // The frame is a frame: the border sits back, the design comes forward.
    const weight = central && index < central ? 2.6 : 1.4;
    const step = Math.max(1, Math.floor(points.length / 300));
    const kept = points.filter((_, i) => i % step === 0 || i === points.length - 1);
    return `<polyline points="${kept.map(([x, y]) =>
      `${(x * k + ox).toFixed(1)},${(oy - y * k).toFixed(1)}`).join(" ")}"` +
      ` fill="none" stroke="#141414" stroke-width="${weight}" stroke-linecap="round" stroke-linejoin="round"/>`;
  });
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${SIZE} ${SIZE}" width="${SIZE}" height="${SIZE}" role="img" aria-label="${label}">` +
    `<rect width="${SIZE}" height="${SIZE}" fill="#fff"/>${fillsSvg}${lines.join("")}</svg>`;
}

export function svgForFigure(figure, label) {
  return svgFrom(figure.paths, label, figure.fills, { centralCount: figure.centralCount });
}

export function svgForRecord(record, all = {}) {
  return svgForFigure(figureFor(record, all), `${record.uid}: ${record.name}`);
}

export function plainSvgForRecord(record) {
  return svgFrom([pointsOf(record)], `${record.uid}: ${record.name}`);
}

let cache = null;

export function clearIlluminateCache() {
  cache = null;
}

// The build is memoised: 238 figures is about a second of work, and the page
// and its figure route must not each pay it. The stamp is the two data files'
// mtimes, so an edit to the registry or the notes rebuilds on the next request
// instead of serving yesterday's borders.
function dataStamp(base) {
  return ["workbench/curve-registry.json", "workbench/curve-notes.json"]
    .map((file) => {
      try { return statSync(path.join(base, file)).mtimeMs; } catch { return 0; }
    })
    .join(":");
}

export async function buildIlluminations(root) {
  const base = root || repoRoot();
  const stamp = dataStamp(base);
  if (cache && cache.base === base && cache.stamp === stamp) return cache;
  // the database-backed registry is loaded here, not at import: figureFor and the SVG writers
  // are pure and must import under plain Node (the tests do), and a static .ts import blocked
  // that with ERR_UNKNOWN_FILE_EXTENSION.
  const { loadRegistry } = await import("./registry.ts");
  const registry = (await loadRegistry(base)).curves;
  const rows = Object.fromEntries(registry.map((record) => [record.name, record]));
  const byUid = Object.fromEntries(registry.map((record) => [record.uid, record]));
  const byList = (name) => registry.filter((record) => record.lists.includes(name));
  const byWeight = (a, b) => (b.importance || 0) - (a.importance || 0);

  const sections = [
    { title: "Fig. 1–50 · found", records: byList("found").slice(0, 50) },
    // Only the finder curves that were actually picked: starred or rated.
    // Unstarred finder rows are the candidate pool, not the collection.
    { title: "Finder · picked", records: byList("finder").filter((r) => r.starred || (r.importance || 0) > 0) },
    { title: "Roses", records: registry.filter((r) => r.family_id === "rose" && !r.name.includes("k-4")) },
    { title: "B | solve, save, take away", records: byList("B") },
  ];

  let n = 0;
  const built = sections.map((section) => ({
    title: section.title,
    items: section.records.slice().sort(byWeight).map((record) => {
      n += 1;
      const border = record.border_uid ? byUid[record.border_uid] : null;
      const figure = figureFor(record, rows, border);
      return {
        n,
        uid: record.uid,
        name: record.name,
        id: `fig-${n}`,
        svg: svgFrom(figure.paths, `Fig. ${n}: ${record.name}`, figure.fills, { centralCount: figure.centralCount }),
        perSide: figure.perSide,
        marginPercent: figure.margin,
        rotation: figure.rotation,
        pieces: figure.pieces,
        importance: record.importance || 0,
        tooWide: figure.tooWide,
        failed: figure.failed,
      };
    }),
  }));
  cache = {
    total: n,
    sections: built,
    base,
    stamp,
    byId: Object.fromEntries(built.flatMap((section) => section.items.map((item) => [item.id, item]))),
  };
  return cache;
}
