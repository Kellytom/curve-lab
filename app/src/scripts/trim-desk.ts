// The trim desk's one page behaviour: preview by reload, save by POST.
//
// The maths is the server's (app/src/lib/trim-curve.ts, in the page's first paint); this script
// only sends the cut and says what came back. A save reloads the page (the dev server watches the
// registry and the plate), so the result travels in the URL, as the cut desk learned to do.

import { mirrorPair } from "../lib/trim-curve.ts";

const state = document.getElementById("trim-state") as HTMLElement | null;
const form = document.getElementById("trim-form") as HTMLFormElement | null;
const fromInput = form?.querySelector('input[name="from"]') as HTMLInputElement | null;
const toInput = form?.querySelector('input[name="to"]') as HTMLInputElement | null;

// The operator's rule (2026-11-24): "each time follow that algorithm of (num-denom)/denom for the
// end". Typing a start fraction and leaving the field sets the end to its mirror, ordered; typing
// the end afterwards still overrides it, and a bad fraction leaves both fields alone.
if (fromInput && toInput) {
  fromInput.addEventListener("change", () => {
    try {
      const pair = mirrorPair(fromInput.value);
      fromInput.value = pair.from;
      toInput.value = pair.to;
    } catch { /* not a fraction yet; the page reports it on preview */ }
  });
}

function say(text: string, kind = ""): void {
  if (!state) return;
  state.textContent = text;
  state.className = `trim-state ${kind}`;
}

if (form) {
  form.addEventListener("submit", async (event: SubmitEvent) => {
    const save = form.querySelector<HTMLButtonElement>("#trim-save");
    const submitter = (event.submitter as HTMLElement | null) || save;
    // the preview button is a plain GET of the page; only the save button is posted. Compare the
    // element, not its id: a button with no id used to fall through and save.
    if (submitter && submitter !== save) return;
    event.preventDefault();
    const data = new window.FormData(form);
    const body = {
      uid: String(data.get("uid") || ""),
      from: String(data.get("from") || ""),
      to: String(data.get("to") || ""),
      widthPct: Number(data.get("widthPct")),
      plus: Number(data.get("plus")),
      minus: Number(data.get("minus")),
      profile: String(data.get("profile") || "bow"),
      name: String(data.get("name") || ""),
    };
    if (save) save.disabled = true;
    say("cutting…", "busy");
    try {
      const response = await fetch("/api/trim-curve", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(result.error || `cut failed: ${response.status}`);
      const what = `t ${result.trim.from} → ${result.trim.to}: ` +
        `${result.trim.keptStations} stations kept, ${result.trim.droppedStations} dropped`;
      const query = new URLSearchParams({
        saved: `${result.uid} ${result.name} saved — ${what}`,
        new: result.uid,
      });
      if (result.warning) query.set("warning", result.warning);
      location.href = `/trim/${body.uid}?${query}`;
    } catch (error) {
      say(`not saved: ${(error as Error).message}`, "bad");
    } finally {
      if (save) save.disabled = false;
    }
  });
}
