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
    event.preventDefault();
    const data = new window.FormData(form);
    const body = {
      uid: data.get("uid"),
      cusp: Number(data.get("cusp")),
      keep: data.get("keep") === "short" ? "short" : "long",
      name: data.get("name") || "",
    };
    const button = form.querySelector("button[type=submit]");
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
      say(`${result.uid} ${result.name} saved — ${result.cut.kept} units kept, ` +
        `${result.cut.dropped} dropped${result.warning ? ` (${result.warning})` : ""}`, "ok");
      const link = document.createElement("a");
      link.href = `/plates#${result.uid}`;
      link.textContent = ` see ${result.uid} on the plates →`;
      state.appendChild(link);
    } catch (error) {
      say(`not saved: ${error.message}`, "bad");
    } finally {
      if (button) button.disabled = false;
    }
  });
}
