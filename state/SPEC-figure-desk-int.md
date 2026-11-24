# SPEC-figure-desk-int — the figure desk (dot plots, algorithmic only)

*2026-11-23, sidechat. Third version of the page. The operator's direction:
"make an algorithmic only attempt, no cubic beziers. you can just plot the
dots… use what you have available from the whole repo… throw out the last
attempt, and try again." Version 2 (emblems as cubic chains) is thrown out;
this spec is the dot-plot page.*

## What it is for

The emblem-level desk: sacred emblems — ichthys fish, heart, Latin cross,
chi-rho — each drawn as **plotted exact stations and nothing else**. No cubic
Bézier appears anywhere on the page. It answers: how far does pure rational
arithmetic get the emblem collection, with the house figure engine doing the
rendering?

## The words this page owns

- **station** — a point whose two coordinates are exact rationals, carried as
  a [numerator, denominator] pair of BigInts.
- **dot** — the plotted picture of one station; a float read from the
  fraction. The read never writes back.
- **flare / tail** (fish) — belly depth and tail length; the parameter row.
- **cusp** — a true corner of the emblem (the heart's cleavage and point),
  drawn as two chains meeting, never smoothed through.

## How it is built

- `app/src/lib/emblem-dots.js` — the only place stations are computed.
  Rational arithmetic on BigInt; `unitCircle` gives the rational circle
  x=(1−t²)/(1+t²), y=2t/(1+t²); every emblem is one chain plus its mirror.
- `app/src/pages/figure-desk.astro` — the page: builds panels in the
  frontmatter with the house engine `app/src/lib/plot-figure.js`
  (`paths: []`, all dots in `stations`), server-rendered, no client script,
  so there are no controls to die.
- `tests/js/emblem-dots.test.js` — six tests: reduction, the fish's exact
  tail crossing, the heart's cusps and true mirror, ring membership.

## Layout

BaseLayout, `container`. Two-and-two panel grid (fish, heart; cross,
chi-rho), then a three-fish parameter row, then the exact-vs-plot section and
the proves/does-not-prove section. Legends inside the frame, from the engine.

## Rules, each with a check

1. **No cubic Bézier on the page.** Panels pass `paths: []` always.
   Check: `grep -n "paths: \[\]" app/src/pages/figure-desk.astro` finds one
   place (the `panel` helper), and `grep -c bezier app/src/lib/emblem-dots.js`
   finds only the comment saying there is none.
2. **Stations are exact.** Every coordinate is an `fr()` fraction pair.
   Check: `node --test tests/js/emblem-dots.test.js` — 6 green.
3. **Mirrors are exact.** `mirrorX`/`mirrorY` negate the numerator; no float
   round trip. Check: the heart test compares the chains pairwise.
4. **The only float is the plotted pixel.** `toFloat` is the single exit.
   Check: the test file imports nothing else that yields floats.
5. **Legends ≥ 15 px** at full width — the engine's own legend band does this.
6. **`npm --prefix app run check`** stays at 0 errors.

## Inherited invariants

- Stations exact, drawing (here: nothing) between them, figure says so.
- The page fits the house margin; no second font.
- Cusps are meeting chains — the lesson from the scrapped cubic heart
  (`state/PROBLEMS-figure-desk-int.md` §3).
