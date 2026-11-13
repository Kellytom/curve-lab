// The septic sandbox: a general polynomial curve and a PH septic, side by side.
//
// Panel A: r(t) = (x(t), y(t)), each axis span * sum n_k t^k for k = 1..7.
// Panel B: the PH septic, r' = w^2 with w cubic, so the position is degree 7.

(function () {
  const span = 625;

  // ---------- shared ----------
  const value = (coefficients, t) => {
    let total = 0;
    for (let i = coefficients.length - 1; i >= 0; i--) total = total * t + coefficients[i];
    return total;
  };
  const derivative = coefficients => coefficients.slice(1).map((c, i) => c * (i + 1));
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

  function exactBend(speedX, speedY) {
    let cx = centred(speedX), cy = centred(speedY);
    const size = Math.max(cx.length, cy.length);
    cx = cx.concat(new Array(size - cx.length).fill(0));
    cy = cy.concat(new Array(size - cy.length).fill(0));
    let arc = 0, chordRe = 0, chordIm = 0;
    for (let k = 0; k < size; k++) {
      for (let l = 0; l < size; l++) {
        const w = weight(k + l);
        if (!w) continue;
        arc += (cx[k] * cx[l] + cy[k] * cy[l]) * w;
        chordRe += (cx[k] * cx[l] - cy[k] * cy[l]) * w;
        chordIm += (cx[k] * cy[l] + cy[k] * cx[l]) * w;
      }
    }
    const chord = Math.hypot(chordRe, chordIm);
    return { arc, chord: [chordRe, chordIm], bend: chord > 1e-15 ? arc / chord : Infinity };
  }

  function pitch(speedX, speedY) {
    const decimalPlaces = v => { const s = String(+v.toFixed(6)); const d = s.indexOf("."); return d < 0 ? 0 : s.length - d - 1; };
    const scale = Math.pow(10, Math.max(...speedX.concat(speedY).map(decimalPlaces)));
    const scaledX = speedX.map(v => Math.round(v * scale));
    const scaledY = speedY.map(v => Math.round(v * scale));
    const multiply = (a, b) => {
      const out = new Array(a.length + b.length - 1).fill(0);
      a.forEach((x, i) => b.forEach((y, j) => { out[i + j] += x * y; }));
      return out;
    };
    const gcd = (a, b) => (b ? gcd(b, a % b) : a);
    const lcm = (a, b) => a / gcd(a, b) * b;
    const xSquared = multiply(scaledX, scaledX), ySquared = multiply(scaledY, scaledY);
    const xTimesY = multiply(scaledX, scaledY);
    let result = 1;
    for (let j = 0; j < xSquared.length; j++) {
      for (const numerator of [xSquared[j] - (ySquared[j] || 0), 2 * xTimesY[j]]) {
        if (!numerator) continue;
        const denominator = scale * scale * (j + 1);
        result = lcm(result, denominator / gcd(Math.abs(numerator), denominator));
      }
    }
    return result;
  }

  function metrics(speedX, speedY) {
    const exact = exactBend(speedX, speedY);
    const derivativeX = derivative(speedX), derivativeY = derivative(speedY);
    let closest = Infinity;
    for (let i = 0; i <= 600; i++) {
      const t = i / 600;
      closest = Math.min(closest, Math.hypot(value(speedX, t), value(speedY, t)));
    }
    const wronskian = t => value(speedX, t) * value(derivativeY, t) - value(speedY, t) * value(derivativeX, t);
    let inflection = null;
    for (let i = 0; i < 600 && inflection === null; i++) {
      const low = i / 600, high = (i + 1) / 600;
      if (wronskian(low) * wronskian(high) <= 0) {
        let a = low, b = high;
        for (let k = 0; k < 40; k++) {
          const middle = (a + b) / 2;
          if (wronskian(a) * wronskian(middle) <= 0) b = middle; else a = middle;
        }
        inflection = (a + b) / 2;
      }
    }
    return { bend: exact.bend, pitch: pitch(speedX, speedY), inflection, closest };
  }

  // ---------- the drawing ----------
  function draw(plot, points, title, subtitle, marks) {
    const width = 720, height = 700, left = 74, right = 40, top = 92, bottom = 64;
    const xs = points.map(p => p[0]), ys = points.map(p => p[1]);
    const rawMinX = Math.min(...xs, 0), rawMaxX = Math.max(...xs);
    const rawMinY = Math.min(...ys, 0), rawMaxY = Math.max(...ys);
    const padX = Math.max(1, (rawMaxX - rawMinX) * 0.06), padY = Math.max(1, (rawMaxY - rawMinY) * 0.06);
    const minX = rawMinX - padX, maxX = rawMaxX + padX;
    const minY = rawMinY - padY, maxY = rawMaxY + padY;
    const plotWidth = width - left - right, plotHeight = height - top - bottom;
    const scale = Math.min(plotWidth / Math.max(1e-6, maxX - minX), plotHeight / Math.max(1e-6, maxY - minY));
    const offsetX = left + (plotWidth - (maxX - minX) * scale) / 2;
    const offsetY = top + (plotHeight - (maxY - minY) * scale) / 2;
    const fx = v => offsetX + (v - minX) * scale;
    const fy = v => offsetY + (maxY - v) * scale;
    const path = "M" + points.map(p => fx(p[0]).toFixed(1) + "," + fy(p[1]).toFixed(1)).join("L");
    let art = `<rect width="${width}" height="${height}" fill="#fbf7ec"/>` +
      `<text x="${left}" y="28" font-size="15" font-weight="600" fill="#2e2413">${title}</text>` +
      `<text x="${left}" y="46" font-size="12" fill="#7b6c4e">${subtitle}</text>` +
      `<line x1="${offsetX.toFixed(1)}" y1="${fy(0).toFixed(1)}" x2="${(offsetX + (maxX - minX) * scale).toFixed(1)}" y2="${fy(0).toFixed(1)}" stroke="#c9bfa6" stroke-dasharray="3 5"/>` +
      `<line x1="${fx(0).toFixed(1)}" y1="${offsetY.toFixed(1)}" x2="${fx(0).toFixed(1)}" y2="${(offsetY + (maxY - minY) * scale).toFixed(1)}" stroke="#c9bfa6" stroke-dasharray="3 5"/>` +
      `<path d="${path}" fill="none" stroke="#2e2413" stroke-width="2.4"/>` +
      `<text x="${left + plotWidth / 2}" y="${height - 18}" font-size="13" text-anchor="middle" fill="#2e2413">x, grid units</text>` +
      `<text x="20" y="${top + plotHeight / 2}" font-size="13" text-anchor="middle" fill="#2e2413" transform="rotate(-90 20 ${top + plotHeight / 2})">y, grid units</text>`;
    (marks || []).forEach(mark => {
      art += `<circle cx="${fx(mark[0]).toFixed(1)}" cy="${fy(mark[1]).toFixed(1)}" r="4" fill="#fbf7ec" stroke="#a23b2a" stroke-width="2"/>`;
    });
    plot.innerHTML = art;
  }

  // ---------- panel A: the general polynomial ----------
  const aKeys = { x: [], y: [] };
  ["x", "y"].forEach(axis => {
    for (let k = 1; k <= 7; k++) aKeys[axis].push(`a${axis}${k}`);
  });
  const aDefaults = {
    ax1: 1, ax2: 0, ax3: 0, ax4: 0, ax5: 0, ax6: 0, ax7: 0,
    ay1: 0.2, ay2: -1.5, ay3: 4.5, ay4: -2.0, ay5: 1.8, ay6: -2.4, ay7: 0.4
  };
  const aState = { ...aDefaults };
  const aGrid = document.getElementById("a-controls");
  const aRow = (axis) => {
    const row = document.createElement("div");
    row.className = "spine-row";
    const label = document.createElement("span");
    label.textContent = axis;
    row.append(label);
    for (let k = 1; k <= 7; k++) {
      const cell = document.createElement("label");
      cell.className = "spine-cell";
      const name = document.createElement("span");
      name.textContent = "t^" + k;
      const input = document.createElement("input");
      input.type = "number"; input.step = "0.1"; input.value = aState[`a${axis}${k}`];
      input.addEventListener("input", () => { aState[`a${axis}${k}`] = +input.value; drawA(); });
      cell.append(name, input);
      row.append(cell);
    }
    return row;
  };
  aGrid.append(aRow("x"), aRow("y"));

  function drawA() {
    const points = [];
    for (let i = 0; i <= 400; i++) {
      const t = i / 400;
      let x = 0, y = 0;
      for (let k = 1; k <= 7; k++) {
        x += aState[`ax${k}`] * Math.pow(t, k);
        y += aState[`ay${k}`] * Math.pow(t, k);
      }
      points.push([span * x, span * y]);
    }
    const end = points[points.length - 1];
    const tangent = points[points.length - 1][1] - points[points.length - 2][1];
    draw(document.getElementById("a-plot"), points,
         "A | the general polynomial",
         "r(t) = span * sum n_k t^k on each axis, k = 1..7 | the endpoint and its exit slope are below",
         [[0, 0], end]);
    const vectors = [];
    for (let k = 1; k <= 7; k++) vectors.push(Math.round(aState[`ay${k}`] * span * [1, 2, 6, 24, 120, 720, 5040][k - 1]));
    document.getElementById("a-readout").textContent =
      `endpoint (${end[0].toFixed(0)}, ${end[1].toFixed(0)}) | exit slope ${(tangent / (span / 400)).toFixed(3)} | ` +
      `y control vectors u_k = n_k*span*k! : ${vectors.slice(4).join(", ")}`;
  }
  drawA();

  // ---------- panel B: the PH septic ----------
  const bDefaults = { bx0: 2, bx1: -3, bx2: 3, bx3: 0.3, by0: 2, by1: -12, by2: 12, by3: 0 };
  const bState = { ...bDefaults };
  const bGrid = document.getElementById("b-controls");
  const bRow = axis => {
    const row = document.createElement("div");
    row.className = "spine-row";
    const label = document.createElement("span");
    label.textContent = axis;
    row.append(label);
    for (let k = 0; k <= 3; k++) {
      const cell = document.createElement("label");
      cell.className = "spine-cell";
      const name = document.createElement("span");
      name.textContent = "t^" + k;
      const input = document.createElement("input");
      input.type = "number"; input.step = "0.05"; input.value = bState[`b${axis}${k}`];
      input.addEventListener("input", () => { bState[`b${axis}${k}`] = +input.value; drawB(); });
      cell.append(name, input);
      row.append(cell);
    }
    return row;
  };
  bGrid.append(bRow("x"), bRow("y"));

  function drawB() {
    const speedX = [bState.bx0, bState.bx1, bState.bx2, bState.bx3];
    const speedY = [bState.by0, bState.by1, bState.by2, bState.by3];
    const points = [[0, 0]];
    let x = 0, y = 0;
    const steps = 900;
    for (let i = 1; i <= steps; i++) {
      const t = (i - 0.5) / steps;
      const a = value(speedX, t), b = value(speedY, t);
      x += (a * a - b * b) / steps;
      y += 2 * a * b / steps;
      points.push([x, y]);
    }
    const m = metrics(speedX, speedY);
    draw(document.getElementById("b-plot"), points,
         "B | the PH septic: r' = w^2 with w cubic",
         "w = (b_x) + i (b_y), each cubic | the position is degree 7 and the offsets are rational",
         [[0, 0], points[points.length - 1]]);
    document.getElementById("b-readout").textContent =
      `bend ${m.bend.toFixed(3)} | pitch ${m.pitch.toLocaleString()} | ` +
      `inflection ${m.inflection === null ? " - " : m.inflection.toFixed(3)} | closest ${m.closest.toFixed(3)}`;
    drawChordTerms(speedX, speedY);
  }

  // The chord terms of the septic: w^2 has degree 6, so seven vectors.
  function chordTerms(speedX, speedY) {
    const terms = [];
    for (let m = 0; m <= 6; m++) {
      let re = 0, im = 0;
      for (let j = 0; j <= 3; j++) {
        const k = m - j;
        if (k < 0 || k > 3) continue;
        re += speedX[j] * speedX[k] - speedY[j] * speedY[k];
        im += speedX[j] * speedY[k] + speedY[j] * speedX[k];
      }
      terms.push([re / (m + 1), im / (m + 1)]);
    }
    return terms;
  }

  function drawChordTerms(speedX, speedY) {
    const plot = document.getElementById("b-vectors");
    const terms = chordTerms(speedX, speedY);
    const heads = [[0, 0]];
    let x = 0, y = 0;
    terms.forEach(term => { x += term[0]; y += term[1]; heads.push([x, y]); });
    const extent = Math.max(1e-9, ...heads.map(point => Math.max(Math.abs(point[0]), Math.abs(point[1]))));
    const width = 720, height = 420, pad = 60;
    const scale = Math.min(width - 2 * pad, height - 2 * pad) / 2 / extent * 0.92;
    const cx = width / 2, cy = height / 2;
    const fx = value => cx + value * scale;
    const fy = value => cy - value * scale;
    const colours = ["#1f5fa8", "#a23b2a", "#5b7f3a", "#8a5a9e", "#c07a1f", "#3f8a8a", "#8a3b2a"];
    let art = `<rect width="${width}" height="${height}" fill="#fbf7ec"/>` +
      `<text x="${pad}" y="28" font-size="15" font-weight="600" fill="#2e2413">B | the chord terms</text>` +
      `<text x="${pad}" y="48" font-size="12" fill="#7b6c4e">w^2 has degree 6, so seven vectors; head to tail they sum to the chord (dashed)</text>`;
    for (let i = 0; i < terms.length; i++) {
      art += `<line x1="${fx(heads[i][0]).toFixed(1)}" y1="${fy(heads[i][1]).toFixed(1)}" ` +
        `x2="${fx(heads[i + 1][0]).toFixed(1)}" y2="${fy(heads[i + 1][1]).toFixed(1)}" ` +
        `stroke="${colours[i]}" stroke-width="2.6"/>`;
      art += `<circle cx="${fx(heads[i + 1][0]).toFixed(1)}" cy="${fy(heads[i + 1][1]).toFixed(1)}" r="3" fill="${colours[i]}"/>`;
    }
    art += `<line x1="${fx(0).toFixed(1)}" y1="${fy(0).toFixed(1)}" x2="${fx(x).toFixed(1)}" y2="${fy(y).toFixed(1)}" ` +
      `stroke="#2e2413" stroke-width="2" stroke-dasharray="6 4"/>` +
      `<circle cx="${fx(0).toFixed(1)}" cy="${fy(0).toFixed(1)}" r="4" fill="#2e2413"/>` +
      `<text x="${fx(x) + 8}" y="${fy(y) - 8}" font-size="12" fill="#2e2413">chord (${x.toFixed(3)}, ${y.toFixed(3)})</text>`;
    for (let i = 0; i < terms.length; i++) {
      art += `<text x="${pad}" y="${height - 16 - (terms.length - 1 - i) * 16}" font-size="11" fill="${colours[i]}">` +
        `T${i} = (${terms[i][0].toFixed(3)}, ${terms[i][1].toFixed(3)})</text>`;
    }
    plot.innerHTML = art;
  }
  // The classic shapes: make consecutive terms perpendicular, or close the chord.
  const dot2 = (u, v) => u[0] * v[0] + u[1] * v[1];
  const parametersOf = () => [bState.bx1, bState.bx2, bState.bx3,
                              bState.by0, bState.by1, bState.by2, bState.by3];
  const speedOf = params => ({ x: [1, params[0], params[1], params[2]],
                               y: [params[3], params[4], params[5], params[6]] });
  const cost = (params, mode) => {
    const speed = speedOf(params);
    const terms = chordTerms(speed.x, speed.y);
    if (mode === "right") {
      let total = 0;
      for (let m = 0; m < 6; m++) { const d = dot2(terms[m], terms[m + 1]); total += d * d; }
      return total;
    }
    const sum = terms.reduce((acc, term) => [acc[0] + term[0], acc[1] + term[1]], [0, 0]);
    return sum[0] * sum[0] + sum[1] * sum[1];
  };
  function solve(mode) {
    let params = parametersOf();
    let best = cost(params, mode);
    let step = 0.05;
    const h = 1e-5;
    for (let iteration = 0; iteration < 4000; iteration++) {
      const gradient = params.map((value, i) => {
        const trial = params.slice();
        trial[i] += h;
        return (cost(trial, mode) - best) / h;
      });
      const norm = Math.hypot(...gradient) || 1;
      let improved = false;
      for (let attempt = 0; attempt < 40; attempt++) {
        const trial = params.map((value, i) => value - step * gradient[i] / norm);
        const value = cost(trial, mode);
        if (value < best) { params = trial; best = value; improved = true; step *= 1.2; break; }
        step *= 0.5;
      }
      if (!improved) break;
      if (best < 1e-20) break;
    }
    const speed = speedOf(params);
    const scale = bState.bx0 || 1;   // the solver fixes speedMid.x = 1; scale back
    bState.bx1 = scale * speed.x[1]; bState.bx2 = scale * speed.x[2]; bState.bx3 = scale * speed.x[3];
    bState.by0 = scale * speed.y[0]; bState.by1 = scale * speed.y[1]; bState.by2 = scale * speed.y[2]; bState.by3 = scale * speed.y[3];
    const inputs = document.querySelectorAll("#b-controls input");
    [bState.bx0, bState.bx1, bState.bx2, bState.bx3,
     bState.by0, bState.by1, bState.by2, bState.by3].forEach((value, i) => {
      if (inputs[i]) inputs[i].value = +value.toFixed(6);
    });
    drawB();
  }

  document.getElementById("b-right").addEventListener("click", () => solve("right"));
  document.getElementById("b-close").addEventListener("click", () => solve("close"));
  drawB();
})();
