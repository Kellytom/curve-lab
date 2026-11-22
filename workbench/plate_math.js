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

  // Curvature and its side, station by station: { kappa, side }, where side = +1 means the
  // centre of curvature is on the + normal side (so the + rail is the inside there).
  function curvatureStations(u, v, samples) {
    const u2 = multiply(u, u), v2 = multiply(v, v), uv = multiply(u, v);
    const x1 = add(u2, scalePoly(v2, -1));
    const y1 = scalePoly(uv, 2);
    const x2 = scalePoly(add(multiply(u, derivative(u)), scalePoly(multiply(v, derivative(v)), -1)), 2);
    const y2 = scalePoly(add(multiply(derivative(u), v), multiply(u, derivative(v))), 2);
    return samples.map((sample) => {
      const t = sample.t;
      const a = value(x1, t), b = value(y1, t);
      const speed = Math.hypot(a, b);
      if (speed < 1e-12) return { kappa: Infinity, side: 0 };
      const cross = a * value(y2, t) - b * value(x2, t);
      return { kappa: Math.abs(cross) / speed ** 3, side: Math.sign(cross) };
    });
  }

  // Which side folds is a geometric question, not a width question: only the rail on the
  // inside of a turn can fold, because it runs toward the centre of curvature. The outside
  // rail moves away from the centre and cannot. The operator, 2026-11-22: "figure out which
  // side is buckling and make that thin, and the outer rail can be wider ... the curve on
  // the inner side should be close to the spine, the curve on the outside can be wider."
  //
  // The inner side at a station is the sign of the signed curvature: the unit normal used by
  // the rails is the tangent turned +90°, and a positive cross product puts the centre of
  // curvature on that side. So `side = +1` measures only the stations where the + rail is
  // inside, and `side = -1` only those where the - rail is inside.
  function curvatureWorstSide(u, v, side, strength, profileName, samples = 400) {
    const u2 = multiply(u, u), v2 = multiply(v, v), uv = multiply(u, v);
    const x1 = add(u2, scalePoly(v2, -1));
    const y1 = scalePoly(uv, 2);
    const x2 = scalePoly(add(multiply(u, derivative(u)), scalePoly(multiply(v, derivative(v)), -1)), 2);
    const y2 = scalePoly(add(multiply(derivative(u), v), multiply(u, derivative(v))), 2);
    const clamped = Math.max(-0.95, Math.min(4, Number(strength) || 0));
    let worst = 0;
    for (let i = 0; i <= samples; i += 1) {
      const t = i / samples;
      const a = value(x1, t), b = value(y1, t);
      const speed = Math.hypot(a, b);
      if (speed < 1e-12) return Infinity;
      const cross = a * value(y2, t) - b * value(x2, t);
      if (Math.sign(cross) !== side) continue;
      const curvature = Math.abs(cross) / speed ** 3;
      const factor = Math.abs(1 + clamped * profileAt(profileName, t));
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
    const askedPercent = width;
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
    // The inner side of a turn is the one that folds; the outer side moves away from the
    // centre of curvature and cannot. So the band is cut per station: each rail keeps the
    // asked width, except where it is on the inside of a tight turn, where it stops at the
    // largest safe distance and hugs the spine. No break, no second construction — the same
    // character law with a ceiling (operator, 2026-11-22: "the curve on the inner side should
    // be close to the spine, the curve on the outside can be wider").
    const stations = curvatureStations(u, v, samples);
    const clamp = (value) => Math.max(-0.95, Math.min(4, Number(value) || 0));
    const base = (askedPercent / 100) * size;
    const safeAt = (i) => (stations[i].kappa > 0 && Number.isFinite(stations[i].kappa)
      ? FOLD_LIMIT / stations[i].kappa
      : (stations[i].kappa === Infinity ? 0 : Infinity));
    let wasCut = false;
    const arc = [0];
    for (let i = 1; i < samples.length; i += 1) {
      arc.push(arc[i - 1] + Math.hypot(samples[i].x - samples[i - 1].x, samples[i].y - samples[i - 1].y));
    }
    // A corner's offset is a miter: the rail shoots out along the bisector and back, which
    // reads as a bevel on the outside edge. Smoothing the normal over a few stations rounds
    // that corner without moving the spine or the distance law.
    const smoothNormals = samples.map((s, i) => {
      let nx = 0, ny = 0;
      for (let k = -2; k <= 2; k += 1) {
        const n = samples[Math.max(0, Math.min(samples.length - 1, i + k))];
        nx += n.nx; ny += n.ny;
      }
      const len = Math.hypot(nx, ny) || 1;
      return [nx / len, ny / len];
    });
    const railFor = (sign, strength) => {
      const room = samples.map((s, i) => {
        const factor = 1 + clamp(strength) * profileAt(profileName, s.t);
        const want = base * factor;
        if (stations[i].side !== sign) return want;
        if (safeAt(i) < want) { wasCut = true; return safeAt(i); }
        return want;
      });
      // Row curvature is analytic and smooth, so the ceiling needs no smoothing here: a
      // slope limit would drag a short tight bend's thin width along the whole curve.
      return samples.map((s, i) => [s.x + sign * room[i] * smoothNormals[i][0],
        s.y + sign * room[i] * smoothNormals[i][1]]);
    };
    const rails = [];
    let note;
    const drawn = [];
    const railPlus = railFor(1, plus);
    const railMinus = railFor(-1, minus);
    const gapPlus = railPlus.map((p, i) => Math.hypot(p[0] - samples[i].x, p[1] - samples[i].y));
    const gapMinus = railMinus.map((p, i) => Math.hypot(p[0] - samples[i].x, p[1] - samples[i].y));
    if (Math.max(...gapPlus) > 1e-12 || Math.max(...gapMinus) > 1e-12) {
      rails.push(railPlus, railMinus);
      drawn.push(...gapPlus, ...gapMinus);
      const biggest = Math.max(...drawn) / size * 100;
      const smallest = Math.min(...drawn) / size * 100;
      note = `character rails · ${smallest.toFixed(2)}% to ${biggest.toFixed(2)}% of the size` +
        ` · ${profileName} ${plus}/${minus}`;
    } else {
      note = "the rail has no safe width at all (infinite curvature) · spine only";
    }
    width = rails.length ? Math.min(...drawn) / size * 100 : 0;
    const foldAt = (d, i, side) => {
      const kappa = stations[i].kappa;
      if (Number.isNaN(kappa)) return 0;
      if (!Number.isFinite(kappa)) return d > 0 ? Infinity : 0;
      return stations[i].side === side ? d * kappa : 0;
    };
    const worstPlus = Math.max(...gapPlus.map((d, i) => foldAt(d, i, 1)));
    const worstMinus = Math.max(...gapMinus.map((d, i) => foldAt(d, i, -1)));
    const spinePoints = samples.map((s) => [s.x, s.y]);
    const paths = [spinePoints, ...rails];
    if (rails.length) {
      rails.forEach((r) => {
        paths.push([spinePoints[0], r[0]]);
        paths.push([spinePoints[spinePoints.length - 1], r[r.length - 1]]);
      });
    }
    // The tuner's note: how far the inside had to come in.
    const widest = rails.length ? Math.max(...drawn) / size * 100 : 0;
    const buckles = rails.length > 0 && wasCut;
    const buckleNote = buckles
      ? `the band would buckle above that — the inside is cut to ${width.toFixed(2)}%, ` +
        `the outside is ${widest.toFixed(2)}%`
      : null;
    return { name: row.name, paths, spine: spinePoints, width, asked: askedPercent,
             widthPlus: rails.length ? Math.max(...gapPlus) / size * 100 : 0,
             widthMinus: rails.length ? Math.max(...gapMinus) / size * 100 : 0,
             buckles, buckleNote, profileName,
             plus, minus,
             fold: (() => {
               const value = Math.max(worstPlus, worstMinus);
               return Number.isFinite(value) ? value : 0;
             })(), note };
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
             width: raw.width, asked: raw.asked, widthPlus: raw.widthPlus,
             widthMinus: raw.widthMinus, fold: raw.fold, buckles: raw.buckles,
             buckleNote: raw.buckleNote, profileName: raw.profileName, note: raw.note };
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
    // Per side, as on a row curve: only the inside of a turn can fold.
    const signed = walk.map((p, i) => {
      const a = tangents[Math.max(0, i - 1)];
      const b = tangents[Math.min(walk.length - 1, i + 1)];
      const step = arc[Math.min(walk.length - 1, i + 1)] - arc[Math.max(0, i - 1)];
      const turn = Math.atan2(a[0] * b[1] - a[1] * b[0], a[0] * b[0] + a[1] * b[1]);
      return {
        curvature: step > 1e-12 ? Math.abs(turn) / step : 0,
        side: Math.sign(turn),
      };
    });
    // Per station, as on a row curve: the inside of a turn is capped at the local safe
    // distance, the outside keeps the asked width.
    let wasCut = false;
    // Round the miter at a corner: a smoothed tangent spreads the outside rail's spike over
    // a few stations instead of shooting out and back (the "bevel" the operator saw).
    const smoothTangents = tangents.map((t, i) => {
      let tx = 0, ty = 0;
      for (let k = -6; k <= 6; k += 1) {
        const n = tangents[Math.max(0, Math.min(tangents.length - 1, i + k))];
        tx += n[0]; ty += n[1];
      }
      const len = Math.hypot(tx, ty) || 1;
      return [tx / len, ty / len];
    });
    const railFor = (side, strength) => {
      const room = walk.map((p, i) => {
        const factor = 1 + clamp(strength) * profileAt(profile, arc[i] / total);
        const want = base * factor;
        if (signed[i].side !== side || !(signed[i].curvature > 0)) return want;
        const safe = FOLD_LIMIT / signed[i].curvature;
        if (safe < want) { wasCut = true; return safe; }
        return want;
      });
      // The sampled curvature is noisy, so the path band keeps the continuous ceiling
      // (register 45) — at a slope of 1 per unit arc, so a tight bend does not drag the
      // whole curve thin.
      const distance = pinchCap(room, arc, 0.4);
      return walk.map((p, i) => {
        const [tx, ty] = smoothTangents[i];
        const d = side * distance[i];
        return [p[0] - ty * d, p[1] + tx * d];
      });
    };
    const railPlus = railFor(1, plus);
    const railMinus = railFor(-1, minus);
    const gapOf = (rail) => rail.map((p, i) => Math.hypot(p[0] - walk[i][0], p[1] - walk[i][1]));
    const gapPlus = gapOf(railPlus);
    const gapMinus = gapOf(railMinus);
    const drawnGaps = [...gapPlus, ...gapMinus];
    const usedPercentPlus = (Math.max(...gapPlus) / size) * 100;
    const usedPercentMinus = (Math.max(...gapMinus) / size) * 100;
    const usedPercent = (Math.min(...drawnGaps) / size) * 100;

    const paths = [walk, railPlus, railMinus];
    const widest = (Math.max(...drawnGaps) / size) * 100;
    const note = `path rails · ${usedPercent.toFixed(2)}% to ${widest.toFixed(2)}% of the size` +
      ` · ${profile} ${plus}/${minus} · ${walk.length} points from ${stored.length} stored`;
    const buckles = wasCut;
    const buckleNote = buckles
      ? `the band would buckle above that — the inside is cut to ${usedPercent.toFixed(2)}%, ` +
        `the outside is ${widest.toFixed(2)}%`
      : null;
    return { paths, bbox: bbox(paths.flat()), width: usedPercent, asked: widthPercent,
             widthPlus: usedPercentPlus, widthMinus: usedPercentMinus,
             buckles, buckleNote, note };
  }

  // Where a drawn rail crosses itself. Those are the future cut points: a rail that closes a
  // loop on itself has to be cut there before it can be a printed side curve. Non-adjacent
  // segments only, and a cell grid keeps it near linear for a 1600-point rail.
  function selfIntersections(points, cell = 0) {
    const pts = (points || []).filter((p) => Number.isFinite(p[0]) && Number.isFinite(p[1]));
    if (pts.length < 4) return [];
    const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
    const size = Math.hypot(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)) || 1;
    const step = cell > 0 ? cell : size / 64;
    const buckets = new Map();
    const keyOf = (x, y) => `${Math.floor(x / step)},${Math.floor(y / step)}`;
    for (let i = 0; i < pts.length - 1; i += 1) {
      const [x0, y0] = pts[i], [x1, y1] = pts[i + 1];
      const xa = Math.floor(Math.min(x0, x1) / step), xb = Math.floor(Math.max(x0, x1) / step);
      const ya = Math.floor(Math.min(y0, y1) / step), yb = Math.floor(Math.max(y0, y1) / step);
      for (let gx = xa; gx <= xb; gx += 1) {
        for (let gy = ya; gy <= yb; gy += 1) {
          const key = `${gx},${gy}`;
          if (!buckets.has(key)) buckets.set(key, []);
          buckets.get(key).push(i);
        }
      }
    }
    const seen = new Set();
    const hits = [];
    const cross = (a, b, c, d) => {
      const r = [b[0] - a[0], b[1] - a[1]];
      const q = [d[0] - c[0], d[1] - c[1]];
      const den = r[0] * q[1] - r[1] * q[0];
      if (Math.abs(den) < 1e-12) return null;
      const t = ((c[0] - a[0]) * q[1] - (c[1] - a[1]) * q[0]) / den;
      const u = ((c[0] - a[0]) * r[1] - (c[1] - a[1]) * r[0]) / den;
      if (t <= 1e-9 || t >= 1 - 1e-9 || u <= 1e-9 || u >= 1 - 1e-9) return null;
      return [a[0] + t * r[0], a[1] + t * r[1]];
    };
    for (const list of buckets.values()) {
      for (let i = 0; i < list.length; i += 1) {
        for (let j = i + 1; j < list.length; j += 1) {
          const a = list[i], b = list[j];
          if (Math.abs(a - b) < 2) continue;       // sharing a station is not a crossing
          const pair = a < b ? `${a}:${b}` : `${b}:${a}`;
          if (seen.has(pair)) continue;
          seen.add(pair);
          const hit = cross(pts[a], pts[a + 1], pts[b], pts[b + 1]);
          if (hit) hits.push({ x: hit[0], y: hit[1], a, b });
        }
      }
    }
    // one dot per crossing place, not per segment pair
    const merged = [];
    for (const hit of hits) {
      if (!merged.some((m) => Math.hypot(m.x - hit.x, m.y - hit.y) < size * 0.002)) merged.push(hit);
    }
    return merged;
  }

  return { value, spine, curvaturePeak, curvatureWorst, rail, sideRail, refinePath, bbox, group, prepared, pathGroup,
           selfIntersections,
           profileAt,
           cross, leaf, chain, frame, design, rotate, translate, scale, scaleY,
           flipY, strokeFor, symmetry };
});
