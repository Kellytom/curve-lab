// The hub's windows: a still first, the real page when the window is reached.
//
// Four live iframes at once made the hub slow to open and kept four pages running. Each window
// shows a screenshot, and the iframe replaces it only when the window comes into view (or is
// clicked). The small print under the window says which of the three states it is in.

const windows = [...document.querySelectorAll("[data-window]")];

function start(win) {
  if (win.dataset.loaded) return;
  win.dataset.loaded = "1";
  const hint = win.parentElement?.querySelector("[data-hint]");
  if (hint) hint.textContent = "loading…";
  const frame = document.createElement("iframe");
  frame.src = win.dataset.src;
  frame.title = win.dataset.title || "live page";
  frame.loading = "eager";
  frame.addEventListener("load", () => {
    const still = win.querySelector(".shot");
    if (still) still.remove();
    if (hint) hint.textContent = "live page · scroll inside the frame for more";
  });
  win.appendChild(frame);
}

const observer = new window.IntersectionObserver((entries) => {
  for (const entry of entries) {
    if (entry.isIntersecting) start(entry.target);
  }
}, { rootMargin: "320px" });

for (const win of windows) {
  observer.observe(win);
  // a click on the still loads it now, in place, instead of only opening a tab
  win.addEventListener("click", (event) => {
    if (win.dataset.loaded) return;
    event.preventDefault();
    start(win);
  });
}
