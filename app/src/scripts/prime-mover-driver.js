// The prime-mover driver, shared by every page that needs it.
//
// One source of truth: stage I draws it, stage II feeds it into polynomials. A
// step is a p-triple divided by its hypotenuse, so every station is a ratio of
// whole numbers and nothing is sampled. No complex step: its length would not be
// a ratio (state/EXACT-NUMBERS-int.md).

export const TRIPLES = {
  "3,4,5": { legs: [3, 4], hypotenuse: 5, steps: 7 },
  "7,24,25": { legs: [7, 24], hypotenuse: 25, steps: 5 },
  "44,117,125": { legs: [44, 117], hypotenuse: 125, steps: 6 },
  "56,783,785": { legs: [56, 783], hypotenuse: 785, steps: 1 },
};

export const gcd = (a, b) => (b ? gcd(b, Math.abs(a) % b) : Math.abs(a));

export function ratio(value, denominator) {
  const sign = value < 0 ? "−" : "";
  const size = Math.abs(value);
  return denominator === 1 ? `${sign}${size}` : `${sign}${size}/${denominator}`;
}

export function iText(k, steps) {
  const divisor = gcd(k, steps) || 1;
  const above = k / divisor;
  const below = steps / divisor;
  if (above === 0) return "0";
  const sign = above > 0 ? "+" : "−";
  return below === 1 ? `${sign}${Math.abs(above)}` : `${sign}${Math.abs(above)}/${below}`;
}

export function reduceTriple(a, b, denominator) {
  const divisor = gcd(gcd(a, b), denominator) || 1;
  return [a / divisor, b / divisor, denominator / divisor];
}

export function driverRows(triple) {
  const [legX, legY] = triple.legs;
  const { hypotenuse, steps } = triple;
  const rows = [{ k: 0, a: 1, b: 0, denominator: 1 }];
  let a = 1;
  let b = 0;
  let denominator = 1;
  for (let k = 1; k <= steps; k += 1) {
    const nextA = legX * a - legY * b;
    const nextB = legY * a + legX * b;
    a = nextA;
    b = nextB;
    denominator *= hypotenuse;
    rows.push({ k, a, b, denominator });
  }
  const negativeHalf = rows.slice(1)
    .map((row) => ({ k: -row.k, a: row.a, b: -row.b, denominator: row.denominator }))
    .reverse();
  return { rows: [...negativeHalf, ...rows], steps, grid: denominator };
}

// --- exact rationals for stage II ------------------------------------------
// A rational is {n, d} in lowest terms with d > 0, held as BigInt so a cube of a
// denominator can never overflow. Nothing rounds, ever.

const bigGcd = (a, b) => (b ? bigGcd(b, a % b) : (a < 0n ? -a : a));

export function rational(n, d = 1n) {
  let num = BigInt(n);
  let den = BigInt(d);
  if (den === 0n) throw new Error("zero denominator");
  if (den < 0n) { num = -num; den = -den; }
  const divisor = bigGcd(num, den) || 1n;
  return { n: num / divisor, d: den / divisor };
}

export const multiply = (p, q) => rational(p.n * q.n, p.d * q.d);
export const add = (p, q) => rational(p.n * q.d + q.n * p.d, p.d * q.d);
export const subtract = (p, q) => rational(p.n * q.d - q.n * p.d, p.d * q.d);
export const cube = (p) => multiply(multiply(p, p), p);

// "−n/d", or just "n" when the denominator is 1
export function rationalText(value) {
  const sign = value.n < 0n ? "−" : "";
  const size = value.n < 0n ? -value.n : value.n;
  return value.d === 1n ? `${sign}${size}` : `${sign}${size}/${value.d}`;
}

// the denominator a value needs, as a plain number for display
export const denominatorOf = (value) => Number(value.d);

// The hit points: where the triangle walk meets the 25 circle.
//
// **What is stored is only two things:** the initial triangle's hypotenuse and the
// rotation. Everything else is generated.
//
//   apex      the first hypotenuse, (24, 7)             — the first triangle
//   rotation  the turn between apices, (527, 336, 625)  — the two reflections
//
// The rotation is the composition of the two reflections that share a side, which is
// why it is the *square* of the step: 527 + 336i = (24 + 7i)², and 625 = 25². A
// station is the apex multiplied by the rotation k times; nothing else is kept.
// A triple chosen on the page gives both of these:
//   apex      (x, y)                    the first hypotenuse
//   rotation  (x² − y², 2xy, z²)        the double angle, as a Gaussian rational
export function walkFor(name = "7,24,25") {
  const triple = TRIPLES[name] || TRIPLES["7,24,25"];
  const [a, b] = triple.legs.map(BigInt).sort((p, q) => (p > q ? -1 : 1));
  const z = BigInt(triple.hypotenuse);
  return {
    name,
    legs: [a, b],
    hypotenuse: z,
    apex: [a, b],
    rotation: [a * a - b * b, 2n * a * b, z * z],
    turn: (2 * Math.atan2(Number(b), Number(a)) * 180) / Math.PI,
  };
}

export const WALK = {
  triple: "7,24,25",
  apex: [24n, 7n],
  rotation: [527n, 336n, 625n],
};

// The settled walk, as points on the UNIT circle: start at (1, 0) and multiply by
// the stored rotation `power` times a station. One object for every stage, so the
// curves cannot drift away from the walk again.
export function unitWalk(count = 12, power = 1) {
  const [cx, cy, cd] = WALK.rotation;
  const bigGcd = (a, b) => (b ? bigGcd(b, a % b) : (a < 0n ? -a : a));
  let x = 1n;
  let y = 0n;
  let d = 1n;
  const out = [];
  for (let k = 0; k < count; k += 1) {
    out.push({ k, x, y, d });
    for (let stepIndex = 0; stepIndex < power; stepIndex += 1) {
      const nx = cx * x - cy * y;
      const ny = cy * x + cx * y;
      const nd = cd * d;
      const divisor = bigGcd(bigGcd(nx, ny), nd) || 1n;
      x = nx / divisor;
      y = ny / divisor;
      d = nd / divisor;
    }
  }
  return out;
}

// **walker(k)** — the closed form of the whole walk, in one expression:
//
//     walker(k) = (24 + 7i)^(2k+1) / 5^(4k)
//
// A point on radius 25: a Gaussian integer over a power of 5. This is the object the
// curves are built from. Two vanes at amplitudes a and b, the second stepping `power`
// times as fast, are a·walker(k) + b·walker(power·k); both terms share the factor
// (24 + 7i)^(2k), so the sum factors into one Gaussian integer over 25^(2·power·k).
export function walker(k, power = 1, tripleName = "7,24,25") {
  const walk = walkFor(tripleName);
  const [doubleX, doubleY, doubleD] = walk.rotation;
  const bigGcd = (a, b) => (b ? bigGcd(b, a % b) : (a < 0n ? -a : a));
  let x = walk.apex[0];
  let y = walk.apex[1];
  let d = 1n;
  for (let stepIndex = 0; stepIndex < k * power; stepIndex += 1) {
    const nx = doubleX * x - doubleY * y;
    const ny = doubleY * x + doubleX * y;
    const nd = doubleD * d;
    const divisor = bigGcd(bigGcd(nx, ny), nd) || 1n;
    x = nx / divisor;
    y = ny / divisor;
    d = nd / divisor;
  }
  return { x, y, d };
}

// The same walk sampled more finely: one triangle turn a station (16.26°) instead of
// the double angle. Same triangle, same circle, more stations — which is what a
// spirograph needs, since its inner vane must complete several turns.
export function fineWalk(count = 111, tripleName = "7,24,25") {
  const { legs, hypotenuse } = walkFor(tripleName);
  const [legX, legY] = legs;
  const bigGcd = (a, b) => (b ? bigGcd(b, a % b) : (a < 0n ? -a : a));
  let x = legX;
  let y = legY;
  let d = 1n;
  const out = [];
  for (let k = 0; k < count; k += 1) {
    out.push({ k, x, y, d });
    const nx = legX * x - legY * y;
    const ny = legY * x + legX * y;
    const nd = hypotenuse * d;
    const divisor = bigGcd(bigGcd(nx, ny), nd) || 1n;
    x = nx / divisor;
    y = ny / divisor;
    d = nd / divisor;
  }
  return out;
}

// The half walk: quadrants I and IV only, |angle| ≤ 90°. The forward stations and
// their mirrors below the axis, and nothing past the vertical — which halves the step
// count and therefore the denominators.
export function quadrantPoints(tripleName = "56,783,785") {
  const walk = walkFor(tripleName);
  const step = walk.turn;                      // degrees between apices
  const reach = Math.max(1, Math.floor(90 / step));
  const out = [];
  for (let k = -reach; k <= reach; k += 1) {
    const point = walker(Math.abs(k), 1, tripleName);
    const sign = k < 0 ? -1n : 1n;
    out.push({ k, x: point.x, y: point.y * sign, d: point.d });
  }
  return out;
}

export function hitPoints(tripleName = "7,24,25", count = 12) {
  const triple = TRIPLES[tripleName] || TRIPLES["7,24,25"];
  // the walk starts with the LONGER leg along x, which is the orientation the
  // triangle figure draws: the apex of the first triangle is (24, 7)
  const [legX, legY] = triple.legs.map(BigInt).sort((a, b) => (a > b ? -1 : 1));
  const hypotenuse = BigInt(triple.hypotenuse);
  const doubleX = legX * legX - legY * legY;   // 527
  const doubleY = 2n * legX * legY;            // 336
  const doubleD = hypotenuse * hypotenuse;     // 625
  const bigGcd = (a, b) => (b ? bigGcd(b, a % b) : (a < 0n ? -a : a));

  // the first apex is the point the hypotenuse reaches: (legX, legY)
  let x = legX;
  let y = legY;
  let d = 1n;
  const out = [];
  for (let k = 0; k < count; k += 1) {
    out.push({ k, x, y, d });
    const nx = doubleX * x - doubleY * y;
    const ny = doubleY * x + doubleX * y;
    const nd = doubleD * d;
    const divisor = bigGcd(bigGcd(nx, ny), nd) || 1n;
    x = nx / divisor;
    y = ny / divisor;
    d = nd / divisor;
  }
  return out;
}

// **The boundary.** Exact values are BigInt; drawing values are numbers, and the
// conversion happens here and nowhere else. A caller that needs a point for a picture
// uses `.x` and `.y`; a caller that needs the exact value uses `.num` and `.den`.
// Nothing outside this file may call Number() on a BigInt.
export const rationalFloat = (value) => toFloat(value.n, value.d);

export const PRECISION = 2 ** -30;   // the worst a drawing value can be off, in units

export function station(point) {
  const sx = fixed(point.x, point.d);
  const sy = fixed(point.y, point.d);
  return {
    k: point.k, num: point.x, den: point.d,
    x: sx.value, y: sy.value,
    exact: sx.exact && sy.exact,
  };
}

// A BigInt ratio as a drawing number, by shift.
//
// The value is n/d. Both may have hundreds of digits, so neither may be turned into a
// float first. Instead the numerator is shifted left by `bits` and the division is done
// in BigInt — the quotient is a fixed-point value with `bits` binary places:
//
//     q = (n << bits) / d        value ≈ q / 2^bits
//
// The shift is exact, the division truncates at 2^-bits (about 1e-9 at 30 bits, far
// below a pixel), and `exact` reports whether anything was truncated at all. This works
// for any size of n and d: the quotient is small because the shift is a fixed number of
// bits, not a fixed multiplier.
export function fixed(n, d = 1n, bits = 30) {
  if (d === 0n) return { value: 0, exact: true };
  const shifted = n << BigInt(bits);
  const quotient = shifted / d;
  const exact = quotient * d === shifted;
  return { value: Number(quotient) / 2 ** bits, exact };
}

// The older name, kept so nothing calls Number() on a BigInt by habit.
export const toFloat = (n, d = 1n) => fixed(n, d).value;
