// The 90 named curves, as framed illuminations, A/B/C/D.
//
//   node scripts/frames_build.mjs            # report only
//   node scripts/frames_build.mjs --write    # render the four, write the list
//
// A is the curve as the database says it is (the note's offsets, width, plus,
// minus, profile). B forces the offsets on, filled, for the centre and the
// border. C adds the corner rule from the two leg directions: a natural 90°
// corner turns the motif, everything else stops the band at the corner. D is C
// plus the seam and the proportion. Each row carries the numbers and one short
// `note`, so the page prints the same words the file holds.
//
// The figure is named `illus-<name>` with the last postfix dropped — the
// variant number is what changed, not the plate — except where dropping it
// would give two plates one name; there the whole name is kept. The twins are
// `illus-<name>-B`, `-C`, `-D`.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright-core";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const WRITE = process.argv.includes("--write");
const FRAMES_DIR = path.join(ROOT, "app", "public", "frames");
const SVG_DIR = path.join(ROOT, "build", "frames-svg");
const require = createRequire(import.meta.url);
const P = require(path.join(ROOT, "workbench", "plate_math.js"));

const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));
const notes = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-notes.json"), "utf8"));
const figures = JSON.parse(readFileSync(path.join(ROOT, "app", "public", "figures", "index.json"), "utf8"));

const noteByUid = new Map((notes.curves || []).map((note) => [note.uid, note]));
const figureByUid = new Map((figures.curves || []).map((figure) => [figure.uid, figure]));
const byUid = new Map(registry.curves.map((curve) => [curve.uid, curve]));

// A curve is chosen when its note does not set it aside, and it has a name.
const chosen = registry.curves
  .filter((curve) => !(noteByUid.get(curve.uid)?.candidate))
  .map((curve) => {
    const note = noteByUid.get(curve.uid) || {};
    return { ...curve, chosenName: note.name || curve.name };
  });

const dropPostfix = (name) => {
  const match = String(name).match(/-(\d+)$/);
  return match ? name.slice(0, -(match[1].length + 1)) : name;
};

// One plate, one name: where two curves reduce to the same base, keep both
// numbers rather than let one overwrite the other.
const baseCount = new Map();
for (const curve of chosen) {
  const base = dropPostfix(curve.chosenName);
  baseCount.set(base, (baseCount.get(base) || 0) + 1);
}

const settingsOf = (note) => ({
  offsets: note.offsets ?? 0,
  widthPct: note.widthPct ?? 0,
  plus: note.plus ?? 0,
  minus: note.minus ?? 0,
  profile: note.profile ?? null,
});

// The two leg directions from the sampled path: the tangent over the first and
// the last few stations. `delta` is the gap in degrees, 0..180.
function legGap(curve) {
  const points = curve.path || P.spine(curve.speedX, curve.speedY, 400).map((s) => [s.x, s.y]);
  const n = points.length;
  const angle = (a, b) => (Math.atan2(b[1] - a[1], b[0] - a[0]) * 180) / Math.PI;
  const leg0 = angle(points[0], points[Math.min(4, n - 1)]);
  // The end leg points out of the curve, so a monotone line reads 180°.
  const leg1 = angle(points[n - 1], points[Math.max(0, n - 5)]);
  let delta = Math.abs(leg1 - leg0);
  if (delta > 180) delta = 360 - delta;
  return Math.round(delta);
}

// Within 20° of a right angle, the motif turns and splits the corner; every
// other curve stops the band with a plain cap.
function cornerRule(delta) {
  const corner = Math.abs(delta - 90) <= 20;
  return {
    cornerRule: corner ? "corner" : "stop",
    cornerGap: corner ? Math.round((Math.abs(90 - delta) / 2) * 10) / 10 : null,
  };
}

function noteFor(row) {
  const parts = [];
  if (row.variant === "A") parts.push("A: as stored.");
  if (row.variant === "B") parts.push("B: offsets on, band filled.");
  if (row.variant === "C") {
    parts.push(row.cornerRule === "corner"
      ? `C: delta ${row.delta}°, corner ${row.cornerGap}°.`
      : `C: delta ${row.delta}°, stop.`);
  }
  if (row.variant === "D") parts.push("D: C plus a declared waist gap and 50% centre / 9% band.");
  if (row.cornerRule === "corner" && row.cornerGap > 2) parts.push("Miter visible at the corners.");
  if (row.seam === "crossing") parts.push("The waist still crosses.");
  if (row.variant === "A" && row.offsets === 0) parts.push("Try the rails.");
  return parts.join(" ");
}

const rows = chosen.flatMap((curve) => {
  const base = dropPostfix(curve.chosenName);
  const shared = (baseCount.get(base) || 0) > 1;
  const illus = `illus-${shared ? curve.chosenName : base}`;
  const note = noteByUid.get(curve.uid) || {};
  const settings = settingsOf(note);
  const figure = figureByUid.get(curve.uid) || {};
  const delta = legGap(curve);
  const { cornerRule: rule, cornerGap } = cornerRule(delta);
  const common = {
    uid: curve.uid,
    name: curve.chosenName,
    sharedBase: shared,
    perSide: figure.perSide ?? null,
    marginPercent: figure.marginPercent ?? null,
    tooWide: Boolean(figure.tooWide),
    failed: Boolean(figure.failed),
    delta,
    cornerGap,
    cornerRule: rule,
  };
  const rowFor = (variant, extra) => {
    const row = {
      ...common,
      illus: variant === "A" ? illus : `${illus}-${variant}`,
      variant,
      ...settings,
      ...extra,
    };
    row.frame = `/frames/${row.illus}.png`;
    row.note = noteFor(row);
    return row;
  };
  return [
    rowFor("A", {}),
    rowFor("B", { offsets: 1 }),
    rowFor("C", { offsets: 1 }),
    rowFor("D", { offsets: 1, seam: "gap" }),
  ];
});

const chosenUids = new Set(rows.map((row) => row.uid));
const notesOnly = registry.curves
  .filter((curve) => !chosenUids.has(curve.uid))
  .map((curve) => ({
    uid: curve.uid,
    name: curve.name,
    candidate: Boolean(noteByUid.get(curve.uid)?.candidate),
    figure: `/figures/${curve.uid}.png`,
  }));

const missingFigure = [...new Set(rows.map((row) => row.uid))]
  .filter((uid) => !figureByUid.has(uid));
const shared = rows.filter((row) => row.variant === "A" && row.sharedBase);

console.log(`chosen ${rows.length / 4}; A/B/C/D rows ${rows.length}; figures present ${rows.length / 4 - missingFigure.length}; listed as [NOTE] ${notesOnly.length}`);
for (const row of shared) console.log(`  name kept: ${row.name} -> ${row.illus}`);
if (missingFigure.length) for (const uid of missingFigure) console.log(`  MISSING figure: ${uid}`);

if (WRITE) {
  mkdirSync(FRAMES_DIR, { recursive: true });
  mkdirSync(SVG_DIR, { recursive: true });
  const { figureFor, svgForFigure } = await import("../app/src/lib/bordered.js");

  const browser = await chromium.launch({
    executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    headless: true,
  });
  const page = await browser.newPage({ viewport: { width: 600, height: 600 } });
  let rendered = 0;
  for (const row of rows) {
    const curve = byUid.get(row.uid);
    if (!curve) continue;
    const note = noteByUid.get(row.uid) || {};
    const record = {
      ...curve,
      ...settingsOf(note),
      ...(row.variant === "B" ? { offsets: 1 } : {}),
    };
    const figure = figureFor(record, {}, null);
    const svg = svgForFigure(figure, `${row.illus}: ${row.name}`);
    const svgFile = path.join(SVG_DIR, `${row.illus}.svg`);
    writeFileSync(svgFile, svg);
    await page.setContent(
      `<style>html,body{margin:0;background:#fff}svg{display:block;width:600px;height:600px}</style>${svg}`,
      { waitUntil: "load" });
    await page.screenshot({ path: path.join(FRAMES_DIR, `${row.illus}.png`), type: "png" });
    rendered += 1;
  }
  await browser.close();

  const frames = {
    format: "curve-lab.frames/1",
    note: "the 90 chosen curves as framed illuminations, A, B, C, D; names are illus-<name> with the last postfix dropped; the PNGs are thumbnails, not print plates",
    thumbnailPixels: 600,
    curves: rows,
    notes: notesOnly,
  };
  writeFileSync(path.join(ROOT, "workbench", "frames.json"), JSON.stringify(frames, null, 1) + "\n");

  const lines = [
    "# FRAMES-int — the 90 chosen curves as framed illuminations",
    "",
    "Generated by `node scripts/frames_build.mjs --write`. Do not edit by hand.",
    "",
    `- **${rows.length / 4}** plates, each named \`illus-<name>\`, the last postfix dropped, with **A**, **B**, **C** and **D**.`,
    "- **A** is the note's stored offsets; **B** forces the offsets on, filled, for the centre and the border; **C** adds the corner rule from the two leg directions; **D** is C plus a declared waist gap and the 50% centre / 9% band.",
    "- The PNGs are **thumbnails** (600 px), kept so the set can be seen and ordered.",
    "  Print plates are a later step; nothing here is a final export.",
    `- **${shared.length}** kept the postfix, because two curves share a base: ${shared.map((row) => `${row.name} → ${row.illus}`).join("; ") || "none"}.`,
    `- **${notesOnly.length}** curves in \`/figures\` are not among the 90 and are marked **[NOTE]** below.`,
    "",
    "The frame rule is the lab's (see `state/DESIGN-int.md` §Square and frame): the",
    "side is n × the curve's chord, the border is the same curve repeated, and the",
    "figure is tight to the drawn marks with a 1.2% margin.",
    "",
    "## The 90",
    "",
    "| plate | source name | uid | a side | border % | offsets (A) | delta | rule |",
    "|---|---|---|---|---|---|---|---|",
    ...rows.filter((row) => row.variant === "A").map((row) => `| ${row.illus} | ${row.name} | ${row.uid} | ${row.perSide ?? "?"} | ${row.marginPercent ?? "?"} | ${row.offsets} | ${row.delta}° | ${row.cornerRule} |`),
    "",
    "## [NOTE] — framed, not yet named",
    "",
    "These are on `/figures` and have no chosen name. Move one to the top of the",
    "naming desk with **restore** on `/finder-candidates` (it is a candidate), or",
    "name it directly if it is not.",
    "",
    "| uid | name | current state |",
    "|---|---|---|",
    ...notesOnly.map((row) => `| ${row.uid} | ${row.name} | ${row.candidate ? "candidate" : "chosen but unnamed?"} |`),
    "",
  ];
  writeFileSync(path.join(ROOT, "state", "FRAMES-int.md"), lines.join("\n"));
  console.log(`wrote workbench/frames.json, ${rendered} A/B/C/D PNGs, state/FRAMES-int.md`);
}
