// Class V: a Tschirnhausen half, trimmed at both ends, mirrored and joined at the tip.
//
// The operator, 2026-11-23: "take a simple Tschirnhausen and cut it in half. slice 1/4 or less
// off each side and joint them again. this will make a design like a gothic arch, pointed at
// the top, with two curved parts that join".
//
// The Tschirnhausen cubic is x = t² − 3, y = t(t² − 3). Its half t ∈ [0, 2.4] runs from the
// node out to the tip. Joining two copies at the tip, mirrored, gives the arch: the apex is the
// tip, the feet are the trimmed node ends. Nothing here is stored; it is a design bed.

export const tschirnhausen = (t) => ({ x: t * t - 3, y: t * (t * t - 3) });
export const tangent = (t) => ({ x: 2 * t, y: 3 * t * t - 3 });

export function half({ from = 0, to = 2.4, samples = 300 } = {}) {
  const pts = [];
  for (let i = 0; i <= samples; i += 1) {
    const t = from + ((to - from) * i) / samples;
    pts.push({ ...tschirnhausen(t), t });
  }
  return pts;
}

// trim = the share of the half's parameter range taken off EACH end, 0 … 0.25
// Split a stored outline at its self-crossing — the Tschirnhausen's node — into the arm
// before the crossing and the arm after it. This is the "cut it in half" of the operator's
// instructions, done on the curve as it is stored rather than on the old parameter range.
export function nodeSplit(points) {
  const n = points.length;
  for (let i = 0; i < n - 1; i += 1) {
    for (let j = i + 3; j < n - 1; j += 1) {
      const a = points[i], b = points[i + 1], c = points[j], d = points[j + 1];
      const rx = b.x - a.x, ry = b.y - a.y;
      const qx = d.x - c.x, qy = d.y - c.y;
      const den = rx * qy - ry * qx;
      if (Math.abs(den) < 1e-12) continue;
      const t = ((c.x - a.x) * qy - (c.y - a.y) * qx) / den;
      const u = ((c.x - a.x) * ry - (c.y - a.y) * rx) / den;
      if (t < 0 || t > 1 || u < 0 || u > 1) continue;
      const cross = { x: a.x + t * rx, y: a.y + t * ry };
      return [points.slice(0, i + 1).concat([cross]), [cross].concat(points.slice(j + 1))];
    }
  }
  return null;
}

// The plain cut in half: the stored outline split at its own middle station, which is the
// operator's "cut it in half" on the curve as it now stands (the node-split gave only the short
// tip arm, and the arch came out narrow).
export function midSplit(points) {
  const n = points.length;
  if (n < 12) return null;
  const mid = Math.floor(n / 2);
  return [points.slice(0, mid + 1), points.slice(mid)];
}

// Type B, the shortcut: cut the curve at a point before the middle, drop the middle, and
// continue on the mirrored point on the other side. The cut point is the apex, and because the
// tangent is mirrored across the vertical through it, the two arms meet at a sharp angle: the
// first curve stops, the point is the nadir, the second part carries on.
export function shortcutArch(half, { cutFrac = 0.25, joinAt = "outer" } = {}) {
  if (!half || half.length < 12) return null;
  const i = Math.max(2, Math.round(half.length * Math.min(0.45, Math.max(0.02, cutFrac))));
  let pts = half.slice(cutFrac >= 0.5 ? half.length - i : i);
  if (pts.length < 4) return null;
  if (joinAt === "outer") pts = pts.slice().reverse();
  const apex = pts[0];
  const moved = pts.map((p) => ({ x: p.x - apex.x, y: p.y - apex.y }));
  const left = moved.map((p) => ({ x: -p.x, y: p.y }));
  return { left, right: moved, apex: { x: 0, y: 0 } };
}

// The arch from a stored half: trim a share off each end, mirror, join at the chosen end.
export function archOfHalf(half, { trim = 0.1, joinAt = "tip" } = {}) {
  if (!half || half.length < 10) return null;
  const cut = Math.max(1, Math.round(half.length * Math.min(0.25, trim)));
  let pts = half.slice(cut, half.length - cut);
  if (pts.length < 6) return null;
  const joinEnd = joinAt === "tip" ? pts[pts.length - 1] : pts[0];
  const moved = pts.map((p) => ({ x: p.x - joinEnd.x, y: p.y - joinEnd.y }));
  const left = moved.map((p) => ({ x: -p.x, y: p.y }));
  return { left, right: moved, apex: { x: 0, y: 0 } };
}

export function arch({ trim = 0.1, to = 2.4, joinAt = "tip", samples = 300 } = {}) {
  const span = to;
  const a = trim * span;
  const b = to - trim * span;
  if (b <= a) return null;
  const pts = [];
  for (let i = 0; i <= samples; i += 1) {
    const t = a + ((b - a) * i) / samples;
    pts.push({ ...tschirnhausen(t), t });
  }
  // the joining end is the rule's "tip" (t = b) or the node's side (t = a)
  const right = joinAt === "tip" ? pts : pts.slice().reverse();
  const apex = right[right.length - 1];
  const moved = right.map((p) => ({ x: p.x - apex.x, y: p.y - apex.y, t: p.t }));
  const left = moved.map((p) => ({ x: -p.x, y: p.y, t: p.t }));
  return { left, right: moved, apex: { x: 0, y: 0 } };
}

// the angle the two arms make at the apex, in degrees (180 is a straight join, 0 a cusp)
export function apexAngle(arch) {
  if (!arch) return null;
  const arm = (side) => {
    const a = side[side.length - 1];
    const b = side[side.length - 2];
    const dx = b.x - a.x, dy = b.y - a.y;
    const len = Math.hypot(dx, dy) || 1;
    return { x: dx / len, y: dy / len };
  };
  const r = arm(arch.right);
  const l = arm(arch.left);
  const dot = Math.max(-1, Math.min(1, r.x * l.x + r.y * l.y));
  return (Math.acos(dot) * 180) / Math.PI;
}

// the arch as one stroke: left foot up to the apex, then the right side down to its foot
export function archPath(built) {
  if (!built) return [];
  // both halves run foot -> apex; the arch is the left half, then the right half reversed
  return [...built.left, ...built.right.slice().reverse().slice(1)];
}

// side curves for a sampled outline, the plate's law: outside at the ask, inside capped at
// 0.9/kappa; a spike at the apex is rounded by dropping the far station to its neighbours
export function sides(points, widthPercent = 2, strength = 1.3) {
  const xs = points.map((p) => p.x), ys = points.map((p) => p.y);
  const size = Math.hypot(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)) || 1;
  const base = (widthPercent / 100) * size;
  const n = points.length;
  const normals = points.map((p, i) => {
    const a = points[Math.max(0, i - 1)], b = points[Math.min(n - 1, i + 1)];
    const tx = b.x - a.x, ty = b.y - a.y;
    const len = Math.hypot(tx, ty) || 1;
    return { x: -ty / len, y: tx / len };
  });
  const curvature = points.map((p, i) => {
    const a = points[Math.max(0, i - 1)], b = points[Math.min(n - 1, i + 1)];
    const v1 = { x: p.x - a.x, y: p.y - a.y };
    const v2 = { x: b.x - p.x, y: b.y - p.y };
    const l1 = Math.hypot(v1.x, v1.y) || 1, l2 = Math.hypot(v2.x, v2.y) || 1;
    const cross = (v1.x * v2.y - v1.y * v2.x) / (l1 * l2);
    const dot = (v1.x * v2.x + v1.y * v2.y) / (l1 * l2);
    const turn = Math.atan2(cross, dot);
    const step = 0.5 * (l1 + l2) || 1;
    return { kappa: Math.abs(turn / step), side: Math.sign(turn) };
  });
  // a cusp in the spine (the apex) closes the band: the distance tapers to zero there, so the
  // two sides meet at the point instead of crossing through it
  const turnAt = points.map((p, i) => {
    const a = points[Math.max(0, i - 1)], b = points[Math.min(n - 1, i + 1)];
    const v1 = { x: p.x - a.x, y: p.y - a.y };
    const v2 = { x: b.x - p.x, y: b.y - p.y };
    const l1 = Math.hypot(v1.x, v1.y) || 1, l2 = Math.hypot(v2.x, v2.y) || 1;
    const dot = (v1.x * v2.x + v1.y * v2.y) / (l1 * l2);
    return (Math.acos(Math.max(-1, Math.min(1, dot))) * 180) / Math.PI;
  });
  const cusps = turnAt.map((t, i) => (t > 60 ? i : -1)).filter((i) => i >= 0);
  const taperAt = (i) => {
    let factor = 1;
    for (const c of cusps) {
      const d = Math.abs(i - c);
      if (d < 14) factor = Math.min(factor, d / 14);
    }
    return factor;
  };
  const rail = (sign) => {
    const distances = points.map((p, i) => {
      const t = i / (n - 1);
      const bow = 1 + strength * 4 * t * (1 - t);
      let d = base * bow;
      if (curvature[i].side === sign && curvature[i].kappa > 1e-9) d = Math.min(d, 0.9 / curvature[i].kappa);
      return d * taperAt(i);
    });
    // a cusp turns the rail through a miter, which is far longer than the width; the median
    // distance is the honest width there, so anything past twice it is the miter, not the band
    const sorted = distances.slice().sort((a, b) => a - b);
    const median = sorted[Math.floor(sorted.length / 2)] || base;
    const limit = Math.max(median * 2, base);
    return points.map((p, i) => {
      const d = Math.min(distances[i], limit);
      return { x: p.x + sign * d * normals[i].x, y: p.y + sign * d * normals[i].y };
    });
  };
  const round = (line) => {
    const out = line.map((p) => ({ ...p }));
    for (let pass = 0; pass < 4; pass += 1) {
      for (let i = 1; i < out.length - 1; i += 1) {
        const a = out[i - 1], b = out[i], c = out[i + 1];
        const v1 = { x: b.x - a.x, y: b.y - a.y }, v2 = { x: c.x - b.x, y: c.y - b.y };
        const l1 = Math.hypot(v1.x, v1.y) || 1, l2 = Math.hypot(v2.x, v2.y) || 1;
        const dot = (v1.x * v2.x + v1.y * v2.y) / (l1 * l2);
        if ((Math.acos(Math.max(-1, Math.min(1, dot))) * 180) / Math.PI > 100) {
          out[i] = { x: (a.x + c.x) / 2, y: (a.y + c.y) / 2 };
        }
      }
    }
    return out;
  };
  // the two rails are drawn for the arch's inside and outside; each takes its own cap
  return { left: round(rail(-1)), right: round(rail(1)) };
}

export function sizeOf(arch) {
  const pts = [...arch.left, ...arch.right];
  const xs = pts.map((p) => p.x), ys = pts.map((p) => p.y);
  return {
    width: Math.max(...xs) - Math.min(...xs),
    height: Math.max(...ys) - Math.min(...ys),
    foot: Math.min(...ys),
    apexY: 0,
  };
}
