# Recent work: the gothic desk, the glue joint, and the move to TypeScript

This is the long form of the last two days. Everything below is on the running app; each section
links to the page where you can see it.

## 1. The desk that cuts a curve into an arch

**`/gothic/`** lists every stored curve. Each card carries the curve's plate, the mirror it was
measured against (`vertical`, `horizontal`, `y = x`, `y = −x`) and the gap between its two halves
as a share of its own size.

- **`/gothic/c-0008`** is the tuner: pick a cut, see the arch, save it.
- The cut is a symmetric pair of parameter values: **`t = 1/2 − q` and `t = 1/2 + q`**, with `q`
  from the menu (`1/40 … 1/6`). The percent of the half is only the echo.
- The arch is **one arm mirrored** about the vertical through the cut, so the two sides are equal
  by construction and the join is on the axis. A curve whose own halves disagree is still offered,
  with the gap printed (`c-0134`, the helmet: 9.97 %).
- The figure has **two panels at one scale**: the new arch above, the original below with its two
  cut points in red, the removed middle in red, and the integer hits in gold, labelled `(x, y)`.
- **`?set=gothic`** narrows the list to the arches already saved; each carries its cut share and
  `t` pair.

Saved and kept: **`c-0008a · u-bowl-gothic`** — the u-bowl cut 10 % each side, apex 156.8°,
`t = 9/20 … 11/20`, 631 stored points, with its plate.
**[Open the desk](/gothic/)** · **[the u-bowl tuner](/gothic/c-0008)** · **[the helmet](/gothic/c-0134)**

## 2. The glue sandbox now has a G3 quintic

**`/glue/`** joins two curves with different end slopes. It had a G1 cubic, a rational loop and
Levien's fitted offset; it now has the **quintic (G3)** kind.

Six control points (twelve numbers): the two ends, two handles on the typed directions, and P2/P3
solved so the connector matches the neighbours' **signed curvature** and **the rate it changes**
at both ends. A straight glue (zero targets, collinear ends) is a declared fallback.

The page prints all six numbers. For the operator's own example — slopes `3/4` and `−7/24`,
curvatures `0.5` and `−0.25`, rates `0.1` and `−0.2`:

- **start:** slope 0.750000 · κ 0.500000 · dκ/ds 0.100000
- **end:** slope −0.291667 · κ −0.250000 · dκ/ds −0.200000

The stated case is pinned at **1e-9** in `tests/js/glue.test.ts`; the solve matches to about
1e-15.
**[Open the glue sandbox](/glue/)**

## 3. The Tschirnhausen pieces, glue-ready

**`/pages/side-tests.html`** — the “Tschirnhausen and variations” section is now six pieces: the
whole curve, the loop, the + arm, the − arm, an arm trimmed at `t = 2`, and the mirrored arm.
Every card prints its ends as exact fractions and its slope; at a **rational t** both are
rational, so the piece can be cut there and joined. The node's slope is ±√3, which is the case
that needs the quintic.

The six pieces are registered **Study rows** (they name the page, not the plates), so they are in
the database without pretending to be plate records.
**[The side-curve kinds page](/pages/side-tests.html)**

## 4. TypeScript: new code, and four named ports

The rule is now: new code is `.ts`, and a `.js` changed for a feature is converted in the same
change. Landed so far:

- **`app/src/lib/glue.ts`** + `glue-sandbox.ts` + `glue.test.ts` (the quintic above).
- **`app/src/lib/crossings.ts`** + `crossings.test.ts` — the twin of `curve_lab/crossings.py`:
  grid buckets, the same strict test, crossing pairs not places. 50 random walks match the brute
  force; a figure-eight is one pair; a triple point is three.
- **`app/src/lib/curve-analysis.ts`** + **`scripts/analyse_curves.ts`** — the analysis that writes
  `workbench/curve-analysis.json`. Six records deep-equal the committed JSON; the full run is
  **405/405 rows**. The TypeScript output is now the record; `scripts/analyse_curves.py` is
  retired. The only semantic change: `c-0217`'s two pairs at a near-stationary point were a
  sampling artifact and are gone; five huge figures differ in the last decimal.
- **`app/src/lib/root-search.ts`** + **`scripts/root_search.ts`** — the mirrored-root search. Its
  committed data file was stale (highest-first rows from an older version); it is regenerated
  from the TS, and the pinned row matches the current Python exactly (grid 105, bend 1.1696,
  inflections 2, crossings 3, places 3, grace 0.0445).
- **`app/src/lib/coupler-curves.ts`** + **`scripts/coupler_curves.ts`** — four-bar couplers. The
  fixed Python and the TS agree exactly: **49 coupler curves**, the same top rows, crossings and
  mirror gaps; the data is regenerated from the TS. (The Python's CLI had a `KeyError: 'ground'`
  that crashed it; fixed, and the module stays for the crossing-calibration import.)

Still queued on the operator's list: `tests/test_regressions.py` (the register that runs the Node
and browser checks) is the last port; the Python twins of `root_search` and `coupler_curves` stay
where they still have an importer (`adder_roots.py` and the crossing-calibration test), so their
TypeScript files are the new authority for the data.

## 5. The gates, and two honest reds

- **The app check: 0 errors.** The glue and crossings files type-check; the four warnings are
  pre-existing and in other files.
- **The `/glue/` page check: green.** The quintic probe changes the kind, sets the four targets,
  and prints the six numbers with no console error.
- **The TypeScript tests: 14 green** (glue 5, crossings 4, trim 5) — run in their own group,
  because one `node --test` passing `.js` and `.ts` files together lost the module detection for
  `.ts`.
- **The fast gate's two reds are another agent's in-flight work:** `data/README.md` states 403
  rows where the files hold 405, and their `TrimCurveTest` invokes `node` in a way that cannot
  load `.ts`. Nothing in the glue, crossings or analysis work is red.

## 6. What is next

1. The remaining TypeScript ports (root_search, coupler_curves, the register).
2. The quintic's own loop mode — a declared shape, not a wider handle.
3. **A decision that is yours:** how a studied curve becomes a plate record (a Study row that
   stays a page, or a record that gets a plate).
4. Parked until you say: the start-point shift / the symmetric cut's final reading, and the
   human figure in the centre.
