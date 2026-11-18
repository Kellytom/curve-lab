# The G3 showcase

> **draft A** — a working draft, not a final text.
> One page for the overall view. Cubic first; a quintic only when the curve
> genuinely needs it. Everything on the page is a measurement, not a drawing.

<!-- updated:start -->
Updated 2026-11-18 · commit `6d53c36`
<!-- updated:end -->

The live pages are generated into `workbench/` and served by the lab, not by
this book:

- `workbench/g3-showcase.html` — the one page: lead,
  quintic-required set, cusp family, and the full gallery.
- `workbench/g3-notes.html` — the continuity ladder, the
  circle, and the error tables.
- `workbench/g3-handover.html` — the standalone gallery copy.
- `workbench/g3-diagnostics.html` — the red
  rings and the zoomable problem areas.

## What it is for

The destination is a curve that **Inkscape or a glyph editor can open as
ordinary Bézier nodes** and edit without a smoothness surprise. That means:

- four-point cubic spans where a cubic chain can carry the curve;
- every join measured in position, tangent, curvature and curvature-rate;
- the editable data stated: integer control points, handle lengths and the
  rational slope of each handle;
- the join errors kept, but on the notes page rather than in the way of the
  showcase.

The showcase is not a gallery of pretty shapes. It is the handoff sheet and
the proof that the handoff is smooth.

## The continuity ladder and the gate

At a join, the gate measures four gaps:

| gap | what it is | exact construction | integer-rounded source |
|---|---|---|---|
| `|Δp|` | position | `1e-9` | `1e-5` |
| angle | tangent direction | `1e-6°` | `1e-6°` |
| `|Δκ|` | curvature | `1e-9` | `1e-5` |
| `|Δ(dκ/ds)|` | curvature-rate | `1e-9` | `1e-5` |

The `1e-9` values are **floating-point noise** for exact constructions: a
single cubic cut into pieces, a degree-elevated span, or a join solved
algebraically. They are not a universal law. The recovered LAC page has
**integer-rounded control points**, so its joins are G3 only to the data's
precision. Across the 31 recovered LAC chains the measured residual runs from
`5.6e-8` to `7.96e-6`; LAC Fig. 6 is at `5.6e-8`. Requiring `1e-9` there asks
the data to be more precise than it is, and the old code responded by
re-fitting a quintic. The source tolerance is therefore **`1e-5`**, while exact
constructions keep `1e-9`. The gate is a **declared per-source tolerance**;
the page still prints each measured gap. The gaps are separate: a source chain
can have a tiny `dκ/ds` residual and still fail a `0.1°` tangent gap or a
curvature gap.

Two further checks matter:

- **Interior speed floor.** A join-only test can pass two spans that each
  graze a near-cusp inside. A span is admitted only when its speed never falls
  below **10% of its chord**. This is what keeps the `dκ/ds` graph readable
  and the "smooth" badge honest.
- **Fidelity.** A curve is admitted only when the geometric deviation from
  the source is under **5% of the curve's own size**. A source corner smoothed
  inside that tolerance is delivered smooth; the fit says so explicitly when
  it had to trim a singular endpoint.

## Degree: cubic first

A curve goes to Inkscape or a glyph editor as **four-point cubic spans**. A
cubic has four control points; meeting G3 at both ends asks for six
conditions (tangent direction, curvature and curvature-rate at each end). A
single cubic is therefore over-determined for a generic G3 join. A quintic
span has six control points and two free handle lengths, which is exactly
enough to meet the six conditions and still follow the source. That is why the
quintic exists — and why it is a fallback, not a default.

The rule:

1. Try a cubic chain first.
2. Use a quintic span only when no cubic chain can meet the gate and the
   tolerance.
3. The **lead** of the showcase carries only the few curves that need it —
   about five to ten — and each one states its specific reason.
4. The same page carries the **full gallery** below, so one page gives the
   overall view. The quintic spans may appear in the side construction panels
   as the working view.
5. The full fallback index may also exist as `g3-handover.html`.

### The LAC correction

The recovered LAC spines are **already cubic Bézier chains** — six four-point
spans each, with integer control points at the page scale. LAC Fig. 6
(`p = 0, turn 270`) is labelled **S44 · Fig. 6 · LAC: p = 0, turn 270** in the
showcase notes, not `LAC · Fig. 6`. Its joins measure G3 at `5.6e-8`,
which is the precision of the integer-rounded source. It is carried as its own
cubic spans at the source tolerance, **not** re-fitted as a quintic. The
S-number is `38 + figure number`: Fig. 1 is S39, Fig. 6 is S44.

The other recovered LAC chains are **not G3**: their spans meet in position,
but their tangent gaps run up to `0.19°` and their curvature gaps up to
`1.3e-4`. They are rejected with those measured reasons; they are not silently
re-fitted as quintics. Finding a cubic G3 construction for those chains is the
open cubic-first task, and the diagnostics page shows where the joins fail.

The five curves that remain in the quintic-required lead are there for stated
reasons, not a blanket "not a single cubic":

| curve | why cubic-first fails here |
|---|---|
| Stage II · Fig. 1 · The Euler curve · spine 2 | an Euler curve's curvature grows linearly; a four-point cubic span cannot carry that G3 data |
| heart · Wolfram | sampled heart; no four-point cubic chain carries its G3 data |
| heart · Mangaldan | sampled heart; no four-point cubic chain carries its G3 data |
| primal · fire | grammar-built sampled curve; no four-point cubic chain carries its G3 data |
| misc · Reuleaux triangle | constant-width arcs with corners; the joins need six points |

## The page: what is where

The main showcase is **one page**:

1. **Cubic lead** — six panels, every span four control points. Five are one
   cubic cut into five pieces; the bell is eight independent cubic spans. The
   joins are G3 by identity or by solve, and the panel states its speed floor.
2. **Quintic-required** — the five curves above, each with the specific
   reason and the six-point spans shown in the side construction.
3. **Cusp family** — the complete admitted set, plus rejected comparisons:
   - admitted: astroid, deltoid, nephroid, epicycloid k=3, epicycloid k=5,
     hypocycloid k=5, cardioid, heart · Beutel lower;
   - rejected: semicubical and pear, kept beside them with the measured reason.
4. **Deviation cases** — squircle and heart · Beutel upper, not hidden.
5. **The full gallery** — every G3-complete curve, grouped by source, curve
   left and `dκ/ds` right. This is where the overall view lives.

Figures are numbered consecutively from 1. The gallery follows the lead; the
counts are generated below.

Each gallery panel shows:

- the ideal curve dashed, the delivered G3 chain solid, the joins circled;
- `dκ/ds` against arc length, with green joins and gold declared breaks. The
  gallery carries **no tight ring**; a tight span is ringed in **gold** on the
  diagnostics page only;
- a **record**: branches, spans, deviation as a share of size, worst
  `Δ(dκ/ds)`, native degree, speed floor, and any declared feature;
- a **zoom** button that enlarges the panel and lets you scroll to the mark.

A tight span is below **25% of the chord speed**; the 10% floor is the
admission line. The diagnostics page collects the advisory rings in gold. Red
is reserved for a rejected cusp or a failing join: a declared cusp is never a
red ring. The figure-by-figure fixes and their proofs are tracked in
`state/G3-FIXES-int.md`.

## The handoff table

The six cubic lead panels carry the data the editor needs, in a table under
the figure:

- **control points** — integers at the stated scale (×625 for the integer
  panels), or real for the bell;
- **handle lengths** — an integer when the squared length is a perfect square,
  otherwise the exact `√n`;
- **handle slopes** — reduced fractions of the integer handle vector, or
  `vertical`.

The bell is honestly marked real, not integer. The quintic-required rows are
not handoff rows and do not get the table; their side construction shows the
six-point spans as the working view.

## The error tables

The join error tables moved to `workbench/g3-notes.html`. The
notes page repeats each of the six cubic curves with:

- `|Δp|`, tangent angle, `|Δκ|`, `|Δ(dκ/ds)|`;
- the pass/fail on every body join.

The showcase therefore carries the editable data, and the notes carry the
measurement. The gate is computed from Bézier derivatives, never from the
sampled polyline.

Every figure links to its own entry on the notes page
(`g3-notes.html#note-<curve>`). The entry carries the measurement, the fix
note, the join table and a back-link to `g3-showcase.html#fig-<n>`. A curve
that appears both in the lead and in the gallery shares one note entry.

## The fit and the cache

The catalogue attempts every candidate in `scripts/g3_catalogue.py`:

- exact curves are read from their homogeneous control polygons;
- sampled curves are read through a local cubic fit of their polyline;
- a branch that cannot be interpolated G3 — a cusp, a point at infinity, a
  singular handle solve, or a deviation over 5% — is rejected and named.

The span solve (`quintic_g3` in `scripts/g3_showcase.py`) fixes the endpoints
and tangent directions, solves the two along-tangent components for the
curvature-rate at both ends, and grids the two handle lengths for the smallest
sampled deviation. The speed floor rejects a span that nearly stops inside.

The fit is cached at `workbench/g3-catalogue-cache.json` (gitignored, about
2 MB), keyed by `FIT_VERSION` plus a hash of the fit sources. The first run
after a fit change takes about **3.4 minutes**; later page rebuilds read the
cache in about **3.6 seconds**. Bump `FIT_VERSION` when the span solve or the
speed gate changes.

## Reproduce it

From the repository root:

```sh
# 1. Fit every candidate, write the catalogue page/JSON and the cache.
.venv/bin/python scripts/g3_catalogue.py

# 2. Build the one-page showcase and the notes (cache hit after step 1).
.venv/bin/python scripts/g3_showcase.py

# 3. Build the standalone gallery and the tightest-span diagnostics.
.venv/bin/python scripts/g3_handover.py

# 4. Refresh this document's counts and HTML twin.
.venv/bin/python scripts/g3_showcase_doc.py

# 5. Add the page bars and check the claims.
.venv/bin/python scripts/hub.py
.venv/bin/python -m unittest discover tests
.venv/bin/python scripts/recheck.py
```

The catalogue's JSON is the machine-readable record;
`workbench/g3-showcase.html` is the page; `workbench/g3-notes.html` is the
error tables; `workbench/g3-handover.html` is the standalone fallback copy;
`workbench/g3-diagnostics.html` is the ringed set.

## Counts

<!-- counts:start -->
| | |
|---|---|
| candidates attempted | 232 |
| admitted | 154 |
| G3-complete | 154 |
| smooth handover | 124 |
| complete with a declared feature | 30 |
| cubic-native rows | 22 |
| figures on the showcase | 0 |
| lead figures (cubic + quintic + cusp + deviation) | -154 |
| gallery figures | 154 |
| quintic-required lead | 5 |
| cusp cards | 0 |
| deviation cards | 0 |
<!-- counts:end -->

## What is still open

- **The cubic-first fitter is not universal yet.** The LAC source is corrected
  and the five quintic-required curves are labelled with reasons, but the
  catalogue still has a quintic carrier for curves that are not cubic chains.
  A general cubic-span attempt that records its own failure is the next code
  task.
- **The other LAC chains are G1, not G3.** Fig. 6 (S44) is the genuine cubic
  G3 chain; the rest of the recovered LAC spans have tangent gaps up to
  `0.19°` and curvature gaps up to `1.3e-4`. A cubic G3 construction for them
  is open.
- **The 1e-5 source tolerance is declared, not universal.** Exact
  constructions keep `1e-9`; a measured source gets the precision of its
  data. The page prints the measured gap either way.
- **Smooth is a subset.** The gallery includes curves complete with a declared
  cusp or node. The smooth-handover count is the list to give an editor
  without a caveat.
- **The page is about 5 MB.** The cache makes it cheap to generate, not
  necessarily cheap to open. Lazy-loading the gallery by group is the next
  presentation improvement.
- **No push or deploy is implied.** The local page is the authority; the
  public URL stays private.

## Keeping this document current

The Markdown is the source; the HTML twin is generated, never hand-edited.

1. Edit `docs/G3-showcase-docs.md` (prose and structure).
2. Run `.venv/bin/python scripts/g3_showcase_doc.py`.
   - It fills the **counts** block from the catalogue JSON and the showcase
     page.
   - It stamps the updated line with the date and commit.
   - It writes `docs/G3-showcase-docs.html` and embeds the Markdown's SHA.
3. Run `python -m unittest tests.test_g3_showcase_doc`; it fails if the HTML
   twin or the counts are stale.

When the showcase changes, run the page generators first, then the doc
generator, then the hub. Do not edit `docs/G3-showcase-docs.html` by hand.
