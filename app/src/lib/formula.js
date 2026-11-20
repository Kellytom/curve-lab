// The formula object that travels with every curve: a plain reading, an exact
// rational reading, the parameter, what the curve is good for, and one
// searchable line. Built from the stored rows, never typed by hand.
//
// A `rows` curve is a Pythagorean-hodograph curve: its speed rows are u and v,
// and the curve is x = ∫(u² − v²) dt, y = ∫2uv dt. Integrating a polynomial is
// exact, so the coefficients printed here are the curve, not a sample of it.
// Every coefficient is kept as a fraction n/d in BigInt and reduced; a stored
// decimal row (2.2) is read as the fraction it is (11/5), never rounded.

const SUP = ["⁰", "¹", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹"];

function superscript(power) {
  return String(power).split("").map((digit) => SUP[Number(digit)]).join("");
}

function gcd(a, b) {
  let x = a < 0n ? -a : a;
  let y = b < 0n ? -b : b;
  while (y) [x, y] = [y, x % y];
  return x || 1n;
}

function reduce(n, d) {
  let top = BigInt(n);
  let bottom = BigInt(d);
  if (bottom < 0n) { top = -top; bottom = -bottom; }
  const g = gcd(top, bottom);
  return { n: top / g, d: bottom / g };
}

const ZERO = { n: 0n, d: 1n };

// A stored coefficient as an exact fraction: 2 → 2, 2.2 → 11/5, 1e-7 → 1/10000000.
function fromNumber(value) {
  if (typeof value === "bigint") return reduce(value, 1n);
  const text = String(value);
  const match = /^(-?\d*)(?:\.(\d+))?(?:e([+-]?\d+))?$/i.exec(text);
  if (!match) return reduce(0n, 1n);
  const [, whole, decimals = "", exponent = "0"] = match;
  const digits = `${whole || "0"}${decimals}`;
  let n = BigInt(digits || "0");
  let d = 10n ** BigInt(decimals.length);
  const power = Number(exponent);
  if (power > 0) n *= 10n ** BigInt(power);
  if (power < 0) d *= 10n ** BigInt(-power);
  return reduce(n, d);
}

const mul = (a, b) => reduce(a.n * b.n, a.d * b.d);
const add = (a, b) => reduce(a.n * b.d + b.n * a.d, a.d * b.d);
const sub = (a, b) => add(a, { n: -b.n, d: b.d });

function convolve(a, b) {
  if (!a.length || !b.length) return [];
  const out = Array.from({ length: a.length + b.length - 1 }, () => ZERO);
  for (let i = 0; i < a.length; i += 1) {
    for (let j = 0; j < b.length; j += 1) {
      out[i + j] = add(out[i + j], mul(a[i], b[j]));
    }
  }
  return out;
}

// "78t² − 203t³ + 232/3 t⁴" from fractions in ascending power order.
function polynomial(terms, ascii = false) {
  const parts = [];
  terms.forEach((term, power) => {
    if (!term || term.n === 0n) return;
    const sign = term.n < 0n ? "−" : "+";
    const size = term.n < 0n ? -term.n : term.n;
    const body = term.d === 1n ? `${size}` : `${size}/${term.d}`;
    const variable = power === 0 ? "" : power === 1 ? "t" : ascii ? `t^${power}` : `t${superscript(power)}`;
    parts.push({ sign, text: `${body}${variable}` });
  });
  if (!parts.length) return "0";
  const [first, ...rest] = parts;
  const head = first.sign === "−" ? `−${first.text}` : first.text;
  return head + rest.map((part) => ` ${part.sign} ${part.text}`).join("");
}

// ∫ c_i t^i dt = c_i/(i+1) t^(i+1), reduced, plus the least common denominator
// of the terms that survive.
function integrate(derivative) {
  const integrated = [];
  derivative.forEach((value, power) => {
    integrated[power + 1] = reduce(value.n, value.d * BigInt(power + 1));
  });
  let lcm = 1n;
  for (const term of integrated) {
    if (!term || term.n === 0n) continue;
    lcm = (lcm / gcd(lcm, term.d)) * term.d;
  }
  return { integrated, denominator: lcm };
}

function rowsFormula(record) {
  const u = (record.speedX || []).map(fromNumber);
  const v = (record.speedY || []).map(fromNumber);
  const uu = convolve(u, u);
  const vv = convolve(v, v);
  const uv = convolve(u, v);
  const width = Math.max(uu.length, vv.length);
  const xd = Array.from({ length: width }, (_, i) => sub(uu[i] || ZERO, vv[i] || ZERO));
  const yd = uv.map((value) => ({ n: 2n * value.n, d: value.d }));
  const x = integrate(xd);
  const y = integrate(yd);
  const ascii = (text) => text.replace(/[⁰¹²³⁴⁵⁶⁷⁸⁹]/g, (mark) => `^${SUP.indexOf(mark)}`);
  const lcm = (x.denominator / gcd(x.denominator, y.denominator)) * y.denominator;

  return {
    plain: `x(t) = ${polynomial(x.integrated)};  y(t) = ${polynomial(y.integrated)}`,
    rational: `the same polynomial exactly: every coefficient is a fraction, and the whole curve is an integer over ${lcm}`,
    parameter: "t runs 0 to 1 in equal steps; the stored step and grid give the exact station",
    search: `PH x=${ascii(polynomial(x.integrated, true))}; y=${ascii(polynomial(y.integrated, true))}`,
  };
}

function polylineFormula(record) {
  const points = record.path || record.points || [];
  const count = Array.isArray(points) ? points.length : 0;
  const first = count ? points[0] : null;
  const last = count ? points[count - 1] : null;
  const show = (point) => Array.isArray(point) ? `(${point[0]}, ${point[1]})` : "(?)";
  return {
    plain: `polyline through ${count} stations, ${first ? show(first) : "(none)"} to ${last ? show(last) : "(none)"}`,
    rational: "the stations are stored as written; nothing is resampled or rounded by the export",
    parameter: "k = 0 … station count − 1",
    search: `polyline ${count} stations from ${first ? show(first) : "?"} to ${last ? show(last) : "?"}`,
  };
}

export function formulaFor(record, metric) {
  const base = record.kind === "rows" && (record.speedX || []).length
    ? rowsFormula(record)
    : polylineFormula(record);
  const facts = [];
  if (metric) {
    if (metric.crossings) {
      facts.push(`${metric.crossings} ${metric.crossings === 1 ? "node" : "nodes"}`);
    }
    if (metric.inflections) {
      facts.push(`${metric.inflections} ${metric.inflections === 1 ? "inflection" : "inflections"}`);
    }
    if (metric.bend) facts.push(`bend ${Number(metric.bend).toFixed(3)}`);
  }
  const use = facts.length ? facts.join(", ") : "no metric yet";
  return { ...base, use, search: `${base.search}; ${use}` };
}

export const __testing = { polynomial, integrate, convolve, fromNumber };
