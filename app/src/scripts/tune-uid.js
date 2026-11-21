// The live preview on /tune/<uid>.
//
// The drawing is shared with /tune/ in tune-render.js; the maths is window.PlateMath,
// served from workbench/plate_math.js by /api/plate-math, the file the printed plate
// loads. The form still submits for a no-JavaScript browser; typing redraws in place.

import { render, live, valuesOf } from "./tune-render.js";

const el = (id) => document.getElementById(id);

function start() {
  const data = el("tune-curve");
  const form = el("tune-form");
  if (!data || !form) return;

  const curve = JSON.parse(data.textContent);
  const inputs = {
    widthPct: form.elements.widthPct,
    plus: form.elements.plus,
    minus: form.elements.minus,
    profile: form.elements.profile,
    degrees: form.elements.degrees,
  };
  const preview = el("tune-preview");
  const readout = el("tune-readout");

  const redraw = () => render(preview, readout, curve, valuesOf(inputs));
  live(Object.values(inputs), redraw);
}

start();
