// The plate maths and the exported files, all in JS.
// Run: node --test tests/js
const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const PlateMath = require("../../workbench/plate_math.js");

const ROOT = path.resolve(__dirname, "../..");
const manifest = JSON.parse(fs.readFileSync(path.join(ROOT, "book/plates.json")));
const curves = JSON.parse(fs.readFileSync(path.join(ROOT, "workbench/real-curves.json")));
const rows = Object.fromEntries(curves.curves.map((row) => [row.name, row]));

test("a railed curve is the spine, two rails and four caps", () => {
  const group = PlateMath.group(rows.amper);
  assert.equal(group.paths.length, 7);
  assert.ok(group.note.includes("character rails"));
});

test("a curve whose rail folds is spine only", () => {
  const group = PlateMath.group(rows["inflect-2"]);
  assert.equal(group.paths.length, 1);
  assert.ok(group.note.includes("spine only"));
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
    const png = fs.readFileSync(path.join(ROOT, "book/plates", `${plate.id}.png`));
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

test("the gallery has the starred section, the simple designs and the singles", () => {
  const gallery = fs.readFileSync(path.join(ROOT, "book/index.html"), "utf8");
  assert.ok(gallery.includes("Framed Quintic symmetric figures"));
  assert.ok(gallery.includes("Simple framed symmetric central figures"));
  assert.ok(gallery.includes("Single curves"));
  const starredPath = path.join(ROOT, "workbench/starred.json");
  const starred = fs.existsSync(starredPath)
    ? (JSON.parse(fs.readFileSync(starredPath, "utf8")).plates || []).length : 0;
  assert.equal((gallery.match(/<img /g) || []).length, manifest.plates.length + starred);
});
