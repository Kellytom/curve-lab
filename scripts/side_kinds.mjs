// Several kinds of side curve, on the same few curves, side by side.
//
//   PATH="$HOME/node24/bin:$PATH" node scripts/side_kinds.mjs
//
// Writes workbench/side-tests.html. Every kind is computed from the record, so the panels can
// be compared without any of them becoming the law:
//
//   1. character rail — the current plate law: inside capped at 0.9/kappa, outside at the ask
//   2. speed partner  — the speed pair scaled by (1 - d); a PH position then scales by (1 - d)^2
//   3. parallel offset — a constant normal distance, the mechanical one (expected to fold)
//   4. scaled copy    — the whole spine scaled about its centroid (the rejected one)
//   5. mirror partner — the curve mirrored across its own axis
//
// A stored path uses its own length for the scale, and a linear scale instead of the square.
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import P from "../workbench/plate_math.js";

const ROOT = path.resolve(import.meta.dirname, "..");
const OUT = path.join(ROOT, "workbench", "side-tests.html");
const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));
const byUid = new Map(registry.curves.map((row) => [row.uid, row]));

const UIDS = ["c-0001", "c-0022", "c-0046", "c-0065", "c-0100", "c-0134", "c-0273", "c-0337"];
const D = 0.02;            // the side offset, as a share of the curve's own size
const ASK = 1;             // the character rail's asked width, in percent

const spineOf = (record) => {
  if (Array.isArray(record.path) && record.path.length > 2) {
    return record.path.map(([x, y]) => [x, y]);
  }
  return P.spine(record.speedX || [0], record.speedY || [0], 500).map((s) => [s.x, s.y]);
};

const bbox = (pts) => {
  const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
  return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
};

const centroid = (pts) => {
  const [x0, y0, x1, y1] = bbox(pts);
  return [(x0 + x1) / 2, (y0 + y1) / 2];
};

const scaleAbout = (pts, c, k) => pts.map(([x, y]) => [c[0] + (x - c[0]) * k, c[1] + (y - c[1]) * k]);

const normalsOf = (pts) => pts.map((p, i) => {
  const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
  const tx = b[0] - a[0], ty = b[1] - a[1];
  const len = Math.hypot(tx, ty) || 1;
  return [-ty / len, tx / len];
});

const parallel = (pts, d) => {
  const n = normalsOf(pts);
  return pts.map((p, i) => [p[0] + d * n[i][0], p[1] + d * n[i][1]]);
};

const mirror = (pts) => {
  const [x0, y0, x1, y1] = bbox(pts);
  const axis = (x0 + x1) / 2;
  return pts.map(([x, y]) => [2 * axis - x, y]);
};

function panel(record) {
  const spine = spineOf(record);
  const [x0, y0, x1, y1] = bbox(spine);
  const size = Math.hypot(x1 - x0, y1 - y0) || 1;
  const c = centroid(spine);
  const rows = !record.path;

  const kinds = [];
  // 1. the current law
  const group = rows
    ? (() => { try { return P.group({ speedX: record.speedX, speedY: record.speedY, width: { percent: ASK },
        character: { plus: 1.3, minus: 1.3, profile: "bow" } }); } catch { return null; } })()
    : P.pathGroup(record.path, { widthPercent: ASK, plus: 1.3, minus: 1.3, profile: "bow" });
  kinds.push({
    name: "character rail",
    sides: group && group.paths.length > 2 ? group.paths.slice(1, 3) : [],
    note: group ? `${Number(group.width).toFixed(2)} % inside … ${Math.max(Number(group.widthPlus), Number(group.widthMinus)).toFixed(2)} % outside` : "no band",
  });
  // 2. the speed partner: a PH position scales by (1-d)^2; a path scales linearly
  const k2 = rows ? (1 - D) ** 2 : 1 - D;
  // a row curve's position is the integral of the speed, so scaling the speed scales the
  // position about the ORIGIN; a stored path has no speed, and scales about its centre
  kinds.push({
    name: "speed partner",
    sides: [scaleAbout(spine, rows ? [0, 0] : c, k2)],
    note: rows ? `speed x ${(1 - D).toFixed(2)} -> position x ${k2.toFixed(3)} about the origin`
               : `path scaled ${k2.toFixed(3)} about its centre`,
  });
  // 3. the mechanical parallel
  kinds.push({ name: "parallel offset", sides: [parallel(spine, D * size), parallel(spine, -D * size)], note: `constant ${(D * 100).toFixed(1)} % of the size` });
  // 4. the rejected scaled copy
  kinds.push({ name: "scaled copy", sides: [scaleAbout(spine, c, 1 + D), scaleAbout(spine, c, 1 - D)], note: "the whole outline scaled" });
  // 5. a mirror partner
  kinds.push({ name: "mirror partner", sides: [mirror(spine)], note: "reflected across the box centre" });

  const panels = kinds.map((kind) => {
    const all = [spine, ...kind.sides].flat();
    const [ax, ay, bx, by] = bbox(all);
    const w = 260, h = 200, margin = 14;
    const k = Math.min((w - 2 * margin) / (bx - ax || 1), (h - 2 * margin - 18) / (by - ay || 1));
    const ox = (w - (bx - ax) * k) / 2, oy = (h - (by - ay) * k) / 2;
    const put = ([x, y]) => [ox + (x - ax) * k, h - (oy + (y - ay) * k) - 18];
    const line = (pts, colour, width) => '<path d="M ' +
      pts.map((p) => put(p).map((v) => v.toFixed(1)).join(" ")).join(" L ") +
      `" fill="none" stroke="${colour}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round"/>`;
    const body = line(spine, "#2b2b2b", 1.6) + kind.sides.map((side) => line(side, "#a06a2c", 1.2)).join("");
    return `<figure class="panel"><svg viewBox="0 0 ${w} ${h}" width="${w}" height="${h}">
      <rect width="${w}" height="${h}" fill="#fff"/>${body}
      <text x="10" y="${h - 5}" font-family="ui-monospace, Menlo, monospace" font-size="11" fill="#5a4a36">${kind.name}</text>
    </svg><figcaption>${kind.note}</figcaption></figure>`;
  }).join("");

  return `<section class="curve"><h2>${record.uid} · ${record.name}</h2><div class="row">${panels}</div></section>`;
}

const sections = UIDS.map((uid) => byUid.get(uid)).filter(Boolean).map(panel).join("\n");

// ---- Tschirnhausen, and four variations --------------------------------------------------
// y^2 = x^2 (x + 3), parametrised x = t^2 - 3, y = t (t^2 - 3). The node sits at t = ±√3,
// which is irrational, so the curve has no integer parameter for its crossing point.
const tschirnhausen = (n = 700, lo = -2.4, hi = 2.4) => {
  const pts = [];
  for (let i = 0; i <= n; i += 1) {
    const t = lo + ((hi - lo) * i) / n;
    pts.push([t * t - 3, t * (t * t - 3)]);
  }
  return pts;
};
const tschVariants = (() => {
  const base = tschirnhausen();
  const turn = (pts, deg) => {
    const a = (-deg * Math.PI) / 180, co = Math.cos(a), si = Math.sin(a);
    return pts.map(([x, y]) => [x * co - y * si, x * si + y * co]);
  };
  const [x0, y0] = [Math.min(...base.map((p) => p[0])), Math.min(...base.map((p) => p[1]))];
  return [
    { name: "Tschirnhausen", sides: [base], note: "x = t² − 3, y = t(t² − 3) · node at t = ±√3" },
    { name: "halved", sides: [base.map(([x, y]) => [x / 2, y / 2])], note: "the same curve at half size" },
    { name: "turned 45°", sides: [turn(base, 45)], note: "sampled: the 45° turn carries √2" },
    { name: "mirrored", sides: [base.map(([x, y]) => [-x, y])], note: "reflected across x = 0" },
  ];
})();
const tschPanel = tschVariants.map((variant) => {
  const all = variant.sides.flat();
  const [ax, ay, bx, by] = bbox(all);
  const w = 260, h = 200, margin = 14;
  const k = Math.min((w - 2 * margin) / (bx - ax || 1), (h - 2 * margin - 18) / (by - ay || 1));
  const ox = (w - (bx - ax) * k) / 2, oy = (h - (by - ay) * k) / 2;
  const put = ([x, y]) => [ox + (x - ax) * k, h - (oy + (y - ay) * k) - 18];
  const line = '<path d="M ' + variant.sides[0].map((p) => put(p).map((v) => v.toFixed(1)).join(" ")).join(" L ") +
    '" fill="none" stroke="#2b2b2b" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>';
  return `<figure class="panel"><svg viewBox="0 0 ${w} ${h}" width="${w}" height="${h}">
    <rect width="${w}" height="${h}" fill="#fff"/>${line}
    <text x="10" y="${h - 5}" font-family="ui-monospace, Menlo, monospace" font-size="11" fill="#5a4a36">${variant.name}</text>
  </svg><figcaption>${variant.note}</figcaption></figure>`;
}).join("");
const tschSection = `<section class="curve"><h2>Tschirnhausen and variations</h2><div class="row">${tschPanel}</div></section>`;
const html = `<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>side curve kinds · curve-lab</title>
<style>
  body { margin: 0; padding: 24px; background: #faf6ec; color: #2b2620;
         font: 14px/1.5 ui-sans-serif, system-ui, sans-serif; }
  h1 { font-size: 20px; margin: 0 0 6px; }
  p.lead { margin: 0 0 20px; color: #5a4a36; max-width: 78ch; }
  .curve { margin: 0 0 22px; }
  .curve h2 { font-size: 14px; margin: 0 0 6px; font-family: ui-monospace, Menlo, monospace; color: #7a5a1f; }
  .row { display: flex; flex-wrap: wrap; gap: 8px; }
  .panel { margin: 0; border: 1px solid #e6dccb; background: #fff; }
  .panel figcaption { font: 10px/1.4 ui-monospace, Menlo, monospace; color: #6b5d49; padding: 4px 6px; }
  .panel svg { display: block; }
</style></head><body>
<h1>Several kinds of side curve</h1>
<p class="lead">The same curve drawn five ways. Black is the spine; the ochre lines are the side
curves the kind produces. Nothing here is the law — it is a comparison bed. The character rail is
the current plate law; the speed partner scales the speed pair (a PH position then scales by the
square); the parallel is the mechanical offset; the scaled copy is the one the operator rejected;
the mirror is the other way to get a partner.</p>
${sections}
${tschSection}
</body></html>`;
writeFileSync(OUT, html);
console.log(`${UIDS.length} curves × 5 kinds -> ${path.relative(ROOT, OUT)}`);
