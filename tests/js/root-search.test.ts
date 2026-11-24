import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { candidate, polyFromRoots, describe, closestGrace } from "../../app/src/lib/root-search.ts";

// The TypeScript twin of scripts/root_search.py. The pinned row is from the committed
// workbench/root-candidates.json, which the Python script wrote.

const committed = JSON.parse(readFileSync(new URL("../../workbench/root-candidates.json", import.meta.url), "utf8")) as {
  candidates: Array<Record<string, unknown>>;
};

test("the polynomial clears its denominators exactly", () => {
  // (t - 1/8)(t - 3/4) = t^2 - 7/8 t + 3/32, cleared by 32
  const roots = [{ n: 1n, d: 8n }, { n: 3n, d: 4n }];
  assert.deepEqual(polyFromRoots(roots), [3, -28, 32]);
});

test("the pinned candidate reproduces the committed row", () => {
  const expected = committed.candidates.find((row) => row.name === "pair-1of8-mid1");
  assert.ok(expected);
  const { u, v } = candidate(1, 8, 1);
  assert.deepEqual(u, expected.u);
  assert.deepEqual(v, expected.v);
});

test("the committed set is 60 rows, in the ranking order", () => {
  const rows = committed.candidates;
  assert.equal(rows.length, 60);
  for (let i = 1; i < rows.length; i += 1) {
    const a = rows[i - 1] as { crossings: number; inflections: number; grid: number };
    const b = rows[i] as { crossings: number; inflections: number; grid: number };
    const ordered = a.crossings > b.crossings
      || (a.crossings === b.crossings && a.inflections > b.inflections)
      || (a.crossings === b.crossings && a.inflections === b.inflections && a.grid <= b.grid);
    assert.ok(ordered, `rows ${i - 1} and ${i} are out of order`);
  }
});

test("the pinned candidate's numbers reproduce the committed row", () => {
  const expected = committed.candidates.find((row) => row.name === "pair-1of8-mid1") as {
    grid: number; bend: number; inflections: number; crossings: number; places: number; grace: number;
  };
  const { u, v } = candidate(1, 8, 1);
  const facts = describe(u, v);
  assert.equal(facts.grid, expected.grid);
  assert.equal(facts.inflections, expected.inflections);
  assert.equal(facts.crossings, expected.crossings);
  assert.equal(facts.places, expected.places);
  assert.ok(Math.abs(facts.bend - expected.bend) < 1e-4, `bend ${facts.bend}`);
  assert.ok(Math.abs(closestGrace(u, v) - expected.grace) < 2e-4);
});
