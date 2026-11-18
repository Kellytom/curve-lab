import assert from "node:assert/strict";
import path from "node:path";
import test from "node:test";
import { buildIlluminations } from "../src/lib/bordered.js";

const ROOT = path.resolve(import.meta.dirname, "../..");

test("the gallery has the picked sets, numbered once", () => {
  const gallery = buildIlluminations(ROOT);

  assert.equal(gallery.total, 241);
  assert.deepEqual(
    gallery.sections.map((section) => section.items.length),
    [50, 9, 3, 179],
  );
  assert.match(gallery.sections[0].title, /Fig\. 1.50/);
  assert.match(gallery.sections[3].title, /solve, save, take away/);

  const ids = gallery.sections.flatMap((section) => section.items.map((item) => item.id));
  assert.equal(new Set(ids).size, 241, "an id is repeated");
  assert.deepEqual(ids.slice(0, 3), ["fig-1", "fig-2", "fig-3"]);
  assert.equal(ids.at(-1), "fig-241");

  for (const item of gallery.sections[0].items) {
    assert.match(item.svg, /^<svg/, `${item.name} has no drawing`);
    assert.match(item.svg, /<polyline/, `${item.name} has no path`);
  }
});

test("the roses are the three rational ones, not the old rosettes", () => {
  const gallery = buildIlluminations(ROOT);
  const roses = gallery.sections[2].items.map((item) => item.name);
  assert.deepEqual(roses, [
    "rose-k-2-a-1-b-1",
    "rose-k-2-a-1-b-minus1",
    "rose-k-3-a-1-b-1",
  ]);
});
