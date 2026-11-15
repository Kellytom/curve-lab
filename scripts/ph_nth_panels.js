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
  // The turn is a rule, not a matrix: it is applied about the spine's own
  // centre, which moves whenever the numbers change, so a stored matrix would
  // turn about the wrong point.
  complement.turn = 0;

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
    if (!sliders) return;
    const { mantissa, decade } = decode(number);
    cell.fine.value = Math.abs(mantissa);
    // the decade slider: the size of the number, one step per power of ten
    if (cell.decade) cell.decade.value = String(decade);
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

  // One cell of numbers: a box, a slider, the sign flip and the scale buttons.
  // The power and the axis are written by the grid that holds the cell.
  function makeCell(axis, target, k) {
    const cell = document.createElement("label");
    cell.className = "spine-cell";
    const number = document.createElement("input");
    number.type = "number"; number.step = "0.1";
    number.value = target[axis][k] ?? 0;
    const fine = document.createElement("input");
    fine.type = "range"; fine.min = "0"; fine.max = "10"; fine.step = "0.1";
    fine.title = "size, sign from the box";
    // the second slider: the decade. Two sliders per number, so 24 at degree 11,
    // because the mantissa slider alone cannot reach 1000 or 0.01 quickly.
    const decade = document.createElement("input");
    decade.type = "range"; decade.min = "-2"; decade.max = "6"; decade.step = "1";
    decade.className = "decade";
    decade.title = "decade: the number is the mantissa x 10 to this power";
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
    const elements = { number, fine, decade };
    cells.push({ axis, k, target, ...elements });
    const set = (v) => {
      if (target === state) setName("curve (edited)");
      if (axis === "x") target.x[k] = v; else target.y[k] = v;
      syncCell(elements, v);          // the slider is the source: write the box
      draw();
    };
    number.addEventListener("input", () => {
      const text = number.value.trim();
      if (text === "") return;
      const v = Number(text);
      if (!Number.isFinite(v)) return;
      if (target === state) setName("curve (edited)");
      if (axis === "x") target.x[k] = v; else target.y[k] = v;
      syncCell(elements, v, { write: false });
      draw();
    });
    fine.addEventListener("input", () => {
      const current = axis === "x" ? target.x[k] : target.y[k];
      const sign = current < 0 ? -1 : 1;
      set(sign * +fine.value * Math.pow(10, decode(current).decade));
    });
    decade.addEventListener("input", () => {
      const current = axis === "x" ? target.x[k] : target.y[k];
      const sign = current < 0 ? -1 : 1;
      const mantissa = Math.abs(decode(current).mantissa);
      set(sign * mantissa * Math.pow(10, +decade.value));
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
    pair.append(number, fine, decade, flip, scales);
    steppers(number, direction => {
      const current = axis === "x" ? target.x[k] : target.y[k];
      set(stepInteger(current, direction));
    });
    cell.append(pair);
    return cell;
  }

  // The power a box carries. With exponent step 1 it is the box index; with a
  // fractional step the boxes step by that fraction, so box 1 is t^0.5 at step
  // 1/2 and every label, the formula and the closing sentence follow it.
  const exponentOf = index => index * (window.phPowerStep || 1);
  // written as a fraction, so t^5/2 does not become the rounded t^2.5
  const exponentLabel = value => {
    for (const d of [1, 2, 3, 4, 5, 6]) {
      const n = value * d;
      if (Math.abs(n - Math.round(n)) < 1e-9) {
        return d === 1 ? String(Math.round(n)) : `${Math.round(n)}/${d}`;
      }
    }
    return value.toFixed(3);
  };
  const powerText = index => {
    const value = exponentOf(index);
    if (index === 0) return "t^0";
    if (Math.abs(value - 1) < 1e-9) return "t";
    return `t^${exponentLabel(value)}`;
  };

  // One line per power: the power on the left, then the x number, then the y
  // number. Six lines at degree 11, ten at degree 19.
  function buildPairGrid(target) {
    const grid = document.createElement("div");
    grid.className = "pair-grid";
    const heading = text => {
      const span = document.createElement("span");
      span.className = "axis-head";
      span.textContent = text;
      return span;
    };
    grid.append(document.createElement("span"), heading("x"), heading("y"));
    for (let k = 0; k < speedCount; k++) {
      const power = document.createElement("span");
      power.className = "power-label";
      power.textContent = powerText(k);
      grid.append(power, makeCell("x", target, k), makeCell("y", target, k));
    }
    return grid;
  }

  // the row must be as long as the rung before the boxes are built, or a box
  // asks for a number that is not there yet
  sizePair(state);
  sizePair(complement);
  // the starting row is whole-power data, so at a fractional step it goes into the
  // whole-power boxes and the boxes between them stay zero
  {
    const placedX = expandForStep(defaults.x);
    const placedY = expandForStep(defaults.y);
    const fill = (row, to) => row.slice(0, to).concat(new Array(to).fill(0)).slice(0, to);
    state.x = fill(placedX, speedCount);
    state.y = fill(placedY, speedCount);
  }
  grid.append(buildPairGrid(state));
  if (complementGrid) complementGrid.append(buildPairGrid(complement));
  function writeCells() {
    cells.forEach(cell => syncCell(cell, cell.axis === "x" ? cell.target.x[cell.k] : cell.target.y[cell.k]));
  }

  // Changing the rung must never destroy a number. A coefficient above the new rung
  // is stashed rather than deleted, and comes back when the rung grows again; a
  // coefficient that was never set is zero.
  function sizePair(pair) {
    if (!pair.stash) pair.stash = { x: [], y: [] };
    ["x", "y"].forEach(axis => {
      const row = pair[axis];
      if (row.length > speedCount) {
        pair.stash[axis] = row.slice(speedCount);
        row.length = speedCount;
      }
      while (row.length < speedCount) {
        row.push(pair.stash[axis].length ? pair.stash[axis].shift() : 0);
      }
    });
  }

  // A new rung: every number that still has a box keeps its value, the new
  // boxes start at zero, and the controls are rebuilt so the sliders match the
  // new count. Nothing is rescaled, so an old curve draws the same shape.
  function rebuildControls() {
    sizePair(state);
    sizePair(complement);
    cells.length = 0;
    grid.textContent = "";
    grid.append(buildPairGrid(state));
    if (complementGrid) {
      complementGrid.textContent = "";
      complementGrid.append(buildPairGrid(complement));
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
  const view = { rails: false, character: false, startTerminal: false, endTerminal: false,
                 rotate: false, complement: !window.phNoComplement, focusKnot: false, zoom: 1 };
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

  // The parameter window. t = 0 is where the curve starts, so a negative `from`
  // draws the same curve backwards from its own start, and a `to` past 1 runs on
  // past the end. Nothing is clamped: the tail is the same curve, only longer.
  const range = { from: 0, to: 1 };

  // the points from t = 0 to t = end, as a walk of `steps`
  function walkTo(speed, end, steps) {
    const out = [];
    let x = 0, y = 0;
    const step = end / steps;
    for (let i = 0; i < steps; i++) {
      const t = (i + 0.5) * step;
      const p = value(speed.x, t), q = value(speed.y, t);
      x += (p * p - q * q) * step;
      y += 2 * p * q * step;
      out.push({ t, x, y });
    }
    return out;
  }

  function spineSamples(speed, n = 700) {
    const half = Math.max(2, Math.round(n / 2));
    // a from of 0 has no backwards part; walking it anyway would pile hundreds
    // of duplicate points on the origin and invent crossings there
    const forward = walkTo(speed, range.to, range.from === 0 ? n : half);
    const backward = range.from === 0 ? [] : walkTo(speed, range.from, half).reverse();
    const ordered = backward.concat([{ t: 0, x: 0, y: 0 }], forward);
    return ordered.map(({ t, x, y }) => {
      const p = value(speed.x, t), q = value(speed.y, t);
      const speed2 = p * p + q * q;
      const tx = speed2 > 1e-12 ? (p * p - q * q) / speed2 : 1;
      const ty = speed2 > 1e-12 ? 2 * p * q / speed2 : 0;
      return { t, x, y, tx, ty, nx: -ty, ny: tx };
    });
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

  // Where each crossing sits in t: the crossing point is nearest a sample, and the
  // sample index gives the parameter. Enough to cut at, and simpler than solving.
  function crossingParams(points, tolerance) {
    // A crossing sits at TWO parameters: the curve passes through the same place
    // twice. Both are recorded. Taking only the nearest sample in space picks the
    // wrong branch about half the time, which cut one leg and left the other.
    const hits = [];
    const turn = (ax, ay, bx, by) => ax * by - ay * bx;
    const count = Math.max(1, points.length - 1);
    for (let i = 0; i < points.length - 1; i++) {
      const [ax, ay] = points[i], [bx, by] = points[i + 1];
      const lowX = Math.min(ax, bx), highX = Math.max(ax, bx);
      const lowY = Math.min(ay, by), highY = Math.max(ay, by);
      for (let j = i + 2; j < points.length - 1; j++) {
        const [cx, cy] = points[j], [dx, dy] = points[j + 1];
        if (Math.max(cx, dx) < lowX || Math.min(cx, dx) > highX) continue;
        if (Math.max(cy, dy) < lowY || Math.min(cy, dy) > highY) continue;
        const d1 = turn(bx - ax, by - ay, cx - ax, cy - ay);
        const d2 = turn(bx - ax, by - ay, dx - ax, dy - ay);
        const d3 = turn(dx - cx, dy - cy, ax - cx, ay - cy);
        const d4 = turn(dx - cx, dy - cy, bx - cx, by - cy);
        if (d1 * d2 < 0 && d3 * d4 < 0) {
          const share = d1 / (d1 - d2);
          hits.push({
            x: ax + (bx - ax) * share,
            y: ay + (by - ay) * share,
            tA: (i + share) / count,
            tB: (j + share) / count,
          });
        }
      }
    }
    const kept = [];
    hits.forEach(hit => {
      if (kept.some(other => Math.abs(other.x - hit.x) < tolerance && Math.abs(other.y - hit.y) < tolerance)) return;
      kept.push(hit);
    });
    return kept;
  }

  // the nearest small fraction outward from a value, so a cut point can be named
  const snapOut = (value, direction) => {
    const steps = 48;
    const scaled = value * steps;
    return (direction < 0 ? Math.floor(scaled) : Math.ceil(scaled)) / steps;
  };
  const fractionText = value => {
    if (Math.abs(value - Math.round(value)) < 1e-9) return String(Math.round(value));
    for (const d of [2, 3, 4, 6, 8, 12, 16, 24, 48]) {
      const n = value * d;
      if (Math.abs(n - Math.round(n)) < 1e-9) return `${Math.round(n)}/${d}`;
    }
    return value.toFixed(3);
  };

  // ---------- rebuilding a sub-span as its own curve, exactly ----------
  // z(t) = integral of w(t)^2, so over a span [a, b] the new speed is
  //   W(u) = sqrt(b - a) * w(a + (b - a) u)
  // A span whose length is a square of a fraction keeps every number rational,
  // so the rebuilt rows are whole numbers and the curve stays exact — which is
  // what the Bezier conversion needs. BigInt arithmetic throughout: doubles lose
  // the knot, and a curve that only looks right on screen is not a result.
  const bigGcd = (a, b) => {
    a = a < 0n ? -a : a; b = b < 0n ? -b : b;
    while (b) { const next = a % b; a = b; b = next; }
    return a || 1n;
  };
  const frac = (n, d = 1n) => {
    let top = typeof n === "bigint" ? n : BigInt(n);
    let bottom = typeof d === "bigint" ? d : BigInt(d);
    if (bottom < 0n) { top = -top; bottom = -bottom; }
    const g = bigGcd(top, bottom);
    return { n: top / g, d: bottom / g };
  };
  const fAdd = (p, q) => frac(p.n * q.d + q.n * p.d, p.d * q.d);
  const fMul = (p, q) => frac(p.n * q.n, p.d * q.d);
  const fPow = (p, k) => { let out = frac(1n); for (let i = 0; i < k; i++) out = fMul(out, p); return out; };
  const fBinomial = (n, k) => { let out = 1n; for (let i = 0n; i < BigInt(k); i++) out = (out * (BigInt(n) - i)) / (i + 1n); return out; };

  function spanValuesExact(row, a, span, root) {
    const degree = row.length - 1;
    const out = [];
    for (let k = 0; k <= degree; k++) {
      let total = frac(0n);
      for (let j = k; j <= degree; j++) {
        total = fAdd(total, fMul(fMul(frac(Math.round(row[j] || 0)), frac(fBinomial(j, k))),
                                 fMul(fPow(a, j - k), fPow(span, k))));
      }
      out.push(fMul(total, root));
    }
    return out;
  }

  // one scale for both rows, so the shape is untouched; null if they will not fit
  function sharedIntegers(rows) {
    let scale = 1n;
    rows.forEach(row => row.forEach(value => { scale = (scale / bigGcd(scale, value.d)) * value.d; }));
    const out = [];
    for (const row of rows) {
      const whole = [];
      for (const value of row) {
        const number = (value.n * scale) / value.d;
        if (number > 9007199254740991n || number < -9007199254740991n) return null;
        whole.push(Number(number));
      }
      out.push(whole);
    }
    return out;
  }

  const exactTable = (() => {
    // every square (k/n)^2 for n up to 16: long knots need long spans, and a span
    // that cannot be covered makes the rebuild fall back to the whole curve
    const out = [];
    for (let n = 2; n <= 16; n++) for (let k = 1; k < n; k++) out.push({ lenN: k * k, lenD: n * n, rootN: k, rootD: n });
    return out.sort((p, q) => p.lenN / p.lenD - q.lenN / q.lenD);
  })();

  // the same path the button takes, so a test can check the numbers directly
  // how far the drawn curve is from its own mirror, as a share of its size
  window.phNthSymmetry = () => {
    const points = spineSamples({ x: state.x, y: state.y }).map(s => [s.x, s.y]);
    const mirror = R_mirrorOf(points);
    const size = Math.max(
      Math.max(...points.map(p => p[0])) - Math.min(...points.map(p => p[0])),
      Math.max(...points.map(p => p[1])) - Math.min(...points.map(p => p[1]))) || 1e-9;
    const near = (p, cloud) => Math.min(...cloud.map(q => Math.hypot(p[0] - q[0], p[1] - q[1])));
    const gap = Math.max(Math.max(...mirror.map(p => near(p, points))),
                         Math.max(...points.map(p => near(p, mirror))));
    return +(gap / size).toFixed(4);
  };
  const R_mirrorOf = points => {
    const centre = (Math.min(...points.map(p => p[0])) + Math.max(...points.map(p => p[0]))) / 2;
    return points.map(([x, y]) => [2 * centre - x, y]);
  };

  window.phNthSpanRows = (aN, aD, lenN, lenD, rootN, rootD) => {
    const a = frac(aN, aD), span = frac(lenN, lenD), root = frac(rootN, rootD);
    const rows = sharedIntegers([spanValuesExact(state.x, a, span, root),
                                 spanValuesExact(state.y, a, span, root)]);
    return rows ? { x: rows[0], y: rows[1] } : null;
  };

  // The compass at the foot of the page: the heading is twice the angle of the
  // first pair, so four headings serve eight pairs, and a pair and its negative
  // share a heading.
  function drawCompass() {
    const host = document.getElementById("n-compass");
    if (!host) return;
    const size = 340, cx = size / 2, cy = size / 2, radius = 112;
    const groups = [
      { heading: 0, pairs: [[1, 0], [-1, 0]], speed: 1 },
      { heading: 90, pairs: [[1, 1], [-1, -1]], speed: 2 },
      { heading: 180, pairs: [[0, 1], [0, -1]], speed: 1 },
      { heading: 270, pairs: [[1, -1], [-1, 1]], speed: 2 },
    ];
    const at = (heading, distance) => [cx + Math.cos(heading) * distance,
                                       cy - Math.sin(heading) * distance];
    let art = `<rect width="${size}" height="${size}" fill="#fbf7ec"/>` +
      `<circle cx="${cx}" cy="${cy}" r="${radius}" fill="none" stroke="#d8ccae"/>` +
      `<circle cx="${cx}" cy="${cy}" r="${radius + 26}" fill="none" stroke="#efe7d3"/>`;
    [[0, 1], [1, 0], [0, -1], [-1, 0]].forEach(([dx, dy]) => {
      art += `<line x1="${cx + dx * (radius + 26)}" y1="${cy - dy * (radius + 26)}" ` +
             `x2="${cx - dx * (radius + 26)}" y2="${cy + dy * (radius + 26)}" ` +
             `stroke="#efe7d3"/>`;
    });
    ["0", "90", "180", "270"].forEach((label, index) => {
      const [x, y] = at(index * Math.PI / 2, radius + 26);
      art += `<text x="${x}" y="${y + 4}" font-size="12" fill="#7b6c4e" ` +
             `text-anchor="middle">${label}</text>`;
    });
    groups.forEach(({ heading, pairs, speed }) => {
      const angle = heading * Math.PI / 180;
      const [tipX, tipY] = at(angle, radius - 8);
      art += `<line x1="${cx}" y1="${cy}" x2="${tipX}" y2="${tipY}" ` +
             `stroke="#c9bfa6" stroke-width="2"/>`;
      const [labelX, labelY] = at(angle, radius - 26);
      art += `<text x="${labelX}" y="${labelY}" font-size="12" fill="#2e2413" ` +
             `text-anchor="middle">${pairs[0].join(",")}  ${pairs[1].join(",")}</text>` +
             `<text x="${labelX}" y="${labelY + 13}" font-size="11" fill="#7b6c4e" ` +
             `text-anchor="middle">speed ${speed}</text>`;
    });
    // the curve on this page
    const x0 = state.x[0] || 0, y0 = state.y[0] || 0;
    const heading = 2 * Math.atan2(y0, x0);
    const [tipX, tipY] = at(heading, radius);
    art += `<line x1="${cx}" y1="${cy}" x2="${tipX}" y2="${tipY}" ` +
           `stroke="#2e2413" stroke-width="2.6"/>` +
           `<circle cx="${tipX}" cy="${tipY}" r="4" fill="#2e2413"/>` +
           `<circle cx="${cx}" cy="${cy}" r="4" fill="#1f5fa8"/>`;
    const degrees = ((heading * 180 / Math.PI) % 360 + 360) % 360;
    art += `<text x="${size - 8}" y="14" font-size="10" fill="#7b6c4e" ` +
           `text-anchor="end">Fig. E4</text>`;
    art += `<text x="${cx}" y="${size - 8}" font-size="13" fill="#2e2413" ` +
           `text-anchor="middle">first pair ${x0}, ${y0} &rarr; heading ${degrees.toFixed(1)}&deg;` +
           `, speed ${(x0 * x0 + y0 * y0).toFixed(2)}</text>`;
    host.innerHTML = art;
  }

  // The grid of products: every x number times every other, with the diagonal
  // that makes each power of the curve.
  function drawPairTable() {
    const host = document.getElementById("n-pair-table");
    if (!host) return;
    const count = Math.min(speedCount, 6);
    const cell = 58, left = 74, top = 52;
    const tints = ["#f4ecd7", "#efe4c9", "#f7f1e2"];
    let art = `<rect width="560" height="470" fill="#fbf7ec"/>` +
      `<text x="${left}" y="24" font-size="14" font-weight="600" fill="#2e2413">` +
      `x row multiplied by itself${count < speedCount ? " (the first six powers)" : ""}</text>` +
      `<text x="${left}" y="40" font-size="11" fill="#7b6c4e">each cell is one product; a diagonal is one power</text>`;
    for (let i = 0; i < count; i++) {
      art += `<text x="${left + i * cell + cell / 2}" y="${top - 8}" font-size="11" ` +
             `fill="#7b6c4e" text-anchor="middle">t^${i}</text>` +
             `<text x="${left - 10}" y="${top + i * cell + cell / 2 + 4}" font-size="11" ` +
             `fill="#7b6c4e" text-anchor="end">t^${i}</text>`;
    }
    for (let row = 0; row < count; row++) {
      for (let column = 0; column < count; column++) {
        const power = row + column;
        const product = (state.x[column] || 0) * (state.x[row] || 0);
        const shade = tints[power % tints.length];
        art += `<rect x="${left + column * cell}" y="${top + row * cell}" width="${cell - 3}" ` +
               `height="${cell - 3}" fill="${shade}" stroke="#d8ccae"/>` +
               `<text x="${left + column * cell + 4}" y="${top + row * cell + 13}" font-size="9" ` +
               `fill="#8a3b2a">${power}</text>` +
               `<text x="${left + column * cell + cell / 2 - 1}" y="${top + row * cell + cell / 2 + 6}" ` +
               `font-size="12" fill="#2e2413" text-anchor="middle">${+product.toFixed(2)}</text>`;
      }
    }
    const footY = top + count * cell + 16;
    art += `<text x="${left}" y="${footY}" font-size="11" fill="#2e2413">` +
           `diagonal 0 makes the t term, diagonal 1 the t^2 term, ... diagonal ${2 * (count - 1)} ` +
           `the t^${2 * (count - 1) + 1} term</text>` +
           `<text x="${left}" y="${footY + 15}" font-size="11" fill="#7b6c4e">` +
           `each diagonal is divided by its power plus one</text>` +
           `<text x="548" y="14" font-size="10" fill="#7b6c4e" text-anchor="end">Fig. E2</text>`;
    host.innerHTML = art;
  }

  // The triangle: the root that an ordinary curve carries, and the same root
  // cancelling here because the two speeds are a matched pair.
  function drawLengthFigure(arcText) {
    const host = document.getElementById("n-length");
    if (!host) return;
    const triangle = (x, title, hypotenuse, colour) => {
      const ax = x, ay = 128, bx = x + 120, by = 128, cx = x + 120, cy = 44;
      return `<text x="${x + 10}" y="22" font-size="12" font-weight="600" fill="#2e2413">${title}</text>` +
        `<path d="M${ax},${ay} L${bx},${by} L${cx},${cy} Z" fill="#f7f1e2" stroke="#d8ccae"/>` +
        `<text x="${x + 60}" y="${ay + 16}" font-size="11" fill="#7b6c4e" text-anchor="middle">x'</text>` +
        `<text x="${bx + 6}" y="${(ay + cy) / 2}" font-size="11" fill="#7b6c4e">y'</text>` +
        `<text x="${x + 34}" y="${(ay + cy) / 2 - 6}" font-size="11" fill="${colour}" ` +
        `text-anchor="middle">${hypotenuse}</text>`;
    };
    let art = `<rect width="560" height="190" fill="#fbf7ec"/>` +
      triangle(40, "an ordinary curve", "\u221a(x'\u00b2+y'\u00b2)", "#a23b2a") +
      triangle(330, "these curves", "p\u00b2 + q\u00b2", "#2e2413") +
      `<text x="40" y="158" font-size="11" fill="#a23b2a">the root stays: no clean length</text>` +
      `<text x="330" y="158" font-size="11" fill="#2e2413">the root cancels: a plain polynomial</text>` +
      `<text x="40" y="178" font-size="11" fill="#7b6c4e">` +
      `x'\u00b2 + y'\u00b2 = (p\u00b2 + q\u00b2)\u00b2, so the length is the integral of p\u00b2 + q\u00b2` +
      `</text>` +
      `<text x="548" y="14" font-size="10" fill="#7b6c4e" text-anchor="end">Fig. E3</text>`;
    host.innerHTML = art;
    const exact = document.getElementById("n-length-exact");
    if (exact) exact.textContent = arcText;
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
    const centreOfSpine = spinePoints.length
      ? [spinePoints.reduce((sum, p) => sum + p[0], 0) / spinePoints.length,
         spinePoints.reduce((sum, p) => sum + p[1], 0) / spinePoints.length]
      : [0, 0];
    const turnedAbout = (points, degrees, about) => {
      if (!degrees) return points;
      const angle = degrees * Math.PI / 180;
      const cos = Math.cos(angle), sin = Math.sin(angle);
      return points.map(([x, y]) => {
        const dx = x - about[0], dy = y - about[1];
        return [about[0] + dx * cos - dy * sin, about[1] + dx * sin + dy * cos];
      });
    };
    const complementShown = turnedAbout(
      placed(complement.transform, complementSpine), complement.turn, centreOfSpine);
    const all = spinePoints.slice();
    if (view.complement) all.push(...complementShown);
    if (view.rails) all.push(...leftRail, ...rightRail);
    if (characterLeft) all.push(...characterLeft, ...characterRight);
    if (startEnd) all.push(...startEnd.arc, startEnd.tip);
    if (finishEnd) all.push(...finishEnd.arc, finishEnd.tip);
    const shown = turned(all);
    // where the stroke crosses itself: that cluster is the knot, and the focus
    // frames it instead of the whole curve, which is mostly long legs
    const selfCrossings = crossingsOf(spinePoints, spinePoints,
                                      1e-4 * Math.max(1e-9, Math.max(...shown.map(p => p[0])) -
                                                      Math.min(...shown.map(p => p[0]))));
    const knotsShown = turned(selfCrossings);
    // The frame is chosen first — the knot with a margin when focusing, otherwise
    // the whole curve — and then the zoom scales it about its own centre. Positive
    // zoom magnifies, negative pulls back past the whole figure, |z| < 1 counts as
    // 1. Working this way keeps both directions one piece of arithmetic.
    const xs = shown.map(p => p[0]), ys = shown.map(p => p[1]);
    const padX = Math.max(1e-6, (Math.max(...xs) - Math.min(...xs)) * 0.08);
    const padY = Math.max(1e-6, (Math.max(...ys) - Math.min(...ys)) * 0.08);
    let frame = {
      minX: Math.min(...xs) - padX, maxX: Math.max(...xs) + padX,
      minY: Math.min(...ys) - padY, maxY: Math.max(...ys) + padY,
    };
    if (view.focusKnot && knotsShown.length) {
      const kx = knotsShown.map(p => p[0]), ky = knotsShown.map(p => p[1]);
      const centreX = (Math.min(...kx) + Math.max(...kx)) / 2;
      const centreY = (Math.min(...ky) + Math.max(...ky)) / 2;
      const spread = Math.max(Math.max(...kx) - Math.min(...kx), Math.max(...ky) - Math.min(...ky), 1e-6);
      const half = spread * 0.9;
      frame = { minX: centreX - half, maxX: centreX + half, minY: centreY - half, maxY: centreY + half };
    }
    // a cut end gets a dotted stub, and the frame must have room for it or the clip
    // eats it: 6% of the frame on each side when a cut is in force
    if (range.from > 1e-9 || range.to < 1 - 1e-9) {
      const growX = (frame.maxX - frame.minX) * 0.06;
      const growY = (frame.maxY - frame.minY) * 0.06;
      frame = { minX: frame.minX - growX, maxX: frame.maxX + growX,
                minY: frame.minY - growY, maxY: frame.maxY + growY };
    }
    const zoom = Number(view.zoom);
    const factor = !Number.isFinite(zoom) || Math.abs(zoom) < 1 ? 1 : (zoom > 0 ? 1 / zoom : Math.abs(zoom));
    if (factor !== 1) {
      // aim at the knot when there is one: the centre of the bounding box can sit
      // far from the crossings, and zooming there magnifies empty space — which is
      // exactly what "the zoom does nothing" feels like
      let midX = (frame.minX + frame.maxX) / 2, midY = (frame.minY + frame.maxY) / 2;
      if (knotsShown.length) {
        midX = (Math.min(...knotsShown.map(p => p[0])) + Math.max(...knotsShown.map(p => p[0]))) / 2;
        midY = (Math.min(...knotsShown.map(p => p[1])) + Math.max(...knotsShown.map(p => p[1]))) / 2;
      }
      const halfW = ((frame.maxX - frame.minX) / 2) * factor;
      const halfH = ((frame.maxY - frame.minY) / 2) * factor;
      frame = { minX: midX - halfW, maxX: midX + halfW, minY: midY - halfH, maxY: midY + halfH };
    }
    const { minX, maxX, minY, maxY } = frame;
    const width_ = 900, height = 380, left = 40, right = 24, top = 16, bottom = 24;
    const scale = Math.min((width_ - left - right) / (maxX - minX), (height - top - bottom) / (maxY - minY));
    const ox = left + ((width_ - left - right) - (maxX - minX) * scale) / 2;
    const oy = top + ((height - top - bottom) - (maxY - minY) * scale) / 2;
    const fx = v => ox + (v - minX) * scale, fy = v => oy + (maxY - v) * scale;
    // the frame is published so a test can ask what it is showing
    window.phNthFrame = () => ({ minX, maxX, minY, maxY, scale, focus: view.focusKnot, zoom: view.zoom,
                                 knotCentre: knotsShown.length
                                   ? { x: (Math.min(...knotsShown.map(p => p[0])) + Math.max(...knotsShown.map(p => p[0]))) / 2,
                                       y: (Math.min(...knotsShown.map(p => p[1])) + Math.max(...knotsShown.map(p => p[1]))) / 2 }
                                   : null });
    const path = points => "M" + turned(points).map(p => fx(p[0]).toFixed(1) + "," + fy(p[1]).toFixed(1)).join("L");
    let art = `<rect width="${width_}" height="${height}" fill="#fbf7ec"/>` +
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
    if (view.complement) {
      art += `<path d="${path(complementShown)}" fill="none" stroke="#666666" stroke-opacity="0.6" stroke-width="2"/>`;
    }
    art += `<path d="${path(spinePoints)}" fill="none" stroke="#2e2413" stroke-width="2.4"/>`;
    // a cut end gets a short dotted stub along its own direction, about a quarter of
    // an inch on screen, so the eye reads "the leg continues" rather than "the curve
    // stops here". It is a hint, not geometry: it is not part of the curve.
    const stub = 22;                                  // 22 screen units: a quarter inch or so
    const carried = parts => parts.map(p => [fx(p[0]), fy(p[1])]);
    const dotted = (from, towards) => {
      const dx = towards[0] - from[0], dy = towards[1] - from[1];
      const length = Math.hypot(dx, dy) || 1;
      const end = [from[0] - (dx / length) * stub, from[1] - (dy / length) * stub];
      return `<path d="M${(from[0]).toFixed(1)},${(from[1]).toFixed(1)}L${(end[0]).toFixed(1)},${(end[1]).toFixed(1)}" ` +
             `fill="none" stroke="#6b6152" stroke-width="1.6" stroke-dasharray="3 4"/>`;
    };
    const shownSpine = turned(spinePoints).map(p => [fx(p[0]), fy(p[1])]);
    if (range.from > 1e-9 && shownSpine.length > 2) art += dotted(shownSpine[0], shownSpine[1]);
    if (range.to < 1 - 1e-9 && shownSpine.length > 2) {
      art += dotted(shownSpine[shownSpine.length - 1], shownSpine[shownSpine.length - 2]);
    }
    if (startEnd) art += `<path d="${path(startEnd.arc)}" fill="none" stroke="#a23b2a" stroke-width="2.4"/>`;
    if (finishEnd) art += `<path d="${path(finishEnd.arc)}" fill="none" stroke="#a23b2a" stroke-width="2.4"/>`;
    // the meetings of the two curves, counted and marked
    const meets = view.complement ? crossingsOf(spinePoints, complementShown,
                              1e-4 * Math.max(1e-9, maxX - minX)) : [];
    meets.forEach(([x, y]) => {
      art += `<circle cx="${fx(x).toFixed(1)}" cy="${fy(y).toFixed(1)}" r="3.6" ` +
             `fill="#fbf7ec" stroke="#a23b2a" stroke-width="1.6"/>`;
    });
    art += `<circle cx="${fx(0).toFixed(1)}" cy="${fy(0).toFixed(1)}" r="4" fill="#1f5fa8"/>`;
    // legend inside the figure, 15px, naming the spine first and wrapping when
    // the entries would run past the right edge
    const legend = [["#2e2413", 2.4, "spine"], ["#666666", 2, "complementary curve"]];
    if (range.from > 1e-9 || range.to < 1 - 1e-9) {
      legend.push(["#6b6152", 1.6, "the legs continue past the cut"]);
    }
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
    syncToggles();

    // how much of the figure is knot and how much is leg: the two numbers that
    // answer "make the knot bigger and the legs shorter"
    let knotShare = null, legShare = null;
    if (selfCrossings.length) {
      const diag = Math.max(1e-9, Math.hypot(
        Math.max(...spinePoints.map(p => p[0])) - Math.min(...spinePoints.map(p => p[0])),
        Math.max(...spinePoints.map(p => p[1])) - Math.min(...spinePoints.map(p => p[1]))));
      const spread = Math.max(
        Math.max(...selfCrossings.map(p => p[0])) - Math.min(...selfCrossings.map(p => p[0])),
        Math.max(...selfCrossings.map(p => p[1])) - Math.min(...selfCrossings.map(p => p[1])));
      const legs = Math.max(
        Math.min(...selfCrossings.map(c => Math.hypot(c[0] - spinePoints[0][0], c[1] - spinePoints[0][1]))),
        Math.min(...selfCrossings.map(c => Math.hypot(c[0] - spinePoints[spinePoints.length - 1][0],
                                                      c[1] - spinePoints[spinePoints.length - 1][1]))));
      knotShare = Math.round((spread / diag) * 100);
      legShare = Math.round((legs / diag) * 100);
    }
    const m = metrics(speed.x, speed.y);
    const openness = m.arc > 1e-12 ? Math.hypot(m.chord[0], m.chord[1]) / m.arc : 0;
    const curve = curveOf(speed);
    const degreeOf = terms => { let d = 0; terms.forEach((c, k) => { if (Math.abs(c) > 1e-9) d = k; }); return d; };
    const plain = metrics(state.x, state.y);
    const hookNote = (hook.dx || hook.dy)
      ? ` | grid without the hook 1/${plain.pitch.toLocaleString()}` : "";
    const gridText = m.pitch ? `grid 1/${m.pitch.toLocaleString()}${hookNote}` : "grid n/a: fractional powers";
    const negativeNote = (range.from < 0 && (window.phPowerStep || 1) !== 1)
      ? " | t below 0 uses the odd extension sign(t)|t|^step" : "";
    const inflectionText = m.inflections
      ? `inflections ${m.inflections.length} (max ${2 * speedDegree - 1})`
      : "inflections n/a: fractional powers";
    document.getElementById("n-readout").textContent =
      `bend ${m.bend.toFixed(3)} | ${gridText} | ` + inflectionText + ` | ` +
      `first ${m.inflection === null ? " - " : m.inflection.toFixed(3)} | ` +
      `closest ${m.closest.toFixed(3)} | open ${openness.toFixed(3)} | ` +
      `crosses ${meets.length}` +
      (knotShare === null ? " | no knot: nothing crosses" : ` | knot ${knotShare}% legs ${legShare}%`) +
      negativeNote;
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
    // The worked example at the foot of the page: the same numbers the boxes
    // hold, written out through the formula.
    const explain = document.getElementById("n-formula-explain");
    if (explain) {
      const written = row => {
        const parts = [];
        row.forEach((c, k) => {
          if (!c) return;
          const power = k === 0 ? "" : powerText(k);
          const size = Math.abs(c) === 1 && power ? "" : String(Math.abs(c));
          parts.push(`${c < 0 ? " - " : parts.length ? " + " : ""}${size}${power}`);
        });
        return parts.join("") || "0";
      };
      const x0 = state.x[0] || 0, y0 = state.y[0] || 0;
      explain.textContent =
        `the x speed is  ${written(state.x)}\n` +
        `the y speed is  ${written(state.y)}\n` +
        `the t term of x is ${x0}*${x0} - ${y0}*${y0} = ${x0 * x0 - y0 * y0}\n` +
        `the t term of y is 2 * ${x0} * ${y0} = ${2 * x0 * y0}\n` +
        `${state.x.length} numbers per row: the speed reaches t^${exponentLabel(exponentOf(state.x.length - 1))}, ` +
        `so the curve reaches t^${exponentLabel(2 * exponentOf(state.x.length - 1) + 1)}`;
    }
    const box = document.getElementById("n-json");
    if (box) {
      box.value = JSON.stringify(flatRecord(currentName), null, 2);
    }
    drawBars();
    drawCompass();
    drawPairTable();
    drawLengthFigure(`this curve: length ${m.arc.toFixed(6)}, from a closed form ` +
                     `\u2014 no square root was taken`);
  }

  const multiply = (left, right) => {
    const product = new Array(left.length + right.length - 1).fill(0);
    left.forEach((l, i) => right.forEach((r, j) => { product[i + j] += l * r; }));
    return product;
  };
  function curveOf(speed = state) {
    const xx = multiply(speed.x, speed.x), yy = multiply(speed.y, speed.y), xy = multiply(speed.x, speed.y);
    const x = [0], y = [0];
    // as far as the longer square: the y terms past the x row's length still
    // belong to the position
    for (let j = 0; j < Math.max(xx.length, yy.length); j++) {
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
  // Place the end with the top pair. Adding c t^k to the speed moves the end by
  // 2 c times the integral of w t^k, which is linear in c, so two numbers in the
  // top pair can put the end anywhere near where it was - and the rest of the
  // curve barely moves, because t^k is small away from t = 1.
  function endpointOf(px, py) {
    const curve = curveOf({ x: px, y: py });
    return [curve.x.reduce((sum, v) => sum + v, 0), curve.y.reduce((sum, v) => sum + v, 0)];
  }
  function placeEnd(targetX, targetY) {
    const k = speedCount - 1;
    for (let step = 0; step < 8; step++) {
      const end = endpointOf(state.x, state.y);
      const offX = targetX - end[0], offY = targetY - end[1];
      if (Math.hypot(offX, offY) < 1e-7) break;
      const A = state.x.reduce((sum, v, j) => sum + v / (j + k + 1), 0);
      const B = state.y.reduce((sum, v, j) => sum + v / (j + k + 1), 0);
      const denominator = 2 * (A * A + B * B);
      if (!denominator) return false;
      state.x[k] += (A * offX + B * offY) / denominator;
      state.y[k] += (A * offY - B * offX) / denominator;
    }
    return true;
  }
  const placeButton = document.getElementById("n-place-end");
  if (placeButton) placeButton.addEventListener("click", () => {
    const xField = document.getElementById("n-end-x");
    const yField = document.getElementById("n-end-y");
    const targetX = Number(xField.value), targetY = Number(yField.value);
    if (!Number.isFinite(targetX) || !Number.isFinite(targetY)) return;
    if (!placeEnd(targetX, targetY)) return;
    writeCells();
    draw();
  });

  const turnField = document.getElementById("n-comp-turn");
  if (turnField) turnField.addEventListener("input", () => {
    const v = Number(turnField.value);
    if (!Number.isFinite(v)) return;
    complement.turn = v;
    draw();
  });

  // the window boxes: no clamp, so a tail can run as far as you like, and a
  // slider beside each box for the quick drag. Negative t is allowed; with a
  // fractional exponent the curve is drawn by the odd extension, which the
  // readout says in words when the window goes below zero.
  const windowSliders = {};
  [["n-t-from", "from"], ["n-t-to", "to"]].forEach(([id, side]) => {
    const field = document.getElementById(id);
    const slider = document.getElementById(`${id}-slider`);
    windowSliders[side] = slider;
    if (slider) {
      slider.addEventListener("input", () => {
        const value = Number(slider.value);
        if (field) field.value = String(value);
        if (side === "from" && value === range.to) return;
        if (side === "to" && value === range.from) return;
        range[side] = value;
        draw();
      });
    }
    if (!field) return;
    field.addEventListener("input", () => {
      const v = Number(field.value);
      if (!Number.isFinite(v)) return;
      if (side === "from" && v === range.to) return;
      if (side === "to" && v === range.from) return;
      range[side] = v;
      if (slider) slider.value = String(Math.max(Number(slider.min), Math.min(Number(slider.max), v)));
      draw();
    });
  });

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
    // Found by scripts/ph_find.py, not drawn by hand: the first crosses its own
    // flip six times from four numbers a side, the second is the tightest curve
    // the search found with more than one inflection.
    // From scripts/ph_root_family.py, which walks root positions instead of
    // random coefficients. Same shapes as m-arch and wave3 at a fraction of the
    // grid: pitch 1, 3 and 14 against 15 and 105.
    { name: "m-coarse",
      speedX: [1, 1],
      speedY: [-6, 23, -20],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    { name: "bowl-coarse",
      speedX: [1, 1],
      speedY: [-3, 5],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    { name: "wave-coarse",
      speedX: [1, 0],
      speedY: [-4, 33, -75, 50],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    // The named curves that the PH formula carries, fitted at degree 7 by
    // scripts/ph_carry.py: the deviation from the target is in the comment.
    // Their grids are fine because a fitted transcendental curve needs decimals;
    // the shape is what is being kept, not the integer grid.
    { name: "involute-fit",          // 0.00010 of the size, one and a half turns
      speedX: [0.5951, 37.5019, -207.7699, 519.4995, -1241.3886, 1888.7416, -1368.1424, 370.9987],
      speedY: [-0.0371, 6.6438, 92.4853, -203.4783, 6.5755, 105.8778, 19.7943, -37.2965],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    { name: "catenary-fit",          // 0.00000
      speedX: [2.2425, -2.1364, 2.5227, -0.8004, 0.4702, -0.084, 0.028, 0.0],
      speedY: [-1.4243, 3.3637, -1.6023, 1.2613, -0.2998, 0.1404, -0.0205, 0.0059],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    { name: "euler-fit",             // 0.00002, one full turn
      speedX: [1.0015, -0.1045, 1.7424, -11.9521, 35.6612, -72.0211, 62.6600, -17.9857],
      speedY: [0.0002, -0.0120, 3.2612, -0.1396, -2.5111, 11.7646, -25.4700, 13.1077],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    { name: "logspiral-fit",         // 0.00007, two turns
      speedX: [2.8444, -9.9068, -68.9870, -28.7523, 208.7261, 549.4016, -1086.0085, 446.3495],
      speedY: [2.1810, 23.7130, -54.4823, 133.2243, -1136.2484, 2274.9752, -1585.1451, 352.4053],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    { name: "knot-6",
      speedX: [-2, -2, 3, 4],
      speedY: [3, -6, -4, 2],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    { name: "knot-7",
      speedX: [2, -6, 2, -2, 2],
      speedY: [1, 2, -3, -6, 0],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    { name: "inflect-2",
      speedX: [3, -6, -1, 6],
      speedY: [-3, 6, -2, 0],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    // The higher-degree shapes that earned a place: one three-arch wave, one
    // deep sharp valley, a sharper one, and the two-sharp-turn curve at degree
    // 13. The rest of the batch I handed over were variants of these or flat
    // ribbons; they are one number away from these.
    { name: "wave3",
      speedX: [1, 0, 0, 0, 0, 0],
      speedY: [-5, 46, -108, 72, 0, 0],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    { name: "cusp5-x3",
      speedX: [1, 0, 0, 0, 0, 0],
      speedY: [-3, 30, -120, 240, -240, 96],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    { name: "cusp7-deep",
      speedX: [1, 0, 0, 0, 0, 0, 0, 0],
      speedY: [-4, 56, -336, 1120, -2240, 2688, -1792, 512],
      width: { percent: 1.5 },
      character: { plus: 2, minus: 2, profile: "bow" },
      shear: 0,
      hook: { dx: 0, dy: 0 } },
    { name: "twin-cusp",
      speedX: [2, 0, 0, 0, 0, 0, 0],
      speedY: [8, -108, 594, -1701, 2673, -2187, 729],
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
        turn: +complement.turn,
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
  // A single curve, in the flat shape the septic, quintic and gallery pages
  // already read: no second curve, no matrix, just the rows.
  function flatRecord(name) {
    const m = metrics(state.x, state.y);
    // the position polynomials, so a cut point can be given exactly rather than
    // read off the screen: x(t) and y(t) are polynomials in t
    const position = curveOf({ x: state.x, y: state.y });
    const at = (terms, t) => terms.reduce((sum, c, k) => sum + c * Math.pow(t, k), 0);
    const pointAt = t => ({ t: +t.toFixed(6), x: +at(position.x, t).toFixed(6), y: +at(position.y, t).toFixed(6) });
    const truncation = { from: pointAt(range.from), to: pointAt(range.to) };
    return {
      truncation,
      name,
      category: "S",
      speedX: state.x.map(v => +v),
      speedY: state.y.map(v => +v),
      bend: +m.bend.toFixed(3),
      pitch: m.pitch,
      inflection: m.inflection === null ? null : +m.inflection.toFixed(3),
      inflections: (m.inflections || []).map(value => +value.toFixed(4)),
      closest: +m.closest.toFixed(3),
      width: { percent: width.percent },
      tRange: { from: range.from, to: range.to },
      character: { plus: character.plus, minus: character.minus, profile: character.profile },
      shear: shear.delta,
      hook: { dx: hook.dx, dy: hook.dy },
    };
  }

  function pairOf(item) {
    if (item && item.primary) return item;
    // a curve that states its powers needs no flat row: the powers are the data
    if (item && Array.isArray(item.terms) && item.terms.length &&
        !Array.isArray(item.speedX) && !Array.isArray(item.speedY)) {
      return { ...item, format: "curve-lab.terms/1", category: item.category || "S",
               primary: { speedX: [], speedY: [], transform: identity() },
               complementary: null };
    }
    if (item && Array.isArray(item.speedX) && Array.isArray(item.speedY)) {
      return { ...item, format: "curve-lab.double-knot/1",
               category: item.category || "S",
               primary: { speedX: item.speedX, speedY: item.speedY, transform: identity() },
               complementary: null };
    }
    return null;
  }
  // A stored row is whole-power data. At a fractional step its numbers belong in
  // the boxes whose powers are whole, and every half-power box between them stays
  // zero: t^0, t, t^2 ... at step 1/2, not t^0, t^1/2, t^1 ...
  // A curve may say which power each number belongs to. When it does, that is
  // the truth and the flat row is only a convenience: the value goes in the box
  // whose power it names, and every other box is zero.
  function rowsFromTerms(terms) {
    const step = window.phPowerStep || 1;
    const notes = [];
    const spots = [];
    terms.forEach(term => {
      const power = Number(term.power);
      if (!Number.isFinite(power) || power < 0) {
        notes.push(`power ${term.power} ignored: not a power at or above zero`);
        return;
      }
      const exact = power / step;
      const index = Math.round(exact);
      if (Math.abs(exact - index) > 1e-9) {
        // a term that does not land on a box is refused, not rounded: a rounded
        // term is a different curve, which is the confusion this format removes
        notes.push(`power ${power} is off the step ${step}, so it was left out`);
        return;
      }
      spots.push({ index, x: Number(term.x) || 0, y: Number(term.y) || 0 });
    });
    const highest = spots.reduce((top, spot) => Math.max(top, spot.index), 0);
    if (highest >= speedCount) window.phNthSetDegree(highest);
    const count = speedCount;
    const x = new Array(count).fill(0);
    const y = new Array(count).fill(0);
    spots.forEach(spot => {
      if (spot.index < count) { x[spot.index] = spot.x; y[spot.index] = spot.y; }
    });
    return { x, y, placed: spots.length, notes };
  }

  function expandForStep(row) {
    const step = window.phPowerStep || 1;
    const inverse = 1 / step;
    const factor = Math.abs(inverse - Math.round(inverse)) < 1e-9 ? Math.round(inverse) : 1;
    if (factor === 1) return row.slice();
    const out = new Array((row.length - 1) * factor + 1).fill(0);
    row.forEach((value, k) => { out[k * factor] = value; });
    return out;
  }

  function loadPair(item) {
    const pair = pairOf(item);
    if (!pair) return;
    const fit = row => {
      const spread = expandForStep(row);
      const need = spread.length;
      if (need > speedCount) window.phNthSetDegree(need - 1);
      return spread.slice(0, speedCount).concat(new Array(speedCount).fill(0)).slice(0, speedCount);
    };
    if (Array.isArray(item.terms) && item.terms.length) {
      const built = rowsFromTerms(item.terms);
      // the rung may have grown, so size the pair before writing
      sizePair(state);
      state.x = built.x.slice(0, speedCount);
      state.y = built.y.slice(0, speedCount);
      const status = document.getElementById("n-paste-status");
      if (status) {
        status.textContent = built.notes.length
          ? built.notes.join("; ")
          : `loaded ${built.placed} powers at step ${window.phPowerStep || 1}`;
      }
    } else {
    state.x = fit(pair.primary.speedX);
    state.y = fit(pair.primary.speedY);
    }
    state.transform = (pair.primary.transform || identity()).slice();
    if (pair.complementary && Array.isArray(pair.complementary.speedX)) {
      complement.x = fit(pair.complementary.speedX);
      complement.y = fit(pair.complementary.speedY);
      complement.transform = (pair.complementary.transform || identity()).slice();
      complement.turn = Number(pair.complementary.turn) || 0;
      const turnBox = document.getElementById("n-comp-turn");
      if (turnBox) turnBox.value = String(complement.turn);
    } else {
      flipComplement();
    }
    setName(pair.name || "curve");
    // a record may carry a cut: the whole curve is still in the terms, the window
    // says which part of it this curve is about
    if (pair.truncation && pair.truncation.from && pair.truncation.to) {
      range.from = Number(pair.truncation.from.t);
      range.to = Number(pair.truncation.to.t);
      const fromBox = document.getElementById("n-t-from"), toBox = document.getElementById("n-t-to");
      if (fromBox) fromBox.value = String(range.from);
      if (toBox) toBox.value = String(range.to);
      const fromSlider = document.getElementById("n-t-from-slider"), toSlider = document.getElementById("n-t-to-slider");
      if (fromSlider) fromSlider.value = String(Math.max(-10, Math.min(10, range.from)));
      if (toSlider) toSlider.value = String(Math.max(-10, Math.min(10, range.to)));
    } else if (item && !item.truncation) {
      range.from = 0;
      range.to = 1;
    }
    applyWidth(pair);
    const endX = document.getElementById("n-end-x");
    const endY = document.getElementById("n-end-y");
    if (endX && endY) {
      const end = endpointOf(state.x, state.y);
      endX.value = String(+end[0].toFixed(3));
      endY.value = String(+end[1].toFixed(3));
    }
    if (pair.tRange && Number.isFinite(Number(pair.tRange.from)) && Number.isFinite(Number(pair.tRange.to))) {
      range.from = Number(pair.tRange.from);
      range.to = Number(pair.tRange.to);
      const fromField = document.getElementById("n-t-from");
      const toField = document.getElementById("n-t-to");
      if (fromField) fromField.value = String(range.from);
      if (toField) toField.value = String(range.to);
    }
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

  // a page may switch the seeds off, so its gallery shows only what it means to show
  window.phNthSeeds = window.phHideSeeds ? [] : SEED;

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
  const savePrimary = document.getElementById("n-save-primary");
  if (savePrimary) savePrimary.addEventListener("click", () => {
    const nameField = document.getElementById("n-name");
    const status = document.getElementById("n-paste-status");
    const typed = (nameField.value || "").trim() || `curve ${saved().length + 1}`;
    const name = resolveName(typed, "save this curve");
    const items = saved().filter(item => item.name !== name);
    items.push(flatRecord(name));
    store(items);
    currentName = name;
    nameField.value = "";
    renderSaved();
    window.dispatchEvent(new CustomEvent("ph-nth-saved"));
    if (status) status.textContent = `saved the primary curve as "${name}"`;
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

  // ---------- build a curve from its flat spots ----------
  // The row in the boxes is a polynomial's coefficients, lowest power first. Its
  // roots are the t where the vertical speed is zero, so the stroke runs
  // horizontal there. Choosing the roots and multiplying out is the only way to
  // get a symmetric curve on purpose.
  const gcdPair = (a, b) => {
    a = Math.abs(a); b = Math.abs(b);
    while (b) { const next = a % b; a = b; b = next; }
    return a || 1;
  };
  const lcmPair = (a, b) => a * b / gcdPair(a, b);
  const parseSpot = text => {
    const trimmed = String(text).trim();
    if (!trimmed) return null;
    if (trimmed.includes("/")) {
      const [top, bottom] = trimmed.split("/");
      let n = Number(top), d = Number(bottom);
      if (!Number.isFinite(n) || !Number.isFinite(d) || d === 0) return null;
      if (d < 0) { n = -n; d = -d; }
      const g = gcdPair(n, d);
      return { n: n / g, d: d / g };
    }
    const plain = Number(trimmed);
    if (!Number.isFinite(plain)) return null;
    const n = Math.round(plain * 1000), d = 1000;
    const g = gcdPair(n, d);
    return { n: n / g, d: d / g };
  };
  // Multiply (t - spot) for every spot, exactly, in whole numbers: put every spot
  // over one denominator D, multiply the integer roots out, then clear D^k.
  function rowFromFlatSpots(spots) {
    let D = 1;
    spots.forEach(spot => { D = lcmPair(D, spot.d); });
    const whole = spots.map(spot => spot.n * (D / spot.d));
    let row = [1];
    whole.forEach(root => {
      const next = new Array(row.length + 1).fill(0);
      row.forEach((value, power) => {
        next[power] += -root * value;
        next[power + 1] += value;
      });
      row = next;
    });
    row = row.map((value, power) => value * Math.pow(D, power));
    const divisor = row.reduce((shared, value) => gcdPair(shared, value), 0) || 1;
    return row.map(value => value / divisor);
  }
  const padRow = (row, count) => {
    const out = row.slice(0, count);
    while (out.length < count) out.push(0);
    return out;
  };

  const rootsField = document.getElementById("n-roots");
  const bowField = document.getElementById("n-bow");
  const rootsStatus = document.getElementById("n-roots-status");
  const rootsButton = document.getElementById("n-roots-fill");
  const rootsPreset = document.getElementById("n-roots-preset");

  function fillFromFlatSpots() {
    const spots = String(rootsField ? rootsField.value : "")
      .split(/[,;\s]+/).map(parseSpot).filter(Boolean);
    if (!spots.length) {
      if (rootsStatus) rootsStatus.textContent = "type at least one flat spot, for example 1/2";
      return;
    }
    const bow = (bowField && parseSpot(bowField.value)) || { n: 0, d: 1 };
    const degree = Math.max(spots.length, 2);
    if (degree > 9) {
      if (rootsStatus) rootsStatus.textContent = `too many flat spots: ${spots.length}; this page stops at 9`;
      return;
    }
    // keep the rung the page is already on: shrinking to the smallest fit threw
    // away the longer rows, and with them the half-power boxes to type into
    if (window.phNthDegree().speedCount < degree + 1) window.phNthSetDegree(Math.max(5, degree));
    const count = window.phNthDegree().speedCount;
    // the bow is a fraction, so both rows are scaled by its denominator: a common
    // scale leaves the shape alone and keeps every number whole
    // the flat spots describe a polynomial in t, so its coefficients belong in the
    // boxes whose powers are whole. Writing them straight in put the whole-power
    // curve into the half-power boxes whenever the step was 1/2.
    const whole = rowFromFlatSpots(spots).map(value => value * bow.d);
    const terms = [];
    for (let k = 0; k < Math.max(whole.length, 3); k++) {
      terms.push({ power: k,
                   x: k === 0 ? bow.d : (k === 1 ? bow.n : (k === 2 ? -bow.n : 0)),
                   y: whole[k] || 0 });
    }
    const placed = rowsFromTerms(terms);
    state.x = placed.x.slice(0, count).concat(new Array(count).fill(0)).slice(0, count);
    state.y = placed.y.slice(0, count).concat(new Array(count).fill(0)).slice(0, count);
    writeCells();
    draw();
    const measured = window.recipeMetrics ? window.recipeMetrics(state.x, state.y) : null;
    if (rootsStatus) {
      const scaled = bow.d > 1 ? ` · both rows scaled by ${bow.d} to keep the bow whole` : "";
      const grid = measured && measured.pitch ? ` · grid 1/${measured.pitch}` : " · grid n/a";
      // the mirror only holds at step 1: say so rather than let the picture lie
      const step = window.phPowerStep || 1;
      const warning = Math.abs(step - 1) > 1e-9
        ? ` · placed on whole powers: the ${step.toFixed(2)} boxes stay zero, so the knot is exact`
        : "";
      rootsStatus.textContent = `step ${step.toFixed(2)} · top power t^${exponentLabel(exponentOf(count - 1))} · ` +
        `y ${state.y.join(", ")}` +
        (measured ? ` · bend ${measured.bend.toFixed(3)}${grid}` : "") + scaled + warning;
    }
  }

  // ---------- the ruler: place flat spots by hand ----------
  // One dot per copy, so three dots stacked at 1/2 is the triple flat. Every
  // position is a fraction with a small denominator, mirrored about 1/2.
  // the positions on the strip: every fraction below 1/2 whose denominator is
  // here, plus 1/2 itself. The wider set came with the longer rows (30 numbers),
  // which can carry more distinct flat spots.
  const RULER_DENOMINATORS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20];
  const rulerSpots = (() => {
    const seen = new Map();
    RULER_DENOMINATORS.forEach(d => {
      for (let n = 1; n < d / 2; n++) {
        const g = gcdPair(n, d);
        seen.set(`${n / g}/${d / g}`, { n: n / g, d: d / g, value: (n / g) / (d / g) });
      }
    });
    seen.set("1/2", { n: 1, d: 2, value: 0.5 });
    return [...seen.values()].sort((a, b) => a.value - b.value);
  })();
  const rulerHost = document.getElementById("n-roots-ruler");
  const mirrorBox = document.getElementById("n-roots-mirror");
  const countLabel = document.getElementById("n-roots-count");
  const sameSpot = (a, b) => a.n * b.d === b.n * a.d;
  let marks = [];

  function textOf(spots) {
    return spots.slice().sort((a, b) => a.n / a.d - b.n / b.d)
      .map(spot => `${spot.n}/${spot.d}`).join(", ");
  }
  function applySpots() {
    if (rootsField) rootsField.value = textOf(marks);
    if (countLabel) {
      const copies = {};
      marks.forEach(spot => { const key = `${spot.n}/${spot.d}`; copies[key] = (copies[key] || 0) + 1; });
      const summary = Object.entries(copies).map(([key, times]) => times > 1 ? `${key} x${times}` : key).join(", ");
      countLabel.textContent = marks.length ? `${marks.length} spot${marks.length === 1 ? "" : "s"}: ${summary}` : "no spots yet";
    }
    renderRuler();
  }
  function addSpot(spot, remove) {
    if (remove) {
      const at = marks.findIndex(item => sameSpot(item, spot));
      if (at >= 0) marks.splice(at, 1);
    } else {
      marks.push({ n: spot.n, d: spot.d });
      const mirror = mirrorBox && mirrorBox.checked;
      if (mirror && spot.n * 2 !== spot.d) marks.push({ n: spot.d - spot.n, d: spot.d });
    }
    applySpots();
  }
  function renderRuler() {
    if (!rulerHost) return;
    rulerHost.textContent = "";
    // ticks first, then the labels, in order of importance: the small
    // denominators get a name before the crowded ones do
    rulerSpots.forEach(spot => {
      const tick = document.createElement("span");
      tick.className = "tick";
      tick.style.left = `${spot.value * 100}%`;
      tick.style.height = spot.d <= 6 || spot.d === 8 ? "12px" : "7px";
      rulerHost.append(tick);
    });
    const labelRows = [[], []];
    rulerSpots.slice().sort((a, b) => a.d - b.d || a.value - b.value).forEach(spot => {
      for (let row = 0; row < labelRows.length; row++) {
        if (labelRows[row].every(placed => Math.abs(placed - spot.value) > 0.045)) {
          const label = document.createElement("span");
          label.className = "tick-label";
          label.style.left = `${spot.value * 100}%`;
          label.style.bottom = row === 0 ? "-18px" : "-31px";
          label.textContent = `${spot.n}/${spot.d}`;
          rulerHost.append(label);
          labelRows[row].push(spot.value);
          return;
        }
      }
    });
    // one badge per position, carrying its count: a stacked dot costs vertical
    // space and stops being clickable once the stack grows over the rule
    const counts = new Map();
    marks.forEach(spot => {
      const key = `${spot.n}/${spot.d}`;
      counts.set(key, (counts.get(key) || 0) + 1);
    });
    counts.forEach((times, key) => {
      const [numerator, denominator] = key.split("/").map(Number);
      const spot = { n: numerator, d: denominator };
      const badge = document.createElement("span");
      badge.className = "spot-count";
      badge.style.left = `${(numerator / denominator) * 100}%`;
      badge.dataset.spot = key;
      badge.title = `${key}: ${times} ${times === 1 ? "copy" : "copies"}`;
      // an arrow each side of the count: up adds a copy, down takes one away and
      // stops at zero, because a spot used zero times is simply not used
      const step = (label, title, remove) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "spot-step";
        button.textContent = label;
        button.title = title;
        button.addEventListener("click", event => {
          event.stopPropagation();
          addSpot(spot, remove);
        });
        return button;
      };
      const value = document.createElement("span");
      value.className = "spot-value";
      value.textContent = String(times);
      value.addEventListener("click", event => {
        event.stopPropagation();
        addSpot(spot, event.shiftKey);
      });
      badge.append(step("\u25b2", "one more copy", false), value, step("\u25bc", "one fewer copy", true));
      rulerHost.append(badge);
    });
  }

  if (rulerHost) {
    rulerHost.addEventListener("click", event => {
      const rect = rulerHost.getBoundingClientRect();
      const t = (event.clientX - rect.left) / Math.max(1, rect.width);
      let best = null;
      let closest = 1;
      rulerSpots.forEach(spot => {
        const distance = Math.abs(spot.value - t);
        if (distance < closest) { best = spot; closest = distance; }
      });
      if (best && closest < 0.06) addSpot(best, false);
    });
    // start from the flat spots already in the field
    String(rootsField ? rootsField.value : "").split(/[,;\s]+/).map(parseSpot).filter(Boolean)
      .forEach(spot => marks.push(spot));
    renderRuler();
    if (countLabel) countLabel.textContent = marks.length ? `${marks.length} spots` : "no spots yet";
  }
  const halfSlider = document.getElementById("n-roots-half");
  const halfLabel = document.getElementById("n-roots-half-value");
  if (halfSlider) halfSlider.addEventListener("input", () => {
    const want = Number(halfSlider.value);
    marks = marks.filter(spot => spot.n * 2 !== spot.d);      // drop the 1/2 copies
    for (let i = 0; i < want; i++) marks.push({ n: 1, d: 2 });
    if (halfLabel) halfLabel.textContent = String(want);
    applySpots();
  });
  const bowSlider = document.getElementById("n-bow-slider");
  if (bowSlider) {
    bowSlider.addEventListener("input", () => {
      if (bowField) bowField.value = bowSlider.value;
      applySpots();
    });
    if (bowField) bowField.addEventListener("change", () => {
      const value = Number(bowField.value);
      if (Number.isFinite(value)) bowSlider.value = String(Math.max(-12, Math.min(12, value)));
    });
  }

  // ---------- mirror-safe tweaks on the primary curve ----------
  // Each pattern is exactly balanced about t = 1/2, so the mirror survives: an
  // even row takes an even pattern, an odd row an odd one (the row is odd when it
  // reads as its own negative from the far end).
  const EVEN_PATTERNS = {
    x1: [[1, -1], [2, 1]],
    x2: [[2, 1], [3, -2], [4, 1]],
    x3: [[3, 1], [4, -3], [5, 3], [6, -1]],
  };
  const ODD_PATTERNS = {
    y1: [[1, -1], [2, 3], [3, -2]],
    y2: [[2, -1], [3, 4], [4, -5], [5, 2]],
  };
  const tweakHistory = [];
  // the name of the curve being worked on, in the open, so it can be copied into a
  // conversation. Editing any number marks it as changed rather than renaming it.
  const nameBadge = () => document.getElementById("n-curve-name");
  const setName = name => {
    currentName = name;
    const badge = nameBadge();
    if (badge) badge.textContent = name;
  };

  const tweakTotal = document.getElementById("n-tweak-total");
  // the curve as it stood before the first tweak of this run, so the panel can say
  // what the total change is — and as a fraction, because round fractions are what
  // keep the grid cheap
  let tweakBase = null;
  const asFraction = value => {
    if (Math.abs(value - Math.round(value)) < 1e-9) return String(Math.round(value));
    let best = null;
    for (let d = 2; d <= 64; d++) {
      const n = Math.round(value * d);
      const error = Math.abs(value - n / d);
      if (!best || error < best.error) best = { n, d, error };
    }
    if (best && best.error < 1e-4) {
      const sources = [];
      for (let n2 = 1; n2 < best.d; n2++) sources.push(n2);
      return `${best.n}/${best.d}`;
    }
    return value.toFixed(4);
  };
  function updateTweakTotal() {
    if (!tweakTotal) return;
    if (!tweakBase) { tweakTotal.textContent = "no change from the starting curve yet"; return; }
    const step = window.phPowerStep || 1;
    const parts = [];
    const describe = (before, after, axis) => {
      after.forEach((value, index) => {
        const was = before[index] || 0;
        const delta = +(value - was).toFixed(6);
        if (!delta) return;
        const power = +(index * step).toFixed(3);
        const share = was ? asFraction(delta / was) : null;
        parts.push(`${axis} t^${power} ${delta > 0 ? "+" : ""}${asFraction(delta)}` +
                   (share ? ` (${share} of ${asFraction(was)})` : ""));
      });
    };
    describe(tweakBase.x, state.x, "x");
    describe(tweakBase.y, state.y, "y");
    const now = window.recipeMetrics ? window.recipeMetrics(state.x, state.y) : null;
    const grid = now && now.pitch ? ` · grid 1/${now.pitch.toLocaleString()}` : " · grid n/a at this step";
    tweakTotal.textContent = parts.length ? `total change: ${parts.join("; ")}${grid}` : "no change from the starting curve yet";
  }
  const snapshotBase = () => { if (!tweakBase) tweakBase = { x: state.x.slice(), y: state.y.slice() }; };

  const tweakStatus = document.getElementById("n-tweak-status");
  const tweakSize = document.getElementById("n-tweak-size");
  // the size is a fraction. Its denominator is the grid cost: an addition needs the
  // grid times that denominator, the multiply times its square, because the factor
  // is used twice. A decimal such as 0.1 costs ten, which is why it felt wrong.
  const readSize = () => {
    const spot = parseSpot(tweakSize ? tweakSize.value : "1/4");
    if (!spot || spot.n <= 0) return { value: 0.25, denominator: 4, text: "1/4" };
    return { value: spot.n / spot.d, denominator: spot.d, text: `${spot.n}/${spot.d}` };
  };

  function addToPower(row, power, amount) {
    const step = window.phPowerStep || 1;
    const exact = power / step;
    const index = Math.round(exact);
    if (Math.abs(exact - index) > 1e-9 || index >= row.length) return false;
    row[index] = Math.round((row[index] + amount) * 1e6) / 1e6;
    return true;
  }

  function applyPattern(key, row) {
    let { value: size, denominator, text } = readSize();
    // A share of the coefficient itself: the x pair has equal magnitude, so
    // 16/16 = 1 keeps both the whole numbers and the balance. Divides the pair's
    // own value, so the tweak is integer whenever the divisor divides it.
    const divisorBox = document.getElementById("n-tweak-divisor");
    const divisor = divisorBox ? Number(divisorBox.value) : 0;
    if (divisor && row === state.x) {
      const step = window.phPowerStep || 1;
      const first = Math.round(1 / step);
      const magnitude = Math.abs(row[first] || 0);
      if (magnitude) {
        size = Math.round((magnitude / divisor) * 1e6) / 1e6;
        text = `${magnitude}/${divisor}`;
        denominator = 1;
      }
    }
    const table = row === state.x ? EVEN_PATTERNS : ODD_PATTERNS;
    const pattern = table[key];
    if (!pattern) return;
    snapshotBase();
    tweakHistory.push({ row: row === state.x ? "x" : "y", before: row.slice() });
    let touched = 0;
    pattern.forEach(([power, weight]) => { if (addToPower(row, power, weight * size)) touched += 1; });
    writeCells();
    draw();
    updateTweakTotal();
    if (tweakStatus) {
      const now = window.recipeMetrics ? window.recipeMetrics(state.x, state.y) : null;
      const grid = now && now.pitch ? ` · grid now 1/${now.pitch.toLocaleString()}` : "";
      tweakStatus.textContent = touched
        ? `${row === state.x ? "x" : "y"} row: ${touched} powers moved by ${text} times ` +
          `${pattern.map(p => p[1]).join(", ")}${grid}`
        : "this step cannot reach those powers";
    }
  }

  function multiplyBoth(size, denominator, text) {
    // Done in powers, not in boxes: at step 1/2 a box is half a power, so scaling
    // boxes would put the factor's centre at t = 1/4 and lean the curve. The factor
    // is 1 + size(t - t^2), namely powers 0, 1 and 2.
    const step = window.phPowerStep || 1;
    const factor = [[0, 1], [1, size], [2, -size]];
    const indexOf = power => {
      const exact = power / step;
      const index = Math.round(exact);
      return Math.abs(exact - index) < 1e-9 ? index : null;
    };
    const product = row => {
      const out = new Map();
      row.forEach((value, k) => {
        if (!value) return;
        factor.forEach(([offset, weight]) => {
          const power = +(k * step + offset).toFixed(6);
          out.set(power, (out.get(power) || 0) + value * weight);
        });
      });
      return out;
    };
    const px = product(state.x), py = product(state.y);
    const offGrid = [...px.keys(), ...py.keys()].filter(power => indexOf(power) === null);
    if (offGrid.length) {
      if (tweakStatus) tweakStatus.textContent =
        `this step cannot hold power ${offGrid[0]}: the multiply needs a step that divides 1 and 2`;
      return;
    }
    const top = Math.max(...[...px.keys(), ...py.keys()].map(indexOf)) + 1;
    snapshotBase();
    tweakHistory.push({ row: "both", x: state.x.slice(), y: state.y.slice() });
    if (top > window.phNthDegree().speedCount) window.phNthSetDegree(top - 1);
    sizePair(state);
    const write = row => {
      const out = new Array(speedCount).fill(0);
      row.forEach((value, power) => {
        const index = indexOf(power);
        if (index !== null && index < speedCount) out[index] = +value.toFixed(6);
      });
      return out;
    };
    state.x = write(px);
    state.y = write(py);
    writeCells();
    draw();
    updateTweakTotal();
    if (tweakStatus) {
      const now = window.recipeMetrics ? window.recipeMetrics(state.x, state.y) : null;
      const grid = now && now.pitch ? ` · grid now 1/${now.pitch.toLocaleString()}` : "";
      tweakStatus.textContent =
        `both rows multiplied by 1 + ${text}(t - t^2) in powers, mirror held${grid}`;
    }
  }

  [["n-tweak-x1", "x1", () => state.x], ["n-tweak-x2", "x2", () => state.x],
   ["n-tweak-x3", "x3", () => state.x], ["n-tweak-y1", "y1", () => state.y],
   ["n-tweak-y2", "y2", () => state.y]].forEach(([id, key, row]) => {
    const button = document.getElementById(id);
    if (button) button.addEventListener("click", () => applyPattern(key, row()));
  });
  const tweakBoth = document.getElementById("n-tweak-both");
  if (tweakBoth) tweakBoth.addEventListener("click", () => {
    const { value, denominator, text } = readSize();
    multiplyBoth(value, denominator, text);
  });
  const tweakUndo = document.getElementById("n-tweak-undo");
  if (tweakUndo) tweakUndo.addEventListener("click", () => {
    const last = tweakHistory.pop();
    if (!last) { if (tweakStatus) tweakStatus.textContent = "nothing to undo"; return; }
    // a tweak may have grown the rung, so a restored row is padded to the boxes that
    // exist now rather than left short — a short row makes a box read undefined
    const pad = row => row.slice(0, speedCount).concat(new Array(speedCount).fill(0)).slice(0, speedCount);
    if (last.row === "both") { state.x = pad(last.x); state.y = pad(last.y); }
    else if (last.row === "x") state.x = pad(last.before); else state.y = pad(last.before);
    writeCells();
    draw();
    if (!tweakHistory.length) tweakBase = null;
    updateTweakTotal();
    if (tweakStatus) tweakStatus.textContent = "last tweak undone";
  });

  const cutKnot = document.getElementById("n-cut-knot");
  if (cutKnot) cutKnot.addEventListener("click", () => {
    const speed = { x: state.x, y: state.y };
    const points = spineSamples(speed).map(s => [s.x, s.y]);
    const params = crossingParams(points, 1e-4);
    const status = document.getElementById("n-paste-status");
    if (!params.length) {
      if (status) status.textContent = "this curve does not cross itself, so there is no knot to cut to";
      return;
    }
    // every parameter the curve passes through the knot at, not one per crossing
    const spots = params.flatMap(p => [p.tA, p.tB]);
    const low = snapOut(Math.min(...spots), -1);
    const high = snapOut(Math.max(...spots), +1);
    range.from = Math.max(0, low);
    range.to = Math.min(1, high);
    const fromBox = document.getElementById("n-t-from");
    const toBox = document.getElementById("n-t-to");
    if (fromBox) fromBox.value = String(range.from);
    if (toBox) toBox.value = String(range.to);
    const fromSlider = document.getElementById("n-t-from-slider");
    const toSlider = document.getElementById("n-t-to-slider");
    if (fromSlider) fromSlider.value = String(range.from);
    if (toSlider) toSlider.value = String(range.to);
    view.focusKnot = false;
    if (focusKnot) focusKnot.setAttribute("aria-pressed", "false");
    draw();
    if (status) {
      status.textContent = `cut to t ${fractionText(range.from)} … ${fractionText(range.to)}: ` +
        `the ${params.length} crossings are kept and the legs beyond them are gone`;
    }
  });

  let lastRebuild = null;
  function rebuildSpanExact(low, high, statusPrefix) {
    const status = document.getElementById("n-paste-status");
    const step = window.phPowerStep || 1;
    if (Math.abs(step - 1) > 1e-9) {
      if (status) status.textContent =
        "the rebuild needs whole powers: set the exponent step to 1 first (a half-power row is not a polynomial in t)";
      return false;
    }
    const wanted = Math.min(1, high - low);
    let choice = null, aSteps = 0;
    for (const option of exactTable) {
      const length = option.lenN / option.lenD;
      if (length + 1e-9 < wanted) continue;
      const centre = (low + high) / 2;
      let start = Math.round((centre - length / 2) * 48);
      start = Math.max(0, Math.min(Math.round((1 - length) * 48), start));
      if (start / 48 <= low + 1e-9 && start / 48 + length >= high - 1e-9) {
        choice = option; aSteps = start; break;
      }
    }
    let fellBack = false;
    if (!choice) {
      choice = { lenN: 1, lenD: 1, rootN: 1, rootD: 1 };
      aSteps = 0;
      fellBack = true;
    }
    const built = window.phNthSpanRows(aSteps, 48, choice.lenN, choice.lenD, choice.rootN, choice.rootD);
    if (!built) {
      if (status) status.textContent = "the rebuilt numbers do not fit in whole numbers at this span";
      return false;
    }
    state.x = built.x.slice(0, speedCount).concat(new Array(speedCount).fill(0)).slice(0, speedCount);
    state.y = built.y.slice(0, speedCount).concat(new Array(speedCount).fill(0)).slice(0, speedCount);
    lastRebuild = { from: aSteps / 48, to: aSteps / 48 + choice.lenN / choice.lenD,
                    length: choice.lenN / choice.lenD };
    range.from = 0; range.to = 1;
    const fromBox = document.getElementById("n-t-from"), toBox = document.getElementById("n-t-to");
    if (fromBox) fromBox.value = "0";
    if (toBox) toBox.value = "1";
    writeCells();
    draw();
    if (status) {
      status.textContent = fellBack
        ? `${statusPrefix}the span needed is the whole curve, so nothing was cut`
        : `${statusPrefix}kept t ${aSteps}/48 to ${aSteps}/48 + ${choice.lenN}/${choice.lenD}, ` +
          `length ${choice.lenN}/${choice.lenD} = (${choice.rootN}/${choice.rootD})^2, numbers exact`;
    }
    return !fellBack;
  }

  const rebuildButton = document.getElementById("n-rebuild-span");
  if (rebuildButton && !rebuildButton.disabled) rebuildButton.addEventListener("click", () => {
    const status = document.getElementById("n-paste-status");
    const points = spineSamples({ x: state.x, y: state.y }).map(s => [s.x, s.y]);
    const params = crossingParams(points, 1e-4);
    if (!params.length) {
      if (status) status.textContent = "no knot here: nothing crosses itself, so there is no span to keep";
      return;
    }
    const spots = params.flatMap(p => [p.tA, p.tB]);
    rebuildSpanExact(Math.min(...spots), Math.max(...spots), "rebuilt from the knot: ");
  });

  // cut in arc length: the shape's own measure, not the construction's t
  const arcPercent = document.getElementById("n-arc-percent");
  const arcButton = document.getElementById("n-arc-rebuild");
  const speedAt = t => {
    const v = row => row.reduce((sum, c, k) => sum + c * Math.pow(t, k), 0);
    const p = v(state.x), q = v(state.y);
    return p * p + q * q;                    // |z'(t)| = |w|^2
  };
  const arcUpTo = t => {
    const steps = 1200;
    let total = 0;
    for (let i = 0; i < steps; i++) {
      const at = t * (i + 0.5) / steps;
      total += speedAt(at) * t / steps;
    }
    return total;
  };
  const tForArc = (fraction, whole) => {
    // bisection on the running arc length: the parameter that reaches a share of it
    if (whole <= 0) return fraction;
    const target = fraction * whole;
    let low = 0, high = 1;
    for (let i = 0; i < 50; i++) {
      const middle = (low + high) / 2;
      if (arcUpTo(middle) < target) low = middle; else high = middle;
    }
    return (low + high) / 2;
  };
  if (arcButton) arcButton.addEventListener("click", () => {
    const whole = arcUpTo(1);
    const keep = Math.max(0.1, Math.min(0.99, (Number(arcPercent && arcPercent.value) || 70) / 100));
    const cut = (1 - keep) / 2;
    const low = tForArc(cut, whole);
    const high = tForArc(1 - cut, whole);
    rebuildSpanExact(low, high, `kept ${Math.round(keep * 100)}% of the ink ` +
      `(t ${low.toFixed(3)} to ${high.toFixed(3)}): `);
  });

  // a plain percentage cut: same fraction of t off each end, exact in the JSON
  const cutPercent = document.getElementById("n-cut-percent");
  const cutApply = document.getElementById("n-cut-apply");
  if (cutApply) cutApply.addEventListener("click", () => {
    const percent = Math.max(0, Math.min(49, Number(cutPercent && cutPercent.value) || 0));
    range.from = percent / 100;
    range.to = 1 - percent / 100;
    const fromBox = document.getElementById("n-t-from"), toBox = document.getElementById("n-t-to");
    if (fromBox) fromBox.value = String(range.from);
    if (toBox) toBox.value = String(range.to);
    const fromSlider = document.getElementById("n-t-from-slider"), toSlider = document.getElementById("n-t-to-slider");
    if (fromSlider) fromSlider.value = String(range.from);
    if (toSlider) toSlider.value = String(range.to);
    draw();
    const status = document.getElementById("n-paste-status");
    if (status) {
      status.textContent = `cut ${percent}% off each end: t ${percent}/100 to ${100 - percent}/100, ` +
        "so the kept part and its two end points travel in the JSON";
    }
  });

  const focusKnot = document.getElementById("n-focus-knot");
  if (focusKnot) focusKnot.addEventListener("click", () => {
    view.focusKnot = !view.focusKnot;
    focusKnot.setAttribute("aria-pressed", String(view.focusKnot));
    focusKnot.textContent = view.focusKnot ? "show the whole curve" : "focus the knot";
    draw();
  });
  const zoomSlider = document.getElementById("n-zoom");
  const zoomNumber = document.getElementById("n-zoom-number");
  const setZoom = value => {
    const wanted = Number(value);
    // zero has no meaning for a magnification, so it snaps to 1
    view.zoom = !Number.isFinite(wanted) || Math.abs(wanted) < 1 ? 1 : wanted;
    if (zoomSlider) zoomSlider.value = String(Math.max(-12, Math.min(12, view.zoom)));
    if (zoomNumber) zoomNumber.value = String(view.zoom);
    draw();
  };
  if (zoomSlider) zoomSlider.addEventListener("input", () => setZoom(zoomSlider.value));
  if (zoomNumber) {
    zoomNumber.addEventListener("input", () => setZoom(zoomNumber.value));
    zoomNumber.addEventListener("change", () => setZoom(zoomNumber.value));
  }

  // A save lives in this browser only, so anything worth keeping also goes to a
  // file: the page cannot write to the repo, but a download is one button.
  const downloadButton = document.getElementById("n-download");
  if (downloadButton) downloadButton.addEventListener("click", () => {
    const box = document.getElementById("n-json");
    const text = box ? box.value : JSON.stringify(flatRecord(currentName), null, 2);
    const name = (currentName || "curve").replace(/[^\w.-]+/g, "-");
    const blob = new Blob([text], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `${name}.json`;
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
    const status = document.getElementById("n-paste-status");
    if (status) status.textContent = `downloaded ${name}.json — move it into workbench/ to keep it`;
  });

  // Toggle buttons keep their state visible: aria-pressed is the state, the CSS
  // makes it look pressed, and a screen reader reads it out. Set from the view
  // flags on every draw, so a toggle can never drift out of step with what is shown.
  const toggleButtons = [
    ["n-rails", () => view.rails],
    ["n-character", () => view.character],
    ["n-terminal-start", () => view.startTerminal],
    ["n-terminal-end", () => view.endTerminal],
    ["n-rotate", () => view.rotate],
    ["n-focus-knot", () => view.focusKnot],
    ["n-comp-hide", () => !view.complement],
  ];
  function syncToggles() {
    toggleButtons.forEach(([id, state]) => {
      const button = document.getElementById(id);
      if (button) button.setAttribute("aria-pressed", String(Boolean(state())));
    });
  }

  // the grey curve on or off: sometimes only the primary is wanted
  const hideComplement = document.getElementById("n-comp-hide");
  if (hideComplement) {
    hideComplement.addEventListener("click", () => {
      view.complement = !view.complement;
      hideComplement.textContent = view.complement ? "hide the grey curve" : "show the grey curve";
      hideComplement.setAttribute("aria-pressed", String(!view.complement));
      draw();
    });
  }

  const dotsFill = document.getElementById("n-roots-dots-fill");
  if (dotsFill) dotsFill.addEventListener("click", () => {
    if (rootsField) rootsField.value = textOf(marks);
    if (marks.length) fillFromFlatSpots();
  });

  const undoButton = document.getElementById("n-roots-undo");
  if (undoButton) undoButton.addEventListener("click", () => { marks.pop(); applySpots(); });
  const clearButton = document.getElementById("n-roots-clear");
  if (clearButton) clearButton.addEventListener("click", () => { marks = []; applySpots(); });
  const rootsFieldForTyping = rootsField;
  if (rootsFieldForTyping) rootsFieldForTyping.addEventListener("change", () => {
    marks = String(rootsFieldForTyping.value).split(/[,;\s]+/).map(parseSpot).filter(Boolean)
      .map(spot => ({ n: spot.n, d: spot.d }));
    renderRuler();
  });

  // The exponent step: a slider on the experimental page, with buttons for the
  // named stops. Any value in between is allowed, so 0.75 is a real choice.
  const stepControl = document.getElementById("n-step");
  const stepValue = document.getElementById("n-step-value");
  const stepName = value => {
    if (Math.abs(value - 1) < 1e-9) return "1";
    if (Math.abs(value - 0.5) < 1e-9) return "\u00bd";
    if (Math.abs(value - 1 / 3) < 1e-3) return "\u2153";
    if (Math.abs(value - 0.25) < 1e-9) return "\u00bc";
    return value.toFixed(2).replace(/0+$/, "").replace(/\.$/, "");
  };
  const applyStep = value => {
    // the numbers already in the boxes have powers under the old step. Keep those
    // powers: gather them as terms, then place them again under the new step. A
    // power the new step cannot reach is reported, not silently moved.
    const previous = window.phPowerStep || 1;
    let carried = null;
    if (Math.abs(previous - value) > 1e-12) {
      const terms = [];
      for (let k = 0; k < speedCount; k++) {
        const x = state.x[k] || 0, y = state.y[k] || 0;
        if (x || y) terms.push({ power: k * previous, x, y });
      }
      window.phPowerStep = value;
      const built = rowsFromTerms(terms);
      carried = built;
      const status = document.getElementById("n-paste-status");
      if (status && built.notes.length) status.textContent = built.notes.join("; ");
    }
    window.phPowerStep = value;
    if (carried) {
      sizePair(state);
      state.x = carried.x.slice(0, speedCount);
      state.y = carried.y.slice(0, speedCount);
    }
    if (stepControl && stepControl.type === "range") stepControl.value = String(value);
    if (stepValue) stepValue.textContent = stepName(value);
    rebuildControls();
    writeCells();
    draw();
  };
  if (stepControl) {
    if (Math.abs((window.phPowerStep || 1) - Number(stepControl.value)) > 1e-9) {
      stepControl.value = String(window.phPowerStep || 1);
      if (stepValue) stepValue.textContent = stepName(window.phPowerStep || 1);
    }
    const read = () => applyStep(Number(stepControl.value) || 1);
    stepControl.addEventListener("input", read);
    stepControl.addEventListener("change", read);
    document.querySelectorAll(".step-at").forEach(button => {
      button.addEventListener("click", () => applyStep(Number(button.dataset.step) || 1));
    });
  }

  if (rootsButton) rootsButton.addEventListener("click", fillFromFlatSpots);
  if (rootsPreset) rootsPreset.addEventListener("change", () => {
    // a suggestion names a known curve, so it carries its own exponent step: the
    // knot presets are whole powers, because mirroring only holds there
    const [spots, bow, step] = String(rootsPreset.value || "").split("|");
    if (!spots) return;
    if (rootsField) rootsField.value = spots;
    if (bowField) bowField.value = bow === undefined ? "0" : bow;
    // the step is the operator's, not the suggestion's: it stays where it is
    if (stepControl) stepControl.value = String(window.phPowerStep || 1);
  });

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
  // A saved item may be a pair (primary and complementary) or a single curve;
  // the gallery draws the primary either way.
  const rowsOf = item => (item && item.primary) ? item.primary : item;

  // A stored record carries `terms` (power beside value), not a flat row. The page
  // draws rows, so the row is derived here — one source of truth on disk, a row
  // in memory. A record without terms passes through untouched.
  function withRows(entry) {
    if (!entry || (Array.isArray(entry.speedX) && Array.isArray(entry.speedY))) return entry;
    if (!Array.isArray(entry.terms) || !entry.terms.length) return entry;
    const top = entry.terms.reduce((high, term) => Math.max(high, Number(term.power) || 0), 0);
    const x = new Array(top + 1).fill(0);
    const y = new Array(top + 1).fill(0);
    entry.terms.forEach(term => {
      const index = Number(term.power) || 0;
      x[index] = Number(term.x) || 0;
      y[index] = Number(term.y) || 0;
    });
    const measured = entry.measured || {};
    return { ...entry, speedX: x, speedY: y,
             from: entry.from || "found",     // it came from the finder's file
             bend: measured.bend !== undefined ? measured.bend : entry.bend,
             pitch: measured.grid !== undefined ? measured.grid : entry.pitch };
  }

  function currentList() {
    const locals = {};
    localSaved().forEach(item => { locals[item.name] = item; });
    const out = window.phNthGallery.map(entry => {
      const local = locals[entry.name];
      if (!local) return entry;
      const rows = rowsOf(local);
      return { ...entry, speedX: rows.speedX, speedY: rows.speedY,
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
    found.forEach(entry => {
      if (!out.some(other => other.name === entry.name)) out.push(withRows(entry));
    });
    const known = new Set(out.map(entry => entry.name));
    Object.values(locals).forEach(item => {
      if (known.has(item.name)) return;
      const rows = rowsOf(item);
      const measured = window.recipeMetrics ? window.recipeMetrics(rows.speedX, rows.speedY) : null;
      out.push({ name: item.name, speedX: rows.speedX, speedY: rows.speedY,
                 bend: measured ? +measured.bend.toFixed(3) : "-",
                 pitch: measured ? measured.pitch : "-",
                 from: "local", local: true });
    });
    // no sort here: the order on the page is the order the generator wrote, so a
    // figure can be moved by the generator and stay moved. A rank sort here used to
    // pull a moved operator entry straight back to the top.
    return out;
  }
  // The finder's own file, read at load: every search that ran with --write
  // shows up here without a rebuild, so nothing depends on someone remembering
  // to add it to the seeds.
  let found = [];
  fetch("found-curves.json", { cache: "no-store" })
    .then(response => (response.ok ? response.json() : null))
    .then(document => {
      if (document && Array.isArray(document.curves)) {
        found = document.curves;
        render();
      }
    })
    .catch(() => { /* no file yet, or opened from disk: the seeds still draw */ });

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

  function figureFor(entry, index = 0) {
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
        <span class="gallery-number">Fig. ${index}</span>
        <span class="gallery-name">${entry.name}</span>
        <span class="gallery-tags"><span class="tag">${String(entry.from || "") === "found" ? "found"
          : String(entry.from || "") === "operator" ? "yours"
          : String(entry.from || "").startsWith("fitted") ? "fitted" : "exact"}</span>
        <span class="gallery-metrics">bend ${entry.bend} | ${Number(entry.pitch) ? "grid 1/" + Number(entry.pitch).toLocaleString() : "grid n/a"}</span></span>
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
        <div class="more-grid">
          <div class="more-figure">
            ${entry.original && entry.original.length
                ? miniSvg(null, null, "the source path", null, null, entry.original)
                  + miniSvg(entry.speedX, entry.speedY, "fitted, degree 11", "full", entry)
                : miniSvg(entry.speedX, entry.speedY, entry.from === "found" ? "the curve" : "the curve",
                          "full", entry)}
          </div>
          <div class="more-actions">
            <p class="small mono">x ${entry.speedX.join(", ")}<br>y ${entry.speedY.join(", ")}</p>
            <p class="small mono">bend ${entry.bend} | ${Number(entry.pitch) ? "pitch " + Number(entry.pitch).toLocaleString() : "grid n/a"} | from ${entry.from}</p>
            <textarea rows="4" readonly>${json}</textarea>
            <div class="more-row">
              <button type="button" class="gallery-load">load into the sandbox</button>
              <button type="button" class="gallery-copy">copy JSON</button>
              <button type="button" class="gallery-close">close</button>
              <span class="small mono gallery-status"></span>
            </div>
          </div>
        </div>
      </div>
    </figure>`;
  }

  const render = () => {
    list = currentList();
    const declared = window.phNthKnots || [];
    const byName = new Map(list.map(entry => [entry.name, entry]));
    const knotItems = declared.map(name => byName.get(name)).filter(Boolean);
    const knotNames = new Set(knotItems.map(entry => entry.name));
    const others = list.filter(entry => !knotNames.has(entry.name));
    if (!knotItems.length) {
      host.innerHTML = list.map((entry, index) => figureFor(entry, index + 1)).join("");
      return;
    }
    host.innerHTML =
      `<h2 class="gallery-head" id="n-knots">Knotlike curves</h2>
    <p class="gallery-note">Your two pasted curves come first, tagged <strong>yours</strong>: <code>integer-105</code>
    and <code>integer-70</code>. Then the finds from the symmetric root walk, tagged 
    <strong>found</strong>, so the two sets can be compared row for row. <code>wave3</code>,
    <code>knot-6</code> and <code>knot-7</code> were already on the page. Under each name: the bend,
    the grid, and the meetings the walk measured with the copy that makes the lace.</p>`
      + knotItems.map((entry, index) => figureFor(entry, index + 1)).join("")
      + `<h2 class="gallery-head" id="n-rest">Everything else</h2>`
      + others.map((entry, index) => figureFor(entry, knotItems.length + index + 1)).join("");
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
