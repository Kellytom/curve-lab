/**
 * The quintic sandbox's wiring. No maths here beyond plumbing: everything the page
 * draws comes from `app/src/lib/quintic-lab.ts`.
 *
 * Coordinates: the page (and the pointer) are y down; the model is y up. `toModel`
 * on the way in and `plot` on the way out are the only two places a y flips.
 */

import {
  chainError,
  outline,
  outlineCrossings,
  outlinePath,
  quinticAt,
  rails,
  reduceStroke,
  type Point,
  type WidthProfile,
} from "../lib/quintic-lab.ts";

const WIDTH = 1000;
const HEIGHT = 540;

const pad = document.getElementById("ql-pad") as unknown as SVGSVGElement;
const els = {
  outline: document.getElementById("ql-outline") as unknown as SVGPathElement,
  railsLeft: document.getElementById("ql-rails-left") as unknown as SVGPathElement,
  railsRight: document.getElementById("ql-rails-right") as unknown as SVGPathElement,
  guide: document.getElementById("ql-guide") as unknown as SVGPathElement,
  spine: document.getElementById("ql-spine") as unknown as SVGPathElement,
  points: document.getElementById("ql-points") as unknown as SVGGElement,
  readout: document.getElementById("ql-readout") as unknown as SVGTextElement,
  mode: document.getElementById("ql-mode") as HTMLSelectElement,
  spans: document.getElementById("ql-spans") as HTMLOutputElement,
  spansSlider: document.getElementById("ql-spans-slider") as HTMLInputElement,
  fullness: document.getElementById("ql-fullness") as HTMLOutputElement,
  fullnessSlider: document.getElementById("ql-fullness-slider") as HTMLInputElement,
  ends: document.getElementById("ql-ends") as HTMLOutputElement,
  endsSlider: document.getElementById("ql-ends-slider") as HTMLInputElement,
  middle: document.getElementById("ql-middle") as HTMLOutputElement,
  middleSlider: document.getElementById("ql-middle-slider") as HTMLInputElement,
  peak: document.getElementById("ql-peak") as HTMLOutputElement,
  peakSlider: document.getElementById("ql-peak-slider") as HTMLInputElement,
  power: document.getElementById("ql-power") as HTMLOutputElement,
  powerSlider: document.getElementById("ql-power-slider") as HTMLInputElement,
  tolerance: document.getElementById("ql-tolerance") as HTMLOutputElement,
  toleranceSlider: document.getElementById("ql-tolerance-slider") as HTMLInputElement,
  showRails: document.getElementById("ql-show-rails") as HTMLInputElement,
  showPoints: document.getElementById("ql-show-points") as HTMLInputElement,
  demo: document.getElementById("ql-demo") as HTMLButtonElement,
  clear: document.getElementById("ql-clear") as HTMLButtonElement,
};

/** y up in the model, y down in the page: the one flip on the way in. */
const toModel = (x: number, y: number): Point => [x, HEIGHT - y];
/** ... and the one flip on the way out. */
const plot = (p: Point): string => `${p[0].toFixed(2)},${(HEIGHT - p[1]).toFixed(2)}`;

let stroke: Point[] = [];
let drawing = false;

const profile = (): WidthProfile => ({
  ends: Number(els.endsSlider.value),
  middle: Number(els.middleSlider.value),
  peak: Number(els.peakSlider.value),
  power: Number(els.powerSlider.value),
});

const tolerance = (): number => Number(els.toleranceSlider.value);

/** The smallest chain of cubics whose measured miss is inside the tolerance. */
function cubicsFor(control: Point[]): { cubics: number; miss: number } {
  let cubics = 2;
  let miss = chainError(control, cubics);
  while (miss > tolerance() && cubics < 32) {
    cubics *= 2;
    miss = chainError(control, cubics);
  }
  return { cubics, miss };
}

function pointerPoint(event: PointerEvent): Point {
  const rect = pad.getBoundingClientRect();
  const x = ((event.clientX - rect.left) / rect.width) * WIDTH;
  const y = ((event.clientY - rect.top) / rect.height) * HEIGHT;
  return toModel(x, y);
}

function tracePath(points: Point[]): string {
  if (points.length < 2) return "";
  return points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${plot(p)}`)
    .join(" ");
}

function render(): void {
  const guide = tracePath(stroke);
  els.guide.setAttribute("d", guide);

  if (stroke.length < 4) {
    for (const el of [els.outline, els.spine, els.railsLeft, els.railsRight]) el.setAttribute("d", "");
    els.points.replaceChildren();
    els.readout.textContent = "Draw a stroke: press and drag in the box.";
    return;
  }

  let spans;
  try {
    spans = reduceStroke(stroke, {
      mode: els.mode.value === "lsq" ? "lsq" : "even",
      spans: Number(els.spansSlider.value),
      fullness: Number(els.fullnessSlider.value),
      tolerance: tolerance(),
    });
  } catch (error) {
    els.readout.textContent = `Cannot reduce this stroke: ${(error as Error).message}`;
    return;
  }

  let drawnMiss = 0;
  let chainMiss = 0;
  let cubics = 0;
  const d: string[] = [];
  const railLeft: string[] = [];
  const railRight: string[] = [];
  const spine: string[] = [];
  let widest = 0;
  let narrowest = Number.POSITIVE_INFINITY;
  let crossings = 0;

  const marks: SVGElement[] = [];
  for (const span of spans) {
    const { cubics: use, miss } = cubicsFor(span.control);
    cubics += use;
    chainMiss = Math.max(chainMiss, miss);
    drawnMiss = Math.max(drawnMiss, span.strokeMiss);

    const sides = outline(span.control, profile(), 140);
    widest = Math.max(widest, sides.widest);
    narrowest = Math.min(narrowest, sides.narrowest);
    crossings += outlineCrossings(sides);
    d.push(outlinePath(sides, plot));

    if (els.showRails.checked) {
      const band = rails(span.control, 6, 80);
      railLeft.push(band.left.map((p, i) => `${i === 0 ? "M" : "L"} ${plot(p)}`).join(" "));
      railRight.push(band.right.map((p, i) => `${i === 0 ? "M" : "L"} ${plot(p)}`).join(" "));
    }

    // the spine: the true quintic, sampled densely (the chain's miss is reported)
    const steps = 120;
    spine.push(Array.from({ length: steps + 1 }, (_, k) => {
      const q = quinticAt(span.control, k / steps);
      return `${k === 0 ? "M" : "L"} ${plot(q)}`;
    }).join(" "));

    if (els.showPoints.checked) {
      for (const p of span.control) {
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", String(p[0]));
        circle.setAttribute("cy", String(HEIGHT - p[1]));
        circle.setAttribute("r", "3.5");
        circle.setAttribute("fill", "none");
        circle.setAttribute("stroke", "#c0392b");
        circle.setAttribute("stroke-width", "1");
        marks.push(circle);
      }
    }
  }

  els.outline.setAttribute("d", d.join(" "));
  els.spine.setAttribute("d", spine.join(" "));
  els.railsLeft.setAttribute("d", els.showRails.checked ? railLeft.join(" ") : "");
  els.railsRight.setAttribute("d", els.showRails.checked ? railRight.join(" ") : "");
  els.points.replaceChildren(...marks);

  els.readout.textContent =
    `${spans.length} span${spans.length === 1 ? "" : "s"} · ${cubics} cubics · ` +
    `stroke→quintic ${drawnMiss.toFixed(2)} px · chain ${chainMiss.toFixed(4)} px · ` +
    `width ${narrowest.toFixed(1)}–${widest.toFixed(1)} px` +
    (crossings ? ` · the outline folds itself (${crossings})` : "");
}

function syncOutputs(): void {
  els.spans.textContent = els.spansSlider.value;
  els.fullness.textContent = Number(els.fullnessSlider.value).toFixed(2);
  els.ends.textContent = Number(els.endsSlider.value).toFixed(1);
  els.middle.textContent = Number(els.middleSlider.value).toFixed(1);
  els.peak.textContent = Number(els.peakSlider.value).toFixed(2);
  els.power.textContent = Number(els.powerSlider.value).toFixed(1);
  els.tolerance.textContent = Number(els.toleranceSlider.value).toFixed(3);
}

let pending = false;
function schedule(): void {
  if (pending) return;
  pending = true;
  requestAnimationFrame(() => {
    pending = false;
    syncOutputs();
    render();
  });
}

// -- drawing --------------------------------------------------------------

pad.addEventListener("pointerdown", (event) => {
  event.preventDefault();
  pad.setPointerCapture(event.pointerId);
  drawing = true;
  stroke = [pointerPoint(event)];
  schedule();
});

pad.addEventListener("pointermove", (event) => {
  if (!drawing) return;
  const p = pointerPoint(event);
  const last = stroke[stroke.length - 1];
  // one point per 2 px of pen travel: the reduction resamples anyway
  if (!last || Math.hypot(p[0] - last[0], p[1] - last[1]) > 2) {
    stroke.push(p);
    schedule();
  }
});

const stop = (event: PointerEvent): void => {
  if (!drawing) return;
  drawing = false;
  try {
    pad.releasePointerCapture(event.pointerId);
  } catch {
    /* the pointer was already released */
  }
  schedule();
};
pad.addEventListener("pointerup", stop);
pad.addEventListener("pointercancel", stop);
pad.addEventListener("pointerleave", (event) => {
  if (drawing && event.buttons === 0) stop(event);
});

// -- controls -------------------------------------------------------------

for (const element of [els.spansSlider, els.fullnessSlider, els.endsSlider, els.middleSlider,
  els.peakSlider, els.powerSlider, els.toleranceSlider]) {
  element.addEventListener("input", schedule);
}
for (const element of [els.mode, els.showRails, els.showPoints]) {
  element.addEventListener("change", schedule);
}

const DEMO: Point[] = Array.from({ length: 80 }, (_, i) => {
  const t = i / 79;
  // a hand-like S in model coordinates (y up), 1000 x 540 page
  const x = 120 + 760 * t;
  const y = 260 + 120 * Math.sin(2 * Math.PI * t) - 40 * Math.sin(4 * Math.PI * t);
  return [x, y] as Point;
});

els.demo.addEventListener("click", () => {
  stroke = DEMO.map((p) => [...p] as Point);
  schedule();
});

els.clear.addEventListener("click", () => {
  stroke = [];
  schedule();
});

stroke = DEMO.map((p) => [...p] as Point);
schedule();
