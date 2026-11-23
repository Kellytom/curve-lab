// The plate maths and the exported files, all in JS.
// Run: node --test tests/js
const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const PlateMath = require("../../workbench/plate_math.js");

const ROOT = path.resolve(__dirname, "../..");
const manifest = JSON.parse(fs.readFileSync(path.join(ROOT, "book/old-plates.json")));
const curves = JSON.parse(fs.readFileSync(path.join(ROOT, "workbench/real-curves.json")));
const rows = Object.fromEntries(curves.curves.map((row) => [row.name, row]));

test("a railed curve is the spine, two rails and four caps", () => {
  const group = PlateMath.group(rows.amper);
  assert.equal(group.paths.length, 7);
  assert.ok(group.note.includes("character rails"));
});

test("a curve whose rail folds keeps its band and crosses itself", () => {
  // Amended 2026-11-23 with the operator's words: "letting each rail cross itself at a tight
  // turn, marking every crossing with a red dot, hiding the small loop as an invisible span."
  // The inside cap is withdrawn; the rail is the asked offset, so this curve folds, and the
  // plate marks the crossing instead of shortening the band.
  const group = PlateMath.group(rows["inflect-2"]);
  assert.equal(group.paths.length, 7);
  assert.ok(group.fold > 0.9, `fold ${group.fold}`);
  assert.equal(group.buckles, true);
  const crossings = group.paths.slice(1, 3)
    .reduce((count, rail) => count + PlateMath.railHoles(rail).crossings.length, 0);
  assert.ok(crossings > 0, "the fold must cross itself so the plate can mark it");
});

test("a cross in a 3x3 frame is 16 groups of seven paths", () => {
  const spec = manifest.plates.find((plate) => plate.id.startsWith("cross-frame"));
  const design = PlateMath.design(spec, rows);
  assert.equal(design.paths.length, 16 * 7);
  assert.ok(design.note.includes("character rails"));
});

test("a leaf in a 3x3 frame is 14 groups", () => {
  const spec = manifest.plates.find((plate) => plate.id.startsWith("leaf-frame"));
  assert.equal(PlateMath.design(spec, rows).paths.length, 14 * 7);
});

test("every plate has its SVG and a 300 dpi PNG at the long side", () => {
  for (const plate of manifest.plates) {
    const svg = fs.readFileSync(path.join(ROOT, "book/svg", `${plate.id}.svg`), "utf8");
    assert.ok(!svg.includes("<text"), plate.id);
    assert.ok(svg.includes('fill="#ffffff"'), plate.id);
    const width = Number(svg.match(/width="(\d+)"/)[1]);
    const height = Number(svg.match(/height="(\d+)"/)[1]);
    assert.equal(Math.max(width, height), manifest.longSide, plate.id);
    const png = fs.readFileSync(path.join(ROOT, "book/old-plates", `${plate.id}.png`));
    assert.equal(png.readUInt32BE(16), width, plate.id);
    assert.equal(png.readUInt32BE(20), height, plate.id);
    let offset = 8;
    let dpi = 0;
    while (offset < png.length) {
      const length = png.readUInt32BE(offset);
      const type = png.toString("ascii", offset + 4, offset + 8);
      if (type === "pHYs") dpi = Math.round(png.readUInt32BE(offset + 8) * 0.0254);
      offset += 12 + length;
    }
    assert.equal(dpi, 300, plate.id);
  }
});

test("symmetry is measured, and the category follows the operator", () => {
  assert.equal(PlateMath.symmetry(rows["u-bowl"]).kind, "mirror");
  assert.equal(PlateMath.symmetry(rows["swan"]).symmetric, false);
  assert.equal(PlateMath.symmetry(rows["new-symmetric"]).kind, "half-turn");
  assert.equal(rows["u-bowl"].category, "symmetric");
  assert.equal(rows["v-sharp"].category, "asymmetric");  // measured mirror, but not chosen
  assert.equal(rows["swan"].category, "asymmetric");
  assert.equal(rows["lace-1of8-3"].source, "found");
  assert.equal(rows["lace-1of8-3"].category, "symmetric");
  for (const row of curves.curves) {
    assert.ok(row.symmetry, row.name);
    assert.ok(["symmetric", "asymmetric"].includes(row.category), row.name);
  }
});

test("the curve data is whole: count matches, no empty or zero rows", () => {
  assert.equal(curves.count, curves.curves.length);
  for (const row of curves.curves) {
    const speeds = [...row.speedX, ...row.speedY].map(Number);
    assert.ok(speeds.some((value) => value !== 0), row.name);
  }
});

test("a frame pattern can use both curves", () => {
  const a = PlateMath.group(rows.amper);
  const b = PlateMath.group(rows.swan);
  const border = PlateMath.frame(a, b, 2, 2, 45, "ab", false);
  assert.equal(border.length, 8);
  const south = border.filter((item) => item.name === "south");
  assert.deepEqual(south.map((item) => item.letter), ["a", "b"]);
});

test("the gallery is the Astro page, and book/index.html only redirects", async () => {
  // The redirect was re-added (commit 927059e) so an old port still reaches the
  // Astro gallery; the generated gallery itself is gone. app/tests/gallery.test.mjs
  // guards the same file.
  const redirect = fs.readFileSync(path.join(ROOT, "book/index.html"), "utf8");
  assert.match(redirect, /location\.replace/);
  assert.doesNotMatch(redirect, /<figure>/);
  const { buildGallery } = await import(
    require("node:url").pathToFileURL(path.join(ROOT, "app/src/lib/gallery.js")).href);
  const gallery = buildGallery({ root: ROOT, starred: [] });
  assert.equal(gallery.designs.length, 2);
  assert.equal(gallery.designs.length + gallery.singles.length, manifest.plates.length);
});

test("a chain joins b's first point to a's last, and prints the corner", () => {
  const design = PlateMath.design(
    { form: "chain", curve: "u-bowl", curveB: "v-sharp" }, rows);
  assert.match(design.note, /chain/);
  assert.match(design.note, /join -?[0-9.]+°/);
  const first = design.paths[0];
  const second = design.paths[7];  // one railed group is seven paths
  const end = first[first.length - 1];
  const start = second[0];
  assert.ok(Math.hypot(end[0] - start[0], end[1] - start[1]) < 1e-9,
    "the two curves do not meet");
});
