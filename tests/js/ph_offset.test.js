// The JS exact core against the numbers the Python core already proved.
// Run: node --test tests/js
const { test } = require("node:test");
const assert = require("node:assert/strict");

const { Rational } = require("../../workbench/exact.js");
const poly = require("../../workbench/poly_exact.js");
const ph = require("../../workbench/ph_offset.js");

const r = (text) => Rational.from(text);
const strings = (list) => list.map((value) => value.toString());

// integer-105: the speed pair the sandbox page writes.
const U = ["2", "-5", "6"].map(r);
const V = ["4", "-20", "20", "-2"].map(r);

test("a rational normalises, compares and refuses floats", () => {
  assert.equal(new Rational(6n, -8n).toString(), "-3/4");
  assert.equal(r("3/7").add(r("2/7")).toString(), "5/7");
  assert.equal(r("3/7").mul(r("7/3")).toString(), "1");
  assert.equal(r("1/3").compare(r("1/2")), -1);
  assert.throws(() => Rational.from(0.5), /string/);
});

test("polynomials multiply, integrate and evaluate exactly", () => {
  const t = [r("0"), r("1")];
  assert.equal(poly.multiply(t, t)[2].toString(), "1");
  assert.deepEqual(strings(poly.integrate(t)), ["0", "0", "1/2"]);
  assert.equal(poly.evaluate(t, r("1/2")).toString(), "1/2");
});

test("the exact polynomials are the ones the Python core pins", () => {
  const [x, y] = ph.curve(U, V);
  assert.deepEqual(strings(x),
    ["0", "-12", "70", "-511/3", "189", "-444/5", "40/3", "-4/7"]);
  assert.deepEqual(strings(y),
    ["0", "16", "-60", "328/3", "-112", "52", "-4"]);
  assert.deepEqual(strings(ph.speedSquared(U, V)),
    ["20", "-180", "609", "-876", "516", "-80", "4"]);
});

test("the rail is perpendicular and exactly d from the spine", () => {
  const d = r("41/1120");
  const [xPrime, yPrime] = ph.hodographPair(U, V);
  const sigma = ph.speedSquared(U, V);
  for (const t of ["1/3", "1/2", "2/5"].map(r)) {
    const spine = ph.pointAt(U, V, 0, t);
    const rail = ph.pointAt(U, V, d, t);
    const dx = rail[0].sub(spine[0]);
    const dy = rail[1].sub(spine[1]);
    const hx = poly.evaluate(xPrime, t);
    const hy = poly.evaluate(yPrime, t);
    assert.equal(dx.mul(hx).add(dy.mul(hy)).toString(), "0");
    assert.equal(dx.mul(hy.neg()).add(dy.mul(hx)).toString(),
                 d.mul(poly.evaluate(sigma, t)).toString());
  }
});

test("integer-105's first interior hit is the midpoint at grid 3360", () => {
  const first = ph.firstInteriorHit(U, V);
  assert.equal(first.scale.toString(), "3360");
  assert.deepEqual(first.t, [1, 2]);
  assert.deepEqual(strings(first.point), ["-1849/3360", "59/48"]);
});

test("at grid 3360 the spine has exactly three points", () => {
  const hits = ph.hitsAtScale(U, V, 3360n);
  assert.deepEqual(hits.map((h) => h.point.map(String)),
    [["-1849", "4130"], ["0", "0"], ["2112", "4480"]]);
});

test("a rail hits only when the distance is chosen for it", () => {
  assert.equal(ph.firstInteriorHit(U, V, r("41/1120")).scale.toString(), "3360");
  assert.equal(ph.firstInteriorHit(U, V, r("3/100")).scale.toString(), "688800");
});

test("the symmetric candidate's station is grid 15, its rail grid 5", () => {
  const u = ["1"].map(r);
  const v = ["1", "-4", "4"].map(r);
  assert.deepEqual(strings(ph.pointAt(u, v, 0, r("1/2"))), ["2/5", "1/3"]);
  assert.equal(ph.firstInteriorHit(u, v).scale.toString(), "15");
  assert.deepEqual(ph.hitsAtScale(u, v, 15n).map((h) => h.point.map(String)),
    [["0", "0"], ["6", "5"], ["12", "10"]]);
  assert.equal(ph.firstInteriorHit(u, v, r("1/15")).scale.toString(), "5");
});
