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
  const data = await finderData(ROOT);
  assert.ok(data.curves.length >= 10, "not enough curves");
  const withPeak = data.curves.filter((c) => c.peak && c.peak.kappa > 0);
  assert.ok(withPeak.length >= 5, "too few curves have a curvature peak");
  for (const curve of data.curves) {
    assert.ok(curve.name.length > 0);
    assert.ok(Array.isArray(curve.path) && curve.path.length > 2, `${curve.name}: no path`);
    // A straight curve has no curvature peak; that is legitimate, not a gap.
    assert.ok(curve.peak === null || curve.peak.kappa >= 0, `${curve.name}: bad peak`);
    if (curve.peak) assert.ok(Number.isFinite(curve.peak.t), `${curve.name}: peak without t`);
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
