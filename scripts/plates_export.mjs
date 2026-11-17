// Export the book plates: SVG, PNG at 300 dpi, and the gallery. All in JS.
//
//   node scripts/plates_export.mjs
//
// Reads book/plates.json and workbench/real-curves.json, composes each plate
// with workbench/plate_math.js, writes book/svg/<id>.svg and book/render.html,
// screenshots every plate with Playwright, stamps 300 dpi, then writes
// book/index.html. No Python in the path.

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { createRequire } from "node:module";
import { resolve } from "node:path";
import { chromium } from "playwright-core";

const require = createRequire(import.meta.url);
const PlateMath = require("../workbench/plate_math.js");

const ROOT = resolve(import.meta.dirname, "..");
const BOOK = resolve(ROOT, "book");
const SVG_DIR = resolve(BOOK, "svg");
const PNG_DIR = resolve(BOOK, "plates");
const DPI = 300;
const MARGIN_SHARE = 0.012;

const manifest = JSON.parse(readFileSync(resolve(BOOK, "plates.json"), "utf8"));
const curveData = JSON.parse(readFileSync(resolve(ROOT, "workbench", "real-curves.json"), "utf8"));
if (curveData.count !== curveData.curves.length) {
  throw new Error("real-curves.json: count does not match the curve list");
}
for (const row of curveData.curves) {
  const speeds = [...row.speedX, ...row.speedY].map(Number);
  if (!speeds.some((value) => value !== 0)) {
    throw new Error(`real-curves.json: ${row.name} has no nonzero speed`);
  }
}
const rows = Object.fromEntries(curveData.curves.map((row) => [row.name, row]));

// Stars from the lab: the lab cannot write a file, so it downloads
// workbench/starred.json and the operator drops it in. Absent is not an error.
const starredPath = resolve(ROOT, "workbench", "starred.json");
let starred = [];
if (existsSync(starredPath)) {
  const data = JSON.parse(readFileSync(starredPath, "utf8"));
  starred = (data.plates || []).map((plate) => ({ ...plate, kind: "star" }));
}

// -- the plate ---------------------------------------------------------------

function compose(plate) {
  if (plate.kind === "star") {
    const patched = { ...rows };
    const patch = (name) => {
      if (!name || !rows[name]) return;
      patched[name] = {
        ...rows[name],
        width: { percent: plate.width ?? (rows[name].width || {}).percent ?? 1.5 },
        character: {
          plus: plate.plus ?? (rows[name].character || {}).plus ?? 2,
          minus: plate.minus ?? (rows[name].character || {}).minus ?? 2,
          profile: plate.profile ?? (rows[name].character || {}).profile ?? "bow",
        },
      };
    };
    patch(plate.curve); patch(plate.curveB);
    if (plate.form === "single") {
      const group = PlateMath.group(patched[plate.curve]);
      return { paths: group.paths, bbox: PlateMath.bbox(group.paths.flat()),
               note: `${group.note} · starred` };
    }
    const data = PlateMath.design({
      form: plate.form, curve: plate.curve, curveB: plate.curveB,
      leg: plate.leg, pattern: plate.pattern, alternate: plate.alternate,
      frame: plate.frame ? { perWidth: plate.perWidth, perHeight: plate.perHeight } : null,
    }, patched);
    return { paths: data.paths, bbox: data.bbox, note: `${data.note} · starred` };
  }
  if (plate.kind === "design") {
    const data = PlateMath.design(plate, rows);
    const symmetry = rows[plate.curve] && rows[plate.curve].symmetry;
    return { paths: data.paths, bbox: data.bbox,
             note: data.note + (symmetry ? ` · curve ${symmetry.kind}` : "") };
  }
  const group = PlateMath.group(rows[plate.name]);
  const symmetry = rows[plate.name] && rows[plate.name].symmetry;
  return { paths: group.paths, bbox: PlateMath.bbox(group.paths.flat()),
           note: group.note + (symmetry ? ` · ${symmetry.kind}` : "") };
}

function plateSvg(composed, longSide, strokeShare) {
  const [x0, y0, x1, y1] = composed.bbox;
  const width = x1 - x0, height = y1 - y0;
  let pxW, pxH;
  if (width >= height) { pxW = longSide; pxH = Math.max(1, Math.round(longSide * height / width)); }
  else { pxH = longSide; pxW = Math.max(1, Math.round(longSide * width / height)); }
  const margin = Math.round(MARGIN_SHARE * longSide);
  const innerW = pxW - 2 * margin, innerH = pxH - 2 * margin;
  const k = Math.min(innerW / width, innerH / height);
  const offX = (innerW - width * k) / 2, offY = (innerH - height * k) / 2;
  const put = ([x, y]) => [margin + offX + (x - x0) * k,
                           pxH - (margin + offY + (y - y0) * k)];
  const stroke = Math.max(1, strokeShare * longSide);
  const body = [`<rect width="${pxW}" height="${pxH}" fill="#ffffff"/>`];
  composed.paths.forEach((path) => {
    const text = path.map((p) => { const q = put(p); return `${q[0].toFixed(1)},${q[1].toFixed(1)}`; }).join(" ");
    body.push(`<polyline points="${text}" fill="none" stroke="#111111" `
      + `stroke-width="${stroke.toFixed(2)}" stroke-linecap="round" `
      + `stroke-linejoin="round"/>`);
  });
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${pxW}" height="${pxH}" `
    + `viewBox="0 0 ${pxW} ${pxH}">${body.join("")}</svg>`;
  return { svg, pxW, pxH };
}

// -- png dpi, in JS ----------------------------------------------------------

const CRC = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n += 1) {
    let c = n;
    for (let k = 0; k < 8; k += 1) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[n] = c >>> 0;
  }
  return table;
})();

function crc32(buffer) {
  let c = 0xffffffff;
  for (const byte of buffer) c = CRC[(c ^ byte) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function chunk(type, body) {
  const length = Buffer.alloc(4);
  length.writeUInt32BE(body.length);
  const typeBuffer = Buffer.from(type, "ascii");
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(Buffer.concat([typeBuffer, body])));
  return Buffer.concat([length, typeBuffer, body, crc]);
}

function setDpi(path) {
  const data = readFileSync(path);
  const metres = Math.round(DPI / 0.0254);
  const body = Buffer.alloc(9);
  body.writeUInt32BE(metres, 0);
  body.writeUInt32BE(metres, 4);
  body[8] = 1;
  const parts = [data.subarray(0, 8)];
  let offset = 8;
  let inserted = false;
  while (offset < data.length) {
    const length = data.readUInt32BE(offset);
    const type = data.toString("ascii", offset + 4, offset + 8);
    if (type !== "pHYs") {
      if (type === "IDAT" && !inserted) { parts.push(chunk("pHYs", body)); inserted = true; }
      parts.push(data.subarray(offset, offset + 12 + length));
    }
    offset += 12 + length;
  }
  writeFileSync(path, Buffer.concat(parts));
}

function pngSize(path) {
  const data = readFileSync(path);
  return [data.readUInt32BE(16), data.readUInt32BE(20)];
}

// -- render, screenshot, gallery --------------------------------------------

const plates = [];
[...starred, ...manifest.plates].forEach((plate) => {
  const composed = compose(plate);
  const { svg, pxW, pxH } = plateSvg(composed, manifest.longSide, manifest.strokeShare);
  plates.push({ ...plate, ...composed, svg, pxW, pxH });
});

mkdirSync(SVG_DIR, { recursive: true });
mkdirSync(PNG_DIR, { recursive: true });
plates.forEach((plate) => writeFileSync(resolve(SVG_DIR, `${plate.id}.svg`), plate.svg));

const render = `<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;padding:0;background:#fff}.plate{background:#fff;overflow:hidden;line-height:0}
</style></head><body>${plates.map((p) => `<div class="plate" id="plate-${p.id}" style="width:${p.pxW}px;height:${p.pxH}px">${p.svg}</div>`).join("")}</body></html>`;
writeFileSync(resolve(BOOK, "render.html"), render);

const candidates = [process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"].filter(Boolean);
let browser = null;
for (const executablePath of candidates) {
  try { browser = await chromium.launch({ executablePath, headless: true }); break; } catch { /* next */ }
}
if (!browser) browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 3400, height: 3400 }, deviceScaleFactor: 1 });
await page.goto("file://" + resolve(BOOK, "render.html"), { waitUntil: "load" });
await page.waitForTimeout(200);
for (const plate of plates) {
  await page.locator(`#plate-${plate.id}`).screenshot({
    path: resolve(PNG_DIR, `${plate.id}.png`), animations: "disabled",
  });
}
await browser.close();

// -- the table and the gallery ----------------------------------------------

const fmt = (n) => n.toFixed(2);
console.log("plate                          kind   info                                        pixels  dpi    bytes");
for (const plate of plates) {
  const path = resolve(PNG_DIR, `${plate.id}.png`);
  setDpi(path);
  const [w, h] = pngSize(path);
  const info = plate.kind === "design" || plate.kind === "star"
    ? `${plate.paths.length} paths · ${plate.note}`
    : plate.note;
  console.log(`${plate.id.padEnd(30)} ${plate.kind.padEnd(6)} ${info.slice(0, 42).padEnd(42)} `
    + `${String(w).padStart(4)}x${String(h).padEnd(5)} ${String(DPI).padStart(4)} `
    + `${String(readFileSync(path).length).padStart(8)}`);
}

const starredPlates = plates.filter((plate) => plate.kind === "star");
const designs = plates.filter((plate) => plate.kind === "design");
const singles = plates.filter((plate) => plate.kind === "seed");
const cards = (group) => group.map((plate) =>
  `<figure><img src="plates/${plate.id}.png" width="${plate.pxW}" height="${plate.pxH}" alt="${plate.id}">`
  + `<figcaption><b>${plate.id}</b><br>${plate.note}</figcaption></figure>`).join("");
const gallery = `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Book plates — temporary export</title>
<style>
body{margin:0;background:#fff;color:#111;font:14px/1.55 Georgia,serif}
main{max-width:1120px;margin:0 auto;padding:30px 22px 60px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:17px;margin:34px 0 4px;font-weight:600}
.lead{color:#666;margin:0 0 18px}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:26px}
figure{margin:0}img{width:100%;height:auto;display:block;border:1px solid #eee}
figcaption{font:11px/1.5 ui-monospace,Menlo,monospace;color:#555;margin-top:6px}
</style></head><body><main>
<h1>Book plates — temporary export</h1>
<p class="lead">${plates.length} plates · ${designs.length} central designs and ${singles.length} single curves · white ground, no text on the image, tight to the curve · labels outside, two columns · names are <code>&lt;descriptor&gt;-&lt;variant&gt;-t-exp-c-&lt;serial&gt;</code></p>
<h2>Framed Quintic symmetric figures</h2>
<p class="lead">Starred in the square and frame lab, then exported from <code>workbench/starred.json</code>. ${starredPlates.length ? "" : "No stars yet: star a design in the lab and download the file."}</p>
<div class="grid">${starredPlates.length ? cards(starredPlates) : ""}</div>
<h2>Simple framed symmetric central figures</h2>
<p class="lead">Cross and leaf, each in a frame, every copy carrying its character rails and closed at the ends. The arch is a single-curve plate and a lab form; a natural-leg frame of arches overlaps itself, so it is not offered framed.</p>
<div class="grid">${cards(designs)}</div>
<h2>Single curves</h2>
<p class="lead">${singles.length} plates, one saved curve each with its character rails.</p>
<div class="grid">${cards(singles)}</div>
</main></body></html>`;
writeFileSync(resolve(BOOK, "index.html"), gallery);
console.log(resolve(BOOK, "index.html"));
