// The gothic desk's maths: the mirror is measured, the cut is symmetric, the arch is built from
// one arm and its mirror, and a half-turn-only curve is refused instead of drawn as a point.
//
// The operator, 2026-11-23: "the curve is mirrored around an x axis already ... from there, move
// back a little for the first cut, and forward the same amount for the second cut."

import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  bestAxis, cutArch, characterOf, integerHits, asFraction, archFigure,
  MIRROR_GAP_LIMIT, MIN_SHARE, MAX_SHARE,
} from "../../app/src/lib/gothic.ts";
import { pointsOf } from "../../app/src/lib/curve-points.ts";

const sample = (f, n = 200) => Array.from({ length: n }, (_, i) => f(i / (n - 1)));
const parabola = sample((t) => [t, (t - 0.5) ** 2]); // mirror: vertical through x = 0.5
const diagonal = sample((t) => [t, 1 - t]); // mirror: y = x (the segment is perpendicular to it)
const odd = sample((t) => [t - 0.5, (t - 0.5) ** 3 + (t - 0.5)]); // half turn only
const wonky = sample((t) => [t, t * t + 0.3 * t]); // no symmetry

test("a vertical mirror through the middle is found exactly", () => {
  const axis = bestAxis(parabola);
  assert.equal(axis.id, "vertical");
  assert.ok(axis.gap < 1e-12, `gap ${axis.gap}`);
});

test("a mirror on y = x is found too", () => {
  const axis = bestAxis(diagonal);
  assert.equal(axis.id, "y=x");
  assert.ok(axis.gap < 1e-12, `gap ${axis.gap}`);
});

test("a curve with no mirror can still be cut from one arm, with the gap carried", () => {
  const forced = cutArch(wonky, { force: true });
  assert.ok(forced);
  assert.equal(forced.mirrored, false);
  assert.ok(forced.gap > MIRROR_GAP_LIMIT);
});

test("a half-turn-only curve is not called mirrored", () => {
  // the odd curve maps to itself under a half turn, but no line mirrors it; a pointed join
  // would be a claim the curve cannot keep
  const axis = bestAxis(odd);
  assert.ok(axis.gap > MIRROR_GAP_LIMIT, `gap ${axis.gap}`);
  assert.equal(cutArch(odd), null);
});

test("the arch is symmetric station for station, apex up and feet level", () => {
  const arch = cutArch(parabola, { share: 0.15 });
  assert.ok(arch);
  const drawn = arch.drawn;
  const size = Math.hypot(
    Math.max(...drawn.map((p) => p[0])) - Math.min(...drawn.map((p) => p[0])),
    Math.max(...drawn.map((p) => p[1])) - Math.min(...drawn.map((p) => p[1])));
  for (let i = 0; i < drawn.length; i += 1) {
    const other = drawn[drawn.length - 1 - i];
    assert.ok(Math.abs(drawn[i][0] + other[0]) < 1e-9 * size, `x pair ${i}`);
    assert.ok(Math.abs(drawn[i][1] - other[1]) < 1e-9 * size, `y pair ${i}`);
  }
  assert.ok(arch.feetLevel < 1e-9);
  const apex = drawn[arch.cutIndex];
  assert.ok(apex[1] >= Math.max(...drawn.map((p) => p[1])) - 1e-9 * size, "apex is the top");
  assert.ok(drawn[0][1] < apex[1], "the feet are below the apex");
});

test("the arch is one stroke: no step over 5 % of its width", () => {
  const arch = cutArch(parabola, { share: 0.2 });
  const drawn = arch.drawn;
  let worst = 0;
  for (let i = 1; i < drawn.length; i += 1) {
    worst = Math.max(worst, Math.hypot(drawn[i][0] - drawn[i - 1][0], drawn[i][1] - drawn[i - 1][1]));
  }
  assert.ok(worst <= 0.05 * arch.width, `worst step ${worst} of width ${arch.width}`);
});

test("a bigger cut keeps less curve and changes the apex angle", () => {
  const small = cutArch(parabola, { share: 0.05 });
  const large = cutArch(parabola, { share: 0.25 });
  assert.ok(large.keptShare < small.keptShare);
  assert.ok(Math.abs(large.apexAngle - small.apexAngle) > 1,
    `angles ${small.apexAngle} and ${large.apexAngle} should differ`);
  assert.ok(small.share >= MIN_SHARE && large.share <= MAX_SHARE);
});

test("the share is clamped to the desk's range", () => {
  const tiny = cutArch(parabola, { share: 0.001 });
  const huge = cutArch(parabola, { share: 4 });
  assert.equal(tiny.share, MIN_SHARE);
  assert.equal(huge.share, MAX_SHARE);
});

test("a zero character value falls through to the preset", () => {
  assert.deepEqual(characterOf({ widthPct: 0, plus: 0, minus: 0, profile: "" }), {
    widthPct: 1.5, plus: 2.5, minus: 0.1, profile: "bow",
  });
  assert.deepEqual(characterOf({ widthPct: 2.2, plus: 6, minus: 1, profile: "s" }), {
    widthPct: 2.2, plus: 6, minus: 1, profile: "s",
  });
});

test("the stored set has mirrored curves, and each one builds an arch", () => {
  const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));
  const measured = registry.curves
    .filter((curve) => Array.isArray(curve.path) && curve.path.length >= 12)
    .map((curve) => ({ curve, axis: bestAxis(curve.path) }))
    .filter((entry) => entry.axis && entry.axis.gap <= MIRROR_GAP_LIMIT);
  assert.ok(measured.length >= 10, `${measured.length} mirrored stored curves`);

  for (const { curve, axis } of measured.slice(0, 5)) {
    const arch = cutArch(curve.path, { axis });
    assert.ok(arch, `${curve.uid} did not build`);
    assert.ok(arch.feetLevel < 1e-9, `${curve.uid} feet level ${arch.feetLevel}`);
    const drawn = arch.drawn;
    assert.ok(Math.abs(drawn[0][0] + drawn[drawn.length - 1][0]) < 1e-6 * arch.width, `${curve.uid} feet`);
    assert.ok(arch.path.length > 3 && arch.keptShare > 0 && arch.keptShare < 1);
  }
});

test("the reference curve c-0273 is cuttable", () => {
  const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));
  const record = registry.curves.find((curve) => curve.uid === "c-0273");
  assert.ok(record && Array.isArray(record.path));
  const axis = bestAxis(record.path);
  assert.ok(axis && axis.gap <= MIRROR_GAP_LIMIT, `gap ${axis && axis.gap}`);
  const arch = cutArch(record.path, { axis });
  assert.ok(arch);
  assert.ok(arch.apexAngle > 0 && arch.apexAngle <= 180);
});

test("a rows record is sampled from its speed polynomials, with the plate's sampler", () => {
  // The operator, 2026-11-23: the "rows only" records are high-degree parametric polynomials,
  // not stored lines — the equation is in the record as speedX / speedY.
  const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));
  const record = registry.curves.find((curve) => curve.uid === "c-0022");
  assert.equal(record.kind, "rows");
  assert.ok(!Array.isArray(record.path));
  const points = pointsOf(record);
  assert.ok(points.length >= 500, `${points.length} stations`);
  assert.ok(points.every(([x, y]) => Number.isFinite(x) && Number.isFinite(y)));
  const axis = bestAxis(points);
  assert.ok(axis && axis.gap <= MIRROR_GAP_LIMIT, `gap ${axis && axis.gap}`);
  const arch = cutArch(points, { axis });
  assert.ok(arch && arch.apexAngle > 0 && arch.apexAngle <= 180);
});

test("a stored path is used as it stands", () => {
  const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));
  const record = registry.curves.find((curve) => curve.uid === "c-0273");
  const points = pointsOf(record);
  assert.equal(points.length, record.path.length);
  assert.deepEqual(points[0], [record.path[0][0], record.path[0][1]]);
});

test("the cut is reported as the exact t pair", () => {
  const dense = sample((t) => [t, (t - 0.5) ** 2], 701);
  const arch = cutArch(dense, { share: 0.1 });
  assert.deepEqual(arch.t.map((value) => asFraction(value)), ["9/20", "11/20"]);
});

test("a requested t step is honoured, and the nearest station is stated", () => {
  const dense = sample((t) => [t, (t - 0.5) ** 2], 701);
  const exact = cutArch(dense, { q: 1 / 20 });
  assert.equal(asFraction(exact.q), "1/20");
  assert.deepEqual(exact.tRequested.map((value) => asFraction(value)), ["9/20", "11/20"]);
  assert.deepEqual(exact.t.map((value) => asFraction(value)), ["9/20", "11/20"]);

  const rough = cutArch(sample((t) => [t, (t - 0.5) ** 2], 200), { q: 1 / 8 });
  assert.deepEqual(rough.tRequested.map((value) => asFraction(value)), ["3/8", "5/8"]);
  // the drawn cut is the nearest stored station, never silently a different request
  assert.ok(Math.abs(rough.t[0] - 0.375) < 1 / 199);
});

test("integer hits are the stations near whole-number points", () => {
  const line = sample((t) => [t * 2, t * 2], 101);
  const hits = integerHits(line);
  assert.deepEqual(hits.map((hit) => [hit.x, hit.y]), [[0, 0], [1, 1], [2, 2]]);
  assert.deepEqual(hits.map((hit) => hit.t), [0, 0.5, 1]);
});

test("the figure has the new arch on top and the original below, at one scale", () => {
  const dense = sample((t) => [t, (t - 0.5) ** 2], 701);
  const arch = cutArch(dense, { share: 0.1 });
  const figure = archFigure(arch, { source: dense, hits: integerHits(dense) });
  assert.match(figure, /the new arch/);
  assert.match(figure, /the original/);
  assert.match(figure, /t = 9\/20 … 11\/20/);
  assert.match(figure, /same scale/);
  assert.equal((figure.match(/<svg/g) || []).length, 1);
  assert.ok(!figure.includes("NaN"), "no path may carry NaN");
});

test("the figure is clean on a real, non-mirrored parent", () => {
  const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));
  const record = registry.curves.find((curve) => curve.uid === "c-0134");
  const points = pointsOf(record);
  const axis = bestAxis(points);
  const arch = cutArch(points, { axis, force: true });
  assert.ok(arch);
  const figure = archFigure(arch, { source: points, hits: integerHits(points) });
  assert.ok(!figure.includes("NaN"), "the rails must be real on a non-mirrored parent");
  assert.match(figure, /one arm mirrored/);
});
