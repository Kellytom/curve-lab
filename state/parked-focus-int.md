# parked-focus-int — directions pushed onto the stack, newest first

Pushed by `/fstart <direction>`, popped by `/fstart return`. A parked row is
still work: it says why it stopped, what exists, and what the next attempt needs.

## 1. The figure desk (parked 2026-11-24)

- **What it is:** `/figure-desk/` — sacred emblems (ichthys, heart, Latin cross,
  chi-rho) plotted as exact rational stations only, no cubic Bézier.
- **Why parked.** The operator, 2026-11-24: "that was just GLM trying its best,
  but it failed … we have to make a better spec for GLM or you to try again …
  save that project for later."
- **What exists:** `app/src/lib/emblem-dots.js` (BigInt fraction pairs; 6 tests
  green under `~/node24/bin/node`), `app/src/pages/figure-desk.astro`
  (server-rendered, `paths: []`), `state/SPEC-figure-desk-int.md`,
  `state/PROBLEMS-figure-desk-int.md`, plus the human-figure sprint record in
  `deep2/notes/figure-sprint-1.md` and `scripts/figure_sprint1.py`.
- **What a retry needs.** The spec is the fault, not the arithmetic. It says
  what to build but not what makes an emblem read as that emblem, and it allows
  `.js` where the house rule is TypeScript. Rewrite the spec first, name the
  check that fails when an emblem is unrecognisable, then rebuild.
