// The gallery's panels. Loaded at the end of the page by
// scripts/ph_quintic_gallery.py; edit here, not in the generated HTML.

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
window.polynomialValue = function (coefficients, t) {
  let total = 0;
  for (let i = coefficients.length - 1; i >= 0; i--) total = total * t + coefficients[i];
  return total;
};
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
  let inflection = null;
  for (let i = 0; i < sampleCount && inflection === null; i++) {
    const lowT = i / sampleCount, highT = (i + 1) / sampleCount;
    if (wronskian(lowT) * wronskian(highT) <= 0) {
      let low = lowT, high = highT;
      for (let k = 0; k < 40; k++) {
        const middle = (low + high) / 2;
        if (wronskian(low) * wronskian(middle) <= 0) high = middle; else low = middle;
      }
      inflection = (low + high) / 2;
    }
  }
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
  return { bend: exact.bend, arc: exact.arc, chord: exact.chord, pitch, inflection, closest, endpoint };
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

(function () {
  const plotElement = document.getElementById("q7-plot");
  const canvasWidth = 900, canvasHeight = 420, plotMargin = 46, sampleCount = 800;
  const targetSpeedX = [0.2, -2, 2], targetSpeedY = [0.4, -1.5, 1.6];
  const evalQuadratic = (coefficients, t) => coefficients[0] + coefficients[1] * t + coefficients[2] * t * t;
  const derivativeQuadratic = (coefficients, t) => coefficients[1] + 2 * coefficients[2] * t;
  function redraw() {
    const shiftA = +document.getElementById("q7-shift-a").value;
    const scaleB = +document.getElementById("q7-scale-b").value;
    const morphLambda = +document.getElementById("q7-morph-lambda").value;
    const speedX = [1, -shiftA, shiftA].map((startCoefficient, i) => startCoefficient + morphLambda * (targetSpeedX[i] - startCoefficient));
    const speedY = [1, -scaleB, scaleB].map((startCoefficient, i) => startCoefficient + morphLambda * (targetSpeedY[i] - startCoefficient));
    window.panelRecipes.q7 = { u: speedX, v: speedY };
    const curvePoints = [];
    let pointX = 0, pointY = 0;
    curvePoints.push([0, 0]);
    for (let i = 1; i <= sampleCount; i++) {
      const t = (i - 0.5) / sampleCount, speedXValue = evalQuadratic(speedX, t), speedYValue = evalQuadratic(speedY, t);
      pointX += (speedXValue * speedXValue - speedYValue * speedYValue) / sampleCount;
      pointY += 2 * speedXValue * speedYValue / sampleCount;
      curvePoints.push([pointX, pointY]);
    }
    const headingAngles = [];
    for (let i = 0; i <= sampleCount; i++) {
      const t = i / sampleCount, speedXValue = evalQuadratic(speedX, t), speedYValue = evalQuadratic(speedY, t);
      headingAngles.push(Math.atan2(2 * speedXValue * speedYValue, speedXValue * speedXValue - speedYValue * speedYValue));
    }
    const unwrappedAngles = [headingAngles[0]];
    for (let i = 1; i <= sampleCount; i++) {
      let angle = headingAngles[i];
      while (angle - unwrappedAngles[i - 1] > Math.PI) angle -= 2 * Math.PI;
      while (angle - unwrappedAngles[i - 1] < -Math.PI) angle += 2 * Math.PI;
      unwrappedAngles.push(angle);
    }
    const wronskianAt = t => {
      const speedXValue = evalQuadratic(speedX, t), speedYValue = evalQuadratic(speedY, t);
      return speedXValue * derivativeQuadratic(speedY, t) - speedYValue * derivativeQuadratic(speedX, t);
    };
    let inflectionParameter = null;
    for (let i = 0; i < sampleCount; i++) {
      const lowT = i / sampleCount, highT = (i + 1) / sampleCount;
      if (wronskianAt(lowT) * wronskianAt(highT) <= 0) {
        let low = lowT, high = highT;
        for (let k = 0; k < 40; k++) {
          const middle = (low + high) / 2;
          if (wronskianAt(low) * wronskianAt(middle) <= 0) high = middle; else low = middle;
        }
        inflectionParameter = (low + high) / 2;
        break;
      }
    }
    const inflectionIndex = inflectionParameter === null ? sampleCount / 2 : Math.round(inflectionParameter * sampleCount);
    const turnBefore = Math.abs(unwrappedAngles[inflectionIndex] - unwrappedAngles[0]) * 180 / Math.PI;
    const turnAfter = Math.abs(unwrappedAngles[sampleCount] - unwrappedAngles[inflectionIndex]) * 180 / Math.PI;
    const balancePercent = 100 * Math.min(turnBefore, turnAfter) / Math.max(turnBefore, turnAfter);
    let arcLength = 0;
    for (let i = 1; i < curvePoints.length; i++) arcLength += Math.hypot(curvePoints[i][0] - curvePoints[i - 1][0], curvePoints[i][1] - curvePoints[i - 1][1]);
    const chordLength = Math.hypot(curvePoints[sampleCount][0] - curvePoints[0][0], curvePoints[sampleCount][1] - curvePoints[0][1]);
    const bendRatio = chordLength > 1e-9 ? arcLength / chordLength : Infinity;
    const coordinateXs = curvePoints.map(point => point[0]), coordinateYs = curvePoints.map(point => point[1]);
    const minX = Math.min(...coordinateXs), maxX = Math.max(...coordinateXs);
    const minY = Math.min(...coordinateYs), maxY = Math.max(...coordinateYs);
    const plotScale = Math.min((canvasWidth - 2 * plotMargin) / Math.max(1e-6, maxX - minX),
                               (canvasHeight - 2 * plotMargin) / Math.max(1e-6, maxY - minY));
    const offsetX = plotMargin + (canvasWidth - 2 * plotMargin - (maxX - minX) * plotScale) / 2;
    const offsetY = plotMargin + (canvasHeight - 2 * plotMargin - (maxY - minY) * plotScale) / 2;
    const toPixelX = value => offsetX + (value - minX) * plotScale;
    const toPixelY = value => offsetY + (maxY - value) * plotScale;
    const pathData = "M" + curvePoints.map(point => toPixelX(point[0]).toFixed(1) + "," + toPixelY(point[1]).toFixed(1)).join("L");
    const headingMarker = (markerX, markerY, speedXValue, speedYValue, directionSign) => {
      const tangentX = speedXValue * speedXValue - speedYValue * speedYValue;
      const tangentY = 2 * speedXValue * speedYValue;
      const tangentLength = Math.hypot(tangentX, tangentY) || 1;
      const unitX = directionSign * tangentX / tangentLength, unitY = -directionSign * tangentY / tangentLength, markerRadius = 17;
      const markerCenterX = toPixelX(markerX) + unitX * (5 + markerRadius);
      const markerCenterY = toPixelY(markerY) + unitY * (5 + markerRadius);
      return `<circle cx="${markerCenterX}" cy="${markerCenterY}" r="${markerRadius}" fill="#1f5fa8" fill-opacity="0.07" stroke="#1f5fa8" stroke-width="1.8"/>` +
        `<line x1="${markerCenterX - unitX * markerRadius * 0.62}" y1="${markerCenterY - unitY * markerRadius * 0.62}" x2="${markerCenterX + unitX * markerRadius * 0.62}" y2="${markerCenterY + unitY * markerRadius * 0.62}" stroke="#1f5fa8" stroke-width="2.4" stroke-linecap="round"/>`;
    };
    plotElement.innerHTML =
      `<rect width="${canvasWidth}" height="${canvasHeight}" fill="#fbf7ec"/>` +
      `<path d="${pathData}" fill="none" stroke="#2e2413" stroke-width="2.4"/>` +
      `<circle cx="${toPixelX(curvePoints[inflectionIndex][0])}" cy="${toPixelY(curvePoints[inflectionIndex][1])}" r="5" fill="#fbf7ec" stroke="#a23b2a" stroke-width="2.2"/>` +
      headingMarker(curvePoints[0][0], curvePoints[0][1], evalQuadratic(speedX, 0), evalQuadratic(speedY, 0), -1) +
      headingMarker(curvePoints[sampleCount][0], curvePoints[sampleCount][1], evalQuadratic(speedX, 1), evalQuadratic(speedY, 1), 1) +
      `<text x="${plotMargin}" y="${canvasHeight - 12}" font-size="12" fill="#7b6c4e">bend ${bendRatio.toFixed(2)} (arc / chord) | inflection ${inflectionParameter === null ? " - " : inflectionParameter.toFixed(2)} | turn ${turnBefore.toFixed(0)} deg / ${turnAfter.toFixed(0)} deg | b = ${scaleB.toFixed(1)} | a = ${shiftA.toFixed(1)} | morphLambda = ${morphLambda.toFixed(2)}</text>`;
    document.getElementById("q7-readout").textContent =
      `bend ${bendRatio.toFixed(2)} | inflection ${inflectionParameter === null ? " - " : inflectionParameter.toFixed(2)}`;
  }
  for (const controlId of ["q7-shift-a", "q7-scale-b", "q7-morph-lambda"]) document.getElementById(controlId).addEventListener("input", redraw);
  redraw();
})();

(function () {
  const plotElement = document.getElementById("q8-plot");
  const canvasWidth = 900, canvasHeight = 470, plotMargin = 46, plotTopMargin = 88, sampleCount = 800;
  const controlIds = ["q8-speed-x0", "q8-speed-x1", "q8-speed-x2", "q8-speed-y0", "q8-speed-y1", "q8-speed-y2"];
  function redraw() {
    const controlValues = controlIds.map(controlId => +document.getElementById(controlId).value);
    const speedX = controlValues.slice(0, 3), speedY = controlValues.slice(3, 6);
    window.panelRecipes.q8 = { u: speedX, v: speedY };
    const evalQuadratic = (coefficients, t) => coefficients[0] + coefficients[1] * t + coefficients[2] * t * t;
    const metrics = window.recipeMetrics(speedX, speedY);
    const curvePoints = [];
    let pointX = 0, pointY = 0;
    curvePoints.push([0, 0]);
    for (let i = 1; i <= sampleCount; i++) {
      const t = (i - 0.5) / sampleCount, speedXValue = evalQuadratic(speedX, t), speedYValue = evalQuadratic(speedY, t);
      pointX += (speedXValue * speedXValue - speedYValue * speedYValue) / sampleCount;
      pointY += 2 * speedXValue * speedYValue / sampleCount;
      curvePoints.push([pointX, pointY]);
    }
    const coordinateXs = curvePoints.map(point => point[0]), coordinateYs = curvePoints.map(point => point[1]);
    const minX = Math.min(...coordinateXs), maxX = Math.max(...coordinateXs);
    const minY = Math.min(...coordinateYs), maxY = Math.max(...coordinateYs);
    const plotScale = Math.min((canvasWidth - 2 * plotMargin) / Math.max(1e-6, maxX - minX),
                               (canvasHeight - plotMargin - plotTopMargin) / Math.max(1e-6, maxY - minY));
    const offsetX = plotMargin + (canvasWidth - 2 * plotMargin - (maxX - minX) * plotScale) / 2;
    const offsetY = plotTopMargin + (canvasHeight - plotMargin - plotTopMargin - (maxY - minY) * plotScale) / 2;
    const toPixelX = value => offsetX + (value - minX) * plotScale;
    const toPixelY = value => offsetY + (maxY - value) * plotScale;
    const pathData = "M" + curvePoints.map(point => toPixelX(point[0]).toFixed(1) + "," + toPixelY(point[1]).toFixed(1)).join("L");
    const centeredConstant = coefficients => coefficients[0] + coefficients[1] / 2 + coefficients[2] / 4;
    const centeredLinear = coefficients => coefficients[1] + coefficients[2];
    const formatTwoDecimals = value => (Math.abs(value) < 5e-9 ? "0" : value.toFixed(2));
    const readoutText = `bend ${metrics.bend.toFixed(2)} | pitch ${metrics.pitch.toLocaleString()} | ` +
      `inflection ${metrics.inflection === null ? " - " : metrics.inflection.toFixed(2)} | closest ${metrics.closest.toFixed(2)}`;
    const inflectionMarker = metrics.inflection === null ? "" :
      `<circle cx="${toPixelX(curvePoints[Math.round(metrics.inflection * sampleCount)][0])}" cy="${toPixelY(curvePoints[Math.round(metrics.inflection * sampleCount)][1])}" r="5" fill="#fbf7ec" stroke="#a23b2a" stroke-width="2.2"/>`;
    plotElement.innerHTML =
      `<rect width="${canvasWidth}" height="${canvasHeight}" fill="#fbf7ec"/>` +
      `<text x="${plotMargin}" y="28" font-size="15" font-weight="600" fill="#2e2413">Fig. Q8 | the recipe playground</text>` +
      `<text x="${plotMargin}" y="48" font-size="12" fill="#7b6c4e">curve: the quintic built from your six numbers | red ring: the inflection (the tangent turns the other way)</text>` +
      `<path d="${pathData}" fill="none" stroke="#2e2413" stroke-width="2.4"/>` + inflectionMarker +
      `<text x="${plotMargin}" y="${canvasHeight - 12}" font-size="12" fill="#7b6c4e">${readoutText}</text>`;
    const formatTerm = (coefficient, symbol) => (Math.abs(coefficient) < 5e-9 ? "" : (coefficient < 0 ? ` - ${formatTwoDecimals(-coefficient)}${symbol}` : ` + ${formatTwoDecimals(coefficient)}${symbol}`));
    const formatCenteredRecipe = coefficients => `${formatTwoDecimals(coefficients[2])} h^2${formatTerm(centeredLinear(coefficients), " h")}${formatTerm(centeredConstant(coefficients), "")}`;
    document.getElementById("q8-readout").textContent = readoutText;
    document.getElementById("q8-centered-form").textContent =
      `u = ${formatCenteredRecipe(speedX)} | v = ${formatCenteredRecipe(speedY)}   (h = t - 1/2)`;
    const closedForm = window.closedFormOf(speedX, speedY);
    document.getElementById("q8-closed-form").textContent =
      `r(t) = (${window.formatPolynomial(closedForm.xTerms)}) + i (${window.formatPolynomial(closedForm.yTerms)})`;
  }
  const parseRecipeValue = text => {
    const parts = String(text).split("/");
    return parts.length === 2 ? Number(parts[0]) / Number(parts[1]) : Number(parts[0]);
  };
  const presetRow = document.getElementById("q8-presets");
  (window.phPresets || []).forEach(preset => {
    const presetButton = document.createElement("button");
    presetButton.type = "button";
    presetButton.textContent = preset.label;
    presetButton.addEventListener("click", () => {
      preset.u.concat(preset.v).map(parseRecipeValue).forEach((value, i) => {
        document.getElementById(controlIds[i]).value = value;
        document.getElementById(controlIds[i] + "-slider").value = value;
      });
      redraw();
    });
    presetRow.append(presetButton);
  });
  controlIds.forEach(controlId => {
    const numberInput = document.getElementById(controlId), rangeInput = document.getElementById(controlId + "-slider");
    numberInput.addEventListener("input", () => { rangeInput.value = numberInput.value; redraw(); });
    rangeInput.addEventListener("input", () => { numberInput.value = rangeInput.value; redraw(); });
  });
  redraw();
})();

(function () {
  const canvasWidth = 900, canvasHeight = 470, plotMargin = 46, plotTopMargin = 88, sampleCount = 800;
  function drawCurve(plotElement, speedX, speedY, figureTitle) {
    const evalQuadratic = (coefficients, t) => coefficients[0] + coefficients[1] * t + coefficients[2] * t * t;
    const metrics = window.recipeMetrics(speedX, speedY);
    const curvePoints = [[0, 0]];
    let pointX = 0, pointY = 0;
    for (let i = 1; i <= sampleCount; i++) {
      const t = (i - 0.5) / sampleCount, speedXValue = evalQuadratic(speedX, t), speedYValue = evalQuadratic(speedY, t);
      pointX += (speedXValue * speedXValue - speedYValue * speedYValue) / sampleCount;
      pointY += 2 * speedXValue * speedYValue / sampleCount;
      curvePoints.push([pointX, pointY]);
    }
    const coordinateXs = curvePoints.map(point => point[0]), coordinateYs = curvePoints.map(point => point[1]);
    const minX = Math.min(...coordinateXs), maxX = Math.max(...coordinateXs);
    const minY = Math.min(...coordinateYs), maxY = Math.max(...coordinateYs);
    const plotScale = Math.min((canvasWidth - 2 * plotMargin) / Math.max(1e-6, maxX - minX),
                               (canvasHeight - plotMargin - plotTopMargin) / Math.max(1e-6, maxY - minY));
    const offsetX = plotMargin + (canvasWidth - 2 * plotMargin - (maxX - minX) * plotScale) / 2;
    const offsetY = plotTopMargin + (canvasHeight - plotMargin - plotTopMargin - (maxY - minY) * plotScale) / 2;
    const toPixelX = value => offsetX + (value - minX) * plotScale;
    const toPixelY = value => offsetY + (maxY - value) * plotScale;
    const pathData = "M" + curvePoints.map(point => toPixelX(point[0]).toFixed(1) + "," + toPixelY(point[1]).toFixed(1)).join("L");
    const readoutText = `bend ${metrics.bend.toFixed(2)} | pitch ${metrics.pitch.toLocaleString()} | inflection ${metrics.inflection === null ? " - " : metrics.inflection.toFixed(2)} | closest ${metrics.closest.toFixed(2)}`;
    const inflectionMarker = metrics.inflection === null ? "" :
      `<circle cx="${toPixelX(curvePoints[Math.round(metrics.inflection * sampleCount)][0])}" cy="${toPixelY(curvePoints[Math.round(metrics.inflection * sampleCount)][1])}" r="5" fill="#fbf7ec" stroke="#a23b2a" stroke-width="2.2"/>`;
    plotElement.innerHTML =
      `<rect width="${canvasWidth}" height="${canvasHeight}" fill="#fbf7ec"/>` +
      `<text x="${plotMargin}" y="28" font-size="15" font-weight="600" fill="#2e2413">${figureTitle}</text>` +
      `<text x="${plotMargin}" y="48" font-size="12" fill="#7b6c4e">curve: the quintic from the sliders | red ring: the inflection</text>` +
      `<path d="${pathData}" fill="none" stroke="#2e2413" stroke-width="2.4"/>` + inflectionMarker +
      `<text x="${plotMargin}" y="${canvasHeight - 12}" font-size="12" fill="#7b6c4e">${readoutText}</text>`;
    return readoutText;
  }
  function buildRecipePanel(controlsId, plotId, readoutId, figureTitle, controlSpecs, recipeFromControls, presets, columnCount) {
    const controlsHost = document.getElementById(controlsId);
    const plotElement = document.getElementById(plotId);
    const readoutElement = document.getElementById(readoutId);
    const closedFormElement = document.createElement("p");
    closedFormElement.className = "small mono";
    readoutElement.after(closedFormElement);
    const controlValues = {};
    const controlGrid = document.createElement("div");
    controlGrid.className = "control-grid";
    if (columnCount) controlGrid.style.gridTemplateColumns = `repeat(${columnCount}, minmax(0, 1fr))`;
    controlSpecs.forEach(controlSpec => {
      controlValues[controlSpec.key] = controlSpec.value;
      const rowLabel = document.createElement("label");
      rowLabel.className = "control-row";
      const symbolLabel = document.createElement("span");
      symbolLabel.textContent = controlSpec.label;
      const numberInput = document.createElement("input");
      numberInput.type = "number"; numberInput.step = controlSpec.step; numberInput.value = controlSpec.value;
      const rangeInput = document.createElement("input");
      rangeInput.type = "range"; rangeInput.min = controlSpec.min; rangeInput.max = controlSpec.max;
      rangeInput.step = controlSpec.step; rangeInput.value = controlSpec.value;
      numberInput.addEventListener("input", () => { rangeInput.value = numberInput.value; controlValues[controlSpec.key] = +numberInput.value; redraw(); });
      rangeInput.addEventListener("input", () => { numberInput.value = rangeInput.value; controlValues[controlSpec.key] = +rangeInput.value; redraw(); });
      rowLabel.append(symbolLabel, numberInput, rangeInput);
      controlGrid.append(rowLabel);
    });
    controlsHost.append(controlGrid);
    if (presets && presets.length) {
      const presetRow = document.createElement("div");
      presetRow.className = "preset-row";
      presets.forEach(preset => {
        const presetButton = document.createElement("button");
        presetButton.type = "button";
        presetButton.textContent = preset.label;
        presetButton.addEventListener("click", () => {
          preset.values.forEach((presetValue, i) => {
            controlValues[controlSpecs[i].key] = presetValue;
            const controlRow = controlGrid.children[i];
            controlRow.querySelector("input[type=number]").value = presetValue;
            controlRow.querySelector("input[type=range]").value = presetValue;
          });
          redraw();
        });
        presetRow.append(presetButton);
      });
      controlsHost.append(presetRow);
    }
    function redraw() {
      const recipe = recipeFromControls(controlValues);
      window.panelRecipes[controlsId] = { u: recipe.speedX, v: recipe.speedY };
      readoutElement.textContent = drawCurve(plotElement, recipe.speedX, recipe.speedY, figureTitle);
      const closedForm = window.closedFormOf(recipe.speedX, recipe.speedY);
      closedFormElement.textContent =
        `r(t) = (${window.formatPolynomial(closedForm.xTerms)}) + i (${window.formatPolynomial(closedForm.yTerms)})`;
    }
    redraw();
  }
  buildRecipePanel("q9-controls", "q9-plot", "q9-readout", "Fig. Q9 | the bend-2 curve (recommended)",
    [{ key: "lineSlope", label: "k", min: 2, max: 6, step: 0.1, value: 4 },
     { key: "lineIntercept", label: "c", min: -10, max: -2, step: 0.1, value: -6 }],
    values => ({ speedX: [2, -3, 3], speedY: [2 * values.lineSlope + values.lineIntercept, -3 * values.lineSlope, 3 * values.lineSlope] }),
    [{ label: "bend 2.00 (k = 4, c = -6)", values: [4, -6] }], 2);
  buildRecipePanel("q10-controls", "q10-plot", "q10-readout", "Fig. Q10 | proposal 2: the even pair",
    [{ key: "speedXAtEnds", label: "speedXAtEnds", min: -1, max: 2, step: 0.05, value: 0.6 },
     { key: "speedXCurvature", label: "speedXCurvature", min: 0, max: 4, step: 0.05, value: 0.5 },
     { key: "speedYAtEnds", label: "speedYAtEnds", min: -1, max: 2, step: 0.05, value: 0.7 },
     { key: "speedYCurvature", label: "speedYCurvature", min: 0, max: 8, step: 0.05, value: 4 }],
    values => ({ speedX: [values.speedXAtEnds, -values.speedXCurvature, values.speedXCurvature],
                 speedY: [values.speedYAtEnds, -values.speedYCurvature, values.speedYCurvature] }),
    [{ label: "bend 1.91 | 0.6 / 0.5 / 0.7 / 4", values: [0.6, 0.5, 0.7, 4] },
     { label: "bend 2.01 | 0.5 / 0.5 / 0.78 / 4", values: [0.5, 0.5, 0.78, 4] },
     { label: "bend 2.69 | 0.5 / 0.5 / 0.7 / 4", values: [0.5, 0.5, 0.7, 4] }], 2);
  buildRecipePanel("q11-controls", "q11-plot", "q11-readout", "Fig. Q11 | proposal 3: the tilted pair",
    [{ key: "speedXAtEnds", label: "speedXAtEnds", min: -1, max: 8, step: 0.01, value: 0.592 },
     { key: "speedXCurvature", label: "speedXCurvature", min: 0, max: 8, step: 0.01, value: 0.53 },
     { key: "speedYAtEnds", label: "speedYAtEnds", min: -1, max: 8, step: 0.01, value: 0.694 },
     { key: "speedYLinear", label: "speedYLinear", min: -60, max: 0, step: 0.05, value: -4.048 },
     { key: "speedYCurvature", label: "speedYCurvature", min: 0, max: 60, step: 0.05, value: 4.099 }],
    values => ({ speedX: [values.speedXAtEnds, -values.speedXCurvature, values.speedXCurvature],
                 speedY: [values.speedYAtEnds, values.speedYLinear, values.speedYCurvature] }),
    [{ label: "the 2.04 find", values: [0.592, 0.53, 0.694, -4.048, 4.099] },
     { label: "x10 of 0.6 / 0.7 | pitch 6", values: [6, 5, 7, -40, 40] },
     { label: "x10 of 0.5 / 0.7 | pitch 2", values: [5, 5, 7, -40, 40] }]);
})();

(function () {
  const plotElement = document.getElementById("q13-plot");
  const exactElement = document.getElementById("q13-exact");
  const termsElement = document.getElementById("q13-terms");
  const canvasWidth = 900, canvasHeight = 520;
  const plotLeft = 46, plotRight = 606, plotTop = 96, plotBottom = 470;
  const diagramLeft = 630, diagramRight = 872, diagramTop = 150, diagramBottom = 392;
  const sampleCount = 700;
  const specs = [
    { key: "speedMidX", label: "speedMid.x", min: -4, max: 4, step: 0.05, value: 1.25, terms: ["#1f5fa8", "#a23b2a"] },
    { key: "speedMidY", label: "speedMid.y", min: -4, max: 4, step: 0.05, value: -1, terms: ["#1f5fa8", "#a23b2a"] },
    { key: "slopeMidX", label: "slopeMid.x", min: -4, max: 4, step: 0.05, value: 0, terms: ["#a23b2a"] },
    { key: "slopeMidY", label: "slopeMid.y", min: -4, max: 4, step: 0.05, value: 0, terms: ["#a23b2a"] },
    { key: "curvatureMidX", label: "curvatureMid.x", min: -16, max: 16, step: 0.05, value: 3, terms: ["#a23b2a", "#5b7f3a"] },
    { key: "curvatureMidY", label: "curvatureMid.y", min: -16, max: 16, step: 0.05, value: 12, terms: ["#a23b2a", "#5b7f3a"] }
  ];
  const presets = [
    { label: "bend 2 pick", values: [1.25, -1, 0, 0, 3, 12] },
    { label: "the target", values: [-0.3, 0.05, 0, 0.1, 2, 1.6] },
    { label: "near closure", values: [1, 0, 0, 0, -6.33, 5.66] },
    { label: "closure", values: [1, 0, 0, 0, -6.6667, 5.9628] },
    { label: "the triangle (3.34)", values: [0.25, -0.85, 0.95, 1.75, 3.15, 6.75] }
  ];
  const state = {};
  const grid = document.createElement("div");
  grid.className = "control-grid";
  specs.forEach(spec => {
    state[spec.key] = spec.value;
    const row = document.createElement("label");
    row.className = "control-row";
    const name = document.createElement("span");
    (spec.terms || []).forEach(colour => {
      const dot = document.createElement("span");
      dot.className = "term-dot";
      dot.style.background = colour;
      name.append(dot);
    });
    name.append(spec.label);
    const numberInput = document.createElement("input");
    numberInput.type = "number"; numberInput.step = spec.step; numberInput.value = spec.value;
    const rangeInput = document.createElement("input");
    rangeInput.type = "range"; rangeInput.min = spec.min; rangeInput.max = spec.max;
    rangeInput.step = spec.step; rangeInput.value = spec.value;
    numberInput.addEventListener("input", () => { rangeInput.value = numberInput.value; state[spec.key] = +numberInput.value; redraw(); });
    rangeInput.addEventListener("input", () => { numberInput.value = rangeInput.value; state[spec.key] = +rangeInput.value; redraw(); });
    row.append(name, numberInput, rangeInput);
    grid.append(row);
  });
  document.getElementById("q13-controls").append(grid);
  const presetRow = document.createElement("div");
  presetRow.className = "preset-row";
  presets.forEach(preset => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = preset.label;
    button.addEventListener("click", () => {
      preset.values.forEach((value, i) => {
        state[specs[i].key] = value;
        const row = grid.children[i];
        row.querySelector("input[type=number]").value = value;
        row.querySelector("input[type=range]").value = value;
      });
      redraw();
    });
    presetRow.append(button);
  });
  document.getElementById("q13-controls").append(presetRow);

  // the inverse: three chord terms -> speedMid, slopeMid, curvatureMid
  const inverseSpecs = [
    { key: "t1x", label: "T1.x", value: -0.66 }, { key: "t1y", label: "T1.y", value: -0.425 },
    { key: "t2x", label: "T2.x", value: 0.907 }, { key: "t2y", label: "T2.y", value: 0.112 },
    { key: "t3x", label: "T3.x", value: -0.446 }, { key: "t3y", label: "T3.y", value: 0.532 }
  ];
  const inverseState = {};
  const inverseRow = document.getElementById("q13-inverse");
  inverseSpecs.forEach(spec => {
    inverseState[spec.key] = spec.value;
    const label = document.createElement("label");
    label.className = "control-row";
    const name = document.createElement("span");
    name.textContent = spec.label;
    const input = document.createElement("input");
    input.type = "number"; input.step = 0.001; input.value = spec.value;
    input.addEventListener("input", () => { inverseState[spec.key] = +input.value; });
    label.append(name, input);
    inverseRow.append(label);
  });
  const solveButton = document.createElement("button");
  solveButton.type = "button";
  solveButton.className = "action-button";
  solveButton.textContent = "solve for the recipe";
  solveButton.addEventListener("click", () => {
    const complexSqrt = (re, im) => {
      const magnitude = Math.hypot(re, im), angle = Math.atan2(im, re) / 2;
      return [Math.sqrt(magnitude) * Math.cos(angle), Math.sqrt(magnitude) * Math.sin(angle)];
    };
    const t1 = [inverseState.t1x, inverseState.t1y];
    const t2 = [inverseState.t2x, inverseState.t2y];
    const t3 = [inverseState.t3x, inverseState.t3y];
    const speedMid = complexSqrt(t1[0], t1[1]);
    const curvatureMid = complexSqrt(80 * t3[0], 80 * t3[1]);
    const product = complexProduct(speedMid, curvatureMid);
    const slopeSquare = [12 * t2[0] - 2 * product[0], 12 * t2[1] - 2 * product[1]];
    const slopeMid = complexSqrt(slopeSquare[0], slopeSquare[1]);
    const recovered = { speedMidX: speedMid[0], speedMidY: speedMid[1],
                        slopeMidX: slopeMid[0], slopeMidY: slopeMid[1],
                        curvatureMidX: curvatureMid[0], curvatureMidY: curvatureMid[1] };
    Object.keys(recovered).forEach((key, index) => {
      const value = +recovered[key].toFixed(4);
      state[key] = value;
      const row = grid.children[index];
      row.querySelector("input[type=number]").value = value;
      row.querySelector("input[type=range]").value = value;
    });
    redraw();
  });
  inverseRow.append(solveButton);

  const dot = (a, b) => a[0] * b[0] + a[1] * b[1];
  const complexProduct = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
  const fmt = value => (Math.abs(value) < 5e-9 ? "0" : value.toFixed(3));
  const complexText = z => `${fmt(z[0])} ${z[1] < 0 ? "-" : "+"} ${fmt(Math.abs(z[1]))}i`;

  function redraw() {
    const speedMid = [state.speedMidX, state.speedMidY];
    const slopeMid = [state.slopeMidX, state.slopeMidY];
    const curvatureMid = [state.curvatureMidX, state.curvatureMidY];
    const speedX = [speedMid[0] - slopeMid[0] / 2 + curvatureMid[0] / 4,
                    slopeMid[0] - curvatureMid[0], curvatureMid[0]];
    const speedY = [speedMid[1] - slopeMid[1] / 2 + curvatureMid[1] / 4,
                    slopeMid[1] - curvatureMid[1], curvatureMid[1]];
    window.panelRecipes.q13 = { u: speedX, v: speedY };

    const arc = dot(speedMid, speedMid)
      + (dot(slopeMid, slopeMid) + 2 * dot(speedMid, curvatureMid)) / 12
      + dot(curvatureMid, curvatureMid) / 80;
    const firstTerm = complexProduct(speedMid, speedMid);
    const middleProduct = complexProduct(speedMid, curvatureMid).map(value => 2 * value);
    const slopeSquare = complexProduct(slopeMid, slopeMid);
    const secondTerm = [(middleProduct[0] + slopeSquare[0]) / 12, (middleProduct[1] + slopeSquare[1]) / 12];
    const thirdTerm = complexProduct(curvatureMid, curvatureMid).map(value => value / 80);
    const chord = [firstTerm[0] + secondTerm[0] + thirdTerm[0],
                   firstTerm[1] + secondTerm[1] + thirdTerm[1]];
    const chordLength = Math.hypot(chord[0], chord[1]);
    const bend = chordLength > 1e-12 ? arc / chordLength : Infinity;

    const evalQuadratic = (coefficients, t) => coefficients[0] + coefficients[1] * t + coefficients[2] * t * t;
    const curvePoints = [[0, 0]];
    let pointX = 0, pointY = 0;
    for (let i = 1; i <= sampleCount; i++) {
      const t = (i - 0.5) / sampleCount;
      const a = evalQuadratic(speedX, t), b = evalQuadratic(speedY, t);
      pointX += (a * a - b * b) / sampleCount;
      pointY += 2 * a * b / sampleCount;
      curvePoints.push([pointX, pointY]);
    }
    let arcSampled = 0;
    for (let i = 1; i < curvePoints.length; i++) {
      arcSampled += Math.hypot(curvePoints[i][0] - curvePoints[i - 1][0], curvePoints[i][1] - curvePoints[i - 1][1]);
    }
    const chordSampled = Math.hypot(curvePoints[sampleCount][0] - curvePoints[0][0],
                                    curvePoints[sampleCount][1] - curvePoints[0][1]);
    const bendSampled = chordSampled > 1e-9 ? arcSampled / chordSampled : Infinity;

    const coordinateXs = curvePoints.map(point => point[0]);
    const coordinateYs = curvePoints.map(point => point[1]);
    const minX = Math.min(...coordinateXs), maxX = Math.max(...coordinateXs);
    const minY = Math.min(...coordinateYs), maxY = Math.max(...coordinateYs);
    const plotWidth = plotRight - plotLeft, plotHeight = plotBottom - plotTop;
    const plotScale = Math.min(plotWidth / Math.max(1e-6, maxX - minX),
                               plotHeight / Math.max(1e-6, maxY - minY));
    const offsetX = plotLeft + (plotWidth - (maxX - minX) * plotScale) / 2;
    const offsetY = plotTop + (plotHeight - (maxY - minY) * plotScale) / 2;
    const toPixelX = value => offsetX + (value - minX) * plotScale;
    const toPixelY = value => offsetY + (maxY - value) * plotScale;
    const pathData = "M" + curvePoints.map(point => toPixelX(point[0]).toFixed(1) + "," + toPixelY(point[1]).toFixed(1)).join("L");

    // the chord diagram: the three terms head to tail
    const terms = [firstTerm, secondTerm, thirdTerm];
    let cumulativeX = 0, cumulativeY = 0;
    const heads = [[0, 0]];
    terms.forEach(termValue => {
      cumulativeX += termValue[0];
      cumulativeY += termValue[1];
      heads.push([cumulativeX, cumulativeY]);
    });
    const extent = Math.max(1e-6, ...heads.map(head => Math.max(Math.abs(head[0]), Math.abs(head[1]))));
    const diagramCenterX = (diagramLeft + diagramRight) / 2;
    const diagramCenterY = (diagramTop + diagramBottom) / 2;
    const diagramScale = Math.min(diagramRight - diagramLeft, diagramBottom - diagramTop) / 2 / extent * 0.9;
    const diagramX = value => diagramCenterX + value * diagramScale;
    const diagramY = value => diagramCenterY - value * diagramScale;
    const colours = ["#1f5fa8", "#a23b2a", "#5b7f3a"];
    let diagram = "";
    for (let i = 0; i < terms.length; i++) {
      diagram += `<line x1="${diagramX(heads[i][0]).toFixed(1)}" y1="${diagramY(heads[i][1]).toFixed(1)}" ` +
        `x2="${diagramX(heads[i + 1][0]).toFixed(1)}" y2="${diagramY(heads[i + 1][1]).toFixed(1)}" ` +
        `stroke="${colours[i]}" stroke-width="2.4"/>`;
    }
    diagram += `<line x1="${diagramX(0).toFixed(1)}" y1="${diagramY(0).toFixed(1)}" ` +
      `x2="${diagramX(chord[0]).toFixed(1)}" y2="${diagramY(chord[1]).toFixed(1)}" ` +
      `stroke="#2e2413" stroke-width="2" stroke-dasharray="5 4"/>`;
    diagram += `<circle cx="${diagramX(chord[0]).toFixed(1)}" cy="${diagramY(chord[1]).toFixed(1)}" r="3.5" fill="#2e2413"/>`;

    plotElement.innerHTML =
      `<rect width="${canvasWidth}" height="${canvasHeight}" fill="#fbf7ec"/>` +
      `<text x="${plotLeft}" y="28" font-size="15" font-weight="600" fill="#2e2413">Fig. Q13 | the exact bend formula, live</text>` +
      `<text x="${plotLeft}" y="48" font-size="12" fill="#7b6c4e">left: the curve from speedMid, slopeMid and curvatureMid | right: the three chord vectors head to tail, and their sum</text>` +
      `<path d="${pathData}" fill="none" stroke="#2e2413" stroke-width="2.4"/>` +
      `<text x="${plotLeft}" y="${canvasHeight - 16}" font-size="12" fill="#7b6c4e">bend ${bend.toFixed(3)} exact | ${bendSampled.toFixed(3)} sampled</text>` +
      diagram +
      `<text x="${diagramLeft}" y="${diagramTop - 14}" font-size="12" font-weight="600" fill="#2e2413">chord terms</text>` +
      `<text x="${diagramLeft}" y="${diagramBottom + 20}" font-size="11" fill="#1f5fa8">speedMid^2</text>` +
      `<text x="${diagramLeft}" y="${diagramBottom + 36}" font-size="11" fill="#a23b2a">+ (2 speedMid*curvatureMid + slopeMid^2)/12</text>` +
      `<text x="${diagramLeft}" y="${diagramBottom + 52}" font-size="11" fill="#5b7f3a">+ curvatureMid^2/80</text>` +
      `<text x="${diagramLeft}" y="${diagramBottom + 68}" font-size="11" fill="#2e2413">dashed: the chord, |chord| = ${chordLength.toFixed(3)}</text>`;

    exactElement.textContent =
      `arc   = ${arc.toFixed(4)}\n` +
      `chord = ${complexText(chord)}   |chord| = ${chordLength.toFixed(4)}\n` +
      `bend  = ${chordLength < 1e-9 ? "unbounded (closure)" : bend.toFixed(4)}`;
    termsElement.textContent =
      `speedMid^2 = ${complexText(firstTerm)}  |  ` +
      `(2 speedMid*curvatureMid + slopeMid^2)/12 = ${complexText(secondTerm)}  |  ` +
      `curvatureMid^2/80 = ${complexText(thirdTerm)}`;
  }
  redraw();
})();

(function () {
  const counter = document.getElementById("saved-count");
  counter.textContent = String(window.curveSaver.count());
  document.querySelectorAll(".save-curve").forEach(button => {
    button.addEventListener("click", () => {
      const key = button.dataset.panel;
      const recipe = window.panelRecipes[key];
      if (!recipe) return;
      const metrics = window.recipeMetrics(recipe.u, recipe.v);
      const closed = window.closedFormOf(recipe.u, recipe.v);
      window.curveSaver.add({
        saved: new Date().toISOString(),
        panel: key,
        u: recipe.u.map(value => String(value)),
        v: recipe.v.map(value => String(value)),
        bend: +metrics.bend.toFixed(2),
        pitch: metrics.pitch,
        inflection: metrics.inflection === null ? null : +metrics.inflection.toFixed(2),
        closest: +metrics.closest.toFixed(2),
        endpoint: metrics.endpoint.map(value => String(+value.toFixed(6))),
        closedForm: `(${window.formatPolynomial(closed.xTerms)}) + i (${window.formatPolynomial(closed.yTerms)})`
      });
      counter.textContent = String(window.curveSaver.count());
      button.textContent = "saved";
      setTimeout(() => { button.textContent = "save this curve"; }, 900);
    });
  });
  document.getElementById("saved-download").addEventListener("click", () => window.curveSaver.download());
  document.getElementById("saved-clear").addEventListener("click", () => {
    window.curveSaver.clear();
    counter.textContent = "0";
  });
})();

// Fig. Q14 - any degree: two coefficient lists in, curve and metrics out.
(function () {
  const plotElement = document.getElementById("q14-plot");
  if (!plotElement) return;
  const readout = document.getElementById("q14-readout");
  const hitsOut = document.getElementById("q14-hits");
  const canvasWidth = 900, canvasHeight = 470, plotMargin = 46, plotTopMargin = 88, sampleCount = 900;
  const parseToken = text => {
    const parts = String(text).split("/");
    return parts.length === 2 ? Number(parts[0]) / Number(parts[1]) : Number(parts[0]);
  };
  const parseList = text => String(text).split(/[\s,]+/).filter(Boolean).map(parseToken);
  const curveValue = (terms, t) => terms.reduce((sum, term, j) => sum + (term[0] / term[1]) * Math.pow(t, j + 1), 0);

  function redraw() {
    const speedX = parseList(document.getElementById("q14-u").value);
    const speedY = parseList(document.getElementById("q14-v").value);
    if (!speedX.length || !speedY.length || speedX.concat(speedY).some(Number.isNaN)) {
      readout.textContent = "two lists of numbers, please";
      return;
    }
    const metrics = window.recipeMetrics(speedX, speedY);
    const closed = window.closedFormOf(speedX, speedY);
    const points = [];
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (let i = 0; i <= sampleCount; i++) {
      const t = i / sampleCount;
      const x = curveValue(closed.xTerms, t), y = curveValue(closed.yTerms, t);
      points.push([x, y]);
      minX = Math.min(minX, x); maxX = Math.max(maxX, x);
      minY = Math.min(minY, y); maxY = Math.max(maxY, y);
    }
    const plotScale = Math.min((canvasWidth - 2 * plotMargin) / Math.max(1e-6, maxX - minX),
                               (canvasHeight - plotMargin - plotTopMargin) / Math.max(1e-6, maxY - minY));
    const offsetX = plotMargin + (canvasWidth - 2 * plotMargin - (maxX - minX) * plotScale) / 2;
    const offsetY = plotTopMargin + (canvasHeight - plotMargin - plotTopMargin - (maxY - minY) * plotScale) / 2;
    const toPixelX = value => offsetX + (value - minX) * plotScale;
    const toPixelY = value => offsetY + (maxY - value) * plotScale;
    const pathData = "M" + points.map(point => toPixelX(point[0]).toFixed(1) + "," + toPixelY(point[1]).toFixed(1)).join("L");
    const heading = `Fig. Q14 | any degree | speed degree ${speedX.length - 1} / ${speedY.length - 1}`;
    plotElement.innerHTML =
      `<rect width="${canvasWidth}" height="${canvasHeight}" fill="#fbf7ec"/>` +
      `<text x="${plotMargin}" y="28" font-size="15" font-weight="600" fill="#2e2413">${heading}</text>` +
      `<text x="${plotMargin}" y="48" font-size="12" fill="#7b6c4e">curve: r(t) = integral of (u + i v)^2 | bend, pitch and the rest are exact for these coefficients</text>` +
      `<path d="${pathData}" fill="none" stroke="#2e2413" stroke-width="2.4"/>`;
    readout.textContent = `bend ${metrics.bend.toFixed(3)} | pitch ${metrics.pitch.toLocaleString()} | ` +
      `inflection ${metrics.inflection === null ? " - " : metrics.inflection.toFixed(3)} | closest ${metrics.closest.toFixed(3)}`;
    const grid = metrics.pitch;
    const stops = [];
    if (grid <= 20000) {
      for (let m = 0; m <= grid; m++) {
        const t = m / grid;
        const x = curveValue(closed.xTerms, t) * grid, y = curveValue(closed.yTerms, t) * grid;
        if (Math.abs(x - Math.round(x)) < 1e-6 && Math.abs(y - Math.round(y)) < 1e-6) {
          stops.push(`(${Math.round(x)}, ${Math.round(y)})`);
        }
      }
    }
    hitsOut.textContent = `hits at the stops (t = m/pitch, numeric): ${stops.length ? stops.join(" ") : "none"}`;
  }

  document.getElementById("q14-draw").addEventListener("click", redraw);
  ["q14-u", "q14-v"].forEach(id => document.getElementById(id).addEventListener("change", redraw));
  redraw();
})();
