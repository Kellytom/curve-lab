import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { rowFor, DEFAULTS, TARGET_GAP_PERCENT, presetWidthPercent } from "../../scripts/lib/plate-row.mjs";
import P from "../../workbench/plate_math.js";

// The operator's words: "I CANT BELIEVE WE ARE DEALING WITH PARALLEL CURVE".
// They were right. The plate's row builder carried a duplicate `character:` key, and the
// second key won, so plus and minus were always 0 — a plain parallel offset — whatever the
// desk said. These tests fail if the desk's values ever stop reaching the plate again.

const curve = (() => {
  const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));
  return registry.curves.find((row) => row.name === "curlicue");
})();

const record = { name: curve.name, speedX: curve.speedX, speedY: curve.speedY };

test("the desk's plus and minus reach the plate row", () => {
  const row = rowFor(record, { desk: { widthPct: 6, plus: 2.5, minus: 0.1, profile: "bow" } });
  assert.equal(row.character.plus, 2.5);
  assert.equal(row.character.minus, 0.1);
  assert.equal(row.width.percent, 6);
});

test("a note wins over the desk row, and the desk row wins over the defaults", () => {
  const noted = rowFor(record, { note: { width_pct: 9, plus: 1 }, desk: { widthPct: 6, plus: 2.5 } });
  assert.equal(noted.width.percent, 9);
  assert.equal(noted.character.plus, 1);
  assert.equal(noted.character.minus, DEFAULTS.minus);

  const bare = rowFor(record);
  assert.equal(bare.width.percent, presetWidthPercent(bare.character));
  assert.equal(bare.character.plus, DEFAULTS.plus);
});

// behaviour, not a string: build the plate's own group and measure the two sides
const offsets = (row) => {
  const group = P.group(row);
  assert.ok(group.paths.length >= 3, "spine and two rails expected");
  const [spine, plusRail, minusRail] = group.paths;
  assert.equal(plusRail.length, spine.length, "a rail runs station for station with the spine");
  assert.equal(minusRail.length, spine.length);
  const distance = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);
  const spread = (rail) => {
    const widths = spine.map((p, i) => distance(p, rail[i]));
    return { min: Math.min(...widths), max: Math.max(...widths) };
  };
  return { plus: spread(plusRail), minus: spread(minusRail) };
};

test("an asymmetric row draws two different sides, not one parallel pair", () => {
  const row = rowFor(record, { desk: { widthPct: 6, plus: 2.5, minus: 0.1, profile: "bow" } });
  const { plus, minus } = offsets(row);
  assert.ok(plus.max / plus.min > 2, `the + rail must widen along the curve, got ${plus.max / plus.min}`);
  assert.ok(minus.max / minus.min < 1.3, `the - rail is nearly straight, got ${minus.max / minus.min}`);
});

test("plus = minus = 0 is the only case that is a parallel offset", () => {
  const row = rowFor(record, { desk: { widthPct: 6, plus: 0, minus: 0, profile: "bow" } });
  const { plus, minus } = offsets(row);
  const flat = (s) => Math.abs(s.max - s.min) < 1e-9;
  assert.ok(flat(plus) && flat(minus), "zero character must be a true parallel offset");
});

test("the preset solves for the drawn gap, not a fixed width", () => {
  // The operator, 2026-11-22: "half are too thin and half are too thick ... you should have
  // algorithms to figure that out already and fix it before i even see it. right? check the
  // thickness". The good references are c-0001a (1.9 % drawn gap) and c-0161 (2.3 %), so the
  // preset solves the base width that puts the drawn median gap at 2 % of the curve's size.
  assert.equal(TARGET_GAP_PERCENT, 2);
  assert.equal(DEFAULTS.plus, 2.5);
  assert.equal(DEFAULTS.minus, 0.1);
  const row = rowFor(record);
  assert.ok(row.width.percent > 0.9 && row.width.percent < 1.2,
    `the 2 % target is about 1.07 % of base width, got ${row.width.percent}`);

  // behaviour: measure the drawn gap on a row curve whose guard does not bind (c-0010)
  const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));
  const wide = registry.curves.find((r) => r.uid === "c-0010");
  const wideRow = rowFor({ name: wide.name, speedX: wide.speedX, speedY: wide.speedY });
  // the plates draw both sides at one strength, the average of the saved pair
  const strength = (Math.abs(wideRow.character.plus) + Math.abs(wideRow.character.minus)) / 2;
  const group = P.group({ ...wideRow, character: { ...wideRow.character, plus: strength, minus: strength } });
  const [spine, ...rails] = group.paths;
  const xs = spine.map((p) => p[0]), ys = spine.map((p) => p[1]);
  const size = Math.hypot(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys));
  const gaps = rails.slice(0, 2).flatMap((rail) =>
    spine.map((p, i) => Math.hypot(rail[i][0] - p[0], rail[i][1] - p[1]))).sort((a, b) => a - b);
  const median = gaps[Math.floor(gaps.length / 2)] / size * 100;
  assert.ok(Math.abs(median - TARGET_GAP_PERCENT) < 0.5,
    `the drawn median gap is ${median.toFixed(2)} %, not the 2 % target`);

  assert.equal(rowFor(record, { desk: { widthPct: 6 } }).width.percent, 6,
    "a saved row always keeps its own width");
});

test("a placeholder zero in a note does not win over the desk row", () => {
  // The 2026-11 note migration wrote 0 into width, plus and minus for untouched curves;
  // taking those zeros at face value drew a 0 % band, and plus = minus = 0 is a parallel
  // offset. The desk row's tuned values must still reach the plate.
  const row = rowFor(record, {
    note: { widthPct: 0, plus: 0, minus: 0, profile: null },
    desk: { widthPct: 1, plus: 2.5, minus: 0.1, profile: "bow" },
  });
  assert.equal(row.width.percent, 1);
  assert.equal(row.character.plus, 2.5);
  assert.equal(row.character.minus, 0.1);
  assert.equal(row.character.profile, "bow");
});

test("a stored path takes the preset like every other curve", () => {
  // The operator, 2026-11-21: "i didnt ask for spines only. i asked for clean curves like
  // the first two." The doubles and flourishes are stored paths, but a zero or missing note
  // is the placeholder here too; the preset band applies. A saved width still wins.
  const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));
  const path = registry.curves.find((row) => Array.isArray(row.path) && row.path.length > 2);
  assert.ok(path, "a stored-path record is needed for this test");
  for (const note of [{ widthPct: 0, plus: 0, minus: 0, profile: null }, {}]) {
    const row = rowFor(path, { note, desk: {} });
    assert.equal(row.width.percent, presetWidthPercent(row.character));
    assert.equal(row.character.plus, DEFAULTS.plus);
    assert.equal(row.character.minus, DEFAULTS.minus);
  }
  const saved = rowFor(path, { note: { widthPct: 1.5, plus: 2, minus: 2, profile: "bow" }, desk: {} });
  assert.equal(saved.width.percent, 1.5);
});
