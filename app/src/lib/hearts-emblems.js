// The two hearts: the Sacred Heart and the Immaculate Heart, built from curves.
//
// The heart is the classical parametric heart, x = 16 sin³t, y = 13 cos t − 5 cos 2t −
// 2 cos 3t − cos 4t, sampled — the project's own heart (the implicit one) is not rational, so
// a heart here is a drawing, never an exact record, and the page says so.
//
// The emblems are the traditional ones:
//   Sacred Heart   — heart, flame above, a cross rising from the flame, rays around
//   Immaculate     — heart pierced by a sword, roses at the foot, rays around
// Every part is a parameter, so proportions can be judged rather than guessed.

export function heartPoints(n = 400) {
  const pts = [];
  for (let i = 0; i <= n; i += 1) {
    const t = (2 * Math.PI * i) / n;
    const x = 16 * Math.sin(t) ** 3;
    const y = 13 * Math.cos(t) - 5 * Math.cos(2 * t) - 2 * Math.cos(3 * t) - Math.cos(4 * t);
    pts.push({ x: x / 16, y: y / 16 });
  }
  return pts;
}

// a flame: a teardrop, widest low, drawn as two mirrored Bézier halves
export function flamePoints(size = 0.25, n = 80) {
  const out = [];
  const height = size * 2.2;
  for (let i = 0; i <= n; i += 1) {
    const t = i / n;
    // width profile: 0 at the base, widest at 0.35, 0 at the tip, with a slight lean
    const w = Math.sin(Math.PI * Math.min(1, t / 0.75)) * size;
    out.push({ x: -w * 0.5, y: t * height });
  }
  for (let i = n; i >= 0; i -= 1) {
    const t = i / n;
    const w = Math.sin(Math.PI * Math.min(1, t / 0.75)) * size;
    out.push({ x: w * 0.5, y: t * height });
  }
  return out;
}

// the cross above the flame: an upright and a bar, in relative units
export function crossPaths(height = 0.32, bar = 0.18) {
  const shaft = [
    { x: -bar * 0.09, y: 0 }, { x: -bar * 0.09, y: height },
    { x: bar * 0.09, y: height }, { x: bar * 0.09, y: 0 }, { x: -bar * 0.09, y: 0 },
  ];
  const armY = height * 0.66;
  const arms = [
    { x: -bar * 0.45, y: armY - bar * 0.09 }, { x: -bar * 0.45, y: armY + bar * 0.09 },
    { x: bar * 0.45, y: armY + bar * 0.09 }, { x: bar * 0.45, y: armY - bar * 0.09 },
    { x: -bar * 0.45, y: armY - bar * 0.09 },
  ];
  return [shaft, arms];
}

// rays from a centre: alternating long and short, as the emblems have
export function rayPaths(count = 16, r0 = 0.55, r1 = 0.95, centre = { x: 0, y: 0.05 }) {
  const out = [];
  for (let i = 0; i < count; i += 1) {
    const angle = (2 * Math.PI * i) / count - Math.PI / 2;
    const outer = i % 2 ? r0 + (r1 - r0) * 0.68 : r1;
    const len = Math.abs(Math.cos(angle)) < 0.35 ? outer * 0.92 : outer;
    out.push([
      { x: centre.x + r0 * Math.cos(angle), y: centre.y + r0 * Math.sin(angle) },
      { x: centre.x + len * Math.cos(angle), y: centre.y + len * Math.sin(angle) },
    ]);
  }
  return out;
}

// the sword of the Immaculate Heart: a blade through the heart, hilt above
export function swordPaths(angleDeg = -28, length = 1.5) {
  const a = (angleDeg * Math.PI) / 180;
  const dir = { x: Math.cos(a), y: Math.sin(a) };
  const mid = { x: 0, y: 0.05 };
  const half = length / 2;
  const tip = { x: mid.x - dir.x * half, y: mid.y - dir.y * half };
  const pommel = { x: mid.x + dir.x * half, y: mid.y + dir.y * half };
  const normal = { x: -dir.y, y: dir.x };
  const w = 0.035;
  const blade = [
    tip,
    { x: mid.x + normal.x * w, y: mid.y + normal.y * w },
    { x: mid.x + dir.x * half * 0.55 + normal.x * w, y: mid.y + dir.y * half * 0.55 + normal.y * w },
    { x: mid.x + dir.x * half * 0.55 - normal.x * w, y: mid.y + dir.y * half * 0.55 - normal.y * w },
    { x: mid.x - normal.x * w, y: mid.y - normal.y * w },
    tip,
  ];
  const guard = [
    { x: mid.x + dir.x * half * 0.5 - normal.x * 0.16, y: mid.y + dir.y * half * 0.5 - normal.y * 0.16 },
    { x: mid.x + dir.x * half * 0.5 + normal.x * 0.16, y: mid.y + dir.y * half * 0.5 + normal.y * 0.16 },
    pommel,
  ];
  return [blade, guard];
}

// a rose: a small circle with five petals around it
export function rosePaths(radius = 0.09, centre = { x: -0.35, y: -0.62 }, petals = 5) {
  const ring = [];
  for (let i = 0; i <= 40; i += 1) {
    const a = (2 * Math.PI * i) / 40;
    ring.push({ x: centre.x + radius * Math.cos(a), y: centre.y + radius * Math.sin(a) });
  }
  const petalsOut = [];
  for (let i = 0; i < petals; i += 1) {
    const a = (2 * Math.PI * i) / petals;
    petalsOut.push([
      { x: centre.x + radius * 0.4 * Math.cos(a), y: centre.y + radius * 0.4 * Math.sin(a) },
      { x: centre.x + radius * 1.25 * Math.cos(a), y: centre.y + radius * 1.25 * Math.sin(a) },
    ]);
  }
  return { ring, petals: petalsOut };
}


// ---- the letters under the hearts -------------------------------------------------------
//
// A decorative C and M, drawn as outlines rather than set in a font: two concentric strokes
// for the C (a ribbon with a thin inner line) and a pointed M with serifs. They are drawings,
// like the rest of the emblem, and scale with the heart.

export function letterC(size = 1, centre = { x: 0, y: 0 }) {
  const outer = [];
  const inner = [];
  const r = 0.5 * size;
  const open = Math.PI / 4;           // the mouth opens to the right
  for (let i = 0; i <= 60; i += 1) {
    const a = open + ((2 * Math.PI - 2 * open) * i) / 60;
    outer.push({ x: centre.x + r * Math.cos(a), y: centre.y + r * Math.sin(a) });
    const ri = r * 0.72;
    inner.push({ x: centre.x + ri * Math.cos(a), y: centre.y + ri * Math.sin(a) });
  }
  // the two terminals, so the ribbon closes into a letter rather than an arc
  const capTop = [outer[0], inner[0]];
  const capBottom = [outer[outer.length - 1], inner[inner.length - 1]];
  return [outer, inner, capTop, capBottom];
}

export function letterM(size = 1, centre = { x: 0, y: 0 }) {
  const h = size;
  const w = size * 0.95;
  const left = centre.x - w / 2;
  const right = centre.x + w / 2;
  const top = centre.y + h / 2;
  const bottom = centre.y - h / 2;
  const serif = size * 0.13;
  const stroke = [
    { x: left, y: bottom },
    { x: left, y: top },
    { x: centre.x, y: top - h * 0.45 },
    { x: right, y: top },
    { x: right, y: bottom },
  ];
  const feet = [
    [{ x: left - serif, y: bottom }, { x: left + serif, y: bottom }],
    [{ x: right - serif, y: bottom }, { x: right + serif, y: bottom }],
  ];
  const tops = [
    [{ x: left - serif * 0.7, y: top }, { x: left + serif * 0.7, y: top }],
    [{ x: right - serif * 0.7, y: top }, { x: right + serif * 0.7, y: top }],
  ];
  return [stroke, ...feet, ...tops];
}
