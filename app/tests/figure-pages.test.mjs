import test from "node:test";
import assert from "node:assert/strict";

import { PER_PAGE, pageCount, pageSlice } from "../src/lib/figure-pages.js";

const registry = Array.from({ length: 371 }, (_, index) => ({ uid: `c-${index}` }));

test("the figures sheet is split into pages of fifty", () => {
  assert.equal(PER_PAGE, 50);
  assert.equal(pageCount(371), 8);
  assert.equal(pageCount(0), 1);
  const first = pageSlice(registry, 1);
  assert.equal(first.items.length, 50);
  assert.equal(first.start, 0);
  assert.equal(first.end, 50);
  const last = pageSlice(registry, 8);
  assert.equal(last.items.length, 21);
  assert.equal(last.start, 350);
  assert.equal(last.end, 371);
});

test("an out-of-range or nonsense page clamps to a real page", () => {
  assert.equal(pageSlice(registry, "99").page, 8);
  assert.equal(pageSlice(registry, "abc").page, 1);
  assert.equal(pageSlice(registry, "-3").page, 1);
});

test("every curve appears on exactly one page", () => {
  const seen = [];
  for (let page = 1; page <= pageCount(registry.length); page += 1) {
    seen.push(...pageSlice(registry, page).items.map((item) => item.uid));
  }
  assert.equal(seen.length, registry.length);
  assert.equal(new Set(seen).size, registry.length);
});
