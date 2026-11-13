// The septic sandbox: a general polynomial curve and a PH septic, side by side.
//
// Panel A: r(t) = (x(t), y(t)), each axis span * sum n_k t^k for k = 1..7.
// Panel B: the PH septic, r' = w^2 with w cubic, so the position is degree 7.

(function () {
  const span = 625;

  // ---------- shared ----------
  const value = window.polynomialValue;
  const metrics = window.recipeMetrics;

  // ---------- the drawing ----------
  function draw(plot, points, title, subtitle, marks) {
    const width = 720, height = 520, left = 74, right = 40, top = 92, bottom = 64;
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
      input.type = "number"; input.step = "0.05"; input.min = "-5"; input.max = "5";
      input.value = aState[`a${axis}${k}`];
      const slider = document.createElement("input");
      slider.type = "range"; slider.min = "-5"; slider.max = "5"; slider.step = "0.05";
      slider.value = aState[`a${axis}${k}`];
      input.addEventListener("input", () => {
        slider.value = input.value; aState[`a${axis}${k}`] = +input.value; drawA();
      });
      slider.addEventListener("input", () => {
        input.value = slider.value; aState[`a${axis}${k}`] = +slider.value; drawA();
      });
      const pair = document.createElement("div");
      pair.className = "cell-inputs";
      pair.append(input, slider);
      cell.append(name, pair);
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
  const bCells = [];
  const decode = value => {
    if (!value) return { mantissa: 0, decade: 0 };
    const decade = Math.max(-2, Math.min(6, Math.floor(Math.log10(Math.abs(value)))));
    return { mantissa: value / Math.pow(10, decade), decade: decade };
  };
  // Never write a field back while it is the source of the change: a partial
  // entry ("-" or "0.") reads as an empty value in a number input, and writing
  // "0" over it eats the sign or the decimal point.
  function syncBCell(cell, value, { number = true, sliders = true } = {}) {
    if (number) cell.number.value = +value.toFixed(6);
    if (sliders) {
      const parts = decode(value);
      cell.fine.value = parts.mantissa;
      cell.decade.value = parts.decade;
    }
  }
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
      input.type = "number"; input.step = "0.05";
      input.value = bState[`b${axis}${k}`];
      const slider = document.createElement("input");
      slider.type = "range"; slider.min = "-16"; slider.max = "16"; slider.step = "0.05";
      const decade = document.createElement("input");
      decade.type = "range"; decade.min = "-2"; decade.max = "6"; decade.step = "1";
      decade.className = "decade";
      decade.title = "x 10^n";
      const elements = { number: input, fine: slider, decade: decade };
      bCells.push(elements);
      const stateKey = `b${axis}${k}`;
      const setValue = (value, sync) => {
        bState[stateKey] = value;
        syncBCell(elements, value, sync);
        drawB();
      };
      input.addEventListener("input", () => {
        const text = input.value.trim();
        if (text === "") return;                 // mid-entry: "-", "0.", "1e"
        const value = Number(text);
        if (!Number.isFinite(value)) return;
        setValue(value, { number: false });      // the field is the source
      });
      slider.addEventListener("input", () => {
        setValue(slider.value * Math.pow(10, +decade.value), { sliders: false });
      });
      decade.addEventListener("input", () => {
        // scale what the state holds, not the snapped slider value
        const mantissa = decode(bState[stateKey]).mantissa;
        setValue(mantissa * Math.pow(10, +decade.value), { sliders: false });
      });
      const pair = document.createElement("div");
      pair.className = "cell-inputs";
      pair.append(input, slider, decade);
      cell.append(name, pair);
      row.append(cell);
    }
    return row;
  };
  bGrid.append(bRow("x"), bRow("y"));
  [bState.bx0, bState.bx1, bState.bx2, bState.bx3,
   bState.by0, bState.by1, bState.by2, bState.by3].forEach((value, i) => {
    if (bCells[i]) syncBCell(bCells[i], value);
  });

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
    const curve = curveOf(speedX, speedY);
    const degreeOf = terms => {
      let degree = 0;
      terms.forEach((coefficient, k) => { if (Math.abs(coefficient) > 1e-9) degree = k; });
      return degree;
    };
    const degreeX = degreeOf(curve.x), degreeY = degreeOf(curve.y);
    const degree = Math.max(degreeX, degreeY);
    const product = multiply(curve.x, curve.y);
    const flat = product.every(coefficient => Math.abs(coefficient) < 1e-12);
    const flags = [degree === 7 ? `degree 7 (x ${degreeX}, y ${degreeY})`
                                : `degree ${degree} (x ${degreeX}, y ${degreeY}) - no t^7 term anywhere`];
    if (flat) flags.push("one coordinate is identically zero: an axis-aligned straight line");
    if (m.closest <= 1e-9) flags.push("the speed vanishes: a cusp");
    if (m.inflection === null) flags.push("no inflection: a C, not an S");
    const grade = flags.join(" | ");
    document.getElementById("b-grade").textContent = grade;
    document.getElementById("b-formula").textContent =
      `x(t) = ${polynomialText(curve.x)}\ny(t) = ${polynomialText(curve.y)}`;
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
    const width = 720, height = 520, pad = 60;
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
  // r(t) = integral of w^2, coefficient by coefficient.
  const multiply = (left, right) => {
    const product = new Array(left.length + right.length - 1).fill(0);
    left.forEach((l, i) => right.forEach((r, j) => { product[i + j] += l * r; }));
    return product;
  };
  function curveOf(speedX, speedY) {
    const xx = multiply(speedX, speedX), yy = multiply(speedY, speedY), xy = multiply(speedX, speedY);
    const x = [0], y = [0];
    for (let j = 0; j < xx.length; j++) {
      x.push((xx[j] - (yy[j] || 0)) / (j + 1));
      y.push(2 * xy[j] / (j + 1));
    }
    return { x, y };
  }
  const polynomialText = terms => {
    const parts = [];
    terms.forEach((coefficient, k) => {
      if (k === 0 || Math.abs(coefficient) < 5e-4) return;
      parts.push(`${coefficient < 0 ? " - " : " + "}${Math.abs(coefficient).toFixed(3)} t^${k}`);
    });
    return parts.join("").replace(/^ \+ /, "") || "0";
  };

  // The classic shapes: make consecutive terms perpendicular, or close the chord.
  const dot2 = (u, v) => u[0] * v[0] + u[1] * v[1];
  const parametersOf = () => [bState.bx1, bState.bx2, bState.bx3,
                              bState.by0, bState.by1, bState.by2, bState.by3];
  const speedOf = params => ({ x: [1, params[0], params[1], params[2]],
                               y: [params[3], params[4], params[5], params[6]] });
  const arcLength = (speedX, speedY) => {
    let total = 0;
    const steps = 400;
    for (let i = 0; i < steps; i++) {
      const t = (i + 0.5) / steps;
      const a = value(speedX, t), b = value(speedY, t);
      total += (a * a + b * b) / steps;
    }
    return total;
  };
  const cost = (params, mode, targetArc) => {
    const speed = speedOf(params);
    const terms = chordTerms(speed.x, speed.y);
    if (mode === "right") {
      let total = 0;
      for (let m = 0; m < 6; m++) { const d = dot2(terms[m], terms[m + 1]); total += d * d; }
      return total;
    }
    const sum = terms.reduce((acc, term) => [acc[0] + term[0], acc[1] + term[1]], [0, 0]);
    const chordCost = sum[0] * sum[0] + sum[1] * sum[1];
    // the arc-length constraint: a closed curve must not shrink to a point
    const arcCost = targetArc === undefined ? 0 : (arcLength(speed.x, speed.y) - targetArc) ** 2;
    const scale = Math.max(1e-9, targetArc === undefined ? 1 : targetArc) ** 2;
    return (chordCost + arcCost) / scale;
  };
  function solve(mode) {
    let params = parametersOf();
    const start = speedOf(params);
    const targetArc = mode === "close" ? arcLength(start.x, start.y) : undefined;
    let best = cost(params, mode, targetArc);
    let step = 0.05;
    const h = 1e-5;
    for (let iteration = 0; iteration < 4000; iteration++) {
      const gradient = params.map((value, i) => {
        const trial = params.slice();
        trial[i] += h;
        return (cost(trial, mode, targetArc) - best) / h;
      });
      const norm = Math.hypot(...gradient) || 1;
      let improved = false;
      for (let attempt = 0; attempt < 40; attempt++) {
        const trial = params.map((value, i) => value - step * gradient[i] / norm);
        const value = cost(trial, mode, targetArc);
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
    writeSpeed();
    drawB();
  }

  const speedValues = () => [bState.bx0, bState.bx1, bState.bx2, bState.bx3,
                             bState.by0, bState.by1, bState.by2, bState.by3];
  function writeSpeed() {
    speedValues().forEach((value, i) => {
      if (bCells[i]) syncBCell(bCells[i], value);
    });
  }
  function setSpeed(speedX, speedY) {
    [bState.bx0, bState.bx1, bState.bx2, bState.bx3] = speedX;
    [bState.by0, bState.by1, bState.by2, bState.by3] = speedY;
    writeSpeed();
    drawB();
  }

  // ---------- named curves ----------
  const seed = (window.septicCurves || []).map(curve => ({
    name: curve.name, speedX: curve.speedX, speedY: curve.speedY
  }));
  const storageKey = "septic-sandbox-curves";
  const localSaved = () => {
    try { return JSON.parse(localStorage.getItem(storageKey) || "[]"); } catch (error) { return []; }
  };
  const storeSaved = items => localStorage.setItem(storageKey, JSON.stringify(items));
  const allSaved = () => {
    const byName = {};
    seed.concat(localSaved()).forEach(item => { byName[item.name] = item; });
    return Object.values(byName);
  };
  function renderSaved() {
    const row = document.getElementById("b-saved");
    row.textContent = "";
    allSaved().forEach(item => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = item.name;
      button.title = JSON.stringify(item.speedX) + " / " + JSON.stringify(item.speedY);
      button.addEventListener("click", () => setSpeed(item.speedX, item.speedY));
      row.append(button);
    });
  }
  document.getElementById("b-save").addEventListener("click", () => {
    const nameInput = document.getElementById("b-name");
    const name = (nameInput.value || "").trim() || `curve ${localSaved().length + 1}`;
    const metrics = window.recipeMetrics(
      [bState.bx0, bState.bx1, bState.bx2, bState.bx3],
      [bState.by0, bState.by1, bState.by2, bState.by3]);
    const items = localSaved().filter(item => item.name !== name);
    items.push({
      name: name,
      speedX: [bState.bx0, bState.bx1, bState.bx2, bState.bx3],
      speedY: [bState.by0, bState.by1, bState.by2, bState.by3],
      bend: +metrics.bend.toFixed(3),
      pitch: metrics.pitch,
      inflection: metrics.inflection === null ? null : +metrics.inflection.toFixed(3),
      closest: +metrics.closest.toFixed(3)
    });
    storeSaved(items);
    nameInput.value = "";
    renderSaved();
  });
  document.getElementById("b-download").addEventListener("click", () => {
    const payload = { title: "septic sandbox curves", curves: allSaved() };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "septic-curves.json";
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
  });
  renderSaved();

  document.getElementById("b-load").addEventListener("click", () => {
    const status = document.getElementById("b-paste-status");
    const text = document.getElementById("b-paste").value.trim();
    if (!text) { status.textContent = "paste a curve or a {\"curves\": [...]} document"; return; }
    try {
      const data = JSON.parse(text);
      const list = Array.isArray(data) ? data : (data.curves ? data.curves : [data]);
      const items = localSaved();
      let loaded = 0;
      list.forEach(item => {
        if (!item || !Array.isArray(item.speedX) || !Array.isArray(item.speedY)) return;
        const name = item.name || `pasted ${items.length + 1}`;
        const record = { name: name,
                         speedX: item.speedX.map(Number), speedY: item.speedY.map(Number) };
        const index = items.findIndex(entry => entry.name === name);
        if (index >= 0) items[index] = record; else items.push(record);
        loaded += 1;
        if (loaded === 1) setSpeed(record.speedX, record.speedY);
      });
      storeSaved(items);
      renderSaved();
      status.textContent = loaded ? `${loaded} curve${loaded === 1 ? "" : "s"} loaded`
                                 : "no speedX / speedY in that JSON";
    } catch (error) {
      status.textContent = "not JSON: " + error.message;
    }
  });

  document.getElementById("b-right").addEventListener("click", () => solve("right"));
  document.getElementById("b-close").addEventListener("click", () => solve("close"));
  drawB();
})();

// Fig. Q16 - G2 Hermite interpolation at degree 7.
// Data: two points, two tangent angles, two curvatures.  The curve is a PH
// septic r' = w^2 with w cubic, eight real unknowns; six conditions plus two
// fairness terms, solved by Gauss-Newton.
(function () {
  const plot = document.getElementById("c-plot");
  if (!plot) return;
  const readout = document.getElementById("c-readout");
  const width = 720, height = 520, left = 70, right = 50, top = 92, bottom = 64;
  const specs = [
    { key: "theta0", label: "angle 0 (deg)", min: -180, max: 180, step: 1, value: 60 },
    { key: "theta1", label: "angle 1 (deg)", min: -180, max: 180, step: 1, value: 120 },
    { key: "k0", label: "curvature 0", min: -4, max: 4, step: 0.05, value: 0 },
    { key: "k1", label: "curvature 1", min: -4, max: 4, step: 0.05, value: 0 },
    { key: "ex", label: "end x", min: 0.2, max: 3, step: 0.05, value: 1 },
    { key: "ey", label: "end y", min: -1.5, max: 1.5, step: 0.05, value: 0 }
  ];
  const state = {};
  const grid = document.createElement("div");
  grid.className = "control-grid";
  specs.forEach(spec => {
    state[spec.key] = spec.value;
    const row = document.createElement("label");
    row.className = "control-row";
    const name = document.createElement("span");
    name.textContent = spec.label;
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
  document.getElementById("c-controls").append(grid);

  const cx = z => [z[0], z[1]];
  const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1]];
  const mul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
  const scale = (a, s) => [a[0] * s, a[1] * s];
  const conj = a => [a[0], -a[1]];
  const abs = a => Math.hypot(a[0], a[1]);

  // w(t) = a + b t + c t^2 + d t^3, p = [a,b,c,d] each [re, im]
  const wAt = (p, t) => add(add(p[0], scale(p[1], t)), add(scale(p[2], t * t), scale(p[3], t * t * t)));
  const wPrimeAt = (p, t) => add(p[1], add(scale(p[2], 2 * t), scale(p[3], 3 * t * t)));
  const dAt = (p, t) => {
    const w = wAt(p, t), wp = wPrimeAt(p, t);
    return scale(mul(w, w), 1); // r' = w^2
  };
  const curvatureAt = (p, t) => {
    const w = wAt(p, t), wp = wPrimeAt(p, t);
    const w2 = abs(w) ** 2;
    return 2 * (conj(w)[0] * wp[1] - conj(w)[1] * wp[0]) / (w2 * w2);
  };
  const displacement = p => {
    // integral of w^2 from 0 to 1, power basis
    const [a, b, c, d] = p;
    let total = [0, 0];
    const addTerm = (z, s) => { total = add(total, scale(z, s)); };
    addTerm(mul(a, a), 1);
    addTerm(mul(a, b), 1);
    addTerm(add(mul(b, b), scale(mul(a, c), 2)), 1 / 3);
    addTerm(add(mul(a, d), mul(b, c)), 1 / 2);
    addTerm(add(scale(mul(b, d), 2), mul(c, c)), 1 / 5);
    addTerm(mul(c, d), 1 / 3);
    addTerm(mul(d, d), 1 / 7);
    return total;
  };

  const residuals = (p, data) => {
    const a2 = mul(p[0], p[0]);
    const w1 = wAt(p, 1), w12 = mul(w1, w1);
    const t0 = [Math.cos(data.th0), Math.sin(data.th0)];
    const t1 = [Math.cos(data.th1), Math.sin(data.th1)];
    const delta = displacement(p);
    return [
      (a2[0] * t0[1] - a2[1] * t0[0]) / Math.max(1e-9, abs(a2)),
      (w12[0] * t1[1] - w12[1] * t1[0]) / Math.max(1e-9, abs(w12)),
      delta[0] - data.dx,
      delta[1] - data.dy,
      curvatureAt(p, 0) - data.k0,
      curvatureAt(p, 1) - data.k1
    ];
  };

  function solveLinear(matrix, rhs) {
    const n = rhs.length;
    const m = matrix.map((row, i) => row.concat([rhs[i]]));
    for (let col = 0; col < n; col++) {
      let pivot = col;
      for (let row = col + 1; row < n; row++) if (Math.abs(m[row][col]) > Math.abs(m[pivot][col])) pivot = row;
      [m[col], m[pivot]] = [m[pivot], m[col]];
      const divider = m[col][col] || 1e-12;
      for (let k = col; k <= n; k++) m[col][k] /= divider;
      for (let row = 0; row < n; row++) {
        if (row === col) continue;
        const factor = m[row][col];
        for (let k = col; k <= n; k++) m[row][k] -= factor * m[col][k];
      }
    }
    return m.map(row => row[n]);
  }

  function gaussNewton(data, start) {
    let p = start.map(z => z.slice());
    let best = residuals(p, data);
    let bestNorm = Math.hypot(...best);
    let lambda = 1e-3;
    for (let iteration = 0; iteration < 200; iteration++) {
      const r = residuals(p, data);
      const n = 8, J = [];
      for (let j = 0; j < n; j++) {
        const h = 1e-6;
        const q = p.map(z => z.slice());
        q[Math.floor(j / 2)][j % 2] += h;
        const rq = residuals(q, data);
        J.push(r.map((value, i) => (rq[i] - value) / h));
      }
      // normal equations J^T J + lambda I
      const A = Array.from({ length: n }, () => new Array(n).fill(0));
      const b = new Array(n).fill(0);
      for (let i = 0; i < r.length; i++) {
        for (let a = 0; a < n; a++) {
          b[a] -= J[a][i] * r[i];
          for (let k = 0; k < n; k++) A[a][k] += J[a][i] * J[k][i];
        }
      }
      for (let a = 0; a < n; a++) A[a][a] += lambda;
      const step = solveLinear(A, b);
      const trial = p.map((z, i) => [z[0] + step[2 * i], z[1] + step[2 * i + 1]]);
      const norm = Math.hypot(...residuals(trial, data));
      if (norm < bestNorm) {
        p = trial; bestNorm = norm; best = residuals(trial, data); lambda = Math.max(1e-9, lambda / 3);
      } else {
        lambda *= 10;
      }
      if (bestNorm < 1e-10 || lambda > 1e6) break;
    }
    return { p, norm: bestNorm };
  }

  let last = null;
  function redraw() {
    const data = {
      th0: state.theta0 * Math.PI / 180, th1: state.theta1 * Math.PI / 180,
      k0: state.k0, k1: state.k1, dx: state.ex, dy: state.ey
    };
    const a0 = Math.sqrt(Math.hypot(data.dx, data.dy) || 1);
    let best = null;
    for (let trial = 0; trial < 4; trial++) {
      const noise = trial === 0 ? 0 : 0.35;
      const start = [
        [a0 * Math.cos(data.th0 / 2) + noise * (Math.random() - 0.5), a0 * Math.sin(data.th0 / 2) + noise * (Math.random() - 0.5)],
        [noise * (Math.random() - 0.5), noise * (Math.random() - 0.5)],
        [noise * (Math.random() - 0.5), noise * (Math.random() - 0.5)],
        [noise * (Math.random() - 0.5), noise * (Math.random() - 0.5)]
      ];
      const result = gaussNewton(data, start);
      if (best === null || result.norm < best.norm) best = result;
    }
    last = best;
    // the curve
    const points = [[0, 0]];
    let x = 0, y = 0;
    const steps = 400;
    for (let i = 1; i <= steps; i++) {
      const t = (i - 0.5) / steps;
      const d = dAt(best.p, t);
      x += d[0] / steps; y += d[1] / steps;
      points.push([x, y]);
    }
    const xs = points.map(q => q[0]).concat([0, data.dx]);
    const ys = points.map(q => q[1]).concat([0, data.dy]);
    const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
    const padX = Math.max(0.05, (maxX - minX) * 0.08), padY = Math.max(0.05, (maxY - minY) * 0.08);
    const plotWidth = width - left - right, plotHeight = height - top - bottom;
    const s = Math.min(plotWidth / (maxX - minX + 2 * padX), plotHeight / (maxY - minY + 2 * padY));
    const ox = left + (plotWidth - (maxX - minX) * s) / 2, oy = top + (plotHeight - (maxY - minY) * s) / 2;
    const fx = v => ox + (v - minX) * s, fy = v => oy + (maxY - v) * s;
    const path = "M" + points.map(q => fx(q[0]).toFixed(1) + "," + fy(q[1]).toFixed(1)).join("L");
    const arrow = (px, py, angle, colour) => {
      const L = 0.22 * Math.max(1, Math.hypot(data.dx, data.dy));
      const ex = px + L * Math.cos(angle), ey = py + L * Math.sin(angle);
      return `<line x1="${fx(px)}" y1="${fy(py)}" x2="${fx(ex)}" y2="${fy(ey)}" stroke="${colour}" stroke-width="1.6"/>` +
        `<circle cx="${fx(ex)}" cy="${fy(ey)}" r="3" fill="${colour}"/>`;
    };
    const circle = (px, py, k, angle, colour) => {
      if (Math.abs(k) < 1e-6) return "";
      const radius = Math.abs(1 / k);
      const sign = k > 0 ? 1 : -1;
      const nx = Math.cos(angle + sign * Math.PI / 2), ny = Math.sin(angle + sign * Math.PI / 2);
      const cxx = px + radius * nx, cyy = py + radius * ny;
      return `<circle cx="${fx(cxx)}" cy="${fy(cyy)}" r="${radius * s}" fill="none" stroke="${colour}" stroke-width="1" stroke-dasharray="4 4" opacity="0.7"/>`;
    };
    plot.innerHTML =
      `<rect width="${width}" height="${height}" fill="#fbf7ec"/>` +
      `<text x="${left}" y="28" font-size="15" font-weight="600" fill="#2e2413">C | G2 Hermite interpolation at degree 7</text>` +
      `<text x="${left}" y="46" font-size="12" fill="#7b6c4e">blue: start tangent, red: end tangent, dashed: the curvature circles | curve: the PH septic</text>` +
      `<path d="${path}" fill="none" stroke="#2e2413" stroke-width="2.4"/>` +
      arrow(0, 0, data.th0, "#1f5fa8") +
      arrow(data.dx, data.dy, data.th1, "#a23b2a") +
      circle(0, 0, data.k0, data.th0, "#1f5fa8") +
      circle(data.dx, data.dy, data.k1, data.th1, "#a23b2a") +
      `<circle cx="${fx(0)}" cy="${fy(0)}" r="4" fill="#fbf7ec" stroke="#2e2413" stroke-width="2"/>` +
      `<circle cx="${fx(data.dx)}" cy="${fy(data.dy)}" r="4" fill="#fbf7ec" stroke="#2e2413" stroke-width="2"/>`;
    const k0 = curvatureAt(best.p, 0), k1 = curvatureAt(best.p, 1);
    const measured = window.recipeMetrics(best.p.map(z => z[0]), best.p.map(z => z[1]));
    readout.textContent =
      `residual ${best.norm.toFixed(4)} | curvature ${k0.toFixed(3)} and ${k1.toFixed(3)} ` +
      `(asked ${data.k0.toFixed(2)} and ${data.k1.toFixed(2)}) | bend ${measured.bend.toFixed(3)} ` +
      `| pitch ${measured.pitch.toLocaleString()}` +
      (best.norm > 0.01 ? " | no clean solution for this data" : "");
  }
  redraw();
})();
