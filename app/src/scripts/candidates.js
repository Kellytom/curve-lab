// Put a set-aside curve back on the naming desk.
//
// The candidates page holds two kinds of curve: the finder curves that were
// never starred, and the chosen ones moved off the desk with "move to notes".
// Restoring clears the candidate flag in the database, so the curve returns to
// /names on the next load.
document.querySelectorAll(".restore").forEach((button) => {
  button.addEventListener("click", async () => {
    const uid = button.dataset.uid;
    button.disabled = true;
    button.textContent = "restoring…";
    try {
      const response = await fetch("/api/curve-notes", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ curves: [{ uid, candidate: false }] }),
      });
      if (!response.ok) throw new Error("restore failed");
      location.reload();
    } catch (error) {
      button.disabled = false;
      button.textContent = `not restored (${error.message})`;
    }
  });
});
