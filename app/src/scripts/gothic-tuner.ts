// The gothic tuner: the cut menu redraws the arch with the same maths the save uses.
//
// The first paint is the page's own SVG; this script replaces it as the menu moves. The readout
// is the same set of numbers in both, so a menu move cannot change what the picture claims.

import {
  bestAxis, cutArch, archFigure, integerHits, asFraction, DEFAULT_Q, MIRROR_GAP_LIMIT,
  type Point,
} from "../lib/gothic.ts";

type CurveData = { uid?: string; name?: string; points?: Point[] };
type SaveResult = { uid?: string; name?: string; error?: string };

const el = (id: string): HTMLElement | null => document.getElementById(id);
const preview = el("gothic-preview");
if (preview) {
  const data = JSON.parse(preview.dataset.curve || "{}") as CurveData;
  const points: Point[] = Array.isArray(data.points) ? data.points : [];
  const axis = points.length >= 12 ? bestAxis(points) : null;
  const hits = points.length >= 12 ? integerHits(points) : [];
  const hitText = hits.length
    ? `integer hits ${hits.map((hit) => `(${hit.x}, ${hit.y}) at t = ${asFraction(hit.t)}`).join(", ")}`
    : "no integer hit within 0.01";
  const select = el("gothic-q") as HTMLSelectElement | null;
  const output = el("gothic-q-out") as HTMLOutputElement | null;
  const readout = el("gothic-readout");
  const form = el("gothic-form") as HTMLFormElement | null;
  const state = el("gothic-state");

  const qOf = (): number => Number(select?.value || DEFAULT_Q);

  const draw = (q: number): void => {
    if (!axis || axis.gap > MIRROR_GAP_LIMIT) return;
    const arch = cutArch(points, { q, axis, force: axis.gap > MIRROR_GAP_LIMIT });
    if (!arch) return;
    preview.innerHTML = archFigure(arch, { label: data.name, source: points, hits });
    if (output) output.textContent = `${Math.round(arch.share * 100)} %`;
    if (readout) {
      const nearest = Math.abs(arch.t[0] - arch.tRequested[0]) > 1e-3
        ? ` · asked ${asFraction(arch.tRequested[0])} … ${asFraction(arch.tRequested[1])}, ` +
          "nearest station"
        : "";
      readout.textContent = `apex ${arch.apexAngle.toFixed(1)}° · ` +
        `${arch.width.toFixed(2)} × ${arch.height.toFixed(2)} model units · ` +
        `feet level ${(arch.feetLevel * 100).toFixed(2)} % · ` +
        `kept ${(arch.keptShare * 100).toFixed(1)} % of the curve · ` +
        `turn ${arch.degrees.toFixed(1)}° · ` +
        `t = ${asFraction(arch.t[0])} … ${asFraction(arch.t[1])} ` +
        `(step ${asFraction(arch.q)})${nearest} · ` +
        `${Math.round(arch.share * 100)} % of the half · ${hitText}` +
        (arch.mirrored ? "" : ` · parent gap ${(arch.gap * 100).toFixed(2)} % (one arm mirrored)`);
    }
  };

  select?.addEventListener("change", () => draw(qOf()));
  draw(qOf());

  form?.addEventListener("submit", async (event: SubmitEvent) => {
    event.preventDefault();
    const button = form.querySelector("button");
    const nameField = form.querySelector('input[name="name"]') as HTMLInputElement | null;
    const name = nameField ? nameField.value : "";
    if (button) button.disabled = true;
    if (state) {
      state.className = "gothic-state busy";
      state.textContent = "cutting…";
    }
    try {
      const response = await fetch("/api/gothic-arch", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ uid: data.uid, q: qOf(), name }),
      });
      const result = (await response.json()) as SaveResult;
      if (!response.ok) throw new Error(result.error || `the save failed (${response.status})`);
      if (state) {
        state.className = "gothic-state ok";
        state.textContent = "saved as ";
        const link = document.createElement("a");
        link.href = `/plates#${result.uid}`;
        link.textContent = `${result.uid} ${result.name}`;
        state.append(link);
        state.append(" · open the plate");
      }
    } catch (error) {
      if (state) {
        state.className = "gothic-state bad";
        state.textContent = String(error instanceof Error ? error.message : error);
      }
    } finally {
      if (button) button.disabled = false;
    }
  });
}
