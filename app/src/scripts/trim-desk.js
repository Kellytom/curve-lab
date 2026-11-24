// The trim desk's one page behaviour: preview by reload, save by POST.
//
// The maths is the server's (app/src/lib/trim-curve.js, in the page's first paint); this script
// only sends the cut and says what came back. A save reloads the page (the dev server watches the
// registry and the plate), so the result travels in the URL, as the cut desk learned to do.

const state = document.getElementById("trim-state");
const form = document.getElementById("trim-form");

function say(text, kind = "") {
  if (!state) return;
  state.textContent = text;
  state.className = `trim-state ${kind}`;
}

if (form) {
  form.addEventListener("submit", async (event) => {
    const save = form.querySelector("#trim-save");
    const submitter = event.submitter || save;
    // the preview button is a plain GET of the page; only the save button is posted. Compare the
    // element, not its id: a button with no id used to fall through and save.
    if (submitter && submitter !== save) return;
    event.preventDefault();
    const data = new window.FormData(form);
    const body = {
      uid: data.get("uid"),
      from: data.get("from"),
      to: data.get("to"),
      widthPct: Number(data.get("widthPct")),
      plus: Number(data.get("plus")),
      minus: Number(data.get("minus")),
      profile: data.get("profile") || "bow",
      name: data.get("name") || "",
    };
    const button = form.querySelector("#trim-save");
    if (button) button.disabled = true;
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
      say(`not saved: ${error.message}`, "bad");
    } finally {
      if (button) button.disabled = false;
    }
  });
}
