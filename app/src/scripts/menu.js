// The menu on one line. The browser measures the row after layout and keeps as many
// options as fit; "full menu" opens the whole list, and "…" appears whenever something
// was left out. One line at any width, no wrapping.
//
// The measurement is taken after fonts and layout settle, and again on resize and on
// zoom (a resize event fires), so a reader who presses Cmd+ twice gets a re-measure.
const ROW = ".menu-line";
const MORE = ".menu-more";
const TOGGLE = ".menu-toggle";
const PANEL = "#menu-panel";

function measure() {
  const row = document.querySelector(ROW);
  const more = document.querySelector(MORE);
  if (!row || !more) return;

  const items = [...row.children];
  for (const item of items) item.hidden = false;
  more.hidden = true;

  // measure the *available* width honestly: the row's own box, not the window
  const available = row.getBoundingClientRect().width;
  let used = 0;
  let hiddenAny = false;
  for (const item of items) {
    const width = item.getBoundingClientRect().width + 16; // gap
    if (used + width > available) {
      item.hidden = true;
      hiddenAny = true;
    } else {
      used += width;
    }
  }
  more.hidden = !hiddenAny;
}

function toggle(force) {
  const panel = document.querySelector(PANEL);
  const toggleButton = document.querySelector(TOGGLE);
  const moreButton = document.querySelector(MORE);
  if (!panel) return;
  const open = force ?? panel.hidden;
  panel.hidden = !open;
  for (const button of [toggleButton, moreButton]) {
    if (button) button.setAttribute("aria-expanded", String(open));
  }
  if (open) panel.querySelector("a")?.focus({ preventScroll: true });
}

function build() {
  const row = document.querySelector(ROW);
  if (!row) return;
  measure();
  document.querySelector(TOGGLE)?.addEventListener("click", () => toggle());
  document.querySelector(MORE)?.addEventListener("click", () => toggle(true));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") toggle(false);
  });
  document.addEventListener("click", (event) => {
    const panel = document.querySelector(PANEL);
    if (!panel || panel.hidden) return;
    if (event.target.closest(PANEL) || event.target.closest(TOGGLE) || event.target.closest(MORE)) return;
    toggle(false);
  });
  window.addEventListener("resize", measure);
  // fonts change the widths; measure once they are ready
  document.fonts?.ready.then(measure);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", build);
} else {
  build();
}
