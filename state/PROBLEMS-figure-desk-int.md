# PROBLEMS-figure-desk-int — every fault the figure desk has had

*The clean spec is `state/SPEC-figure-desk-int.md`. This file is the fault
register for the page; the operator's words, what was wrong, the fix, the guard.*

## 1. The human-figure page (scrapped 2026-11-23)

The operator's words: "move a level down and dont try for human or angelic
figures, but use the heart idea, fish idea, and other ideas that are easier to
render… you can scrap the current stuff."
What was wrong: the page's first version carried the Orans human-figure sprint;
the geometry was sound but the figure was the wrong scope for a desk.
Fix: page rebuilt at emblem level (fish, heart, cross, chi-rho); the human
sprint survives in `scripts/figure_sprint1.py` and `deep2/notes/figure-sprint-1.md`.

## 2. Blank figures — the flip and the viewBox disagreed

What was wrong: the generator's y-flip was changed (`FLIP = 300 − y`) while the
viewBox still assumed the old canvas, so every path was drawn below its own
canvas and all ten figures rendered as empty white boxes (caught in the
render check, never shipped to the operator as "done").
Fix: `FLIP = 110 − y` with `VB = "-150 0 300 220"`, chosen together, and the
comment states the mapping both ways.
Guard: SPEC rule 4 — the flip happens exactly once, in `to_svg` only, and the
page is render-checked (a screenshot with visible figures) before "done".

## 3. The heart had a loop at the cleavage

What was wrong: the heart was drawn as one closed Catmull-Rom ring; the
tangent across the top valley overshot horizontally and tied a small
self-crossing loop beside the left lobe (visible in the line and the fill).
Fix: the heart is two **open** chains, mirrored, meeting at the two true
cusps (cleavage and point) — cusps stay sharp, and each half's fill closes
along the bisector, which is the same line.
Guard: the same render check; and the design lesson is in the spec — an
emblem's cusps are drawn as meeting chains, never smoothed through.

## 4. The head/halo were drawn in model coordinates (human-figure sprint)

What was wrong: circles built in model y-up coordinates were passed to the
path builder without the flip, so they rendered as a small "leaf" far above
the figure.
Fix: `to_svg` applied to every part before path building.
Guard: SPEC rule 4 (one flip, applied in one place).

## 5. Version 2 thrown out; version 3 is dot plots only

The operator's words: "one last shot. using everything we have made, make an
algorithmic only attempt, no cubic beziers. you can just plot the dots…
throw out the last attempt, and try again."
What was wrong: version 2 drew the emblems as cubic Catmull-Rom chains —
against the direction the operator then set.
Fix: the page now plots dots only, via the house engine
(`plot-figure.js`) with `paths: []`; stations come from
`app/src/lib/emblem-dots.js` (BigInt fractions) with six green tests.
The Python generator `scripts/figure_desk.py` is retired — the page is now a
hand-written Astro frontmatter over a tested lib module, which is the house
pattern. `scripts/figure_sprint1.py` and its SVG stay as the human-figure
sprint's record.

