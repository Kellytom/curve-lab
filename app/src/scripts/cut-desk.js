// The cut desk's one page behaviour: pick a dot, choose the arc, save the cut.
//
// The maths is the server's (app/src/lib/cut-doubles.js, in the page's first paint); this
// script only sends the choice and says what came back.

const state = document.getElementById("cut-state");
const form = document.getElementById("cut-form");

function say(text, kind = "") {
  if (!state) return;
  state.textContent = text;
  state.className = `cut-state ${kind}`;
}

if (form) {
  form.addEventListener("submit", async (event) => {
    // the preview button is a plain GET of this page with the values; only the save is posted
    const submitter = event.submitter || form.querySelector("#cut-save");
    if (submitter && submitter.id && submitter.id !== "cut-save") return;
    event.preventDefault();
    const data = new window.FormData(form);
    const choice = String(data.get("mode") || "dot:0");
    const isDot = choice.startsWith("dot:");
    const body = {
      uid: data.get("uid"),
      mode: isDot ? "dot" : choice,
      cusp: isDot ? Number(choice.slice(4)) : 0,
      keep: data.get("keep") === "short" ? "short" : "long",
      widthPct: Number(data.get("widthPct")),
      plus: Number(data.get("plus")),
      minus: Number(data.get("minus")),
      profile: data.get("profile") || "bow",
      name: data.get("name") || "",
    };
    const button = form.querySelector("#cut-save");
    if (button) button.disabled = true;
    say("cutting…", "busy");
    try {
      const response = await fetch("/api/cut-double", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(result.error || `cut failed: ${response.status}`);
      const what = result.cut.mode === "dot"
        ? `${result.cut.kept} units kept, ${result.cut.dropped} dropped`
        : `${result.cut.runs} open curve${result.cut.runs === 1 ? "" : "s"} from the ` +
          `${result.cut.side} half`;
      // A save writes the registry and the plate, and the dev server reloads the page when the
      // files change, so the message is carried in the URL instead of in the DOM: the reloaded
      // page shows it, and so does a bookmark or a refresh.
      const query = new URLSearchParams({
        saved: `${result.uid} ${result.name} saved — ${what}`,
        new: result.uid,
      });
      if (result.warning) query.set("warning", result.warning);
      location.href = `/cut/${body.uid}?${query}`;
    } catch (error) {
      say(`not saved: ${error.message}`, "bad");
    } finally {
      if (button) button.disabled = false;
    }
  });
}
