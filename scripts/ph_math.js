// The shared maths for the curve pages: closed form, metrics, exact bend,
// the polynomial evaluators and the saved-curve store. Loaded first.

window.closedFormOf = (function () {
  const greatestCommonDivisor = (a, b) => (b ? greatestCommonDivisor(b, a % b) : a);
  const decimalPlaces = value => { const text = String(value); const dotIndex = text.indexOf("."); return dotIndex < 0 ? 0 : text.length - dotIndex - 1; };
  return function (speedX, speedY) {
    const maxDecimals = Math.max(...speedX.concat(speedY).map(decimalPlaces));
    const decimalScale = Math.pow(10, maxDecimals);
    const decimalScaleSquared = decimalScale * decimalScale;
    const scaledSpeedX = speedX.map(value => Math.round(value * decimalScale));
    const scaledSpeedY = speedY.map(value => Math.round(value * decimalScale));
    const multiplyPolynomials = (left, right) => {
      const product = new Array(left.length + right.length - 1).fill(0);
      left.forEach((leftCoefficient, i) => right.forEach((rightCoefficient, j) => { product[i + j] += leftCoefficient * rightCoefficient; }));
      return product;
    };
    const speedXSquared = multiplyPolynomials(scaledSpeedX, scaledSpeedX);
    const speedYSquared = multiplyPolynomials(scaledSpeedY, scaledSpeedY);
    const speedXTimesY = multiplyPolynomials(scaledSpeedX, scaledSpeedY);
    const reduceFraction = (numerator, denominator) => {
      const divisor = greatestCommonDivisor(Math.abs(numerator), denominator) || 1;
      return [numerator / divisor, denominator / divisor];
    };
    const xTerms = [], yTerms = [];
    for (let j = 0; j < speedXSquared.length; j++) {
      const denominator = decimalScaleSquared * (j + 1);   // the coefficient of t^(j+1) in r
      xTerms.push(reduceFraction(speedXSquared[j] - (speedYSquared[j] || 0), denominator));
      yTerms.push(reduceFraction(2 * speedXTimesY[j], denominator));
    }
    return { xTerms, yTerms };
  };
})();
window.formatPolynomial = function (terms) {
  const powers = ["", "t", "t^2", "t^3", "t^4", "t^5"];
  let text = "";
  terms.forEach((term, j) => {
    const numerator = term[0], denominator = term[1];
    if (!numerator) return;
    const magnitude = denominator === 1 ? String(Math.abs(numerator)) : `${Math.abs(numerator)}/${denominator}`;
    const coefficient = (denominator === 1 && Math.abs(numerator) === 1) ? "" : magnitude;
    text += (numerator < 0 ? (text ? " - " : "-") : (text ? " + " : "")) + coefficient + powers[j + 1];
  });
  return text || "0";
};

window.panelRecipes = {};
// The exponent step: 1 for whole powers, 1/2 for t^0.5, t^1.5, 5/2 ... The
// experimental page sets window.phPowerStep; every other page leaves it unset,
// so the Horner path below is what they run and nothing changes for them.
window.polynomialValue = function (coefficients, t) {
  const step = window.phPowerStep || 1;
  if (step === 1) {
    let total = 0;
    for (let i = coefficients.length - 1; i >= 0; i--) total = total * t + coefficients[i];
    return total;
  }
  let total = 0;
  for (let i = 0; i < coefficients.length; i++) {
    // a negative t has no real fractional power, so below zero the row is read
    // by the odd extension: sign(t) |t|^(k step). The page says so in words.
    const power = t < 0 ? Math.sign(t) * Math.pow(-t, i * step) : Math.pow(t, i * step);
    total += coefficients[i] * power;
  }
  return total;
};

// Fractional exponents have no whole-number grid and no polynomial Wronskian,
// so the numbers are measured from the curve instead of read off a formula.
function numericMetrics(speedX, speedY) {
  const value = window.polynomialValue;
  const count = 1200;
  let arc = 0, chordRe = 0, chordIm = 0, closest = Infinity;
  for (let i = 0; i < count; i++) {
    const t = (i + 0.5) / count;
    const p = value(speedX, t), q = value(speedY, t);
    arc += (p * p + q * q) / count;
    chordRe += (p * p - q * q) / count;
    chordIm += 2 * p * q / count;
    closest = Math.min(closest, Math.hypot(p, q));
  }
  const chord = Math.hypot(chordRe, chordIm);
  return { bend: chord > 1e-15 ? arc / chord : Infinity, arc, chord: [chordRe, chordIm],
           pitch: 0, inflections: null, inflection: null, closest, inflectionMax: 0 };
}
window.polynomialDerivative = function (coefficients) {
  return coefficients.slice(1).map((coefficient, i) => coefficient * (i + 1));
};
window.exactBend = function (speedX, speedY) {
  const centred = coefficients => {
    const out = new Array(coefficients.length).fill(0);
    coefficients.forEach((coefficient, j) => {
      let binomial = 1;
      for (let k = 0; k <= j; k++) {
        out[k] += coefficient * binomial * Math.pow(0.5, j - k);
        binomial = binomial * (j - k) / (k + 1);
      }
    });
    return out;
  };
  const weight = power => (power % 2 ? 0 : 1 / (Math.pow(2, power) * (power + 1)));
  let cx = centred(speedX), cy = centred(speedY);
  const size = Math.max(cx.length, cy.length);
  cx = cx.concat(new Array(size - cx.length).fill(0));
  cy = cy.concat(new Array(size - cy.length).fill(0));
  let arc = 0, chordRe = 0, chordIm = 0;
  for (let k = 0; k < cx.length; k++) {
    for (let l = 0; l < cx.length; l++) {
      const w = weight(k + l);
      if (!w) continue;
      arc += (cx[k] * cx[l] + cy[k] * cy[l]) * w;
      chordRe += (cx[k] * cx[l] - cy[k] * cy[l]) * w;
      chordIm += (cx[k] * cy[l] + cy[k] * cx[l]) * w;
    }
  }
  const chord = Math.hypot(chordRe, chordIm);
  return { arc, chord: [chordRe, chordIm], bend: chord > 1e-15 ? arc / chord : Infinity };
};
window.recipeMetrics = function (speedX, speedY) {
  if ((window.phPowerStep || 1) !== 1) return numericMetrics(speedX, speedY);
  const sampleCount = 600;
  const value = window.polynomialValue;
  const derivativeX = window.polynomialDerivative(speedX);
  const derivativeY = window.polynomialDerivative(speedY);
  const exact = window.exactBend(speedX, speedY);
  let closest = Infinity;
  for (let i = 0; i <= sampleCount; i++) {
    const t = i / sampleCount;
    closest = Math.min(closest, Math.hypot(value(speedX, t), value(speedY, t)));
  }
  const wronskian = t => value(speedX, t) * value(derivativeY, t) - value(speedY, t) * value(derivativeX, t);
  // Every inflection, not only the first: the count is the useful number,
  // because the Wronskian p q' - q p' has degree at most 2k - 1 for a speed of
  // degree k, so a curve with fewer than that is not using its top powers.
  const inflections = [];
  // a straight line has a Wronskian that is zero everywhere: no inflections,
  // rather than one per sample
  const flatWronskian = Array.from({ length: 9 }, (unused, i) => wronskian(i / 8))
    .every(rate => Math.abs(rate) < 1e-12);
  for (let i = 0; i < sampleCount && !flatWronskian; i++) {
    const lowT = i / sampleCount, highT = (i + 1) / sampleCount;
    if (wronskian(lowT) * wronskian(highT) <= 0) {
      let low = lowT, high = highT;
      for (let k = 0; k < 40; k++) {
        const middle = (low + high) / 2;
        if (wronskian(low) * wronskian(middle) <= 0) high = middle; else low = middle;
      }
      const found = (low + high) / 2;
      // a root at the very start or end means the curve begins or ends with no
      // curvature, not that it turns there; a tangency can be reported twice
      const inside = found > 1e-6 && found < 1 - 1e-6;
      if (inside && !inflections.some(other => Math.abs(other - found) < 1e-4)) {
        inflections.push(found);
      }
    }
  }
  const inflection = inflections.length ? inflections[0] : null;
  const decimalPlaces = value => { const text = String(+value.toFixed(6)); const dot = text.indexOf("."); return dot < 0 ? 0 : text.length - dot - 1; };
  const maxDecimals = Math.max(...speedX.concat(speedY).map(decimalPlaces));
  const decimalScale = Math.pow(10, maxDecimals), decimalScaleSquared = decimalScale * decimalScale;
  const scaledX = speedX.map(value => Math.round(value * decimalScale));
  const scaledY = speedY.map(value => Math.round(value * decimalScale));
  const multiply = (left, right) => {
    const product = new Array(left.length + right.length - 1).fill(0);
    left.forEach((l, i) => right.forEach((r, j) => { product[i + j] += l * r; }));
    return product;
  };
  const greatestCommonDivisor = (a, b) => (b ? greatestCommonDivisor(b, a % b) : a);
  const leastCommonMultiple = (a, b) => a / greatestCommonDivisor(a, b) * b;
  const xSquared = multiply(scaledX, scaledX), ySquared = multiply(scaledY, scaledY);
  const xTimesY = multiply(scaledX, scaledY);
  let pitch = 1;
  for (let j = 0; j < xSquared.length; j++) {
    const numerators = [xSquared[j] - (ySquared[j] || 0), 2 * xTimesY[j]];
    for (const numerator of numerators) {
      if (!numerator) continue;
      const denominator = decimalScaleSquared * (j + 1);
      pitch = leastCommonMultiple(pitch, denominator / greatestCommonDivisor(Math.abs(numerator), denominator));
    }
  }
  const closed = window.closedFormOf(speedX, speedY);
  const endpoint = [closed.xTerms.reduce((sum, term) => sum + term[0] / term[1], 0),
                    closed.yTerms.reduce((sum, term) => sum + term[0] / term[1], 0)];
  return { bend: exact.bend, arc: exact.arc, chord: exact.chord, pitch, inflection,
           inflections, inflectionCount: inflections.length, closest, endpoint };
};
window.curveSaver = (function () {
  const key = "curve-lab-saved-curves";
  const load = () => { try { return JSON.parse(localStorage.getItem(key) || "[]"); } catch (error) { return []; } };
  const store = items => localStorage.setItem(key, JSON.stringify(items));
  return {
    add(record) { const items = load(); items.push(record); store(items); return items.length; },
    count() { return load().length; },
    clear() { store([]); },
    download() {
      const blob = new Blob([JSON.stringify({ title: "curves saved from the ph-quintic gallery", presets: load() }, null, 2)],
                            { type: "application/json" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "ph-quintic-saved.json";
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(link.href), 1000);
    }
  };
})();
