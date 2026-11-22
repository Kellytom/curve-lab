// The review desk's selection and bulk star write.
//
// One selection, one POST to /api/curve-stars, one count back. The page carries no rules:
// the endpoint validates the uids and the rating and refreshes the JSON copy; this script
// only keeps the selection, paints the cards and says what happened.

const el = (id) => document.getElementById(id);
const picks = () => [...document.querySelectorAll(".pick")];
const status = el("review-status");
const say = (text, bad = false) => {
  if (!status) return;
  status.textContent = text;
  status.style.color = bad ? "#9b2c2c" : "#7a6a55";
};
const labelOf = (stars) => (stars > 0 ? `stars ${stars}/10` : "stars none");
const count = () => {
  const chosen = picks().filter((pick) => pick.checked).length;
  const out = el("review-count");
  if (out) out.textContent = `${chosen} selected`;
  return chosen;
};

const apply = async (stars) => {
  const chosen = picks().filter((pick) => pick.checked);
  if (!chosen.length) {
    say("select a curve first", true);
    return;
  }
  const uids = chosen.map((pick) => pick.value);
  const buttons = [...document.querySelectorAll("#review-bar button")];
  buttons.forEach((button) => { button.disabled = true; });
  say(`saving stars ${stars} on ${uids.length}…`);
  try {
    const response = await fetch("/api/curve-stars", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ uids, stars }),
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.error || `save failed: ${response.status}`);
    for (const pick of chosen) {
      const card = pick.closest(".review-card");
      if (!card) continue;
      card.dataset.stars = String(stars);
      const line = card.querySelector("[data-label]");
      if (line) line.textContent = labelOf(stars);
    }
    say(body.warning ? `stars ${stars} on ${body.updated} — ${body.warning}`
      : `stars ${stars} on ${body.updated} curves`);
  } catch (error) {
    say(`not saved: ${error.message}`, true);
  } finally {
    buttons.forEach((button) => { button.disabled = false; });
  }
};

for (const button of document.querySelectorAll("#review-bar button[data-stars]")) {
  button.addEventListener("click", () => apply(Number(button.dataset.stars)));
}
el("review-apply")?.addEventListener("click", () => apply(Number(el("review-stars").value)));
el("review-all")?.addEventListener("change", (event) => {
  for (const pick of picks()) pick.checked = event.target.checked;
  count();
});
for (const pick of picks()) pick.addEventListener("change", count);
count();
