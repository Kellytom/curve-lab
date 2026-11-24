# Fig. H1 — the human-figure sprint, study 1 (2026-11-23)

The operator asked for a 2-D black-and-white sprint at the human figure, built
with algorithms. This is study 1: the **Orans** — the early Christian praying
figure, frontal, arms raised, robed, haloed. It is the simplest sacred human
form, and the oldest (second-century frescoes), which is why it goes first.

## What the algorithm does

1. **One half is designed, the other is reflected.** The right robe side and
   right arm are eight and five rational stations; the left is the mirror
   image, point for point (reflection keeps every length, so exactness
   survives the mirror).
2. **Circles are rational.** The head (r = 26) and halo (r = 38) use
   x = (1−t²)/(1+t²), y = 2t/(1+t²) — no trigonometry of a general angle,
   per `state/DESIGN-int.md` §Trigonometry. Head: 64 stations; halo: 96.
3. **The drawing between stations is a cubic Catmull-Rom chain** — the house
   rule: stations exact, drawing approximate, figure says so.
4. **Two variants, one skeleton:** the line study (left) and the filled
   silhouette (right). Black and white only.

## The proof, as printed by the script

    robe stations: 15 (closed)
    arm stations per side: 5
    head stations: 64, halo stations: 96
    all coordinates rational: yes (Fractions; printed floats are display only)

Run: `.venv/bin/python scripts/figure_sprint1.py` — wrote
`workbench/figure-sprint-1.svg` (6.5 KB), render-checked at 760 px.

## What this proves, and what it does not

- **Proves:** the curve vocabulary (mirror symmetry, rational circles, cubic
  chains) already draws a figure that *reads as human and as prayer* at first
  glance. The three-part difficulty named in the sprint is real, but the
  maths part starts closer than feared: no new machinery was needed for study 1.
- **Does not prove:** the craft. Whether this reads as *sacred* — the
  operator's call, on the rendered figure, not on this note.

## Next steps, in order (each one measurable)

1. **Taper** — robe and arms as bands whose width varies (the character-rail
   law, reused): sleeves widen, wrists narrow.
2. **Folds** — three or four interior fold curves running hem to waist,
   each a mirrored pair, so the robe stops looking like a cone.
3. **Hands** — the hardest single piece; study the head and the hands
   separately before joining.
4. **The face** — nothing drawn yet, deliberately: face first on its own
   study sheet, at large scale.

Files: `scripts/figure_sprint1.py` (the generator), `workbench/figure-sprint-1.svg`
(the figure). One sprint, no other files touched.

## Addendum, same day — the desk moved down a level

The operator scrapped the human-figure desk and pointed the page at the easy
emblems (fish, heart, cross, chi-rho) on Astro standards. This note stays as
the record of the human sprint; the live page is now
`/figure-desk/` (`app/src/pages/figure-desk.astro`), spec
`state/SPEC-figure-desk-int.md`. The heart there is drawn as two open mirrored
chains meeting at its two cusps — the same cusp lesson the figure sprint
needed for hands.
