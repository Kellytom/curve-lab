// The live tuning lab at /tune/.
//
// The maths is not reimplemented here. window.PlateMath is served from
// workbench/plate_math.js by /api/plate-math.js, the same file print_plates.mjs and the
// per-curve page load, so the picture here is the plate's own geometry.
//
// Nothing on this page is saved. The per-curve page (/tune/<uid>) is the one that writes.

const el = (id) => document.getElementById(id);

const state = { uid: "", widthPct: 6, plus: 2, minus: 2, profile: "bow", degrees: 0 };
const cache = new Map();

const number = (input, fallback) => {
  const value = Number(input.value);
  return Number.isFinite(value) ? value : fallback;
};

// one side's distance from the spine, station by station: min, max and how much it grows
function spread(spine, rail) {
  const widths = spine.map((point, i) => Math.hypot(point[0] - rail[i][0], point[1] - rail[i][1]));
  const min = Math.min(...widths);
  const max = Math.max(...widths);
  return { min, max, ratio: min > 0 ? max / min : Infinity };
}

// the drawing box: the curve's own extents, mapped so +y is up (the screen flip happens here)
function frame(paths) {
  const points = paths.flat();
  if (!points.length) return null;
  const xs = points.map((p) => p[0]);
  const ys = points.map((p) => p[1]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs);
  const y0 = Math.min(...ys), y1 = Math.max(...ys);
  const W = 760;
  const spanX = x1 - x0 || 1;
  const H = Math.max(240, Math.round((W * (y1 - y0)) / spanX));
  const k = (W * 0.96) / spanX;
  const ox = W / 2 - ((x0 + x1) / 2) * k;
  const oy = H / 2 + ((y0 + y1) / 2) * k;
  return {
    W, H,
    toPath: (line) => line
      .map(([x, y]) => `${(ox + x * k).toFixed(1)},${(oy - y * k).toFixed(1)}`)
      .join(" L"),
  };
}

function turn(paths, degrees) {
  if (!degrees) return paths;
  const a = (-degrees * Math.PI) / 180;
  const c = Math.cos(a), s = Math.sin(a);
  return paths.map((line) => line.map(([x, y]) => [x * c - y * s, x * s + y * c]));
}

function bandSvg(paths, box) {
  const [spine, plusRail, minusRail] = paths;
  if (paths.length < 3) {
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${box.W} ${box.H}">
      <rect width="${box.W}" height="${box.H}" fill="#fff"/>
      <path d="M${box.toPath(spine)}" fill="none" stroke="#2b2b2b" stroke-width="2.5"/>
    </svg>`;
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${box.W} ${box.H}">
    <rect width="${box.W}" height="${box.H}" fill="#fff"/>
    <path d="M${box.toPath([...spine, ...[...plusRail].reverse()])}Z" fill="#e2e2e2"/>
    <path d="M${box.toPath([...spine, ...[...minusRail].reverse()])}Z" fill="#8a8a8a"/>
    <path d="M${box.toPath(plusRail)}" fill="none" stroke="#3a3a3a" stroke-width="1.5"/>
    <path d="M${box.toPath(minusRail)}" fill="none" stroke="#3a3a3a" stroke-width="1.5"/>
    <path d="M${box.toPath(spine)}" fill="none" stroke="#2b2b2b" stroke-width="2.5"/>
  </svg>`;
}

function say(text) {
  el("lab-readout").textContent = text;
}

function draw() {
  const P = globalThis.PlateMath;
  const curve = cache.get(state.uid);
  if (!P || !curve) return;

  const preview = el("lab-preview");
  let paths = [];
  let used = null;
  let size = 0;

  if (curve.path) {
    paths = [curve.path];
    say("this curve is stored as a path: the plate prints the spine only, so the four " +
        "values do not change it. Pick a curve with speed rows to shape a band.");
    preview.innerHTML = bandSvg(turn(paths, state.degrees), frame(turn(paths, state.degrees)));
    return;
  }

  const row = {
    name: curve.name,
    speedX: curve.speedX,
    speedY: curve.speedY,
    width: { percent: state.widthPct },
    character: { plus: state.plus, minus: state.minus, profile: state.profile },
  };

  let group = null;
  try { group = P.group(row); } catch { group = null; }
  if (group && group.paths.length >= 3) {
    paths = group.paths.slice(0, 3);
    used = group.width;
    // the curve's own size (the diagonal of its box), so a distance reads as a share of it
    const xs = paths[0].map((point) => point[0]);
    const ys = paths[0].map((point) => point[1]);
    size = Math.hypot(
      Math.max(...xs) - Math.min(...xs),
      Math.max(...ys) - Math.min(...ys),
    ) || 1;
  } else if (group) {
    paths = [group.paths[0]];
  } else {
    paths = [P.spine(row.speedX, row.speedY, 400).map((s) => [s.x, s.y])];
  }

  const turned = turn(paths, state.degrees);
  const box = frame(turned);
  preview.innerHTML = box ? bandSvg(turned, box) : "<p>no drawable points at these values</p>";

  if (paths.length < 3) {
    say("at this width the rails would fold through themselves, so only the spine is drawn. " +
        "Lower the width %.");
    return;
  }

  const right = spread(paths[0], paths[1]);
  const left = spread(paths[0], paths[2]);
  const pct = (value) => (100 * value / size).toFixed(1);
  const side = (name, one) =>
    `${name} edge ${pct(one.min)} % → ${pct(one.max)} % of the curve's size ` +
    `(${one.ratio.toFixed(2)}× at the belly)`;
  const same = Math.abs(right.ratio - left.ratio) < 0.005 && Math.abs(right.max - left.max) < 1e-6;
  const cut = used < state.widthPct
    ? ` Band width ${used.toFixed(1)} % — asked ${state.widthPct} %, cut so the band cannot ` +
      "fold over itself."
    : ` Band width ${used.toFixed(1)} %.`;

  say(`${side("Right", right)}. ${same ? "Left edge the same" : side("Left", left)}.` + cut);
}

async function load(uid) {
  if (!cache.has(uid)) {
    const response = await fetch(`/api/curve/${uid}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`curve ${uid}: ${response.status}`);
    cache.set(uid, await response.json());
  }
  return cache.get(uid);
}

async function start() {
  const controls = {
    curve: el("lab-curve"),
    widthPct: el("lab-width"),
    plus: el("lab-plus"),
    minus: el("lab-minus"),
    profile: el("lab-profile"),
    degrees: el("lab-degrees"),
  };
  if (!controls.curve) return;

  const sync = () => {
    state.widthPct = number(controls.widthPct, 6);
    state.plus = number(controls.plus, 2);
    state.minus = number(controls.minus, 2);
    state.profile = controls.profile.value;
    state.degrees = number(controls.degrees, 0);
    el("lab-width-out").value = String(state.widthPct);
    el("lab-plus-out").value = String(state.plus);
    el("lab-minus-out").value = String(state.minus);
  };

  for (const control of [controls.widthPct, controls.plus, controls.minus, controls.profile, controls.degrees]) {
    control.addEventListener("input", () => { sync(); draw(); });
  }

  const show = async () => {
    try {
      await load(state.uid);
      draw();
    } catch (error) {
      say(`${state.uid} could not be loaded: ${error.message}`);
    }
  };

  controls.curve.addEventListener("change", async () => {
    state.uid = controls.curve.value;
    await show();
  });

  state.uid = controls.curve.value;
  sync();
  await show();
}

start();
