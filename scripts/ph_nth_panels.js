// The eleventh power: a PH curve of position degree 11.
//
// r' = w^2 with w of degree 5, so twelve speed numbers (six real, six
// imaginary) and a position of degree 2*5 + 1 = 11. The maths is the same as
// the septic sandbox; only the degree changes, and every loop below is written
// in terms of the speed degree so a higher one is a constant, not a rewrite.

(function () {
  const SPEED_DEGREE = 5;               // w is degree 5
  const POINTS = SPEED_DEGREE + 1;      // 6 pairs
  const DEGREE = 2 * SPEED_DEGREE + 1;  // 11

  const metrics = window.recipeMetrics;
  const value = window.polynomialValue;

  const defaults = {
    x: [2, -5, 6, 1, 0, 0],
    y: [4, -22, 22, -2, 0, 0],
  };
  const state = { x: defaults.x.slice(), y: defaults.y.slice() };
  let currentName = "curve";

  const cells = [];
  const grid = document.getElementById("n-controls");

  function decode(number) {
    if (!number) return { mantissa: 0, decade: 0 };
    const decade = Math.max(-2, Math.min(6, Math.floor(Math.log10(Math.abs(number)))));
    return { mantissa: number / Math.pow(10, decade), decade: decade };
  }
  function syncCell(cell, number, { write = true, sliders = true } = {}) {
    if (write) cell.number.value = +number.toFixed(6);
    if (sliders) cell.fine.value = Math.abs(decode(number).mantissa);
  }

  // a pair of steppers that move a value to the next integer up or down
  function stepInteger(value, direction) {
    if (direction > 0) return Number.isInteger(value) ? value + 1 : Math.floor(value) + 1;
    return Number.isInteger(value) ? value - 1 : Math.ceil(value) - 1;
  }
  function steppers(input, apply) {
    const wrap = document.createElement("span");
    wrap.className = "steppers";
    [["\u25b2", 1], ["\u25bc", -1]].forEach(([label, direction]) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "step";
      button.textContent = label;
      button.title = direction > 0 ? "next integer up" : "next integer down";
      button.addEventListener("click", () => apply(direction));
      wrap.append(button);
    });
    input.insertAdjacentElement("afterend", wrap);
    return wrap;
  }

  function buildRow(axis) {
    const row = document.createElement("div");
    row.className = "spine-row";
    const label = document.createElement("span");
    label.textContent = axis;
    row.append(label);
    for (let k = 0; k < POINTS; k++) {
      const cell = document.createElement("label");
      cell.className = "spine-cell";
      const name = document.createElement("span");
      name.textContent = "t^" + k;
      const number = document.createElement("input");
      number.type = "number"; number.step = "0.1";
      number.value = state[axis][k];
      const fine = document.createElement("input");
      fine.type = "range"; fine.min = "0"; fine.max = "10"; fine.step = "0.1";
      fine.title = "size, sign from the box";
      const scales = document.createElement("span");
      scales.className = "scales";
      [["1", 0], ["10", 1], ["100", 2]].forEach(([label, power]) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "scale";
        button.textContent = label;
        button.title = `mantissa x ${label}`;
        button.addEventListener("click", () => {
          const current = axis === "x" ? state.x[k] : state.y[k];
          set(decode(current).mantissa * Math.pow(10, power));
        });
        scales.append(button);
      });
      const elements = { number, fine };
      cells.push({ axis, k, ...elements });
      const set = (v) => {
        currentName = "curve";
        if (axis === "x") state.x[k] = v; else state.y[k] = v;
        syncCell(elements, v);          // the slider is the source: write the box
        draw();
      };
      number.addEventListener("input", () => {
        const text = number.value.trim();
        if (text === "") return;
        const v = Number(text);
        if (!Number.isFinite(v)) return;
        currentName = "curve";
        if (axis === "x") state.x[k] = v; else state.y[k] = v;
        syncCell(elements, v, { write: false });
        draw();
      });
      fine.addEventListener("input", () => {
        const current = axis === "x" ? state.x[k] : state.y[k];
        const sign = current < 0 ? -1 : 1;
        set(sign * +fine.value * Math.pow(10, decode(current).decade));
      });
      const pair = document.createElement("div");
      pair.className = "cell-inputs";
      pair.append(number, fine, scales);
      steppers(number, direction => {
        const current = axis === "x" ? state.x[k] : state.y[k];
        set(stepInteger(current, direction));
      });
      cell.append(name, pair);
      row.append(cell);
    }
    return row;
  }
  grid.append(buildRow("x"), buildRow("y"));
  function writeCells() {
    cells.forEach(cell => syncCell(cell, cell.axis === "x" ? state.x[cell.k] : state.y[cell.k]));
  }

  // ---------- the offsets, the terminal ----------
  // Parallel for now: r + d*n with d a constant half-width. The flare law moved
  // to workbench/ph-nth-serif-notes.html, where it is studied on its own.
  // d is a percentage of the curve's own size, not an absolute number: a 0.3
  // curve and a 1400 curve should both show their offsets. The size is the
  // diagonal of the spine's bounding box.
  const width = { percent: 1.5 };
  let curveSize = 1;
  const halfWidth = () => Math.max(1e-9, width.percent / 100 * curveSize);

  // what the page draws: the spine alone by default
  const view = { rails: false, character: false, startTerminal: false, endTerminal: false };

  // A character offset: the parallel rail, bowed. The bow is the difference
  // between integrating the speed turned a little at each station
  // (g = w (1 + i eps b(t))) and integrating it untouched, both from the same
  // start. That difference is pinned to zero at both ends, so the rail meets
  // the parallel at +/- d at the start and the end and bows in between. It is
  // the character, not a drift: at character 0 the rail is the parallel rail.
  const character = { strength: 2 };
  function integrateFrom(startX, startY, speedAt, steps) {
    let x = startX, y = startY;
    const points = [[x, y]];
    for (let i = 0; i < steps; i++) {
      const t = (i + 0.5) / steps;
      const [gr, gi] = speedAt(t);
      x += (gr * gr - gi * gi) / steps;
      y += 2 * gr * gi / steps;
      points.push([x, y]);
    }
    return points;
  }
  function characterRail(sign) {
    const steps = 700;
    const spine = spineSamples(steps);
    const start = spine[0];
    const d = halfWidth();
    const from = [start.x + sign * d * start.nx, start.y + sign * d * start.ny];
    const flat = integrateFrom(from[0], from[1], t => [value(state.x, t), value(state.y, t)], steps);
    const eps = 0.08 * character.strength;
    const turned = integrateFrom(from[0], from[1], t => {
      const p = value(state.x, t), q = value(state.y, t);
      const a = sign * eps * 4 * t * (1 - t);
      return [p - a * q, q + a * p];
    }, steps);
    return spine.map((s, i) => {
      const parallel = [s.x + sign * d * s.nx, s.y + sign * d * s.ny];
      const weight = 4 * (i / steps) * (1 - i / steps);
      return [parallel[0] + weight * (turned[i][0] - flat[i][0]),
              parallel[1] + weight * (turned[i][1] - flat[i][1])];
    });
  }

  function spineSamples(n = 700) {
    const out = [];
    let x = 0, y = 0;
    for (let i = 0; i <= n; i++) {
      const t = i / n;
      const p = value(state.x, t), q = value(state.y, t);
      const speed2 = p * p + q * q;
      const tx = speed2 > 1e-12 ? (p * p - q * q) / speed2 : 1;
      const ty = speed2 > 1e-12 ? 2 * p * q / speed2 : 0;
      out.push({ t, x, y, tx, ty, nx: -ty, ny: tx });
      if (i < n) {
        const tm = (i + 0.5) / n;
        const pm = value(state.x, tm), qm = value(state.y, tm);
        x += (pm * pm - qm * qm) / n;
        y += 2 * pm * qm / n;
      }
    }
    return out;
  }

  // the arc through three points: a round terminal of radius d at that end
  function arcThrough(cx, cy, from, to, through, steps = 48) {
    const radius = Math.hypot(from[0] - cx, from[1] - cy) || 1e-9;
    const a0 = Math.atan2(from[1] - cy, from[0] - cx);
    const a1 = Math.atan2(to[1] - cy, to[0] - cx);
    const pick = [a1, a1 + 2 * Math.PI, a1 - 2 * Math.PI].map(end => {
      const mid = (a0 + end) / 2;
      const p = [cx + Math.cos(mid) * radius, cy + Math.sin(mid) * radius];
      return { end, gap: Math.hypot(p[0] - through[0], p[1] - through[1]) };
    }).sort((u, v) => u.gap - v.gap)[0];
    const points = [];
    for (let i = 0; i <= steps; i++) {
      const a = a0 + (pick.end - a0) * i / steps;
      points.push([cx + radius * Math.cos(a), cy + radius * Math.sin(a)]);
    }
    return points;
  }

  // a simple arc terminal: a semicircle of radius d joining the two rails and
  // bulging along the tangent (forward at the end, backward at the start)
  function terminalArc(spine, atStart) {
    const s = atStart ? spine[0] : spine[spine.length - 1];
    const d = halfWidth();
    const sign = atStart ? -1 : 1;
    const A = [s.x + d * s.nx, s.y + d * s.ny];
    const B = [s.x - d * s.nx, s.y - d * s.ny];
    const tip = [s.x + sign * d * s.tx, s.y + sign * d * s.ty];
    const arc = arcThrough(s.x, s.y, A, B, tip);
    return { arc, tip, d };
  }

  // ---------- the drawing ----------
  function draw() {
    const plot = document.getElementById("n-plot");
    const spine = spineSamples();
    const spineXs = spine.map(s => s.x), spineYs = spine.map(s => s.y);
    const diagonal = Math.hypot(Math.max(...spineXs) - Math.min(...spineXs),
                                Math.max(...spineYs) - Math.min(...spineYs));
    const measured = metrics(state.x, state.y);
    curveSize = Math.max(1e-9, Math.max(Math.hypot(measured.chord[0], measured.chord[1]), 0.25 * diagonal));
    const d = halfWidth();
    const leftRail = spine.map(s => [s.x + d * s.nx, s.y + d * s.ny]);
    const rightRail = spine.map(s => [s.x - d * s.nx, s.y - d * s.ny]);
    const characterLeft = view.character ? characterRail(1) : null;
    const characterRight = view.character ? characterRail(-1) : null;
    const startEnd = view.startTerminal ? terminalArc(spine, true) : null;
    const finishEnd = view.endTerminal ? terminalArc(spine, false) : null;
    const all = spine.map(s => [s.x, s.y]);
    if (view.rails) all.push(...leftRail, ...rightRail);
    if (characterLeft) all.push(...characterLeft, ...characterRight);
    if (startEnd) all.push(...startEnd.arc, startEnd.tip);
    if (finishEnd) all.push(...finishEnd.arc, finishEnd.tip);
    const xs = all.map(p => p[0]), ys = all.map(p => p[1]);
    const padX = Math.max(1e-6, (Math.max(...xs) - Math.min(...xs)) * 0.08);
    const padY = Math.max(1e-6, (Math.max(...ys) - Math.min(...ys)) * 0.08);
    const minX = Math.min(...xs) - padX, maxX = Math.max(...xs) + padX;
    const minY = Math.min(...ys) - padY, maxY = Math.max(...ys) + padY;
    const width_ = 720, height = 520, left = 74, right = 40, top = 92, bottom = 64;
    const scale = Math.min((width_ - left - right) / (maxX - minX), (height - top - bottom) / (maxY - minY));
    const ox = left + ((width_ - left - right) - (maxX - minX) * scale) / 2;
    const oy = top + ((height - top - bottom) - (maxY - minY) * scale) / 2;
    const fx = v => ox + (v - minX) * scale, fy = v => oy + (maxY - v) * scale;
    const path = points => "M" + points.map(p => fx(p[0]).toFixed(1) + "," + fy(p[1]).toFixed(1)).join("L");
    let art = `<rect width="${width_}" height="${height}" fill="#fbf7ec"/>` +
      `<text x="${left}" y="28" font-size="15" font-weight="600" fill="#2e2413">The eleventh power: a PH spine${view.rails ? ", a flared full line" : ""}</text>` +
      `<text x="${left}" y="46" font-size="12" fill="#7b6c4e">` +
      (view.rails ? `rails r +/- d n, d constant` : `the spine alone; rails and terminals are below`) +
      `${view.startTerminal || view.endTerminal ? " | terminal: an arc of radius d" : ""}</text>` +
      `<line x1="${fx(minX).toFixed(1)}" y1="${fy(0).toFixed(1)}" x2="${fx(maxX).toFixed(1)}" y2="${fy(0).toFixed(1)}" stroke="#c9bfa6" stroke-dasharray="3 5"/>` +
      `<line x1="${fx(0).toFixed(1)}" y1="${fy(minY).toFixed(1)}" x2="${fx(0).toFixed(1)}" y2="${fy(maxY).toFixed(1)}" stroke="#c9bfa6" stroke-dasharray="3 5"/>`;
    if (view.rails) {
      art += `<path d="${path(leftRail)}" fill="none" stroke="#1f5fa8" stroke-width="1.8"/>` +
             `<path d="${path(rightRail)}" fill="none" stroke="#1f5fa8" stroke-width="1.8"/>`;
    }
    if (characterLeft) {
      art += `<path d="${path(characterLeft)}" fill="none" stroke="#5b7f3a" stroke-width="2"/>` +
             `<path d="${path(characterRight)}" fill="none" stroke="#5b7f3a" stroke-width="2"/>`;
    }
    art += `<path d="${path(spine.map(s => [s.x, s.y]))}" fill="none" stroke="#2e2413" stroke-width="2.4"/>`;
    if (startEnd) art += `<path d="${path(startEnd.arc)}" fill="none" stroke="#a23b2a" stroke-width="2.4"/>`;
    if (finishEnd) art += `<path d="${path(finishEnd.arc)}" fill="none" stroke="#a23b2a" stroke-width="2.4"/>`;
    art += `<circle cx="${fx(0).toFixed(1)}" cy="${fy(0).toFixed(1)}" r="4" fill="#1f5fa8"/>`;
    // legend inside the figure, 15px, naming the spine first
    const legend = [["#2e2413", 2.4, "spine"]];
    if (view.rails) legend.push(["#1f5fa8", 1.8, "parallel rail"]);
    if (view.character) legend.push(["#5b7f3a", 2, "character offset"]);
    if (startEnd || finishEnd) legend.push(["#a23b2a", 2.4, "terminal arc, radius d"]);
    let legendX = left;
    legend.forEach(([colour, widthStroke, text]) => {
      art += `<line x1="${legendX}" y1="${height - 16}" x2="${legendX + 26}" y2="${height - 16}" ` +
        `stroke="${colour}" stroke-width="${widthStroke}"/>` +
        `<text x="${legendX + 34}" y="${height - 11}" font-size="15" fill="#2e2413">${text}</text>`;
      legendX += 34 + text.length * 8.2 + 26;
    });
    plot.innerHTML = art;

    const m = metrics(state.x, state.y);
    const openness = m.arc > 1e-12 ? Math.hypot(m.chord[0], m.chord[1]) / m.arc : 0;
    const curve = curveOf();
    const degreeOf = terms => { let d = 0; terms.forEach((c, k) => { if (Math.abs(c) > 1e-9) d = k; }); return d; };
    document.getElementById("n-readout").textContent =
      `bend ${m.bend.toFixed(3)} | pitch ${m.pitch.toLocaleString()} | ` +
      `inflection ${m.inflection === null ? " - " : m.inflection.toFixed(3)} | ` +
      `closest ${m.closest.toFixed(3)} | open ${openness.toFixed(3)}`;
    const showing = [view.rails ? "parallel rails" : view.character ? "character offsets" : "spine only"];
    if (view.startTerminal) showing.push("start terminal");
    if (view.endTerminal) showing.push("end terminal");
    document.getElementById("n-width-readout").textContent =
      `d ${width.percent.toFixed(2)}% of the curve = ${halfWidth().toFixed(3)} units | showing ${showing.join(", ")}`;
    document.getElementById("n-grade").textContent =
      `degree ${Math.max(degreeOf(curve.x), degreeOf(curve.y))} (x ${degreeOf(curve.x)}, y ${degreeOf(curve.y)})` +
      (m.inflection === null ? " | no inflection: a C, not an S" : "");
    document.getElementById("n-formula").textContent =
      `x(t) = ${polynomialText(curve.x)}\ny(t) = ${polynomialText(curve.y)}\n` +
      `speed, the twelve boxes: x ${state.x.join(", ")} | y ${state.y.join(", ")}`;
    const box = document.getElementById("n-json");
    if (box) {
      box.value = JSON.stringify({
        name: currentName,
        speedX: state.x.map(v => +v),
        speedY: state.y.map(v => +v),
        bend: +m.bend.toFixed(3),
        pitch: m.pitch,
        inflection: m.inflection === null ? null : +m.inflection.toFixed(3),
        closest: +m.closest.toFixed(3),
        degree: [degreeOf(curve.x), degreeOf(curve.y)],
        width: { percent: width.percent },
        character: character.strength,
      }, null, 2);
    }
    drawBars();
  }

  const multiply = (left, right) => {
    const product = new Array(left.length + right.length - 1).fill(0);
    left.forEach((l, i) => right.forEach((r, j) => { product[i + j] += l * r; }));
    return product;
  };
  function curveOf() {
    const xx = multiply(state.x, state.x), yy = multiply(state.y, state.y), xy = multiply(state.x, state.y);
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

  // ---------- the chord terms, as signed bars ----------
  function chordTerms() {
    const terms = [];
    for (let m = 0; m <= 2 * SPEED_DEGREE; m++) {
      let re = 0, im = 0;
      for (let j = 0; j <= SPEED_DEGREE; j++) {
        const k = m - j;
        if (k < 0 || k > SPEED_DEGREE) continue;
        re += state.x[j] * state.x[k] - state.y[j] * state.y[k];
        im += state.x[j] * state.y[k] + state.y[j] * state.x[k];
      }
      terms.push([re / (m + 1), im / (m + 1)]);
    }
    return terms;
  }
  function drawBars() {
    const plot = document.getElementById("n-bars");
    if (!plot) return;
    const terms = chordTerms();
    const rows = terms.length;
    const width = 720, height = 460, pad = 64;
    const left = 76, right = width - pad, top = 60, bottom = height - 96;
    const rowHeight = (bottom - top) / rows;
    const biggest = Math.max(1e-9, ...terms.flatMap(t => [Math.abs(t[0]), Math.abs(t[1])]));
    const zero = (left + right) / 2;
    const xOf = v => zero + v / biggest * (right - left) / 2;
    let art = `<rect width="${width}" height="${height}" fill="#fbf7ec"/>` +
      `<text x="${pad}" y="28" font-size="15" font-weight="600" fill="#2e2413">The eleven chord terms, as signed bars</text>` +
      `<text x="${pad}" y="48" font-size="12" fill="#7b6c4e">T_m = (w^2)_m / (m+1); t^1 to t^11 left to right, x above y in each row</text>`;
    art += `<line x1="${zero}" y1="${top - 6}" x2="${zero}" y2="${bottom + 4}" stroke="#2e2413" stroke-width="1.5"/>`;
    for (let r = 0; r < rows; r++) {
      const centre = top + rowHeight * r + rowHeight / 2;
      art += `<text x="${pad}" y="${(centre + 4).toFixed(1)}" font-size="12" fill="#2e2413">t^${r + 1}</text>`;
      [[terms[r][0], "#2e2413", centre - 5], [terms[r][1], "#8a6a3a", centre + 5]].forEach(([v, colour, y]) => {
        const start = Math.min(zero, xOf(v));
        const length = Math.abs(xOf(v) - zero);
        art += `<rect x="${start.toFixed(1)}" y="${(y - 3.5).toFixed(1)}" width="${Math.max(length, 0.5).toFixed(1)}" height="7" fill="${colour}"/>`;
      });
    }
    plot.innerHTML = art;
  }

  // ---------- the solvers ----------
  const freeIndices = () => {
    const out = [];
    for (let i = 0; i < POINTS; i++) out.push([i, 0]);
    for (let i = 0; i < POINTS; i++) out.push([i, 1]);
    return out;                       // every number except x t^0 stays fixed by scale
  };
  const paramsOf = () => state.x.slice(1).concat(state.y.slice());
  function speedOf(params) {
    return { x: [state.x[0]].concat(params.slice(0, POINTS - 1)),
             y: params.slice(POINTS - 1, 2 * POINTS - 1) };
  }
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
  const chordOf = (speedX, speedY) => {
    const xx = multiply(speedX, speedX), yy = multiply(speedY, speedY), xy = multiply(speedX, speedY);
    let re = 0, im = 0;
    for (let j = 0; j < xx.length; j++) {
      re += (xx[j] - (yy[j] || 0)) / (j + 1);
      im += 2 * xy[j] / (j + 1);
    }
    return [re, im];
  };
  const ratioOf = (speedX, speedY) => {
    const arc = arcLength(speedX, speedY);
    const c = chordOf(speedX, speedY);
    return arc > 1e-12 ? Math.hypot(c[0], c[1]) / arc : 0;
  };
  function cost(params, mode, targetArc, openness) {
    const speed = speedOf(params);
    if (mode === "openness") return (ratioOf(speed.x, speed.y) - openness) ** 2;
    const c = chordOf(speed.x, speed.y);
    const chordCost = c[0] * c[0] + c[1] * c[1];
    const arcCost = targetArc === undefined ? 0 : (arcLength(speed.x, speed.y) - targetArc) ** 2;
    const scale = Math.max(1e-9, targetArc === undefined ? 1 : targetArc) ** 2;
    return (chordCost + arcCost) / scale;
  }
  function solve(mode, openness) {
    let params = paramsOf();
    const start = speedOf(params);
    const targetArc = mode === "close" ? arcLength(start.x, start.y) : undefined;
    let best = cost(params, mode, targetArc, openness);
    let step = 0.05;
    const h = 1e-5;
    for (let iteration = 0; iteration < 4000; iteration++) {
      const gradient = params.map((p, i) => {
        const trial = params.slice();
        trial[i] += h;
        return (cost(trial, mode, targetArc, openness) - best) / h;
      });
      const norm = Math.hypot(...gradient) || 1;
      let improved = false;
      for (let attempt = 0; attempt < 40; attempt++) {
        const trial = params.map((p, i) => p - step * gradient[i] / norm);
        const v = cost(trial, mode, targetArc, openness);
        if (v < best) { params = trial; best = v; improved = true; step *= 1.2; break; }
        step *= 0.5;
      }
      if (!improved || best < 1e-20) break;
    }
    // Eleven parameters are badly scaled for one common step: polish each one
    // on its own line, coarse to fine, which is what makes the solve land.
    for (let pass = 0; pass < 3; pass++) {
      let reach = 0.5 / Math.pow(4, pass);
      let moved = true;
      while (moved && reach > 1e-6) {
        moved = false;
        for (let i = 0; i < params.length; i++) {
          for (const direction of [1, -1]) {
            const trial = params.slice();
            trial[i] += direction * reach * Math.max(1, Math.abs(params[i]));
            const v = cost(trial, mode, targetArc, openness);
            if (v < best) { params = trial; best = v; moved = true; break; }
          }
        }
        if (!moved) reach /= 2;
      }
    }
    const speed = speedOf(params);
    state.x = [state.x[0]].concat(speed.x.slice(1));
    state.y = speed.y.slice();
    currentName = "curve";
    writeCells();
    draw();
  }

  const opennessOf = () => {
    const raw = Number(document.getElementById("n-open-value").value);
    return Number.isFinite(raw) ? Math.min(1, Math.max(0.02, raw)) : 0.25;
  };
  document.getElementById("n-close").addEventListener("click", () => solve("close"));
  document.getElementById("n-open").addEventListener("click", () => solve("openness", opennessOf()));
  const slider = document.getElementById("n-open-slider"), field = document.getElementById("n-open-value");
  slider.addEventListener("input", () => { field.value = slider.value; });
  field.addEventListener("input", () => {
    const v = Number(field.value);
    if (Number.isFinite(v)) slider.value = String(Math.min(1, Math.max(0.02, v)));
  });
  // the width law's three dials
  const strengthField = document.getElementById("n-char");
  if (strengthField) steppers(strengthField, direction => {
    character.strength = stepInteger(character.strength, direction);
    strengthField.value = String(character.strength);
    draw();
  });
  if (strengthField) strengthField.addEventListener("input", () => {
    const v = Number(strengthField.value);
    if (!Number.isFinite(v)) return;
    character.strength = Math.min(3, Math.max(0, v));
    draw();
  });
  const widthField = document.getElementById("n-d");
  if (widthField) steppers(widthField, direction => {
    width.percent = stepInteger(width.percent, direction);
    widthField.value = String(width.percent);
    draw();
  });
  if (widthField) widthField.addEventListener("input", () => {
    const v = Number(widthField.value);
    if (!Number.isFinite(v)) return;
    width.percent = Math.min(20, Math.max(0, v));
    draw();
  });
  [["n-rails", "rails"], ["n-character", "character"],
   ["n-terminal-start", "startTerminal"], ["n-terminal-end", "endTerminal"]]
    .forEach(([id, key]) => {
      const button = document.getElementById(id);
      if (!button) return;
      button.addEventListener("click", () => {
        view[key] = !view[key];
        if (key === "rails" && view.rails) view.character = false;
        if (key === "character" && view.character) view.rails = false;
        const railsButton = document.getElementById("n-rails");
        const characterButton = document.getElementById("n-character");
        if (railsButton) railsButton.classList.toggle("is-on", view.rails);
        if (characterButton) characterButton.classList.toggle("is-on", view.character);
        button.classList.toggle("is-on", view[key]);
        draw();
      });
    });
  document.getElementById("n-zero-top").addEventListener("click", () => {
    state.x[POINTS - 1] = 0; state.y[POINTS - 1] = 0;
    currentName = "curve"; writeCells(); draw();
  });

  // ---------- saved curves ----------
  const applyWidth = item => {
    if (!item) return;
    if (Number.isFinite(Number(item.character))) {
      character.strength = Math.min(3, Math.max(0, Number(item.character)));
      const field = document.getElementById("n-char");
      if (field) field.value = String(character.strength);
    }
    if (!item.width) return;
    const percent = Number(item.width.percent);
    if (!Number.isFinite(percent)) return;
    width.percent = percent;
    const field = document.getElementById("n-d");
    if (field) field.value = String(percent);
  };

  const SEED = [{ name: "amper", speedX: [2, -5, 6, 1, 0, 0], speedY: [4, -22, 22, -2, 0, 0] }];

  const storageKey = "ph-nth-curves";
  const saved = () => { try { return JSON.parse(localStorage.getItem(storageKey) || "[]"); } catch (e) { return []; } };
  const store = items => localStorage.setItem(storageKey, JSON.stringify(items));
  function renderSaved() {
    const row = document.getElementById("n-saved");
    row.textContent = "";
    SEED.concat(saved()).forEach(item => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = item.name;
      button.title = JSON.stringify(item.speedX) + " / " + JSON.stringify(item.speedY);
      button.addEventListener("click", () => {
        state.x = item.speedX.slice(0, POINTS).concat(new Array(POINTS).fill(0)).slice(0, POINTS);
        state.y = item.speedY.slice(0, POINTS).concat(new Array(POINTS).fill(0)).slice(0, POINTS);
        currentName = item.name;
        applyWidth(item);
        writeCells(); draw();
      });
      row.append(button);
    });
  }
  document.getElementById("n-save").addEventListener("click", () => {
    const nameField = document.getElementById("n-name");
    const name = (nameField.value || "").trim() || `curve ${saved().length + 1}`;
    const m = metrics(state.x, state.y);
    const items = saved().filter(item => item.name !== name);
    items.push({ name, speedX: state.x.map(v => +v), speedY: state.y.map(v => +v),
                 bend: +m.bend.toFixed(3), pitch: m.pitch,
                 inflection: m.inflection === null ? null : +m.inflection.toFixed(3),
                 closest: +m.closest.toFixed(3) });
    store(items);
    nameField.value = "";
    renderSaved();
  });
  const renameButton = document.getElementById("n-rename");
  if (renameButton) renameButton.addEventListener("click", () => {
    const field = document.getElementById("n-name");
    const status = document.getElementById("n-paste-status");
    const name = (field.value || "").trim();
    if (!name) { if (status) status.textContent = "type a name, then press rename"; return; }
    const items = saved();
    const index = items.findIndex(item => item.name === currentName);
    if (index >= 0) { items[index].name = name; store(items); }
    currentName = name;
    field.value = "";
    if (status) status.textContent = index >= 0 ? `renamed to ${name}` : `named ${name} (press save to keep it)`;
    renderSaved();
    draw();
  });

  document.getElementById("n-load").addEventListener("click", () => {
    const status = document.getElementById("n-paste-status");
    const text = document.getElementById("n-paste").value.trim();
    if (!text) { status.textContent = "paste a curve or a {\"curves\": [...]} document"; return; }
    try {
      const data = JSON.parse(text);
      const list = Array.isArray(data) ? data : (data.curves ? data.curves : [data]);
      const items = saved();
      let loaded = 0;
      list.forEach(item => {
        if (!item || !Array.isArray(item.speedX) || !Array.isArray(item.speedY)) return;
        const name = item.name || `pasted ${items.length + 1}`;
        const record = { name, speedX: item.speedX.map(Number), speedY: item.speedY.map(Number),
                         width: item.width && Number.isFinite(Number(item.width.percent))
                                ? { percent: Number(item.width.percent) } : undefined,
                         character: Number.isFinite(Number(item.character)) ? Number(item.character) : undefined };
        const index = items.findIndex(entry => entry.name === name);
        if (index >= 0) items[index] = record; else items.push(record);
        loaded += 1;
        if (loaded === 1) {
          state.x = record.speedX.slice(0, POINTS).concat(new Array(POINTS).fill(0)).slice(0, POINTS);
          state.y = record.speedY.slice(0, POINTS).concat(new Array(POINTS).fill(0)).slice(0, POINTS);
          currentName = name;
          applyWidth(record);
          writeCells(); draw();
        }
      });
      store(items);
      renderSaved();
      status.textContent = loaded ? `${loaded} curve${loaded === 1 ? "" : "s"} loaded`
                                 : "no speedX / speedY in that JSON";
    } catch (error) {
      status.textContent = "not JSON: " + error.message;
    }
  });

  writeCells();
  renderSaved();
  draw();
})();
