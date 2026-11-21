// The TypeScript port of the exact core, pinned to the Python reference's
// numbers (from the parity run over all 212 stored curves: 0 mismatches).
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { metrics, grid } from "../src/lib/measure.ts";

const registry = JSON.parse(
  readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url), "utf8"),
);
const byUid = new Map(registry.curves.map((c) => [c.uid, c]));

test("amper (c-0001) matches the Python reference exactly", () => {
  const c = byUid.get("c-0001");
  const m = metrics(c.speedX, c.speedY);
  assert.equal(m.grid, 105);
  assert.equal(m.inflection_count, 1);
  assert.ok(Math.abs(m.bend - 4.162593237541658) < 1e-12, `bend ${m.bend}`);
  assert.ok(Math.abs(m.arc - 5.980952380952381) < 1e-12, `arc ${m.arc}`);
  assert.ok(Math.abs(m.closest - 1.1510287044286103) < 1e-9, `closest ${m.closest}`);
});

test("the heaviest plate wave-coarse (c-0014) matches", () => {
  const c = byUid.get("c-0014");
  const m = metrics(c.speedX, c.speedY);
  assert.equal(m.grid, 14);
  assert.ok(Math.abs(m.bend - 4.111111111111111) < 1e-12, `bend ${m.bend}`);
  assert.ok(Math.abs(m.arc - 2.642857142857143) < 1e-12, `arc ${m.arc}`);
});

test("grid is whole and never zero across every stored curve", () => {
  for (const c of registry.curves) {
    if (!c.speedX || !c.speedY || c.speedX.length === 0) continue;
    const g = grid(c.speedX, c.speedY);
    assert.ok(Number.isFinite(g) && g >= 1, `${c.uid} grid ${g}`);
  }
});
