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
    let distance = (width / 100) * size;
    while (Math.abs(distance) * peak > FOLD_LIMIT && width > WIDTH_FLOOR) {
      width /= 2;
      distance = (width / 100) * size;
    }
    const spinePoints = samples.map((s) => [s.x, s.y]);
    const rails = [];
    let note;
    if (Math.abs(distance) * peak <= FOLD_LIMIT) {
      rails.push(sideRail(samples, distance, 1, plus, profileName, shear, samples.length - 1));
      rails.push(sideRail(samples, distance, -1, minus, profileName, shear, samples.length - 1));
      note = `character rails · width ${width}% · ${profileName} ${plus}/${minus}`;
    } else {
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
             plus, minus, distance, fold: Math.abs(distance) * peak, note };
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

  // ---- rails from a path --------------------------------------------------- //
  // A curve stored as a path has no u, v, so the rail is built from the polyline itself:
  // the local normal at each station, scaled by the width, then shaped by the character —
  // the same plus / minus / profile law, applied to arclength instead of to t.
  function pathGroup(points, options) {
    const opts = options || {};
    const widthPercent = Number(opts.widthPercent ?? 6);
    const plus = Number(opts.plus ?? 2);
    const minus = Number(opts.minus ?? 2);
    const profile = ["bow", "s", "taper"].includes(opts.profile) ? opts.profile : "bow";
    const pts = (points || []).filter((p) => Number.isFinite(p[0]) && Number.isFinite(p[1]));
    if (pts.length < 3) return null;

    const box = bbox(pts);
    const size = Math.hypot(box[2] - box[0], box[3] - box[1]) || 1;
    const base = (widthPercent / 100) * size;

    const arc = [0];
    for (let i = 1; i < pts.length; i += 1) {
      arc.push(arc[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
    }
    const total = arc[arc.length - 1] || 1;

    const shape = (u, strength) => {
      if (profile === "s") return 1 + strength * (2 * u - 1) * 0.5;
      if (profile === "taper") return 1 - strength * u * 0.6;
      return 1 + strength * Math.sin(Math.PI * u) * 0.5;   // bow
    };

    // the offset is capped by the local segment length: past that the rail folds over
    // itself at a tight turn and the band fills the wrong side
    const railFor = (side, strength) => pts.map((p, i) => {
      const before = pts[Math.max(0, i - 1)];
      const after = pts[Math.min(pts.length - 1, i + 1)];
      let tx = after[0] - before[0], ty = after[1] - before[1];
      const len = Math.hypot(tx, ty) || 1;
      tx /= len; ty /= len;
      // the room left before the rail folds is the local radius of curvature: a segment
      // length divided by the turn it makes. A gentle stretch gives a big radius and the
      // full width; a corner gives a small one and a thin rail.
      const segA = Math.hypot(p[0] - before[0], p[1] - before[1]);
      const segB = Math.hypot(after[0] - p[0], after[1] - p[1]);
      const ax = (p[0] - before[0]) / (segA || 1), ay = (p[1] - before[1]) / (segA || 1);
      const bx = (after[0] - p[0]) / (segB || 1), by = (after[1] - p[1]) / (segB || 1);
      const turn = Math.abs(Math.atan2(ax * by - ay * bx, ax * bx + ay * by));
      const radius = Math.min(segA || Infinity, segB || Infinity) / Math.max(turn, 1e-6);
      const room = 0.5 * radius;
      const d = Math.min(base * shape(arc[i] / total, strength), room) * side;
      return [p[0] - ty * d, p[1] + tx * d];
    });

    const paths = [pts, railFor(1, plus), railFor(-1, minus)];
    return { paths, bbox: bbox(paths.flat()),
             note: `path rails · width ${widthPercent}% · ${profile} ${plus}/${minus}` };
  }

  return { value, spine, curvaturePeak, rail, sideRail, bbox, group, prepared, pathGroup,
           cross, leaf, chain, frame, design, rotate, translate, scale, scaleY,
           flipY, strokeFor, symmetry };
});
