// The eleventh power and up: a PH curve whose position degree starts at 11.
//
// r' = w^2 with w of degree k, so 2(k+1) speed numbers (k+1 real, k+1
// imaginary) and a position degree of 2k + 1. The ladder therefore steps by
// two: k = 5, 6, 7, 8, 9 gives position degrees 11, 13, 15, 17, 19, with 12,
// 14, 16, 18 and 20 speed numbers. An even position degree cannot occur:
// p and q of equal top degree both square to a real leading term, so the
// leading position term is always real and of odd degree.
//
// The page sets window.phSpeedDegree before this script runs. The rung buttons
// call window.phNthSetDegree(k) to move up or down without a reload; existing
// curves load into a bigger rung padded with zeros, which leaves the shape
// alone.

(function () {
  const asked = Number(window.phSpeedDegree);
  let speedDegree = Number.isFinite(asked) && asked >= 1 ? Math.round(asked) : 5;
  let speedCount = speedDegree + 1;     // numbers per axis, real or imaginary
  const positionDegree = () => 2 * speedDegree + 1;

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
  const complementGrid = document.getElementById("n-complement-controls");
  // The complementary curve: a second speed pair drawn under the spine. It
  // starts as the spine flipped across the origin, which is the pair that
  // interleaves; its numbers are its own from then on.
  const complement = { x: defaults.x.slice(), y: defaults.y.slice() };

  // Placement is a 3x3 affine matrix, row major, applied to the drawn points:
  // [a b c; d e f; 0 0 1] sends (x, y) to (a x + b y + c, d x + e y + f).
  // Flips, the half turn and the move are all this one object, so the speed
  // numbers stay the curve and the matrix says where the curve sits.
  const identity = () => [1, 0, 0, 0, 1, 0, 0, 0, 1];
  const FLIP_ACROSS = [-1, 0, 0, 0, 1, 0, 0, 0, 1];   // x -> -x
  const UPSIDE_DOWN = [1, 0, 0, 0, -1, 0, 0, 0, 1];   // y -> -y
  state.transform = identity();
  complement.transform = identity();
  const placed = (matrix, points) => points.map(([x, y]) => [
    matrix[0] * x + matrix[1] * y + matrix[2],
    matrix[3] * x + matrix[4] * y + matrix[5],
  ]);
  const compose = (left, right) => {
    const out = new Array(9).fill(0);
    for (let row = 0; row < 3; row++) {
      for (let column = 0; column < 3; column++) {
        out[row * 3 + column] =
          left[row * 3] * right[column] +
          left[row * 3 + 1] * right[3 + column] +
          left[row * 3 + 2] * right[6 + column];
      }
    }
    return out;
  };

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

  // One row of numbers for one axis of one curve. `target` is the curve the row
  // writes to, so the spine and the complementary curve share this code.
  function buildRow(axis, target) {
    const row = document.createElement("div");
    row.className = "spine-row";
    const label = document.createElement("span");
    label.textContent = axis;
    row.append(label);
    for (let k = 0; k < speedCount; k++) {
      const cell = document.createElement("label");
      cell.className = "spine-cell";
      const name = document.createElement("span");
      name.textContent = "t^" + k;
      const number = document.createElement("input");
      number.type = "number"; number.step = "0.1";
      number.value = target[axis][k];
      const fine = document.createElement("input");
      fine.type = "range"; fine.min = "0"; fine.max = "10"; fine.step = "0.1";
      fine.title = "size, sign from the box";
      const scales = document.createElement("span");
      scales.className = "scales";
      [["\u221a2", "root2"], ["\u00d71.1", "euler-step"], ["e", "euler"]].forEach(([label, kind]) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "scale";
        button.textContent = label;
        button.title = kind === "root2" ? "snap to the nearest multiple of sqrt 2"
          : kind === "euler" ? "snap to the nearest multiple of e (2.71828)"
          : "multiply the mantissa by 1.1";
        button.addEventListener("click", () => {
          const current = axis === "x" ? target.x[k] : target.y[k];
          if (kind === "root2") set(Math.round(current / Math.SQRT2) * Math.SQRT2);
          else if (kind === "euler") set(Math.round(current / Math.E) * Math.E);
          else set(current * 1.1);
        });
        scales.append(button);
      });
      [["1", 0], ["10", 1], ["100", 2]].forEach(([label, power]) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "scale";
        button.textContent = label;
        button.title = `mantissa x ${label}`;
        button.addEventListener("click", () => {
          const current = axis === "x" ? target.x[k] : target.y[k];
          set(decode(current).mantissa * Math.pow(10, power));
        });
        scales.append(button);
      });
      const elements = { number, fine };
      cells.push({ axis, k, target, ...elements });
      const set = (v) => {
        if (target === state) currentName = "curve";
        if (axis === "x") target.x[k] = v; else target.y[k] = v;
        syncCell(elements, v);          // the slider is the source: write the box
        draw();
      };
      number.addEventListener("input", () => {
        const text = number.value.trim();
        if (text === "") return;
        const v = Number(text);
        if (!Number.isFinite(v)) return;
        if (target === state) currentName = "curve";
        if (axis === "x") target.x[k] = v; else target.y[k] = v;
        syncCell(elements, v, { write: false });
        draw();
      });
      fine.addEventListener("input", () => {
        const current = axis === "x" ? target.x[k] : target.y[k];
        const sign = current < 0 ? -1 : 1;
        set(sign * +fine.value * Math.pow(10, decode(current).decade));
      });
      // The sign button: the slider carries size only, so the sign lives in the
      // number box. One press flips it, which is the quickest way to try the
      // other half of the family.
      const flip = document.createElement("button");
      flip.type = "button";
      flip.className = "sign";
      flip.textContent = "\u2212";
      flip.title = "flip the sign of this number";
      flip.addEventListener("click", () => {
        const current = axis === "x" ? target.x[k] : target.y[k];
        set(current === 0 ? -1 : -current);
      });
      const pair = document.createElement("div");
      pair.className = "cell-inputs";
      pair.append(number, fine, flip, scales);
      steppers(number, direction => {
        const current = axis === "x" ? target.x[k] : target.y[k];
        set(stepInteger(current, direction));
      });
      cell.append(name, pair);
      row.append(cell);
    }
    return row;
  }
  grid.append(buildRow("x", state), buildRow("y", state));
  if (complementGrid) complementGrid.append(buildRow("x", complement), buildRow("y", complement));
  function writeCells() {
    cells.forEach(cell => syncCell(cell, cell.axis === "x" ? cell.target.x[cell.k] : cell.target.y[cell.k]));
  }

  function sizePair(pair) {
    while (pair.x.length < speedCount) pair.x.push(0);
    while (pair.y.length < speedCount) pair.y.push(0);
    pair.x.length = speedCount;
    pair.y.length = speedCount;
  }

  // A new rung: every number that still has a box keeps its value, the new
  // boxes start at zero, and the controls are rebuilt so the sliders match the
  // new count. Nothing is rescaled, so an old curve draws the same shape.
  function rebuildControls() {
    sizePair(state);
    sizePair(complement);
    cells.length = 0;
    grid.textContent = "";
    grid.append(buildRow("x", state), buildRow("y", state));
    if (complementGrid) {
      complementGrid.textContent = "";
      complementGrid.append(buildRow("x", complement), buildRow("y", complement));
    }
  }

  window.phNthDegree = () => ({ speedDegree, speedCount, degree: positionDegree() });
  window.phNthSetDegree = k => {
    const next = Math.round(Number(k));
    if (!Number.isFinite(next) || next < 1 || next === speedDegree) return;
    speedDegree = next;
    speedCount = speedDegree + 1;
    rebuildControls();
    writeCells();
    draw();
    document.dispatchEvent(new CustomEvent("ph-nth-degree", { detail: window.phNthDegree() }));
  };

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
  const view = { rails: false, character: false, startTerminal: false, endTerminal: false, rotate: false };
  const TURN = -Math.PI / 4;
  const turned = points => view.rotate
    ? points.map(([x, y]) => [x * Math.cos(TURN) - y * Math.sin(TURN),
                              x * Math.sin(TURN) + y * Math.cos(TURN)])
    : points;

  // A character offset: the parallel rail, bowed. The bow is the difference
  // between integrating the speed turned a little at each station
  // (g = w (1 + i eps b(t))) and integrating it untouched, both from the same
  // start. That difference is pinned to zero at both ends, so the rail meets
  // the parallel at +/- d at the start and the end and bows in between. It is
  // the character, not a drift: at character 0 the rail is the parallel rail.
  const character = { plus: 2, minus: 2, profile: "bow" };
  const shear = { delta: 0 };
  // the hook is a rational increment on the t^5 coefficient: (dx, dy).
  // A magnitude and an angle would be irrational and blow the pitch up.
  const hook = { dx: 0, dy: 0 };

  // the bow's profile: one swell, an S, or a taper toward the end
  const bumpAt = t => {
    if (character.profile === "s") return 8 * t * (1 - t) * (1 - 2 * t);
    if (character.profile === "taper") return 6.75 * t * t * (1 - t);
    return 4 * t * (1 - t);
  };

  // the tail hook is a polynomial change of the speed itself: add h e^{i phi}
  // to the t^5 coefficient, so the spine bends without leaving the PH family
  function hookedSpeed() {
    const x = state.x.slice(), y = state.y.slice();
    x[x.length - 1] += hook.dx;
    y[y.length - 1] += hook.dy;
    return { x, y };
  }
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
  function characterRail(sign, speed) {
    const steps = 700;
    const spine = spineSamples(speed, steps);
    const start = spine[0];
    const d = halfWidth();
    const from = [start.x + sign * d * start.nx, start.y + sign * d * start.ny];
    const flat = integrateFrom(from[0], from[1], t => [value(speed.x, t), value(speed.y, t)], steps);
    const eps = 0.08 * (sign > 0 ? character.plus : character.minus);
    const turned = integrateFrom(from[0], from[1], t => {
      const p = value(speed.x, t), q = value(speed.y, t);
      const a = sign * eps * bumpAt(t);
      return [p - a * q, q + a * p];
    }, steps);
    return spine.map((s, i) => {
      const t = i / steps;
      const parallel = [s.x + sign * d * s.nx + shear.delta * t * s.tx,
                        s.y + sign * d * s.ny + shear.delta * t * s.ty];
      const weight = 4 * t * (1 - t);
      return [parallel[0] + weight * (turned[i][0] - flat[i][0]),
              parallel[1] + weight * (turned[i][1] - flat[i][1])];
    });
  }

  function spineSamples(speed, n = 700) {
    const out = [];
    let x = 0, y = 0;
    for (let i = 0; i <= n; i++) {
      const t = i / n;
      const p = value(speed.x, t), q = value(speed.y, t);
      const speed2 = p * p + q * q;
      const tx = speed2 > 1e-12 ? (p * p - q * q) / speed2 : 1;
      const ty = speed2 > 1e-12 ? 2 * p * q / speed2 : 0;
      out.push({ t, x, y, tx, ty, nx: -ty, ny: tx });
      if (i < n) {
        const tm = (i + 0.5) / n;
        const pm = value(speed.x, tm), qm = value(speed.y, tm);
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

  // Where two polylines cross. The bounding box test first, because most
  // segment pairs are far apart; then both orientation tests must change sign.
  function crossingsOf(first, second, tolerance) {
    const hits = [];
    const turn = (ax, ay, bx, by) => ax * by - ay * bx;
    for (let i = 0; i < first.length - 1; i++) {
      const [ax, ay] = first[i], [bx, by] = first[i + 1];
      const lowX = Math.min(ax, bx), highX = Math.max(ax, bx);
      const lowY = Math.min(ay, by), highY = Math.max(ay, by);
      for (let j = 0; j < second.length - 1; j++) {
        const [cx, cy] = second[j], [dx, dy] = second[j + 1];
        if (Math.max(cx, dx) < lowX || Math.min(cx, dx) > highX) continue;
        if (Math.max(cy, dy) < lowY || Math.min(cy, dy) > highY) continue;
        const d1 = turn(bx - ax, by - ay, cx - ax, cy - ay);
        const d2 = turn(bx - ax, by - ay, dx - ax, dy - ay);
        const d3 = turn(dx - cx, dy - cy, ax - cx, ay - cy);
        const d4 = turn(dx - cx, dy - cy, bx - cx, by - cy);
        if (d1 * d2 < 0 && d3 * d4 < 0) {
          const share = d1 / (d1 - d2);
          hits.push([ax + (bx - ax) * share, ay + (by - ay) * share]);
        }
      }
    }
    // two neighbouring segments can both report the same point
    return hits.filter((hit, index) => hits.findIndex(other =>
      Math.abs(other[0] - hit[0]) < tolerance && Math.abs(other[1] - hit[1]) < tolerance) === index);
  }

  // ---------- the drawing ----------
  function draw() {
    const plot = document.getElementById("n-plot");
    const speed = hookedSpeed();
    const spine = spineSamples(speed);
    const complementSpine = spineSamples({ x: complement.x, y: complement.y }).map(s => [s.x, s.y]);
    const spineXs = spine.map(s => s.x), spineYs = spine.map(s => s.y);
    const diagonal = Math.hypot(Math.max(...spineXs) - Math.min(...spineXs),
                                Math.max(...spineYs) - Math.min(...spineYs));
    const measured = metrics(speed.x, speed.y);
    curveSize = Math.max(1e-9, Math.max(Math.hypot(measured.chord[0], measured.chord[1]), 0.25 * diagonal));
    const d = halfWidth();
    const leftRail = spine.map(s => [s.x + d * s.nx, s.y + d * s.ny]);
    const rightRail = spine.map(s => [s.x - d * s.nx, s.y - d * s.ny]);
    const characterLeft = view.character ? characterRail(1, speed) : null;
    const characterRight = view.character ? characterRail(-1, speed) : null;
    const startEnd = view.startTerminal ? terminalArc(spine, true) : null;
    const finishEnd = view.endTerminal ? terminalArc(spine, false) : null;
    const spinePoints = placed(state.transform, spine.map(s => [s.x, s.y]));
    const complementShown = placed(complement.transform, complementSpine);
    const all = spinePoints.slice();
    all.push(...complementShown);
    if (view.rails) all.push(...leftRail, ...rightRail);
    if (characterLeft) all.push(...characterLeft, ...characterRight);
    if (startEnd) all.push(...startEnd.arc, startEnd.tip);
    if (finishEnd) all.push(...finishEnd.arc, finishEnd.tip);
    const shown = turned(all);
    const xs = shown.map(p => p[0]), ys = shown.map(p => p[1]);
    const padX = Math.max(1e-6, (Math.max(...xs) - Math.min(...xs)) * 0.08);
    const padY = Math.max(1e-6, (Math.max(...ys) - Math.min(...ys)) * 0.08);
    const minX = Math.min(...xs) - padX, maxX = Math.max(...xs) + padX;
    const minY = Math.min(...ys) - padY, maxY = Math.max(...ys) + padY;
    const width_ = 720, height = 470, left = 74, right = 40, top = 64, bottom = 76;
    const scale = Math.min((width_ - left - right) / (maxX - minX), (height - top - bottom) / (maxY - minY));
    const ox = left + ((width_ - left - right) - (maxX - minX) * scale) / 2;
    const oy = top + ((height - top - bottom) - (maxY - minY) * scale) / 2;
    const fx = v => ox + (v - minX) * scale, fy = v => oy + (maxY - v) * scale;
    const path = points => "M" + turned(points).map(p => fx(p[0]).toFixed(1) + "," + fy(p[1]).toFixed(1)).join("L");
    let art = `<rect width="${width_}" height="${height}" fill="#fbf7ec"/>` +
      `<text x="${left}" y="26" font-size="15" font-weight="600" fill="#2e2413">The eleventh power: a PH spine${view.rails ? ", a flared full line" : ""}</text>` +
      `<text x="${left}" y="44" font-size="12" fill="#7b6c4e">` +
      (view.rails ? `rails r +/- d n, d constant` : `the spine alone; rails and terminals are below`) +
      `${view.startTerminal || view.endTerminal ? " | terminal: an arc of radius d" : ""}` +
      ` | grey: complementary curve</text>` +
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
    // the complementary curve sits under the spine: 40% grey (#666), so the dark
    // stroke stays the one you read first
    art += `<path d="${path(complementShown)}" fill="none" stroke="#666666" stroke-opacity="0.6" stroke-width="2"/>`;
    art += `<path d="${path(spinePoints)}" fill="none" stroke="#2e2413" stroke-width="2.4"/>`;
    if (startEnd) art += `<path d="${path(startEnd.arc)}" fill="none" stroke="#a23b2a" stroke-width="2.4"/>`;
    if (finishEnd) art += `<path d="${path(finishEnd.arc)}" fill="none" stroke="#a23b2a" stroke-width="2.4"/>`;
    // the meetings of the two curves, counted and marked
    const meets = crossingsOf(spinePoints, complementShown,
                              1e-4 * Math.max(1e-9, maxX - minX));
    meets.forEach(([x, y]) => {
      art += `<circle cx="${fx(x).toFixed(1)}" cy="${fy(y).toFixed(1)}" r="3.6" ` +
             `fill="#fbf7ec" stroke="#a23b2a" stroke-width="1.6"/>`;
    });
    art += `<circle cx="${fx(0).toFixed(1)}" cy="${fy(0).toFixed(1)}" r="4" fill="#1f5fa8"/>`;
    // legend inside the figure, 15px, naming the spine first and wrapping when
    // the entries would run past the right edge
    const legend = [["#2e2413", 2.4, "spine"], ["#666666", 2, "complementary curve"]];
    if (view.rails) legend.push(["#1f5fa8", 1.8, "parallel rail"]);
    if (view.character) legend.push(["#5b7f3a", 2, "character offset"]);
    if (startEnd || finishEnd) legend.push(["#a23b2a", 2.4, "terminal arc, radius d"]);
    if (meets.length) legend.push(["#a23b2a", 1.6, "crossing"]);
    let legendX = left, legendY = height - 44;
    legend.forEach(([colour, widthStroke, text]) => {
      const entry = 34 + text.length * 8.2 + 26;
      if (legendX > left && legendX + entry > width_ - right) {
        legendX = left;
        legendY += 20;
      }
      art += `<line x1="${legendX}" y1="${legendY}" x2="${legendX + 26}" y2="${legendY}" ` +
        `stroke="${colour}" stroke-width="${widthStroke}"/>` +
        `<text x="${legendX + 34}" y="${legendY + 5}" font-size="15" fill="#2e2413">${text}</text>`;
      legendX += entry;
    });
    plot.innerHTML = art;

    const m = metrics(speed.x, speed.y);
    const openness = m.arc > 1e-12 ? Math.hypot(m.chord[0], m.chord[1]) / m.arc : 0;
    const curve = curveOf(speed);
    const degreeOf = terms => { let d = 0; terms.forEach((c, k) => { if (Math.abs(c) > 1e-9) d = k; }); return d; };
    const plain = metrics(state.x, state.y);
    const hookNote = (hook.dx || hook.dy)
      ? ` | grid without the hook 1/${plain.pitch.toLocaleString()}` : "";
    document.getElementById("n-readout").textContent =
      `bend ${m.bend.toFixed(3)} | grid 1/${m.pitch.toLocaleString()}${hookNote} | ` +
      `inflections ${m.inflections ? m.inflections.length : (m.inflection === null ? 0 : 1)}` +
      ` (max ${2 * speedDegree - 1}) | ` +
      `first ${m.inflection === null ? " - " : m.inflection.toFixed(3)} | ` +
      `closest ${m.closest.toFixed(3)} | open ${openness.toFixed(3)} | ` +
      `crosses ${meets.length}`;
    const crossingLabel = document.getElementById("n-crossings");
    if (crossingLabel) {
      crossingLabel.textContent = `${meets.length} crossing${meets.length === 1 ? "" : "s"}`;
    }
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
      box.value = JSON.stringify(pairRecord(currentName), null, 2);
    }
    drawBars();
  }

  const multiply = (left, right) => {
    const product = new Array(left.length + right.length - 1).fill(0);
    left.forEach((l, i) => right.forEach((r, j) => { product[i + j] += l * r; }));
    return product;
  };
  function curveOf(speed = state) {
    const xx = multiply(speed.x, speed.x), yy = multiply(speed.y, speed.y), xy = multiply(speed.x, speed.y);
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
    for (let m = 0; m <= 2 * speedDegree; m++) {
      let re = 0, im = 0;
      for (let j = 0; j <= speedDegree; j++) {
        const k = m - j;
        if (k < 0 || k > speedDegree) continue;
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
    for (let i = 0; i < speedCount; i++) out.push([i, 0]);
    for (let i = 0; i < speedCount; i++) out.push([i, 1]);
    return out;                       // every number except x t^0 stays fixed by scale
  };
  const paramsOf = () => state.x.slice(1).concat(state.y.slice());
  function speedOf(params) {
    return { x: [state.x[0]].concat(params.slice(0, speedCount - 1)),
             y: params.slice(speedCount - 1, 2 * speedCount - 1) };
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
  // the modifiers' dials: two character strengths, the bow profile, the end
  // shear and the tail hook
  const wireNumber = (id, apply, low, high) => {
    const field = document.getElementById(id);
    if (!field) return;
    field.addEventListener("input", () => {
      const v = Number(field.value);
      if (!Number.isFinite(v)) return;
      apply(Math.min(high, Math.max(low, v)));
      draw();
    });
    steppers(field, direction => {
      const v = stepInteger(Number(field.value) || 0, direction);
      field.value = String(v);
      apply(Math.min(high, Math.max(low, v)));
      draw();
    });
  };
  wireNumber("n-char-l", v => { character.plus = v; }, 0, 3);
  wireNumber("n-char-r", v => { character.minus = v; }, 0, 3);
  wireNumber("n-shear", v => { shear.delta = v; }, -10, 10);
  wireNumber("n-hook", v => { hook.dx = v; }, -10, 10);
  wireNumber("n-hook-y", v => { hook.dy = v; }, -10, 10);
  const profileField = document.getElementById("n-prof");
  if (profileField) profileField.addEventListener("change", () => {
    character.profile = profileField.value;
    draw();
  });
  // the coarsest grid: scale the speeds by an integer until the pitch is as
  // small as it can be while the numbers stay readable. Scaling cannot change
  // the bend or the inflection, only the size and the grid.
  const gridButton = document.getElementById("n-grid");
  if (gridButton) gridButton.addEventListener("click", () => {
    const status = document.getElementById("n-paste-status");
    const cap = 6000;   // keeps the numbers four digits or less
    let best = null;
    const base = hookedSpeed();          // the hook is part of the t^5 coefficient
    for (let k = 1; k <= 500; k++) {
      const tx = base.x.map(v => v * k), ty = base.y.map(v => v * k);
      if (Math.max(...tx.map(Math.abs), ...ty.map(Math.abs)) > cap) break;
      const m = metrics(tx, ty);
      const key = [m.pitch, Math.max(...tx.map(Math.abs), ...ty.map(Math.abs))];
      if (!best || key[0] < best.key[0] || (key[0] === best.key[0] && key[1] < best.key[1])) {
        best = { k, key, pitch: m.pitch };
      }
    }
    if (!best) { if (status) status.textContent = "no scale fits under the cap"; return; }
    const before = metrics(base.x, base.y).pitch;
    if (best.k > 1) {
      state.x = state.x.map(v => v * best.k);
      state.y = state.y.map(v => v * best.k);
      hook.dx *= best.k; hook.dy *= best.k;
      const hx = document.getElementById("n-hook"), hy = document.getElementById("n-hook-y");
      if (hx) hx.value = String(+hook.dx.toFixed(6));
      if (hy) hy.value = String(+hook.dy.toFixed(6));
      currentName = "curve";
      writeCells();
      draw();
    }
    if (status) {
      status.textContent = `grid 1/${before.toLocaleString()} -> 1/${best.pitch.toLocaleString()} at x${best.k}` +
        `, largest speed ${best.key[1].toLocaleString()}` +
        (best.k === 1 ? " (already the coarsest)" : "");
    }
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
  [["n-rotate", "rotate"], ["n-rails", "rails"], ["n-character", "character"],
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
    state.x[speedCount - 1] = 0; state.y[speedCount - 1] = 0;
    currentName = "curve"; writeCells(); draw();
  });

  // ---------- saved curves ----------
  const applyWidth = item => {
    if (!item) return;
    if (item.character && typeof item.character === "object") {
      character.plus = Number.isFinite(Number(item.character.plus)) ? Number(item.character.plus) : character.plus;
      character.minus = Number.isFinite(Number(item.character.minus)) ? Number(item.character.minus) : character.minus;
      if (["bow", "s", "taper"].includes(item.character.profile)) character.profile = item.character.profile;
    } else if (Number.isFinite(Number(item.character))) {
      character.plus = character.minus = Math.min(3, Math.max(0, Number(item.character)));
    }
    if (Number.isFinite(Number(item.shear))) shear.delta = Number(item.shear);
    if (item.hook) {
      if (Number.isFinite(Number(item.hook.dx)) || Number.isFinite(Number(item.hook.dy))) {
        hook.dx = Number(item.hook.dx) || 0;
        hook.dy = Number(item.hook.dy) || 0;
      } else if (Number.isFinite(Number(item.hook.magnitude))) {
        // older curves stored a polar hook; convert it once
        const m = Number(item.hook.magnitude), a = (Number(item.hook.angle) || 0) * Math.PI / 180;
        hook.dx = m * Math.cos(a);
        hook.dy = m * Math.sin(a);
      }
    }
    const setField = (id, v) => { const f = document.getElementById(id); if (f) f.value = String(v); };
    setField("n-char-l", character.plus);
    setField("n-char-r", character.minus);
    setField("n-shear", shear.delta);
    setField("n-hook", hook.dx);
    setField("n-hook-y", hook.dy);
    const profile = document.getElementById("n-prof");
    if (profile) profile.value = character.profile;
    if (!item.width) return;
    const percent = Number(item.width.percent);
    if (!Number.isFinite(percent)) return;
    width.percent = percent;
    const field = document.getElementById("n-d");
    if (field) field.value = String(percent);
  };

  // A loaded curve brings its flip with it: the two rows swapped draws the same
  // curve across the origin, so the pair interleaves instead of sitting on top
  // of itself.
  function flipComplement() {
    complement.x = state.x.slice();
    complement.y = state.y.slice();
    complement.transform = compose(FLIP_ACROSS, state.transform);
    writeMoves();
  }

  // The move boxes write straight into the matrix's translation column.
  const moveFields = [];
  function writeMoves() {
    moveFields.forEach(({ field, target, index }) => {
      field.value = String(+target.transform[index].toFixed(4));
    });
  }
  [["n-move-x", state, 2], ["n-move-y", state, 5],
   ["n-comp-move-x", complement, 2], ["n-comp-move-y", complement, 5]]
    .forEach(([id, target, index]) => {
      const field = document.getElementById(id);
      if (!field) return;
      moveFields.push({ field, target, index });
      field.addEventListener("input", () => {
        const v = Number(field.value);
        if (!Number.isFinite(v)) return;
        target.transform[index] = v;
        draw();
      });
    });

  // p(1 - t), so the same curve is drawn from its other end
  function reverseRow(row) {
    const choose = (n, k) => {
      let value = 1;
      for (let i = 1; i <= k; i++) value = value * (n - k + i) / i;
      return value;
    };
    const out = row.map(() => 0);
    row.forEach((coefficient, k) => {
      for (let j = 0; j <= k; j++) out[j] += coefficient * choose(k, j) * Math.pow(-1, k - j);
    });
    return out;
  }

  const complementActions = {
    "n-comp-flip": () => {
      complement.transform = compose(FLIP_ACROSS, complement.transform);
    },
    "n-comp-upside": () => {
      complement.transform = compose(UPSIDE_DOWN, complement.transform);
    },
    "n-comp-reverse": () => {
      complement.x = reverseRow(complement.x);
      complement.y = reverseRow(complement.y);
    },
    "n-comp-reset": flipComplement,
  };
  Object.entries(complementActions).forEach(([id, action]) => {
    const button = document.getElementById(id);
    if (!button) return;
    button.addEventListener("click", () => { action(); writeCells(); writeMoves(); draw(); });
  });

  const SEED = [
    { name: "amper", speedX: [2, -5, 6, 1, 0, 0], speedY: [4, -22, 22, -2, 0, 0] },
    { name: "euler-hook",
      speedX: [2.2, -4.4, 6.6, 1.1, 1.1, -1.1],
      speedY: [4.4, -22, 22, -2.2, 1.1, -1.1],
      width: { percent: 1 },
      character: { plus: 2, minus: 1, profile: "taper" },
      shear: 0,
      hook: { dx: 2.934, dy: -0.624 } },
    { name: "swan",
      speedX: [5, -5, 5, 5, 5, -5],
      speedY: [5, -50, 50, -5, 5, -5],
      width: { percent: 1 },
      character: { plus: 2, minus: 1, profile: "taper" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    { name: "swan-2",
      speedX: [5, -5, 5, 5, 5, -5],
      speedY: [5, -50, 50, -5, 5, -5],
      width: { percent: 1 },
      character: { plus: 2, minus: 1, profile: "taper" },
      shear: 0,
      hook: { dx: -2.988584, dy: 0.261467 } },
    { name: "gosling",
      speedX: [1, -1, 1, 1, 1, 1],
      speedY: [1, -10, 10, -1, 1, 1],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: -1 } },
    { name: "double-tap",
      speedX: [2, -6, 2, 2, 0, 4],
      speedY: [4, -24, 24, -2, 0, 0],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    { name: "curlicue",
      speedX: [10, 20, -660, 1930, -2090, 785],
      speedY: [-5, 200, -875, 1445, -1030, 275],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    { name: "grass",
      speedX: [7.5, -2.5, 7.5, 2.5, 7.5, -2.5],
      speedY: [7.5, -25, 75, -2.5, 7.5, -2.5],
      width: { percent: 1 },
      character: { plus: 2, minus: 1, profile: "taper" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    // The letter strokes. The x row stays positive, so the curve never turns
    // back in x; the y row is the one that changes sign, and each root of the y
    // row inside (0,1) is one arch. u and v cross once, m and w cross twice,
    // and m is w with the y row negated. A higher degree does not make a
    // letter: it adds a wiggle. These are degree 3 and 5 on purpose.
    { name: "u-bowl",
      speedX: [1, 0, 0, 0, 0, 0],
      speedY: [-1, 2, 0, 0, 0, 0],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    { name: "v-sharp",
      speedX: [1, 0, 0, 0, 0, 0],
      speedY: [-1, 6, -12, 8, 0, 0],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    { name: "m-arch",
      speedX: [1, 0, 0, 0, 0, 0],
      speedY: [3, -16, 16, 0, 0, 0],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    { name: "gumdrop",
      speedX: [2, 1, -1, 1, -1, 1, -1, 1, -1, 0],
      speedY: [-10, 137, -675, 1530, -1620, 648, 0, 0, 0, 0],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    { name: "w-arch",
      speedX: [1, 0, 0, 0, 0, 0],
      speedY: [-3, 16, -16, 0, 0, 0],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
  ];

  // The saved shape. One category, one name, two curves; each curve carries its
  // own speed rows and its own 3x3 placement matrix, row major:
  //   [a b c; d e f; 0 0 1] sends (x, y) to (a x + b y + c, d x + e y + f)
  // so a flip, a turn and a move are one object and the numbers stay the curve.
  // Old flat records ({name, speedX, speedY}) still load: pairOf fills them in.
  const category = () => {
    const field = document.getElementById("n-category");
    const typed = field ? field.value.trim() : "";
    return typed || "DK";
  };
  function pairRecord(name) {
    const m = metrics(state.x, state.y);
    return {
      format: "curve-lab.double-knot/1",
      category: category(),
      name,
      primary: {
        speedX: state.x.map(v => +v),
        speedY: state.y.map(v => +v),
        transform: state.transform.map(v => +v),
      },
      complementary: {
        speedX: complement.x.map(v => +v),
        speedY: complement.y.map(v => +v),
        transform: complement.transform.map(v => +v),
      },
      bend: +m.bend.toFixed(3),
      pitch: m.pitch,
      inflection: m.inflection === null ? null : +m.inflection.toFixed(3),
      inflections: (m.inflections || (m.inflection === null ? [] : [m.inflection]))
        .map(value => +value.toFixed(4)),
      inflectionMax: 2 * speedDegree - 1,
      closest: +m.closest.toFixed(3),
      width: { percent: width.percent },
      character: { plus: character.plus, minus: character.minus, profile: character.profile },
      shear: shear.delta,
      hook: { dx: hook.dx, dy: hook.dy },
    };
  }
  function pairOf(item) {
    if (item && item.primary) return item;
    if (item && Array.isArray(item.speedX) && Array.isArray(item.speedY)) {
      return { ...item, format: "curve-lab.double-knot/1",
               category: item.category || "DK",
               primary: { speedX: item.speedX, speedY: item.speedY, transform: identity() },
               complementary: null };
    }
    return null;
  }
  function loadPair(item) {
    const pair = pairOf(item);
    if (!pair) return;
    const fit = row => row.slice(0, speedCount).concat(new Array(speedCount).fill(0)).slice(0, speedCount);
    state.x = fit(pair.primary.speedX);
    state.y = fit(pair.primary.speedY);
    state.transform = (pair.primary.transform || identity()).slice();
    if (pair.complementary && Array.isArray(pair.complementary.speedX)) {
      complement.x = fit(pair.complementary.speedX);
      complement.y = fit(pair.complementary.speedY);
      complement.transform = (pair.complementary.transform || identity()).slice();
    } else {
      flipComplement();
    }
    currentName = pair.name || "curve";
    applyWidth(pair);
    writeCells();
    writeMoves();
    draw();
  }

  const takenNames = () => new Set(SEED.concat(saved()).map(item => item.name));
  const uniqueName = (base, taken) => {
    let name = base, n = 2;
    const used = taken || takenNames();
    while (used.has(name)) name = `${base} ${n++}`;
    return name;
  };
  // a name that already exists is never overwritten silently: OK renames the
  // newcomer, Cancel replaces the old one
  function resolveName(base, action) {
    const taken = takenNames();
    if (!taken.has(base)) return base;
    const fresh = uniqueName(base, taken);
    const rename = window.confirm(
      `A curve called "${base}" already exists.\n\n` +
      `OK: ${action} as "${fresh}"\n` +
      `Cancel: replace "${base}"`);
    return rename ? fresh : base;
  }

  window.phNthSeeds = SEED;

  const storageKey = "ph-nth-curves";
  const saved = () => { try { return JSON.parse(localStorage.getItem(storageKey) || "[]"); } catch (e) { return []; } };
  const store = items => localStorage.setItem(storageKey, JSON.stringify(items));
  function renderSaved() {
    const row = document.getElementById("n-saved");
    row.textContent = "";
    const byName = {};
    SEED.concat(saved()).forEach(item => { byName[item.name] = item; });
    Object.values(byName).forEach(item => {
      const group = document.createElement("span");
      group.className = "saved-item";
      const button = document.createElement("button");
      button.type = "button";
      const pair = pairOf(item);
      const primary = pair ? pair.primary : item;
      button.textContent = (pair && pair.category ? pair.category + " · " : "") + item.name;
      button.title = JSON.stringify(primary.speedX) + " / " + JSON.stringify(primary.speedY);
      button.addEventListener("click", () => loadPair(item));
      group.append(button);
      if (!SEED.some(seed => seed.name === item.name)) {
        const remove = document.createElement("button");
        remove.type = "button";
        remove.className = "saved-remove";
        remove.textContent = "\u00d7";
        remove.title = `delete "${item.name}"`;
        remove.addEventListener("click", () => {
          if (!window.confirm(`Delete "${item.name}" from the saved curves?`)) return;
          store(saved().filter(entry => entry.name !== item.name));
          renderSaved();
          window.dispatchEvent(new CustomEvent("ph-nth-saved"));
          const status = document.getElementById("n-paste-status");
          if (status) status.textContent = `deleted "${item.name}"`;
        });
        group.append(remove);
      }
      row.append(group);
    });
  }
  document.getElementById("n-save").addEventListener("click", () => {
    const nameField = document.getElementById("n-name");
    const status = document.getElementById("n-paste-status");
    const typed = (nameField.value || "").trim() || `curve ${saved().length + 1}`;
    const name = resolveName(typed, "save this curve");
    const speed = hookedSpeed();
    const m = metrics(speed.x, speed.y);
    const items = saved().filter(item => item.name !== name);
    items.push(pairRecord(name));
    store(items);
    currentName = name;
    nameField.value = "";
    renderSaved();
    window.dispatchEvent(new CustomEvent("ph-nth-saved"));
    if (status) status.textContent = `saved as "${name}"`;
  });
  const renameButton = document.getElementById("n-rename");
  if (renameButton) renameButton.addEventListener("click", () => {
    const field = document.getElementById("n-name");
    const status = document.getElementById("n-paste-status");
    let name = (field.value || "").trim();
    if (!name) { if (status) status.textContent = "type a name, then press rename"; return; }
    if (name !== currentName && takenNames().has(name)) {
      const fresh = uniqueName(name);
      if (!window.confirm(
        `A curve called "${name}" already exists.\n\n` +
        `OK: rename this one to "${fresh}"\n` +
        `Cancel: keep the name "${currentName}"`)) {
        if (status) status.textContent = `kept the name ${currentName}`;
        return;
      }
      name = fresh;
    }
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
      const usedHere = takenNames();
      let loaded = 0;
      list.forEach(item => {
        const pair = pairOf(item);
        if (!pair) return;
        const base = pair.name || `pasted ${items.length + 1}`;
        let name = base;
        if (usedHere.has(base)) {
          const fresh = uniqueName(base, usedHere);
          const rename = window.confirm(
            `A curve called "${base}" already exists.\n\n` +
            `OK: load as "${fresh}"\n` +
            `Cancel: replace "${base}"`);
          name = rename ? fresh : base;
        }
        usedHere.add(name);
        const record = { ...pair, name };
        const index = items.findIndex(entry => entry.name === name);
        if (index >= 0) items[index] = record; else items.push(record);
        loaded += 1;
        if (loaded === 1) loadPair(record);
      });
      store(items);
      renderSaved();
      status.textContent = loaded ? `${loaded} curve${loaded === 1 ? "" : "s"} loaded`
                                 : "no speedX / speedY in that JSON";
    } catch (error) {
      status.textContent = "not JSON: " + error.message;
    }
  });

  // the gallery opens a curve into this sandbox
  window.phNthLoad = item => {
    loadPair(item);
    const controls = document.getElementById("n-controls");
    if (controls) controls.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  flipComplement();        // the pair starts flipped, so it crosses
  writeCells();
  renderSaved();
  draw();
})();

// The gallery: spine only, one small figure per curve, two columns.
(function () {
  const host = document.getElementById("n-gallery");
  if (!host || !Array.isArray(window.phNthGallery)) return;

  const storageKey = "ph-nth-curves";
  const localSaved = () => {
    try { return JSON.parse(localStorage.getItem(storageKey) || "[]"); } catch (e) { return []; }
  };
  function currentList() {
    const locals = {};
    localSaved().forEach(item => { locals[item.name] = item; });
    const out = window.phNthGallery.map(entry => {
      const local = locals[entry.name];
      if (!local) return entry;
      return { ...entry, speedX: local.speedX, speedY: local.speedY,
               from: "local fix", local: true };
    });
    const seeds = (window.phNthSeeds || [])
      .filter(seed => !out.some(entry => entry.name === seed.name))
      .map(seed => {
        const measured = window.recipeMetrics ? window.recipeMetrics(seed.speedX, seed.speedY) : null;
        return { ...seed, bend: measured ? +measured.bend.toFixed(3) : "-",
                 pitch: measured ? measured.pitch : "-", from: "seed" };
      });
    out.unshift(...seeds);
    const known = new Set(out.map(entry => entry.name));
    Object.values(locals).forEach(item => {
      if (known.has(item.name)) return;
      const measured = window.recipeMetrics ? window.recipeMetrics(item.speedX, item.speedY) : null;
      out.push({ name: item.name, speedX: item.speedX, speedY: item.speedY,
                 bend: measured ? +measured.bend.toFixed(3) : "-",
                 pitch: measured ? measured.pitch : "-",
                 from: "local", local: true });
    });
    return out;
  }
  let list = currentList();
  const value = window.polynomialValue;

  function samplesOf(entry, steps = 220) {
    let x = 0, y = 0;
    const out = [[0, 0, 0, 0]];
    for (let i = 0; i < steps; i++) {
      const t = (i + 0.5) / steps;
      const a = value(entry.speedX, t), b = value(entry.speedY, t);
      const s2 = a * a + b * b || 1;
      const tx = (a * a - b * b) / s2, ty = 2 * a * b / s2;
      x += (a * a - b * b) / steps;
      y += 2 * a * b / steps;
      out.push([x, y, -ty, tx]);        // point and left normal
    }
    return out;
  }

  function spineOf(entry, steps = 260) {
    let x = 0, y = 0;
    const points = [[0, 0]];
    for (let i = 0; i < steps; i++) {
      const t = (i + 0.5) / steps;
      const a = value(entry.speedX, t), b = value(entry.speedY, t);
      x += (a * a - b * b) / steps;
      y += 2 * a * b / steps;
      points.push([x, y]);
    }
    return points;
  }


  // the character offsets of an entry, in data space: parallel rail plus the
  // bow that the character dials make. Returns null when the entry has none.
  function characterRailsOf(entry, steps = 220) {
    const ch = entry.character;
    if (!ch) return null;
    const percent = entry.width ? Number(entry.width.percent) : 1.5;
    const bump = t => ch.profile === "s" ? 8 * t * (1 - t) * (1 - 2 * t)
      : ch.profile === "taper" ? 6.75 * t * t * (1 - t) : 4 * t * (1 - t);
    const samples = samplesOf(entry, steps);
    const xs = samples.map(q => q[0]), ys = samples.map(q => q[1]);
    const size = Math.max(1e-9, Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys));
    const d = percent / 100 * size;
    const side = sign => {
      const strength = Number(sign > 0 ? ch.plus : ch.minus) || 0;
      if (!strength) return null;
      const eps = 0.08 * strength;
      let fx = 0, fy = 0, gx = 0, gy = 0;
      const out = [];
      for (let i = 0; i < steps; i++) {
        const t = (i + 0.5) / steps;
        const a = value(entry.speedX, t), b = value(entry.speedY, t);
        fx += (a * a - b * b) / steps; fy += 2 * a * b / steps;
        const ang = sign * eps * bump(t);
        const gr = a - ang * b, gi = b + ang * a;
        gx += (gr * gr - gi * gi) / steps; gy += 2 * gr * gi / steps;
        const q = samples[i + 1], t01 = (i + 1) / steps, weight = 4 * t01 * (1 - t01);
        out.push([q[0] + sign * d * q[2] + weight * (gx - fx),
                  q[1] + sign * d * q[3] + weight * (gy - fy)]);
      }
      return out;
    };
    return [side(1), side(-1)].filter(Boolean);
  }

  function miniSvg(speedX, speedY, label, kind = null, entry = null, rawPoints = null) {
    const points = rawPoints || spineOf({ speedX, speedY }, 220);
    const xs = points.map(p => p[0]), ys = points.map(p => p[1]);
    const pad = 0.06 * Math.max(1e-9, Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys));
    const minX = Math.min(...xs) - pad, maxX = Math.max(...xs) + pad;
    const minY = Math.min(...ys) - pad, maxY = Math.max(...ys) + pad;
    const width = 200, height = 150, inset = 8;
    const scale = Math.min((width - 2 * inset) / (maxX - minX), (height - 2 * inset) / (maxY - minY));
    const ox = inset + ((width - 2 * inset) - (maxX - minX) * scale) / 2;
    const oy = inset + ((height - 2 * inset) - (maxY - minY) * scale) / 2;
    const d = "M" + points.map(p => (ox + (p[0] - minX) * scale).toFixed(1) + "," +
                               (oy + (maxY - p[1]) * scale).toFixed(1)).join("L");
    let rails = "";
    const character = entry ? characterRailsOf({ ...entry, speedX, speedY }) : null;
    if (character) {
      rails = character.map(points => `<path d="M` + points.map(q =>
        (ox + (q[0] - minX) * scale).toFixed(1) + "," +
        (oy + (maxY - q[1]) * scale).toFixed(1)).join("L") +
        `" fill="none" stroke="#5b7f3a" stroke-width="1"/>`).join("");
    }
    return `<figure class="pair-cell" data-speed="${kind || "full"}">
      <figcaption>${label}</figcaption>
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${label}">
        <rect width="${width}" height="${height}" fill="#fbf7ec"/>
        ${rails}
        <path d="${d}" fill="none" stroke="#2e2413" stroke-width="1.6"/>
      </svg>
      ${kind === "simple" ? '<button type="button" class="gallery-transfer">transfer to part 1</button>' : ""}
      ${kind ? '<button type="button" class="gallery-load-this">load this one</button>' : ""}
    </figure>`;
  }

  function figureFor(entry) {
    const points = spineOf(entry);
    const xs = points.map(p => p[0]), ys = points.map(p => p[1]);
    const pad = 0.08 * Math.max(1e-9, Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys));
    const minX = Math.min(...xs) - pad, maxX = Math.max(...xs) + pad;
    const minY = Math.min(...ys) - pad, maxY = Math.max(...ys) + pad;
    const width = 200, height = 150, inset = 8;
    const scale = Math.min((width - 2 * inset) / (maxX - minX), (height - 2 * inset) / (maxY - minY));
    const ox = inset + ((width - 2 * inset) - (maxX - minX) * scale) / 2;
    const oy = inset + ((height - 2 * inset) - (maxY - minY) * scale) / 2;
    const d = "M" + points.map(p => (ox + (p[0] - minX) * scale).toFixed(1) + "," +
                               (oy + (maxY - p[1]) * scale).toFixed(1)).join("L");
    const json = JSON.stringify({ name: entry.name, speedX: entry.speedX, speedY: entry.speedY,
                                  bend: entry.bend, pitch: entry.pitch, from: entry.from }, null, 1);
    return `<figure data-name="${entry.name}">
      <button type="button" class="gallery-open" aria-expanded="false">
        <span class="gallery-name">${entry.name}</span>
        <span class="gallery-tags"><span class="tag">${String(entry.from || "").startsWith("fitted") ? "fitted" : "exact"}</span>
        <span class="gallery-metrics">bend ${entry.bend} | grid 1/${Number(entry.pitch).toLocaleString()}</span></span>
      </button>
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${entry.name}, spine${entry.width ? " and rails" : ""}">
        <rect width="${width}" height="${height}" fill="#fbf7ec"/>
        ${(() => {
          const rails = characterRailsOf(entry);
          if (!rails) return "";
          return rails.map(points => `<path d="M` + points.map(q =>
            (ox + (q[0] - minX) * scale).toFixed(1) + "," +
            (oy + (maxY - q[1]) * scale).toFixed(1)).join("L") +
            `" fill="none" stroke="#5b7f3a" stroke-width="1"/>`).join("");
        })()}
        <path d="${d}" fill="none" stroke="#2e2413" stroke-width="1.6"/>
      </svg>
      <div class="more" hidden>
        <div class="pair-row">
          ${entry.original && entry.original.length
              ? miniSvg(null, null, "original", null, null, entry.original)
              : ""}
          ${miniSvg(entry.speedX, entry.speedY, "fitted, degree 11", "full", entry)}
        </div>
        <p class="small mono">x ${entry.speedX.join(", ")}<br>y ${entry.speedY.join(", ")}</p>
        <p class="small mono">bend ${entry.bend} | pitch ${Number(entry.pitch).toLocaleString()} | from ${entry.from}</p>
        <textarea rows="7" readonly>${json}</textarea>
        <div class="more-row">
          <button type="button" class="gallery-load">load into the sandbox</button>
          <button type="button" class="gallery-copy">copy JSON</button>
          <button type="button" class="gallery-close">close</button>
          <span class="small mono gallery-status"></span>
        </div>
      </div>
    </figure>`;
  }

  const render = () => {
    list = currentList();
    host.innerHTML = list.map(figureFor).join("");
  };
  render();
  window.addEventListener("ph-nth-saved", render);

  const closeAll = except => {
    host.querySelectorAll("figure.open").forEach(figure => {
      if (figure === except) return;
      figure.classList.remove("open");
      figure.querySelector(".more").hidden = true;
      figure.querySelector(".gallery-open").setAttribute("aria-expanded", "false");
    });
  };
  host.addEventListener("click", event => {
    const figure = event.target.closest("figure[data-name]");   // the cell, not the pair figure inside it
    if (!figure) return;
    const entry = currentList().find(item => item.name === figure.dataset.name);
    const open = figure.querySelector(".gallery-open");
    const more = figure.querySelector(".more");

    if (event.target.closest(".gallery-open")) {
      const showing = more.hidden;
      closeAll(figure);
      more.hidden = !showing;
      figure.classList.toggle("open", showing);
      open.setAttribute("aria-expanded", String(showing));
      return;
    }
    if (!event.target.closest("button") && !event.target.closest(".more")) {
      const more = figure.querySelector(".more");
      const showing = more.hidden;
      closeAll(figure);
      more.hidden = !showing;
      figure.classList.toggle("open", showing);
      open.setAttribute("aria-expanded", String(showing));
      return;
    }
    if (event.target.closest(".gallery-close")) {
      more.hidden = true;
      figure.classList.remove("open");
      open.setAttribute("aria-expanded", "false");
      return;
    }
    if (event.target.closest(".gallery-load") && entry && window.phNthLoad) {
      window.phNthLoad(entry);
      return;
    }
    if (event.target.closest(".gallery-transfer") && entry && entry.simple) {
      const suggested = `${entry.name} (3 figures)`;
      const name = (window.prompt("Name it in part 1:", suggested) || "").trim();
      if (!name) return;
      const items = localSaved().filter(item => item.name !== name);
      items.push({ name, speedX: entry.simple.speedX, speedY: entry.simple.speedY, from: "transferred" });
      localStorage.setItem(storageKey, JSON.stringify(items));
      window.dispatchEvent(new CustomEvent("ph-nth-saved"));
      return;
    }
    if (event.target.closest(".gallery-load-this") && entry && window.phNthLoad) {
      const cell = event.target.closest(".pair-cell");
      const isSimple = cell && cell.dataset.speed === "simple";
      window.phNthLoad(isSimple
        ? { ...entry, speedX: entry.simple.speedX, speedY: entry.simple.speedY, name: `${entry.name} (3 figures)` }
        : entry);
      return;
    }
    if (event.target.closest(".gallery-copy") && entry) {
      const status = figure.querySelector(".gallery-status");
      const text = figure.querySelector("textarea").value;
      const done = () => { if (status) status.textContent = "copied"; };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, () => {
          figure.querySelector("textarea").select();
          if (status) status.textContent = "select and copy";
        });
      } else {
        figure.querySelector("textarea").select();
        if (status) status.textContent = "select and copy";
      }
    }
  });
})();
