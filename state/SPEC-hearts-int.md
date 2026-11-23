# SPEC — the two hearts (`/hearts/`)

**Status, 2026-11-23:** first slice, both emblems draw.

**The page:** `app/src/pages/hearts.astro`
**The maths:** `app/src/lib/hearts-emblems.js`; the drawing: `app/src/scripts/hearts-sandbox.js`
**The check:** `app/scripts/check-pages.mjs /hearts`

## What it is

The operator: "i need a human face or figure or statue or something symbolizing human form in
the center ... maybe the sacred heart and the immaculate heart." This is the cheapest of the
three routes in `TODO.md`: the two hearts are emblems built from curves, not portraits.

- **The heart** is the classical parametric heart, `x = 16 sin³t`,
  `y = 13 cos t − 5 cos 2t − 2 cos 3t − cos 4t`, sampled. A heart is not rational, so the page
  says **sampled** and nothing here is an exact record.
- **Sacred Heart:** the flame rises from the notch, the cross stands on the flame, and the rays
  alternate long and short (16 is the traditional count).
- **Immaculate Heart:** one sword pierces the heart, roses sit at the foot, the same rays.
- **Every part is a slider** — heart size, flame, cross, rays, sword length and angle, roses —
  so proportions are judged by eye before any of it is fixed.

## Rules

- [x] The page says the heart is sampled, in the figure and in the note. Check: read the page.
- [x] Both emblems draw from the same parts; changing the emblem does not reload. Check: the
  headless capture of both.
- [ ] A chosen emblem is not yet stored as a record or a plate; that waits on the operator
      naming which one goes in the centre and at what size.
