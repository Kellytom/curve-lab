// The drawing shared by /tune/ and /tune/<uid>.
//
// The maths is not here: window.PlateMath is served from workbench/plate_math.js by
// /api/plate-math, the one file the printed plate also loads. This module only asks it
// for the spine and two rails, draws them, and says what the numbers mean.
//
// Nothing is saved here. /tune/<uid> is the page with the save buttons.

const number = (value, fallback) => (Number.isFinite(Number(value)) ? Number(value) : fallback);

// one side's distance from the spine, station by station: min, max and how much it grows
function spread(spine, rail) {
  const widths = spine.map((point, i) => Math.hypot(point[0] - rail[i][0], point[1] - rail[i][1]));
  const min = Math.min(...widths);
  const max = Math.max(...widths);
  return { min, max, ratio: min > 0 ? max / min : Infinity };
}

// the drawing box: the curve's own extents, mapped so +y is up (the screen flip is here)
export function frame(paths) {
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

// the desk's turn is clockwise on screen, so the model turns the other way
function turn(paths, degrees) {
  if (!degrees) return paths;
  const a = (-degrees * Math.PI) / 180;
  const c = Math.cos(a), s = Math.sin(a);
  return paths.map((line) => line.map(([x, y]) => [x * c - y * s, x * s + y * c]));
}

export function bandSvg(paths, box) {
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

// ask the plate maths for the spine and its two rails. Every stored outline takes the
// plate's rail branch: the same character law over the refined walk, with the same
// continuous fold cap, so the page and the plate draw one picture.
function drawing(P, curve, values) {
  if (curve.path) {
    if (P.pathGroup) {
      const group = P.pathGroup(curve.path, {
        widthPercent: values.widthPct, plus: values.plus,
        minus: values.minus, profile: values.profile,
      });
      if (group && group.paths.length >= 3) {
        return { paths: group.paths, kind: "stored", stored: curve.path.length,
                 width: group.width, buckles: group.buckles, buckleNote: group.buckleNote };
      }
    }
    return { paths: [curve.path], kind: "path-spine", stored: curve.path.length };
  }

  const row = {
    name: curve.name,
    speedX: curve.speedX || [],
    speedY: curve.speedY || [],
    width: { percent: values.widthPct },
    character: { plus: values.plus, minus: values.minus, profile: values.profile },
  };
  let group = null;
  try { group = P.group(row); } catch { group = null; }
  if (group && group.paths.length >= 3) {
    return { paths: group.paths.slice(0, 3), kind: "rows", width: group.width,
             buckles: group.buckles, buckleNote: group.buckleNote };
  }
  const spine = P.spine(row.speedX, row.speedY, 400).map((s) => [s.x, s.y]);
  return { paths: [spine], kind: "spine" };
}

function readout(drawn, values, paths) {
  if (drawn.kind === "path-spine") {
    return "this curve is stored as a path; the plate prints the spine only until its " +
      "rail is settled";
  }
  if (paths.length < 3) {
    return "at this width the rails would fold through themselves, so only the spine is " +
      "drawn. Lower the width %.";
  }

  const spine = paths[0];
  const size = (() => {
    const xs = spine.map((point) => point[0]);
    const ys = spine.map((point) => point[1]);
    return Math.hypot(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)) || 1;
  })();
  const pct = (value) => ((100 * value) / size).toFixed(1);
  const right = spread(spine, paths[1]);
  const left = spread(spine, paths[2]);
  const side = (name, one) =>
    `${name} edge ${pct(one.min)} % → ${pct(one.max)} % of the curve's size ` +
    `(${one.ratio.toFixed(2)}× at the belly)`;

  const same = Math.abs(right.ratio - left.ratio) < 0.005 && Math.abs(right.max - left.max) < 1e-9;
  const asked = values.widthPct;
  const used = number(drawn.width, asked);
  const cut = used < Math.abs(asked) - 1e-9
    ? ` Band width ${used.toFixed(1)} % — asked ${asked} %, cut so the band cannot fold ` +
      "over itself. Buckles above that: tune the width by hand."
    : ` Band width ${used.toFixed(1)} %.`;
  const stored = drawn.kind === "stored"
    ? ` Built from the ${drawn.stored} stored points: exact there, approximate between them.`
    : "";
  return `${side("Right", right)}. ${same ? "Left edge the same" : side("Left", left)}.` +
    cut + stored;
}

// draw one curve; returns false (and says why) if the maths did not load
export function render(preview, readoutEl, curve, values) {
  const P = globalThis.PlateMath;
  if (!P) {
    readoutEl.textContent = "the plate maths did not load, so there is nothing to draw; " +
      "reload the page (the file is /api/plate-math)";
    return false;
  }
  const drawn = drawing(P, curve, values);
  const turned = turn(drawn.paths.filter((line) => line && line.length), number(values.degrees, 0));
  const box = frame(turned);
  if (!box) {
    readoutEl.textContent = "no drawable points for this curve at these values";
    return false;
  }
  preview.innerHTML = bandSvg(turned, box);
  readoutEl.textContent = readout(drawn, values, turned);
  return true;
}

// redraw on every control, without a page load
export function live(controls, redraw) {
  for (const control of controls) {
    if (control) control.addEventListener("input", redraw);
  }
}

export const valuesOf = (inputs) => ({
  widthPct: number(inputs.widthPct.value, 1),
  plus: number(inputs.plus.value, 2.5),
  minus: number(inputs.minus.value, 0.1),
  profile: inputs.profile.value || "bow",
  degrees: number(inputs.degrees.value, 0),
});
