import test from "node:test";
import assert from "node:assert/strict";

import { plainNumber } from "../src/lib/plain-number.js";

test("integers print as integers, the operator's own examples", () => {
  for (const value of [5, 25, 3125, 10, 100000]) {
    assert.equal(plainNumber(value), String(value));
  }
});

test("no exponent, however large the number", () => {
  assert.equal(plainNumber(1.23e16), "12300000000000000");
  assert.equal(plainNumber(5e16), "50000000000000000");
  assert.ok(!/e/i.test(plainNumber(1.23e16)));
});

test("a fraction prints as a short decimal, trimmed", () => {
  assert.equal(plainNumber(0.03987036318564625), "0.039870363186");
  assert.equal(plainNumber(2.5), "2.5");
  assert.equal(plainNumber(-0.1), "-0.1");
  assert.equal(plainNumber(0), "0");
  assert.equal(plainNumber(-0), "0");
});
