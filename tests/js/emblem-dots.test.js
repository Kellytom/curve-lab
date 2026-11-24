import test from "node:test";
import assert from "node:assert/strict";
import {
  fr, fNum, fishStations, heartStations, crossStations, chiRhoStations,
  mirrorX, rationalRing, toFloat,
} from "../../app/src/lib/emblem-dots.js";

// The dot-plot desk's law: every station is an exact rational pair, every
// emblem's mirror is its exact reflection, and the cusps land where the
// design says. No cubic Bezier exists in this module to begin with — the
// test pins the arithmetic that the page plots.

test("a fraction reduces and rejects a zero denominator", () => {
  assert.deepEqual(fr(6n, 4n), [3n, 2n]);
  assert.throws(() => fr(1n, 0n), /denominator 0/);
});

test("every fish station is rational and the tail crossing is exact", () => {
  const { upper, lower, eye, crossing } = fishStations({ flare: 40, tail: 80, nose: 66, n: 12 });
  for (const s of [...upper, ...lower]) {
    assert.ok(s.x[1] > 0n && s.y[1] > 0n);
    assert.ok(Number.isFinite(fNum(s.x)) && Number.isFinite(fNum(s.y)));
  }
  // the nose is shared exactly: first upper station == first lower station
  assert.deepEqual(upper[0], lower[0]);
  // the crossing at (nose, 0) is a station of the record, and the stations
  // straddle it: above the axis before it, below after it
  assert.equal(fNum(crossing.x), 66);
  assert.equal(fNum(crossing.y), 0);
  assert.ok(upper.slice(1, 11).every((s) => fNum(s.y) > 0));
  assert.ok(upper.slice(11).every((s) => fNum(s.y) < 0));
  assert.deepEqual(eye.x, fr(-30n));
});

test("the heart's cusps are exact stations and the halves are true mirrors", () => {
  const { right, left, cusps } = heartStations({ n: 8, m: 4 });
  assert.deepEqual(right[0], cusps[0]);                 // the cleavage
  assert.deepEqual(right[right.length - 1], cusps[1]);  // the point
  assert.equal(right.length, left.length);
  const r = toFloat(right), l = toFloat(left);
  // mirrorX maps each station in place: station i of the left chain is the
  // reflection of station i of the right chain
  for (let i = 0; i < r.length; i += 1) {
    assert.ok(Math.abs(r[i][0] + l[i][0]) < 1e-12);
    assert.ok(Math.abs(r[i][1] - l[i][1]) < 1e-12);
  }
  // the side's last station before the cusp is x = 15 (j = m−1), and it dives
  // steeply, so the bottom point is sharp
  const last = right[right.length - 2];
  assert.equal(fNum(last.x), 15);
  const prev = right[right.length - 3];
  assert.ok((fNum(last.y) - fNum(prev.y)) / (fNum(last.x) - fNum(prev.x)) > 1.5);
});

test("the mirror of a station is exact, not a float round trip", () => {
  const s = { x: fr(1n, 3n), y: fr(5n, 7n) };
  assert.deepEqual(mirrorX(s).x, fr(-1n, 3n));
  assert.deepEqual(mirrorX(s).y, fr(5n, 7n));
});

test("a rational ring has no duplicates and stays on its circle", () => {
  const ring = rationalRing(0, 0, fr(1n), 12);
  const seen = new Set(ring.map((s) => `${fNum(s.x)},${fNum(s.y)}`));
  assert.equal(seen.size, ring.length);
  for (const s of ring) {
    const d = fNum(s.x) ** 2 + fNum(s.y) ** 2;
    assert.ok(Math.abs(d - 1) < 1e-12);
  }
});

test("the cross and the chi-rho carry whole-number stations on their strokes", () => {
  const { vertical, horizontal } = crossStations();
  assert.equal(fNum(vertical[0].x), 0);
  assert.equal(fNum(vertical[vertical.length - 1].y), 90);
  const chi = chiRhoStations(12);
  assert.ok(chi.bowl.length >= 24);
  for (const s of chi.bowl) {
    const d = fNum(s.x) ** 2 + (fNum(s.y) - 52) ** 2;
    assert.ok(Math.abs(d - 676) < 1e-9);                // r = 26
  }
});
