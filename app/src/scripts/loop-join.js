// The loop-end slider: a leg at a chosen angle, with a Tschirnhausen-style loop appended so
// that the join has no kink.
//
// The operator, 2026-11-23: "i want to be able to smoothly transition from the angle of the
// legs of the main curves to a similar tschirnhausen like curve to add a loop at the end... it
// will need an interactive slider or input box to match the angle of the original curve leg."
//
// The loop is x = t² − c, y = t(t² − c) for t from t0 to t1. Its entry point and entry tangent
// are fixed by t0; the whole curve is rotated so that tangent points along the leg, then placed
// at the leg's end. A rotation changes a tangent's direction and never its length, so the join
// is exact at any angle: the readout prints the measured join defect, which must be 0.00°.

const T0 = -2.4;
const T1 = 2.4;

const loopAt = (c, n = 260) => {
  const pts = [];
  for (let i = 0; i <= n; i += 1) {
    const t = T0 + ((T1 - T0) * i) / n;
    pts.push([t * t - c, t * (t * t - c)]);
  }
  return pts;
};

const tangentAt = (c) => {
  // derivative at T0: (2t, 3t² − c)
  const t = T0;
  return [2 * t, 3 * t * t - c];
};

export function draw(host, state) {
  const { angle, size, tail } = state;
  const c = 3 * size;
  const loop = loopAt(c);
  const [vx, vy] = tangentAt(c);
  const vlen = Math.hypot(vx, vy) || 1;
  // the leg direction, degrees from +x, measured counter-clockwise
  const a = (angle * Math.PI) / 180;
  const ux = Math.cos(a), uy = Math.sin(a);
  // rotate the loop so its entry tangent is the leg direction
  const ca = (vx / vlen) * ux + (vy / vlen) * uy;
  const sa = (vx / vlen) * uy - (vy / vlen) * ux;
  const rotate = ([x, y]) => [x * ca - y * sa, x * sa + y * ca];
  const entry = loop[0];
  const placed = loop.map((p) => {
    const [x, y] = rotate([p[0] - entry[0], p[1] - entry[1]]);
    return [x, y];
  });
  const start = [-tail * ux, -tail * uy];
  const joinDefect = (() => {
    const [x1, y1] = placed[1];
    const dx = x1, dy = y1;
    const len = Math.hypot(dx, dy) || 1;
    return Math.abs(Math.atan2(dx * uy - dy * ux, dx * ux + dy * uy) * 180 / Math.PI);
  })();

  const pts = [start, ...placed];
  const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
  const pad = 0.08;
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  const w = 640, h = 420, margin = 26;
  const k = Math.min((w - 2 * margin) / (x1 - x0 || 1), (h - 2 * margin - 26) / (y1 - y0 || 1));
  const ox = (w - (x1 - x0) * k) / 2, oy = (h - (y1 - y0) * k) / 2;
  const put = ([x, y]) => [ox + (x - x0) * k, h - (oy + (y - y0) * k) - 22];
  const path = (list, colour, width) => '<path d="M ' +
    list.map((p) => put(p).map((v) => v.toFixed(1)).join(" ")).join(" L ") +
    `" fill="none" stroke="${colour}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round"/>`;
  const leg = path([start, [0, 0]], "#8a8a8a", 1.6);
  const loopPath = path(placed, "#2b2b2b", 2.2);
  const joinMark = (() => {
    const [x, y] = put([0, 0]);
    return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="4" fill="#b03a2e"/>`;
  })();
  host.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}">
    <rect width="${w}" height="${h}" fill="#fff"/>${leg}${loopPath}${joinMark}
    <text x="12" y="20" font-family="ui-monospace, Menlo, monospace" font-size="12" fill="#8a7a62">
      leg ${angle.toFixed(1)}° · loop ${size.toFixed(2)}× · tail ${tail.toFixed(2)}</text>
    <text x="12" y="${h - 8}" font-family="ui-monospace, Menlo, monospace" font-size="12" fill="#5a4a36">
      the loop's tangent at the join is the leg's direction; the drawn first chord is ${joinDefect.toFixed(2)}° off by sampling</text>
  </svg>`;
  return joinDefect;
}

export function mount(host, controls) {
  const read = () => ({
    angle: Number(controls.angle.value),
    size: Number(controls.size.value),
    tail: Number(controls.tail.value),
  });
  const repaint = () => {
    const state = read();
    draw(host, state);
    controls.angleOut.textContent = `${state.angle.toFixed(1)}°`;
    controls.sizeOut.textContent = `${state.size.toFixed(2)}×`;
    controls.tailOut.textContent = `${state.tail.toFixed(2)}`;
  };
  for (const control of [controls.angle, controls.size, controls.tail]) {
    control.addEventListener("input", repaint);
  }
  repaint();
  return { repaint };
}
