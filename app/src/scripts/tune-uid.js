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
  const uid = JSON.parse(el("tune-uid")?.textContent || '""');
  const status = el("tune-status");
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
  live([inputs.profile, inputs.degrees], redraw);

  // Save with the page's own script: the buttons disable while the write and the plate
  // render run, and the state is said beside them. Without JavaScript the same buttons
  // still post the form (formaction + formmethod) and the page comes back with a banner.
  const say = (text, kind) => {
    if (!status) return;
    status.textContent = text;
    status.className = `tune-status ${kind || ""}`;
  };
  const saveButtons = [...form.querySelectorAll("button[formaction]")];
  const save = async (button) => {
    const target = new URL(button.getAttribute("formaction"), location.origin);
    const payload = { ...valuesOf(inputs), curveName: form.elements.curveName?.value || "" };
    if (target.searchParams.get("mode") === "new" && !String(payload.curveName).trim()) {
      say("type a name for the new curve", "bad");
      form.elements.curveName?.focus();
      return;
    }
    saveButtons.forEach((item) => { item.disabled = true; });
    say("saving…", "busy");
    try {
      const response = await fetch(`${target.pathname}${target.search}`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(payload),
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.error || `save failed: ${response.status}`);
      if (body.uid && body.uid !== uid) {
        location.href = `/tune/${body.uid}?saved=${encodeURIComponent(`saved as new: ${body.uid} ${body.name}`)}`;
        return;
      }
      say(body.warning ? `saved — ${body.warning}` : "saved", body.warning ? "bad" : "ok");
    } catch (error) {
      say(`not saved: ${error.message}`, "bad");
    } finally {
      saveButtons.forEach((item) => { item.disabled = false; });
    }
  };
  for (const button of saveButtons) {
    button.addEventListener("click", (event) => {
      event.preventDefault();
      save(button);
    });
  }

  // the three numbers each have a slider: move one and the other follows, then redraw
  for (const key of ["widthPct", "plus", "minus"]) {
    const number = inputs[key];
    const slider = el(`${key}-slider`);
    if (!slider) continue;
    number.addEventListener("input", () => { slider.value = number.value; redraw(); });
    slider.addEventListener("input", () => { number.value = slider.value; redraw(); });
  }
}

start();
