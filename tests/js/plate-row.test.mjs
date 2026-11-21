import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { rowFor, DEFAULTS } from "../../scripts/lib/plate-row.mjs";
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
  assert.equal(bare.width.percent, DEFAULTS.widthPercent);
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

test("an unsaved curve starts at 1.5 % width", () => {
  // The operator, 2026-11-21: "instead of 6%, set width of offsets to 1.5% for the ones i
  // havent saved." 6 % was the old guard's asked width, drawn at about 1.5 after halving;
  // now that the guard is solved directly, the untouched default is the old drawn width.
  assert.equal(DEFAULTS.widthPercent, 1.5);
  assert.equal(rowFor(record).width.percent, 1.5);
  assert.equal(rowFor(record, { desk: { widthPct: 4 } }).width.percent, 4,
    "a saved row always keeps its own width");
});
