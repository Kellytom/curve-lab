// The printed formula is the curve, not a sample of it: parse the plain string
// back into coefficients, evaluate it, and compare with a numerical integral of
// the stored speed rows. If the printed polynomial were wrong, this fails.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { formulaFor } from "../src/lib/formula.js";

const registry = JSON.parse(
  readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url), "utf8"),
);
const metrics = JSON.parse(
  readFileSync(new URL("../../workbench/curve-analysis.json", import.meta.url), "utf8"),
);
const metricByUid = new Map(
  (metrics.curves || []).map((row) => [row.uid || row.name, row]),
);

const SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹";

// "−12t + 78t² − 611/3t³" -> [0, -12, 78, -611/3, ...] as [numerator, denominator]
function parsePolynomial(text) {
  const terms = text.split(/\s+([+−])\s+/);
  const out = [];
  let sign = 1n;
  for (const part of terms) {
    if (part === "+") { sign = 1n; continue; }
    if (part === "−") { sign = -1n; continue; }
    let body = part;
    if (body.startsWith("−")) { sign = -1n; body = body.slice(1); }
    const match = /^(\d+)(?:\/(\d+))?(?:t([⁰¹²³⁴⁵⁶⁷⁸⁹]*))?$/.exec(body);
    if (!match) throw new Error(`cannot parse term: ${part}`);
    const [, whole, denominator = "1", powerMark = ""] = match;
    const power = powerMark
      ? Number([...powerMark].map((mark) => SUP.indexOf(mark)).join(""))
      : body.includes("t") ? 1 : 0;
    const n = sign * BigInt(whole);
    const d = BigInt(denominator);
    out[power] = [n, d];
  }
  return out.map((entry) => entry || [0n, 1n]);
}

function evaluate(coefficients, t) {
  return coefficients.reduce((sum, [n, d], power) => sum + (Number(n) / Number(d)) * t ** power, 0);
}

function numeric(record, t, steps = 20000) {
  const ev = (row, x) => row.reduce((sum, c, i) => sum + c * x ** i, 0);
  let x = 0;
  let y = 0;
  for (let k = 0; k < steps; k += 1) {
    const at = ((k + 0.5) / steps) * t;
    const u = ev(record.speedX, at);
    const v = ev(record.speedY, at);
    x += (u * u - v * v) * (t / steps);
    y += 2 * u * v * (t / steps);
  }
  return { x, y };
}

test("every printed rows formula reproduces the stored speed rows", () => {
  const rows = registry.curves.filter((curve) => (curve.speedX || []).length);
  let checked = 0;
  for (const curve of rows) {
    const formula = formulaFor(curve, metricByUid.get(curve.uid) || null);
    const [xText, yText] = formula.plain.replace(/^x\(t\) = /, "").split(";  y(t) = ");
    const X = parsePolynomial(xText);
    const Y = parsePolynomial(yText);
    const t = 0.37;
    const exact = numeric(curve, t);
    const printedX = evaluate(X, t);
    const printedY = evaluate(Y, t);
    const near = (a, b) => Math.abs(a - b) <= 1e-6 * Math.max(1, Math.abs(b));
    assert.ok(near(printedX, exact.x),
      `${curve.uid} ${curve.name}: x printed ${printedX} integral ${exact.x}`);
    assert.ok(near(printedY, exact.y),
      `${curve.uid} ${curve.name}: y printed ${printedY} integral ${exact.y}`);
    checked += 1;
  }
  assert.ok(checked > 200, `only ${checked} curves checked`);
});

test("the formula carries the five fields the exports need", () => {
  for (const curve of registry.curves.slice(0, 40)) {
    const formula = formulaFor(curve, null);
    for (const key of ["plain", "rational", "parameter", "use", "search"]) {
      assert.equal(typeof formula[key], "string", `${curve.uid} ${key}`);
      assert.ok(formula[key].length > 0, `${curve.uid} ${key} is empty`);
    }
  }
});
