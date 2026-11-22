// Plate maths in JS: the saved curve, its character rails, the caps that close
// the ribbon, and the cross/leaf/arch/frame designs.
//
// This is the one implementation. It loads as a plain script (globalThis.PlateMath)
// or through require from Node, so the export and the page share it.
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.PlateMath = factory();
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const STEPS = 700;
  const DEFAULT_WIDTH = 1.5;
  const DEFAULT_PLUS = 2;
  const DEFAULT_MINUS = 2;
  const DEFAULT_PROFILE = "bow";
  const WIDTH_FLOOR = 0.2;
  const FOLD_LIMIT = 0.9;

  const value = (poly, t) => {
    let total = 0;
    for (let i = poly.length - 1; i >= 0; i -= 1) total = total * t + Number(poly[i]);
    return total;
  };

  const multiply = (a, b) => {
    const out = new Array(a.length + b.length - 1).fill(0);
    a.forEach((x, i) => b.forEach((y, j) => { out[i + j] += x * y; }));
    return out;
  };
  const add = (a, b) => {
    const out = new Array(Math.max(a.length, b.length)).fill(0);
    a.forEach((x, i) => { out[i] += x; });
    b.forEach((x, i) => { out[i] += x; });
    return out;
  };
  const scalePoly = (a, k) => a.map((x) => x * k);
  const derivative = (a) => a.slice(1).map((x, i) => x * (i + 1));

  function spine(u, v, steps = STEPS) {
    const out = [];
    let x = 0, y = 0;
    for (let i = 0; i <= steps; i += 1) {
      const t = i / steps;
      const p = value(u, t), q = value(v, t);
      const speed2 = p * p + q * q;
      const tx = speed2 > 1e-12 ? (p * p - q * q) / speed2 : 1;
      const ty = speed2 > 1e-12 ? (2 * p * q) / speed2 : 0;
      out.push({ t, x, y, tx, ty, nx: -ty, ny: tx });
      if (i < steps) {
        const tm = (i + 0.5) / steps;
        const pm = value(u, tm), qm = value(v, tm);
        x += (pm * pm - qm * qm) / steps;
        y += (2 * pm * qm) / steps;
      }
    }
    return out;
  }

  function curvaturePeak(u, v, samples = 400) {
    const u2 = multiply(u, u), v2 = multiply(v, v), uv = multiply(u, v);
    const x1 = add(u2, scalePoly(v2, -1));
    const y1 = scalePoly(uv, 2);
    const x2 = scalePoly(add(multiply(u, derivative(u)), scalePoly(multiply(v, derivative(v)), -1)), 2);
    const y2 = scalePoly(add(multiply(derivative(u), v), multiply(u, derivative(v))), 2);
    let peak = 0;
    for (let i = 0; i <= samples; i += 1) {
      const t = i / samples;
      const a = value(x1, t), b = value(y1, t);
      const speed = Math.hypot(a, b);
      if (speed < 1e-12) return Infinity;
      const cross = a * value(y2, t) - b * value(x2, t);
      peak = Math.max(peak, Math.abs(cross) / speed ** 3);
    }
    return peak;
  }

  const profileAt = (name, t) => {
    if (name === "s") return 8 * t * (1 - t) * (1 - 2 * t);
    if (name === "taper") return 6.75 * t * t * (1 - t);
    return 4 * t * (1 - t);
  };

  // The fold guard must see the bow, not only the base width. The rail's offset at a
  // station is distance * (1 + strength * profile(t)), and the fold is that offset times
  // the curvature there. A global bow factor over-cut the reference band; this looks at
  // the station where the two actually meet (2026-11-21, c-0001 at 1 % measured 1.28 × the
  // fold limit because the guard ignored the plus).
  function curvatureWorst(u, v, plus, minus, profileName, samples = 400) {
    const u2 = multiply(u, u), v2 = multiply(v, v), uv = multiply(u, v);
    const x1 = add(u2, scalePoly(v2, -1));
    const y1 = scalePoly(uv, 2);
    const x2 = scalePoly(add(multiply(u, derivative(u)), scalePoly(multiply(v, derivative(v)), -1)), 2);
    const y2 = scalePoly(add(multiply(derivative(u), v), multiply(u, derivative(v))), 2);
    const clamp = (value) => Math.max(-0.95, Math.min(4, Number(value) || 0));
    const strengths = [clamp(plus), clamp(minus)];
    let worst = 0;
    for (let i = 0; i <= samples; i += 1) {
      const t = i / samples;
      const a = value(x1, t), b = value(y1, t);
      const speed = Math.hypot(a, b);
      if (speed < 1e-12) return Infinity;
      const cross = a * value(y2, t) - b * value(x2, t);
      const curvature = Math.abs(cross) / speed ** 3;
      const bow = profileAt(profileName, t);
      const factor = Math.max(1, ...strengths.map((strength) => 1 + strength * bow));
      worst = Math.max(worst, curvature * factor);
    }
    return worst;
  }

  function integrate(start, u, v, steps, eps = 0, bump = null) {
    let x = start[0], y = start[1];
    const points = [[x, y]];
    for (let i = 0; i < steps; i += 1) {
      const t = (i + 0.5) / steps;
      let p = value(u, t), q = value(v, t);
      if (eps) {
        const a = eps * bump(t);
        const turned = [p - a * q, q + a * p];
        p = turned[0]; q = turned[1];
      }
      x += (p * p - q * q) / steps;
      y += (2 * p * q) / steps;
      points.push([x, y]);
    }
    return points;
  }

  function rail(samples, u, v, distance, sign, strength, profileName, shear, steps = STEPS) {
    const startSpine = samples[0];
    const start = [startSpine.x + sign * distance * startSpine.nx,
                   startSpine.y + sign * distance * startSpine.ny];
    const flat = integrate(start, u, v, steps);
    const bump = (t) => profileAt(profileName, t);
    const turned = integrate(start, u, v, steps, 0.08 * strength, bump);
    return samples.map((s, i) => {
      const t = i / steps;
      const parallel = [s.x + sign * distance * s.nx + shear * t * s.tx,
                        s.y + sign * distance * s.ny + shear * t * s.ty];
      const weight = 4 * t * (1 - t);
      return [parallel[0] + weight * (turned[i][0] - flat[i][0]),
              parallel[1] + weight * (turned[i][1] - flat[i][1])];
    });
  }

  const bbox = (points) => {
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    points.forEach(([x, y]) => {
      if (x < x0) x0 = x; if (y < y0) y0 = y;
      if (x > x1) x1 = x; if (y > y1) y1 = y;
    });
    return [x0, y0, x1, y1];
  };

  // A character rail: the offset is not a constant. Each side carries its own law,
  // width * (1 + strength * profile(t)), so the right and left bands differ at the same
  // station and each one breathes along the curve. This is what makes it a character rail
  // rather than a parallel offset.
  function sideRail(samples, distance, sign, strength, profileName, shear = 0, steps = STEPS) {
    const strengthClamped = Math.max(-0.95, Math.min(4, Number(strength) || 0));
    return samples.map((s, i) => {
      const t = i / steps;
      const d = distance * (1 + strengthClamped * profileAt(profileName, t));
      return [s.x + sign * d * s.nx + shear * t * s.tx,
              s.y + sign * d * s.ny + shear * t * s.ty];
    });
  }

  function rawGroup(row) {
    const u = row.speedX, v = row.speedY;
    const samples = spine(u, v);
    const size = Math.hypot(...(([a, b, c, d]) => [c - a, d - b])(
      (() => { const s = samples.map((p) => [p.x, p.y]); return bbox(s); })()));
    let width = Number((row.width || {}).percent ?? DEFAULT_WIDTH);
    const character = row.character || {};
    const plus = Number(character.plus ?? DEFAULT_PLUS);
    const minus = Number(character.minus ?? DEFAULT_MINUS);
    let profileName = ["bow", "s", "taper"].includes(character.profile)
      ? character.profile : DEFAULT_PROFILE;
    const shear = Number(row.shear ?? 0);
    const peak = curvaturePeak(u, v);
    // The guard's job is "the largest width that does not fold", not "halve until it fits".
    // Halving made the band jump DOWN as the slider went up: on c-0002, 2.2 % became 1.15 %
    // at the next step, and again at 4.6 % (2026-11-21). This is the same rule —
    // distance × peak ≤ FOLD_LIMIT — solved directly, so the band moves with the slider.
    const worst = curvatureWorst(u, v, plus, minus, profileName);
    const safePercent = worst === 0
      ? Infinity
      : Number.isFinite(worst) && worst > 0
        ? Math.floor((FOLD_LIMIT / worst) * 10000 / size) / 100
        : 0;
    width = Math.min(width, safePercent);
    let distance = width >= WIDTH_FLOOR ? (width / 100) * size : 0;
    const spinePoints = samples.map((s) => [s.x, s.y]);
    const rails = [];
    let note;
    if (distance > 0) {
      rails.push(sideRail(samples, distance, 1, plus, profileName, shear, samples.length - 1));
      rails.push(sideRail(samples, distance, -1, minus, profileName, shear, samples.length - 1));
      note = `character rails · width ${width}% · ${profileName} ${plus}/${minus}`;
    } else {
      width = 0;
      distance = 0;
      note = `rail folds at the ${WIDTH_FLOOR}% floor · spine only`;
    }
    const paths = [spinePoints, ...rails];
    if (rails.length) {
      rails.forEach((r) => {
        paths.push([spinePoints[0], r[0]]);
        paths.push([spinePoints[spinePoints.length - 1], r[r.length - 1]]);
      });
    }
    return { name: row.name, paths, spine: spinePoints, width, profileName,
             plus, minus, distance, fold: distance * worst, note };
  }

  const rotate = (points, deg) => {
    const a = (deg * Math.PI) / 180, c = Math.cos(a), s = Math.sin(a);
    return points.map(([x, y]) => [x * c - y * s, x * s + y * c]);
  };
  const translate = (points, dx, dy) => points.map(([x, y]) => [x + dx, y + dy]);
  const scale = (points, k) => points.map(([x, y]) => [x * k, y * k]);
  const scaleY = (points, k) => points.map(([x, y]) => [x, y * k]);
  const flipY = (points) => points.map(([x, y]) => [x, y === 0 ? 0 : -y]);
  const legOf = (points) => (Math.atan2(points[1][1] - points[0][1], points[1][0] - points[0][0]) * 180) / Math.PI;
  const endLegOf = (points) => (Math.atan2(points[points.length - 1][1] - points[points.length - 2][1],
                                            points[points.length - 1][0] - points[points.length - 2][0]) * 180) / Math.PI;

  function group(row) {
    const raw = rawGroup(row);
    const angle = (Math.atan2(raw.spine[raw.spine.length - 1][1] - raw.spine[0][1],
                              raw.spine[raw.spine.length - 1][0] - raw.spine[0][0]) * 180) / Math.PI;
    let paths = raw.paths.map((path) => rotate(path, -angle));
    const origin = paths[0][0];
    paths = paths.map((path) => translate(path, -origin[0], -origin[1]));
    let spinePath = paths[0];
    const middle = spinePath.slice(1, -1).reduce((sum, p) => sum + p[1], 0)
      / Math.max(1, spinePath.length - 2);
    if (middle < 0) {
      paths = paths.map(flipY);
      spinePath = paths[0];
    }
    const chord = Math.hypot(spinePath[spinePath.length - 1][0] - spinePath[0][0],
                             spinePath[spinePath.length - 1][1] - spinePath[0][1]);
    return { name: raw.name, paths, spine: spinePath, chord,
             startLeg: legOf(spinePath), endLeg: endLegOf(spinePath),
             width: raw.width, profileName: raw.profileName, note: raw.note };
  }

  function prepared(item, chord, leg) {
    let paths = item.paths.map((path) => scale(path, chord / item.chord));
    let spinePath = paths[0];
    if (legOf(spinePath) < 0) {
      paths = paths.map(flipY);
      spinePath = paths[0];
    }
    if (leg !== null && leg !== undefined) {
      const factor = Math.tan((leg * Math.PI) / 180) / Math.tan((legOf(spinePath) * Math.PI) / 180);
      paths = paths.map((path) => scaleY(path, factor));
      spinePath = paths[0];
    }
    return { paths, spine: spinePath, chord };
  }

  function cross(item, side, leg) {
    const preparedItem = prepared(item, side, leg);
    return [["south", 0, 0, 0], ["east", side, 0, 90],
            ["north", side, side, 180], ["west", 0, side, 270]]
      .map(([name, ox, oy, deg]) => ({ name, paths: preparedItem.paths.map(
        (path) => translate(rotate(path, deg), ox, oy)) }));
  }

  function leaf(a, b, leg) {
    const length = a.chord;
    const top = prepared(b, length, leg);
    const bottom = prepared(a, length, leg);
    return [{ name: "bottom", paths: bottom.paths.map(flipY) },
            { name: "top", paths: top.paths }];
  }

  // Two curves end to end, not flipped: b is translated so its first point is
  // a's last point, and each keeps its own natural legs. The corner is the
  // difference between a's end heading and b's start heading — a design
  // decision, printed, not hidden.
  function chain(a, b) {
    const first = prepared(a, a.chord, null);
    const second = prepared(b, b.chord, null);
    const end = first.spine[first.spine.length - 1];
    const start = second.spine[0];
    const moved = second.paths.map((path) =>
      translate(path, end[0] - start[0], end[1] - start[1]));
    let join = endLegOf(first.spine) - legOf(second.spine);
    while (join > 180) join -= 360;
    while (join < -180) join += 360;
    return { items: [{ name: "first", paths: first.paths },
                     { name: "second", paths: moved }],
             join, end: first.spine[first.spine.length - 1] };
  }

  function frame(a, b, perWidth, perHeight, leg, pattern, alternate) {
    const letters = (pattern || "a").replace(/[^ab]/g, "") || "a";
    const length = a.chord;
    const width = perWidth * length, height = perHeight * length;
    const preparedA = prepared(a, length, leg);
    const preparedB = b ? prepared(b, length, leg) : preparedA;
    const edges = [["south", 0, 0, 0, perWidth], ["east", width, 0, 90, perHeight],
                   ["north", width, height, 180, perWidth], ["west", 0, height, 270, perHeight]];
    const out = [];
    edges.forEach(([name, ox, oy, deg, count]) => {
      for (let copy = 0; copy < count; copy += 1) {
        const letter = letters[copy % letters.length];
        const shape = letter === "b" ? preparedB : preparedA;
        let paths = shape.paths.map((path) => translate(path, copy * length, 0));
        if (alternate && copy % 2) paths = paths.map(flipY);
        out.push({ name, copy, letter, paths: paths.map((path) => translate(rotate(path, deg), ox, oy)) });
      }
    });
    return out;
  }

  function design(spec, rows) {
    const a = group(rows[spec.curve]);
    const b = spec.curveB ? group(rows[spec.curveB]) : a;
    const leg = spec.leg === null || spec.leg === undefined ? null : Number(spec.leg);
    let central, centralNote;
    if (spec.form === "cross") {
      central = cross(a, a.chord, leg); centralNote = "cross";
    } else if (spec.form === "leaf") {
      central = leaf(a, b, leg); centralNote = "leaf";
    } else if (spec.form === "chain") {
      const joined = chain(a, b);
      central = joined.items;
      centralNote = `chain · join ${joined.join.toFixed(1)}°`;
    } else if (spec.form === "arch") {
      central = [{ name: "arch", paths: prepared(a, a.chord, leg).paths }];
      centralNote = "arch";
    } else {
      throw new Error(`unknown form ${spec.form}`);
    }
    let border = [];
    if (spec.frame) {
      border = frame(a, spec.curveB ? b : null, Number(spec.frame.perWidth),
                     Number(spec.frame.perHeight), leg, spec.pattern, spec.alternate);
    }
    let centralPaths = central.flatMap((item) => item.paths);
    if (border.length) {
      const cbox = bbox(centralPaths.flat());
      const fbox = bbox(border.flatMap((item) => item.paths).flat());
      const dx = ((fbox[0] + fbox[2]) - (cbox[0] + cbox[2])) / 2;
      const dy = ((fbox[1] + fbox[3]) - (cbox[1] + cbox[3])) / 2;
      centralPaths = centralPaths.map((path) => translate(path, dx, dy));
    }
    const paths = centralPaths.concat(border.flatMap((item) => item.paths));
    const note = [centralNote, spec.frame
      ? `${spec.frame.perWidth}×${spec.frame.perHeight} frame`
      : null, `${spec.curve} · character rails`].filter(Boolean).join(" · ");
    return { paths, bbox: bbox(paths.flat()), note };
  }

  const strokeFor = (widthPt) => Math.max(1, 0.0035 * widthPt);

  // Symmetry, measured on the spine: a half turn about the midpoint, or a
  // mirror about the vertical line through it. `none` is the honest answer for
  // an S curve; the tolerance is 0.5% of the bounding-box diagonal.
  function symmetry(row, samples = 400) {
    const points = spine(row.speedX, row.speedY, samples).map((s) => [s.x, s.y]);
    const mid = points[samples / 2];
    const box = bbox(points);
    const size = Math.hypot(box[2] - box[0], box[3] - box[1]) || 1;
    let half = 0;
    let mirror = 0;
    for (let i = 0; i <= samples; i += 1) {
      const a = points[i];
      const b = points[samples - i];
      half = Math.max(half, Math.hypot(a[0] + b[0] - 2 * mid[0], a[1] + b[1] - 2 * mid[1]));
      mirror = Math.max(mirror, Math.abs(a[0] + b[0] - 2 * mid[0]),
                        Math.abs(a[1] - b[1]));
    }
    const tolerance = 0.005 * size;
    const kind = half <= tolerance ? "half-turn" : mirror <= tolerance ? "mirror" : "none";
    return { kind, symmetric: kind !== "none", half: half / size, mirror: mirror / size };
  }

  // ---- a path curve: refine the walk, then the same character law ----------------- //

  // One segment of a centripetal Catmull-Rom spline through p0..p3. Centripetal (alpha 0.5)
  // is used rather than uniform: uniform overshoots when the stored points are unevenly
  // spaced, and a path's points are uneven.
  function catmullRom(p0, p1, p2, p3, t) {
    const knot = (a, b) => Math.pow(Math.hypot(b[0] - a[0], b[1] - a[1]), 0.5) || 1e-9;
    const t0 = 0, t1 = knot(p0, p1), t2 = t1 + knot(p1, p2), t3 = t2 + knot(p2, p3);
    const at = t1 + t * (t2 - t1);
    const mix = (a, b, ta, tb) => [
      ((tb - at) * a[0] + (at - ta) * b[0]) / (tb - ta),
      ((tb - at) * a[1] + (at - ta) * b[1]) / (tb - ta),
    ];
    const a1 = mix(p0, p1, t0, t1), a2 = mix(p1, p2, t1, t2), a3 = mix(p2, p3, t2, t3);
    return mix(mix(a1, a2, t0, t2), mix(a2, a3, t1, t3), t1, t2);
  }

  // A stored path is a short polyline (39 to 901 points), so drawn as segments it shows the
  // facets. Walk it as a spline through the stored points and sample at a fixed step. The
  // stored points stay exact; everything between them is approximate, and the plate is a
  // drawing of the curve, not the curve itself.
  function refinePath(points, step) {
    const input = (points || []).filter((p) => Number.isFinite(p[0]) && Number.isFinite(p[1]));
    // a repeated stored point makes a zero-length knot interval, and the centripetal
    // parameterisation then divides by zero and cusps; one copy of each point is enough
    const pts = [];
    for (const p of input) {
      const last = pts[pts.length - 1];
      if (!last || Math.hypot(p[0] - last[0], p[1] - last[1]) > 1e-9) pts.push([p[0], p[1]]);
    }
    if (pts.length < 2) return pts.map((p) => [p[0], p[1]]);
    // the end tangents are reflected rather than clamped: clamping repeats an end point,
    // which is the same zero-length knot the duplicate filter just removed
    const at = (i) => {
      if (i < 0) return [2 * pts[0][0] - pts[1][0], 2 * pts[0][1] - pts[1][1]];
      if (i >= pts.length) {
        const n = pts.length - 1;
        return [2 * pts[n][0] - pts[n - 1][0], 2 * pts[n][1] - pts[n - 1][1]];
      }
      return pts[i];
    };
    const span = Number(step) > 0 ? Number(step) : 0;
    const out = [];
    for (let i = 0; i < pts.length - 1; i += 1) {
      const p0 = at(i - 1), p1 = at(i), p2 = at(i + 1), p3 = at(i + 2);
      const chord = Math.hypot(p2[0] - p1[0], p2[1] - p1[1]) || 1;
      const count = span ? Math.max(1, Math.ceil(chord / span)) : 1;
      for (let k = 0; k < count; k += 1) out.push(catmullRom(p0, p1, p2, p3, k / count));
    }
    out.push([pts[pts.length - 1][0], pts[pts.length - 1][1]]);
    return out;
  }

  // A ceiling that changes no faster than `slope` per unit of arc length. The path rail's
  // cap used to be one station at a time, so it jumped wherever the curvature did: on
  // c-0273 the distance moved 4 % of the curve's size in one step and the edge made 105
  // sharp turns. This is the same rule — d ≤ half the local radius — applied continuously.
  function pinchCap(room, arc, slope = 0.25) {
    const cap = room.slice();
    for (let i = 1; i < cap.length; i += 1) {
      cap[i] = Math.min(cap[i], cap[i - 1] + slope * (arc[i] - arc[i - 1]));
    }
    for (let i = cap.length - 2; i >= 0; i -= 1) {
      cap[i] = Math.min(cap[i], cap[i + 1] + slope * (arc[i + 1] - arc[i]));
    }
    return cap;
  }

  // The rail on a path: the refined walk, then the same law as a row curve —
  // distance = base * (1 + strength * profile(u)), u by arclength, one sign per side.
  // The offset is held below half the local radius by a continuous cap, so a corner
  // yields a thin rail instead of a fold, and the edge never jumps between stations.
  function pathGroup(points, options) {
    const opts = options || {};
    const widthPercent = Number(opts.widthPercent ?? 1.5);
    const plus = Number(opts.plus ?? 2);
    const minus = Number(opts.minus ?? 2);
    const profile = ["bow", "s", "taper"].includes(opts.profile) ? opts.profile : "bow";
    const stored = (points || []).filter((p) => Number.isFinite(p[0]) && Number.isFinite(p[1]));
    if (stored.length < 3) return null;

    const box = bbox(stored);
    const size = Math.hypot(box[2] - box[0], box[3] - box[1]) || 1;
    const base = (widthPercent / 100) * size;
    // about 1600 samples across the curve's own size: 2 px apart on a 3000 px plate
    const walk = refinePath(stored, size / 1600);

    const arc = [0];
    for (let i = 1; i < walk.length; i += 1) {
      arc.push(arc[i - 1] + Math.hypot(walk[i][0] - walk[i - 1][0], walk[i][1] - walk[i - 1][1]));
    }
    const total = arc[arc.length - 1] || 1;

    const tangents = walk.map((p, i) => {
      const before = walk[Math.max(0, i - 1)];
      const after = walk[Math.min(walk.length - 1, i + 1)];
      const tx = after[0] - before[0], ty = after[1] - before[1];
      const len = Math.hypot(tx, ty) || 1;
      return [tx / len, ty / len];
    });
    // The one character law, also on a stored path: distance x (1 + strength x
    // profile(t)), capped by the fold guard (distance x curvature <= 0.9). The local
    // pinch cap was tried and reverted (docs/SIDE-CURVES.md, section 2): it is a second
    // construction, and at the same saved number it drew a band about four times too wide.
    const clamp = (value) => Math.max(-0.95, Math.min(4, Number(value) || 0));
    const strengths = [clamp(plus), clamp(minus)];
    const curvature = walk.map((p, i) => {
      const a = tangents[Math.max(0, i - 1)];
      const b = tangents[Math.min(walk.length - 1, i + 1)];
      const step = arc[Math.min(walk.length - 1, i + 1)] - arc[Math.max(0, i - 1)];
      const turn = Math.abs(Math.atan2(a[0] * b[1] - a[1] * b[0], a[0] * b[0] + a[1] * b[1]));
      return turn > 1e-12 && step > 1e-12 ? turn / step : 0;
    });
    let worst = 0;
    walk.forEach((p, i) => {
      const bow = profileAt(profile, arc[i] / total);
      const factor = Math.max(...strengths.map((strength) => Math.abs(1 + strength * bow)), 1e-9);
      worst = Math.max(worst, factor * curvature[i]);
    });
    const safeBase = worst === 0 ? Infinity : (Number.isFinite(worst) ? FOLD_LIMIT / worst : 0);
    const usedBase = Math.min(base, safeBase);
    const usedPercent = (usedBase / size) * 100;
    const railFor = (side, strength) => walk.map((p, i) => {
      const [tx, ty] = tangents[i];
      const want = usedBase * (1 + clamp(strength) * profileAt(profile, arc[i] / total));
      const d = side * want;
      return [p[0] - ty * d, p[1] + tx * d];
    });

    const paths = [walk, railFor(1, plus), railFor(-1, minus)];
    const note = `path rails · width ${usedPercent.toFixed(2)}% of ${widthPercent}% · ${profile} ${plus}/${minus}` +
      ` · ${walk.length} points from ${stored.length} stored · fold ${(usedBase * worst).toFixed(2)}`;
    return { paths, bbox: bbox(paths.flat()), width: usedPercent, note };
  }

  // ---- the band may break at a sharp turn (display only) ---------------------
  //
  // Operator, 2026-11-22: "break the band at each sharp turn". A constant-width band
  // folds where the curve turns tighter than the width; the drawing lifts the band across
  // that stretch and starts it again after, at the asked width. The equation is untouched:
  // the record stays the continuous speed pair (or path), and the break is derived from the
  // curvature at render time. It is stored nowhere and is not part of the curve.
  function curvatureProfile(u, v, samples) {
    const u2 = multiply(u, u), v2 = multiply(v, v), uv = multiply(u, v);
    const x1 = add(u2, scalePoly(v2, -1));
    const y1 = scalePoly(uv, 2);
    const x2 = scalePoly(add(multiply(u, derivative(u)), scalePoly(multiply(v, derivative(v)), -1)), 2);
    const y2 = scalePoly(add(multiply(derivative(u), v), multiply(u, derivative(v))), 2);
    return samples.map((s) => {
      const a = value(x1, s.t), b = value(y1, s.t);
      const speed = Math.hypot(a, b);
      if (speed < 1e-12) return Infinity;
      return Math.abs(a * value(y2, s.t) - b * value(x2, s.t)) / speed ** 3;
    });
  }

  // Where the asked width and its bow fit, the band is drawn; where they would fold, the pen
  // lifts. A run shorter than 4 % of the curve is not a band, and a curve with no run at all
  // returns null so the caller keeps the uniform guard it had.
  function splitGroup(row, options) {
    const opts = options || {};
    const u = row.speedX, v = row.speedY;
    if (!Array.isArray(u) || !Array.isArray(v)) return null;
    const samples = spine(u, v, opts.samples || 1400);
    const points = samples.map((s) => [s.x, s.y]);
    const [x0, y0, x1, y1] = bbox(points);
    const size = Math.hypot(x1 - x0, y1 - y0) || 1;
    const character = row.character || {};
    const widthPercent = Number((row.width || {}).percent ?? DEFAULT_WIDTH);
    const plus = Number(character.plus ?? DEFAULT_PLUS);
    const minus = Number(character.minus ?? DEFAULT_MINUS);
    const profile = ["bow", "s", "taper"].includes(character.profile) ? character.profile : DEFAULT_PROFILE;
    const clamp = (value) => Math.max(-0.95, Math.min(4, Number(value) || 0));
    const strengths = [clamp(plus), clamp(minus)];
    const base = (widthPercent / 100) * size;
    const safe = curvatureProfile(u, v, samples)
      .map((k) => (Number.isFinite(k) && k > 0 ? FOLD_LIMIT / k : Infinity));
    // The offset each side would carry at a station, including its bow.
    const factorAt = (i) => Math.max(
      ...strengths.map((k) => Math.abs(1 + k * profileAt(profile, samples[i].t))), 1e-9);
    // A run is a stretch where the band at `baseDistance` fits: distance x curvature <= 0.9.
    const runsFor = (baseDistance, from = 0, to = samples.length - 1, minLength = 3) => {
      const out = [];
      let i = from;
      while (i <= to) {
        if (!(safe[i] >= baseDistance * factorAt(i) * 1.02)) { i += 1; continue; }
        let j = i;
        while (j + 1 <= to && safe[j + 1] >= baseDistance * factorAt(j + 1) * 1.02) j += 1;
        if (j - i + 1 >= minLength) out.push([i, j]);
        i = j + 1;
      }
      return out;
    };
    const medianOf = (values) => {
      const sorted = values.slice().sort((a, b) => a - b);
      return sorted[Math.floor(sorted.length / 2)] || 1;
    };
    // Bands are normalised to the target gap (operator, 2026-11-22: "check the thickness").
    // Each run solves its own base so the drawn gap is the target there, which matters
    // because the bow is small near the curve's ends and a run there would otherwise be thin.
    const target = Number(opts.targetGapPercent || 0);
    const minRun = Math.max(3, Math.round(samples.length * 0.02));
    const baseForRun = (a, b) => {
      if (!target) return base;
      const factors = [];
      for (let i = a; i <= b; i += 1) factors.push(factorAt(i));
      return ((target / 100) * size) / medianOf(factors);
    };
    const all = [];
    for (let i = 0; i < samples.length; i += 1) all.push(i);
    let runs = runsFor(baseForRun(0, samples.length - 1), 0, samples.length - 1, minRun)
      .map(([a, b]) => [a, b, baseForRun(a, b)]);
    if (target && runs.length) {
      // Two passes: cut the parent at its base, then re-solve the base of each child (its own
      // bow median differs) and cut again. Without the second solve an end run stays at the
      // curve-wide base and draws thin.
      const cut = (list) => {
        const out = [];
        for (const [a, b, runBase] of list) {
          for (const [c, d] of runsFor(runBase, a, b, Math.max(3, Math.round(samples.length * 0.01)))) {
            out.push([c, d, baseForRun(c, d)]);
          }
        }
        return out;
      };
      runs = cut(cut(runs));
    }
    if (!runs.length) return null;
    const segments = runs.map(([a, b, runBase]) => {
      const part = samples.slice(a, b + 1);
      const spinePart = part.map((s) => [s.x, s.y]);
      // The band closes onto the spine at each break, over about an eighth of the run, so the
      // lifted pen leaves a tapered end rather than a straight slash across the band. The
      // curve's own ends are not breaks: there the band keeps its base gap.
      const ramp = Math.min(Math.max(3, Math.round(part.length * 0.08)), Math.max(1, Math.floor(part.length / 5)));
      const taperStart = a > 0;
      const taperEnd = b < samples.length - 1;
      const edgeAt = (i) => Math.min(1,
        taperStart ? i / ramp : 1,
        taperEnd ? (part.length - 1 - i) / ramp : 1,
      );
      const railFor = (sign, strength) => part.map((s, i) => {
        const d = runBase * (1 + clamp(strength) * profileAt(profile, s.t)) * edgeAt(i);
        return [s.x + sign * d * s.nx, s.y + sign * d * s.ny];
      });
      const right = railFor(1, plus);
      const left = railFor(-1, minus);
      const last = spinePart.length - 1;
      return {
        spine: spinePart,
        rails: [right, left,
          [spinePart[0], right[0]], [spinePart[last], right[last]],
          [spinePart[0], left[0]], [spinePart[last], left[last]]],
        t: part.map((s) => s.t),
        from: part[0].t,
        to: part[part.length - 1].t,
      };
    });
    const note = `band broken at ${segments.length} run(s) · ${widthPercent}% ${profile} ${plus}/${minus}`;
    return { name: row.name, segments, width: widthPercent, profileName: profile, note };
  }

  // The same break for a stored path: the same refinement, tangents and arc as pathGroup,
  // but the band is drawn at the asked width wherever it fits and lifted across the rest,
  // tapering onto the spine at each break. Display only, like splitGroup.
  function splitPath(points, options) {
    const opts = options || {};
    const widthPercent = Number(opts.widthPercent ?? DEFAULT_WIDTH);
    const plus = Number(opts.plus ?? DEFAULT_PLUS);
    const minus = Number(opts.minus ?? DEFAULT_MINUS);
    const profile = ["bow", "s", "taper"].includes(opts.profile) ? opts.profile : DEFAULT_PROFILE;
    const stored = (points || []).filter((p) => Number.isFinite(p[0]) && Number.isFinite(p[1]));
    if (stored.length < 3) return null;
    const box = bbox(stored);
    const size = Math.hypot(box[2] - box[0], box[3] - box[1]) || 1;
    const base = (widthPercent / 100) * size;
    const walk = refinePath(stored, size / 1600);
    const arc = [0];
    for (let i = 1; i < walk.length; i += 1) {
      arc.push(arc[i - 1] + Math.hypot(walk[i][0] - walk[i - 1][0], walk[i][1] - walk[i - 1][1]));
    }
    const total = arc[arc.length - 1] || 1;
    const tangents = walk.map((p, i) => {
      const before = walk[Math.max(0, i - 1)];
      const after = walk[Math.min(walk.length - 1, i + 1)];
      const tx = after[0] - before[0], ty = after[1] - before[1];
      const len = Math.hypot(tx, ty) || 1;
      return [tx / len, ty / len];
    });
    const curvature = walk.map((p, i) => {
      const a = tangents[Math.max(0, i - 1)];
      const b = tangents[Math.min(walk.length - 1, i + 1)];
      const step = arc[Math.min(walk.length - 1, i + 1)] - arc[Math.max(0, i - 1)];
      const turn = Math.abs(Math.atan2(a[0] * b[1] - a[1] * b[0], a[0] * b[0] + a[1] * b[1]));
      return turn > 1e-12 && step > 1e-12 ? turn / step : 0;
    });
    const clamp = (value) => Math.max(-0.95, Math.min(4, Number(value) || 0));
    const strengths = [clamp(plus), clamp(minus)];
    const factorAt = (i) => Math.max(
      ...strengths.map((k) => Math.abs(1 + k * profileAt(profile, arc[i] / total))), 1e-9);
    const safeAt = (i) => (curvature[i] > 0 ? FOLD_LIMIT / curvature[i] : Infinity);
    const runsFor = (baseDistance, from = 0, to = walk.length - 1, minLength = 3) => {
      const out = [];
      let i = from;
      while (i <= to) {
        if (!(safeAt(i) >= baseDistance * factorAt(i) * 1.02)) { i += 1; continue; }
        let j = i;
        while (j + 1 <= to && safeAt(j + 1) >= baseDistance * factorAt(j + 1) * 1.02) j += 1;
        if (j - i + 1 >= minLength) out.push([i, j]);
        i = j + 1;
      }
      return out;
    };
    const medianOf = (values) => {
      const sorted = values.slice().sort((a, b) => a - b);
      return sorted[Math.floor(sorted.length / 2)] || 1;
    };
    const target = Number(opts.targetGapPercent || 0);
    const baseForRun = (a, b) => {
      if (!target) return base;
      const factors = [];
      for (let i = a; i <= b; i += 1) factors.push(factorAt(i));
      return ((target / 100) * size) / medianOf(factors);
    };
    const minRun = Math.max(3, Math.round(walk.length * 0.02));
    let runs = runsFor(baseForRun(0, walk.length - 1), 0, walk.length - 1, minRun)
      .map(([a, b]) => [a, b, baseForRun(a, b)]);
    if (target && runs.length) {
      const refined = [];
      for (const [a, b, runBase] of runs) {
        for (const [c, d] of runsFor(runBase, a, b, Math.max(3, Math.round(walk.length * 0.01)))) {
          refined.push([c, d, runBase]);
        }
      }
      runs = refined;
    }
    if (!runs.length) return null;
    const segments = runs.map(([a, b, runBase]) => {
      const part = walk.slice(a, b + 1);
      const spinePart = part.map((p) => [p[0], p[1]]);
      const ramp = Math.min(Math.max(3, Math.round(part.length * 0.08)), Math.max(1, Math.floor(part.length / 5)));
      const taperStart = a > 0;
      const taperEnd = b < walk.length - 1;
      const edgeAt = (k) => Math.min(1,
        taperStart ? k / ramp : 1,
        taperEnd ? (part.length - 1 - k) / ramp : 1);
      const railFor = (side, strength) => part.map((p, k) => {
        const u = (arc[a + k] || 0) / total;
        const want = runBase * (1 + clamp(strength) * profileAt(profile, u)) * edgeAt(k);
        const [tx, ty] = tangents[a + k];
        const d = side * want;
        return [p[0] - ty * d, p[1] + tx * d];
      });
      const right = railFor(1, plus);
      const left = railFor(-1, minus);
      const last = spinePart.length - 1;
      return {
        spine: spinePart,
        rails: [right, left,
          [spinePart[0], right[0]], [spinePart[last], right[last]],
          [spinePart[0], left[0]], [spinePart[last], left[last]]],
        from: (arc[a] || 0) / total,
        to: (arc[b] || 0) / total,
      };
    });
    return { segments, width: widthPercent, note: `path band broken at ${segments.length} run(s)` };
  }

  return { value, spine, curvaturePeak, curvatureWorst, rail, sideRail, refinePath, bbox, group, prepared, pathGroup,
           splitGroup, splitPath, curvatureProfile, profileAt,
           cross, leaf, chain, frame, design, rotate, translate, scale, scaleY,
           flipY, strokeFor, symmetry };
});
