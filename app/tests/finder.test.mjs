// The finder page's data: every curve has a drawing, a verdict and a peak.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { finderData, svgPath } from "../src/lib/finder.js";

const APP = fileURLToPath(new URL("..", import.meta.url));
const ROOT = path.resolve(APP, "..");

test("the finder data is whole", async () => {
  const data = finderData(ROOT);
  assert.ok(data.curves.length >= 10, "not enough curves");
  for (const curve of data.curves) {
    assert.ok(curve.name.length > 0);
    assert.ok(Array.isArray(curve.path) && curve.path.length > 2, `${curve.name}: no path`);
    assert.ok(curve.peak && curve.peak.kappa > 0, `${curve.name}: no peak`);
    assert.equal(typeof curve.proper, "boolean", `${curve.name}: no verdict`);
  }
});

test("the page reads the module and draws each curve", async () => {
  const page = await readFile(path.join(APP, "src", "pages", "finder.astro"), "utf8");
  assert.ok(page.includes('from "../lib/finder.js"'));
  assert.ok(page.includes("svgPath"));
  const { d } = svgPath([[0, 0], [1, 1]], 100);
  assert.ok(d.startsWith("M"));
});
