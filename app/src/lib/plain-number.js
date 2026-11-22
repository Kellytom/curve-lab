// A number as a reader reads it: no exponent, and an integer stays an integer.
//
// The operator, 2026-11-21: "i see ... some numbers i dont like because they have e 16
// and i like numbers like 5, 25, 3125." `toExponential` turned every measure on the
// reduction desk into 1.23e+16 and hid the exact integers. This formats in plain
// decimal instead.

export function plainNumber(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return String(value);
  if (number === 0) return "0";
  if (Number.isInteger(number)) return String(number);
  const magnitude = Math.abs(number);
  // below 1e-12 a plain decimal is noise; say it is zero at the printed precision
  if (magnitude < 1e-12) return "0";
  const digits = magnitude >= 1 ? 6 : 12;
  const plain = number.toFixed(digits);
  if (/e/i.test(plain)) return String(number); // beyond toFixed's range; rare
  return plain.replace(/\.?0+$/, "");
}
