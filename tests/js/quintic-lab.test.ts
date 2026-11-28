// The quintic sandbox's maths: reduce a stroke to six points, then give it a
// width that thins at the ends. The page draws it; these tests hold the numbers.

import { test } from "node:test";
import assert from "node:assert/strict";

import {
  blendFullness,
  catmullRomPath,
  distanceToQuintic,
  fitLeastSquares,
  outline,
  outlineCrossings,
  outlinePath,
  quinticAt,
  rails,
  reduceStroke,
  resamplePolyline,
  sixPointsEven,
  solveThroughSamples,
  widthAt,
  type Point,
} from "../../app/src/lib/quintic-lab.ts";

const wavy = (n = 61): Point[] =>
  Array.from({ length: n }, (_, i) => {
    const x = 20 + 400 * (i / (n - 1));
    const y = 150 - 55 * Math.sin((2 * Math.PI * i) / (n - 1)) - 12 * Math.sin((4 * Math.PI * i) / (n - 1));
    return [x, y] as Point;
  });

// a straight quintic, in the model's y-up space: the simplest known answer
const straight: Point[] = [[0, 0], [40, 0], [80, 0], [120, 0], [160, 0], [200, 0]];

test("the resampled stroke is even by arc length and keeps both ends", () => {
  const stroke = wavy();
  const out = resamplePolyline(stroke, 40);
  assert.equal(out.length, 41);
  assert.deepEqual(out[0], stroke[0]);
  assert.deepEqual(out[out.length - 1], stroke[stroke.length - 1]);
  const gaps: number[] = [];
  for (let i = 1; i < out.length; i += 1) {
    gaps.push(Math.hypot(out[i][0] - out[i - 1][0], out[i][1] - out[i - 1][1]));
  }
  const mean = gaps.reduce((a, b) => a + b, 0) / gaps.length;
  // a curved stroke's chords vary; the spread stays small, and no gap is huge
  for (const gap of gaps) assert.ok(Math.abs(gap - mean) < mean * 0.35, `gap ${gap} around ${mean}`);
});

test("six even points are on the stroke and the solve goes through all six", () => {
  const chunk = resamplePolyline(wavy(), 60);
  const six = sixPointsEven(chunk);
  assert.equal(six.length, 6);
  assert.deepEqual(six[0], chunk[0]);
  assert.deepEqual(six[5], chunk[chunk.length - 1]);
  const control = solveThroughSamples(six);
  for (let k = 0; k < 6; k += 1) {
    const got = quinticAt(control, k / 5);
    assert.ok(Math.hypot(got[0] - six[k][0], got[1] - six[k][1]) < 1e-6);
  }
});

test("the best fit pins the ends and misses the stroke less than six even points", () => {
  const chunk = resamplePolyline(wavy(), 60);
  const even = solveThroughSamples(sixPointsEven(chunk));
  const fitted = fitLeastSquares(chunk);
  assert.deepEqual(fitted[0], chunk[0]);
  assert.deepEqual(fitted[5], chunk[chunk.length - 1]);
  const worst = (control: Point[]) => Math.max(...chunk.map((p) => distanceToQuintic(p, control)));
  assert.ok(worst(fitted) < worst(even), `${worst(fitted)} should beat ${worst(even)}`);
});

test("fullness is the chord at zero and the guide at one", () => {
  const guide: Point[] = [[0, 0], [10, 40], [30, 70], [50, 70], [70, 40], [90, 0]];
  assert.deepEqual(blendFullness(guide, 1), guide);
  const flat = blendFullness(guide, 0);
  for (let i = 1; i < 5; i += 1) {
    assert.ok(Math.abs(flat[i][1]) < 1e-9, "a zero fullness is a straight chord");
  }
});

test("more spans means a smaller miss against the stroke", () => {
  const stroke = wavy();
  const miss = (spans: number) => Math.max(...reduceStroke(stroke, { mode: "lsq", spans, fullness: 1, tolerance: 0.01 }).map((s) => s.strokeMiss));
  const one = miss(1);
  const three = miss(3);
  assert.ok(three < one, `3 spans ${three} should beat 1 span ${one}`);
});

test("the width profile is thin at the ends and widest at its peak", () => {
  const profile = { ends: 1, middle: 14, peak: 0.5, power: 1 };
  assert.ok(Math.abs(widthAt(0, profile) - 1) < 1e-9);
  assert.ok(Math.abs(widthAt(1, profile) - 1) < 1e-9);
  assert.ok(Math.abs(widthAt(0.5, profile) - 14) < 1e-9);
  assert.ok(widthAt(0.25, profile) > 1 && widthAt(0.25, profile) < 14);
  const shifted = { ends: 2, middle: 10, peak: 0.25, power: 2 };
  assert.ok(widthAt(0.25, shifted) > widthAt(0.75, shifted));
});

test("a constant width on a straight line gives two parallel sides", () => {
  const control = solveThroughSamples(straight);
  const sides = rails(control, 6, 60);
  for (const p of sides.left) assert.ok(Math.abs(p[1] - 6) < 1e-6, `left y ${p[1]}`);
  for (const p of sides.right) assert.ok(Math.abs(p[1] + 6) < 1e-6, `right y ${p[1]}`);
  assert.equal(outlineCrossings(sides), 0);
});

test("the swell is measured: narrow at the ends, widest in the middle", () => {
  const control = solveThroughSamples(straight);
  const sides = outline(control, { ends: 1, middle: 12, peak: 0.5, power: 1 }, 80);
  assert.ok(Math.abs(sides.widest - 12) < 1e-9);
  assert.ok(Math.abs(sides.narrowest - 1) < 1e-9);
  const atEnd = Math.abs(sides.left[0][1]);
  const atMiddle = Math.abs(sides.left[40][1]);
  assert.ok(atEnd < atMiddle, `end ${atEnd} should be thinner than middle ${atMiddle}`);
});

test("the outline path closes and is drawn with cubics", () => {
  const control = solveThroughSamples(straight);
  const plot = (p: Point) => `${p[0].toFixed(2)},${p[1].toFixed(2)}`;
  const d = outlinePath(outline(control, { ends: 1, middle: 12, peak: 0.5, power: 1 }, 40), plot);
  assert.ok(d.startsWith("M "));
  assert.ok(d.trim().endsWith("Z"));
  assert.ok((d.match(/C /g) || []).length > 20, "a sampled side must be a cubic chain, not a zigzag");
});

test("the Catmull-Rom chain passes through every sample", () => {
  const pts: Point[] = [[0, 0], [10, 10], [20, 0], [30, -10], [40, 0]];
  const d = catmullRomPath(pts, (p) => `${p[0]},${p[1]}`);
  // every sample appears as a segment end point
  for (const p of pts.slice(1)) {
    assert.ok(d.includes(`C`) && d.includes(`${p[0]},${p[1]}`), `missing ${p}`);
  }
});
