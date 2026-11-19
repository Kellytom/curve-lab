// The gallery's controls: turn the inner curve, and set the pieces per side.
// Every press writes through /api/curve-notes and reloads, so the figure that
// comes back is the one the record now describes.
//
// This lived inline in illuminations.astro, where neither the linter nor the
// type checker could see it. It lives here so a page cannot carry unchecked
// code, and so `no-undef` covers it like any other module.

const post = async (uid, body) => {
  const response = await fetch("/api/curve-notes", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ curves: [{ uid, ...body }] }),
  });
  return response.ok;
};

document.querySelectorAll(".turn").forEach((row) => {
  const uid = row.dataset.uid;
  const flag = row.querySelector(".saveflag");

  row.querySelectorAll("button[data-turn]").forEach((button) => {
    button.addEventListener("click", async () => {
      const rotation = (Number(row.dataset.rot) || 0) + Number(button.dataset.turn);
      flag.textContent = "saving...";
      const ok = await post(uid, { rotation });
      flag.textContent = ok ? "saved" : "failed";
      if (ok) location.reload();
    });
  });

  row.querySelectorAll("button[data-piece]").forEach((button) => {
    button.addEventListener("click", async () => {
      flag.textContent = "saving...";
      const ok = await post(uid, { pieces: Number(button.dataset.piece) });
      flag.textContent = ok ? "saved" : "failed";
      if (ok) location.reload();
    });
  });

  row.parentElement.querySelectorAll(".imp button").forEach((button) => {
    button.addEventListener("click", async () => {
      flag.textContent = "saving...";
      const ok = await post(uid, { importance: Number(button.dataset.imp) });
      flag.textContent = ok ? "saved" : "failed";
      if (ok) location.reload();
    });
  });
});
