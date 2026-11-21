// The live tuning lab at /tune/.
//
// The drawing and the readout are shared with /tune/<uid> in tune-render.js; the maths
// there is window.PlateMath, served from workbench/plate_math.js by /api/plate-math —
// the same file the printed plate loads. Nothing on this page is saved.

import { render, live, valuesOf } from "./tune-render.js";

const el = (id) => document.getElementById(id);
const cache = new Map();

async function load(uid) {
  if (!cache.has(uid)) {
    const response = await fetch(`/api/curve/${uid}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`curve ${uid}: ${response.status}`);
    cache.set(uid, await response.json());
  }
  return cache.get(uid);
}

async function start() {
  const picker = el("lab-curve");
  if (!picker) return;

  const inputs = {
    widthPct: el("lab-width"),
    plus: el("lab-plus"),
    minus: el("lab-minus"),
    profile: el("lab-profile"),
    degrees: el("lab-degrees"),
  };
  const preview = el("lab-preview");
  const readout = el("lab-readout");

  const showValues = () => {
    const values = valuesOf(inputs);
    el("lab-width-out").value = String(values.widthPct);
    el("lab-plus-out").value = String(values.plus);
    el("lab-minus-out").value = String(values.minus);
  };

  const redraw = () => {
    showValues();
    const curve = cache.get(picker.value);
    if (!curve) return;
    render(preview, readout, curve, valuesOf(inputs));
  };

  live(Object.values(inputs), redraw);

  picker.addEventListener("change", async () => {
    try {
      await load(picker.value);
      redraw();
    } catch (error) {
      readout.textContent = `${picker.value} could not be loaded: ${error.message}`;
    }
  });

  showValues();
  try {
    await load(picker.value);
    redraw();
  } catch (error) {
    readout.textContent = `${picker.value} could not be loaded: ${error.message}`;
  }
}

start();
