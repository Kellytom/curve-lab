// One bordered PNG for every curve in the registry, 600 px, plus the measured
// border margin for each. The index page is the Astro route at /figures/.
//
//   node scripts/curve_pngs.mjs
//
// SVG is an intermediate and goes to build/figures-svg (gitignored). The PNGs
// and index.json land in app/public/figures.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { chromium } from "playwright-core";

const { figureFor, svgForFigure } = await import("../app/src/lib/bordered.js");

const ROOT = path.resolve(import.meta.dirname, "..");
const PNG_DIR = path.join(ROOT, "app", "public", "figures");
const SVG_DIR = path.join(ROOT, "build", "figures-svg");
mkdirSync(PNG_DIR, { recursive: true });
mkdirSync(SVG_DIR, { recursive: true });

const only = (() => {
  const at = process.argv.indexOf("--only");
  return at >= 0 ? new Set(process.argv.slice(at + 1).flatMap((v) => v.split(","))) : null;
})();
const allRecords = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8")).curves;
const registry = allRecords.filter((record) => !only || only.has(record.uid));
const byUid = Object.fromEntries(registry.map((record) => [record.uid, record]));
// A curve may name another curve as its border (the note's border_uid). The
// database is the record; this reads its mirror, so the frame drawn here is the
// frame the page shows.
const notes = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-notes.json"), "utf8"));
const borderOf = new Map((notes.curves || []).filter((n) => n.border_uid).map((n) => [n.uid, n.border_uid]));
const items = registry.map((record) => {
  const border = borderOf.get(record.uid);
  const figure = figureFor(record, { [record.name]: record }, border ? byUid[border] : null);
  const svgFile = path.join(SVG_DIR, `${record.uid}.svg`);
  writeFileSync(svgFile, svgForFigure(figure, `${record.uid}: ${record.name}`));
  return {
    record,
    svgFile,
    meta: {
      uid: record.uid,
      name: record.name,
      family: record.family_id,
      perSide: figure.perSide,
      marginPercent: figure.margin,
      failed: figure.failed,
      reason: figure.reason || null,
      tooWide: figure.tooWide || false,
    },
  };
});

const candidates = [
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Chromium.app/Contents/MacOS/Chromium",
];
let browser = null;
for (const executablePath of candidates) {
  try { browser = await chromium.launch({ executablePath, headless: true }); break; } catch { /* next */ }
}
if (!browser) browser = await chromium.launch({ headless: true });

const page = await browser.newPage({ viewport: { width: 600, height: 600 } });
for (const item of items) {
  await page.setContent(
    `<style>html,body{margin:0;background:#fff}svg{display:block;width:600px;height:600px}</style>` +
    readFileSync(item.svgFile, "utf8"),
    { waitUntil: "load" });
  await page.screenshot({ path: path.join(PNG_DIR, `${item.record.uid}.png`), type: "png" });
}
await browser.close();

// The index covers every curve, not only the ones this run drew: a partial run
// (`--only`) must merge, or 270 entries are lost and the gallery empties.
const INDEX = path.join(PNG_DIR, "index.json");
const previousMeta = (() => {
  try {
    return JSON.parse(readFileSync(INDEX, "utf8")).curves || [];
  } catch {
    return [];
  }
})();
const metaByUid = new Map(previousMeta.map((meta) => [meta.uid, meta]));
for (const item of items) metaByUid.set(item.record.uid, item.meta);
const orderedMeta = allRecords
  .map((record) => metaByUid.get(record.uid))
  .filter(Boolean);

writeFileSync(INDEX,
  JSON.stringify({ format: "curve-lab.figures/1", curves: orderedMeta }, null, 1) + "\n");
console.log(`${items.length} bordered PNGs, index now ${orderedMeta.length} curves`);
