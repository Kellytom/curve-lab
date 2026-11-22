// The SVG text layer's tests, pinned to curve_lab/svg.py's laws.
import assert from "node:assert/strict";
import test from "node:test";
import { bbox, escapeXml, gridStep, metadataDesign, parseD, pathD, slug, spanEval, svgNum } from "../src/lib/svg.ts";

const span = { p0: [0, 0], c1: [1, 2], c2: [3, 2], p3: [4, 0] };

test("the number formatter: no exponent, no negative zero, trimmed zeros", () => {
  assert.equal(svgNum(3125), "3125");
  assert.equal(svgNum(0.1), "0.1");
  assert.equal(svgNum(-0.00001), "0");
  assert.equal(svgNum(1.23456, 3), "1.235");
  assert.equal(svgNum(2.5), "2.5");
  assert.throws(() => svgNum(Number.POSITIVE_INFINITY), /non-finite/);
});

test("the path writer emits M then C per span, and its reader recovers them", () => {
  const d = pathD([span, { p0: [4, 0], c1: [5, -2], c2: [7, -2], p3: [8, 0] }]);
  assert.ok(d.startsWith("M 0,0 C "));
  assert.equal((d.match(/C /g) || []).length, 2);
  const parsed = parseD(d);
  assert.equal(parsed[0].command, "M");
  assert.deepEqual(parsed[0].values, [0, 0]);
  assert.equal(parsed[1].command, "C");
  assert.deepEqual(parsed[1].values, [1, 2, 3, 2, 4, 0]);
  assert.equal(parsed[2].values[5], 0); // the second span's end y
});

test("the span evaluates to its endpoints at t = 0 and 1", () => {
  assert.deepEqual(spanEval(span, 0), [0, 0]);
  assert.deepEqual(spanEval(span, 1), [4, 0]);
});

test("the grid step is a round 1/2/2.5/5 × 10^k, about ten lines", () => {
  assert.equal(gridStep(100), 10);
  assert.equal(gridStep(27), 5); // 27/10 = 2.7 → the first round step above it
  assert.equal(gridStep(25), 2.5);
  assert.equal(gridStep(40), 5);
  assert.equal(gridStep(0), 1);
});

test("the bounding box counts control points (the writer's own rule)", () => {
  assert.deepEqual(bbox([span]), [0, 0, 4, 2]);
});

test("a slug keeps alphanumerics and dashes the rest", () => {
  assert.equal(slug("lace-1of10-3-2"), "lace-1of10-3-2");
  assert.equal(slug("swan line/2"), "swan-line-2");
  assert.equal(slug("--x--"), "x");
});

test("the escaper follows the writer's order (ampersand first)", () => {
  assert.equal(escapeXml('a & b < c > d "e"'), "a &amp; b &lt; c &gt; d &quot;e&quot;");
});

test("the design metadata is recovered from a written file", () => {
  const design = { name: "swan", anchor: { x: 0, y: 0, angle: 0 }, segments: [] };
  const text = `<svg><desc id="curve-lab-design">${escapeXml(JSON.stringify(design))}</desc></svg>`;
  assert.deepEqual(metadataDesign(text), design);
  assert.throws(() => metadataDesign("<svg/>"), /no design metadata/);
});
