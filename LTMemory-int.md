# LTMemory-int — long term memory

Read this first, every session. It exists so a new session can be useful in two
minutes, and so the same ground is not dug twice.

## Read in this order

1. **this file** — the map and the invariants.
2. `state/ACHIEVEMENTS-int.md` — every result we have, with the command that
   re-derives it. Start a session with `.venv/bin/python scripts/recheck.py`.
3. `state/HANDOFF-int.md` — current truth, what is in flight, what is next.
4. `goals.md` — the long arc: plant-forms → ornament-forms.
5. `workbench/workbench.html` — the pages, chosen by intent.

Nothing else unless the action names it. `docs/HANDOVER.md` is deliberately long.

## The map

| path | what it is |
|---|---|
| `curve_lab/` | the engine: `Design`, `Segment`, `Piece`, clearance, fillet, junction |
| `curve_lab/measure.py` | **the one exact core**: grid, bend, arc, inflections, closest, in `Fraction` |
| `web/server.py` | the app: auth, rate limit, `/api/render` |
| `workbench/` | the input pages, one per idea; each has one generator |
| `workbench/ph_math.js`, `workbench/ph_nth_panels.js` | the shared page JavaScript, written once by `scripts/build-pages.py`; the pages load these, they do not inline them |
| `workbench/plate_math.js` | the plate maths in JS: character rails, the closing caps, cross/leaf/arch/frame |
| `workbench/real-curves.json` | the 28 saved curves; the lab inlines it and a test compares the copy with the file |
| `scripts/plates_export.mjs` | the book plates in JS: SVG, 300 dpi PNG, gallery |
| `workbench/operator-list.json` | every stored curve as a button, written by `scripts/operator_list.py`; a browser with no list is seeded from it |
| `scripts/` | the generators, the doc builders, and the checkers |
| `scripts/build-pages.py` | rebuilds all eight pages that load the shared JavaScript, then the hub |
| `scripts/exact_numbers.py` | audits every stored record's grid and bend against `curve_lab/measure.py` |
| `scripts/crossing_audit.py` | audits every stored curve's crossing-pair count |
| `scripts/check-saved.mjs`, `scripts/check-rails.mjs` | the headless page checks; run with `scripts/test.py --browser` |
| `docs/` | prose that mkdocs builds; `docs/PH-INTEGER.md` and `docs/HUB.md` are generated |
| `goals.md` | the long arc: plant-forms → ornament-forms; endings, lattice marks, branches |
| `state/` | `HANDOFF-int.md`, `ACHIEVEMENTS-int.md`, `BACKLOG-int.md`, `monitor.log` |
| `founder/` | screenshots and notes, tracked on purpose so they are backed up |
| `tests/` | the suite; `scripts/test.py` runs a fast subset by default |
| `pythagorean-spiral/` | the exact spine layer: rational turns, no floating point |

## Page ↔ generator

Every workbench page is built by one script. If you change a page, change its
script; never the HTML.

| page | generator |
|---|---|
| `workbench/generators.html` | `scripts/generators.py` |
| `workbench/euler-match.html` | `scripts/euler_match.py` |
| `workbench/integer-cubic.html` | `scripts/integer_cubic.py` |
| `workbench/integer-g2.html` | `scripts/integer_g2.py` |
| `workbench/integer-g2-editor.html` | `scripts/integer_g2_editor.py` |
| `workbench/integer-g2-piece.html` | `scripts/integer_g2_piece.py` |
| `workbench/quadratic-s.html` | `scripts/quadratic_s.py` |
| `workbench/pythagorean-families.html` | `scripts/pythagorean_families.py` |
| `workbench/euler-square.html` | `scripts/euler_square.py` |
| `workbench/hearts.html` | `scripts/hearts.py` |
| `workbench/catenary.html` | `scripts/catenary.py` |
| `workbench/primal.html` | `scripts/primal.py` |
| `workbench/principles.html` | `scripts/principles.py` |
| `workbench/spine-sheet.html` | `scripts/spine_sheet.py` |
| `workbench/branch-points.html` | `scripts/branch_points.py` |
| `workbench/piece-model.html` | `scripts/piece_sandbox.py` |
| `workbench/fleur-study-01.html` | `scripts/study_01.py` |
| `workbench/ornament-board.html` | `scripts/board/build-board.mjs` |
| `workbench/workbench.html` (the hub) | `scripts/hub.py` + `workbench/manifest.json` |
| `docs/PH-INTEGER.md` + `.html` | `scripts/ph_doc.py` |

Two pairings have mismatched names (`piece-model`, `fleur-study-01`); they are
listed here rather than renamed, because the scripts are referenced elsewhere.

## The checkers

| command | what it proves |
|---|---|
| `scripts/recheck.py` | the claims re-derived from scratch; writes `state/ACHIEVEMENTS-int.md` |
| `scripts/test.py` | the fast suite; `--full` for everything, `--browser` to add the page checks |
| `scripts/build-pages.py` | rebuilds every page that loads the shared JavaScript — **run after editing `ph_math.js` or `ph_nth_panels.js`** |
| `scripts/exact_numbers.py` | every stored grid and bend equals the exact core (`--write` repairs) |
| `scripts/crossing_audit.py` | every stored crossing count equals the router (`--write` repairs) |
| `scripts/operator_list.py` | rebuilds the button list from the stored records |
| `scripts/check-saved.mjs` | the saved-curve buttons seed, repair, undo and load |
| `scripts/check-rails.mjs` | rails draws, and the complementary controls exist, on five pages |
| `scripts/hub.py` | rebuilds the hub and every page's bar — **run after any page generator** |
| `scripts/monitor.py` | tells a local failure from a network one |

## Working rules learned the hard way

- **The page is the evidence, not the source.** A control that is correct in
  `scripts/` and stale in the browser looks broken; `scripts/build-pages.py`
  plus `tests/test_page_assets.py` exist for that fault.
- **A failed read must never become a write.** The saved-curve store keeps a
  backup and a mirror, and refuses to treat a damaged value as an empty list.
- **Tag a page that works.** `page-works-2026-11-16` is the first; a `git tag`
  after a verified page is cheaper than re-fixing it.
- **One number, one definition.** Grid is grid; the crossing count is *crossing
  pairs*, not places; a triple point is three pairs.

## One server

```sh
.venv/bin/python scripts/serve.py        # http://127.0.0.1:8003
```

Start it at the top of **every** session; it is idempotent, so running it
when it is already up prints "already serving" and exits 0. It serves the repo
and redirects bare page names (`/catenary.html`) to
`/workbench/catenary.html`. Do not start a second `http.server` — 8003 is the
one, and ports 8000/8001/8002 belong to other projects.

## Browsers and links

Two Chromes, one app. The default profile is the expensive one; the throwaway
profile at `$TMPDIR/chrome-curve` is for workbench pages and has no extensions,
no sync. It does **not** restore a session; it opens one local page,
`workbench/tabs.html`, listing only the tabs saved for the current focus.

| want | do |
|---|---|
| workbench pages in the light browser | Dock app `Curve Lab Browser`, or `scripts/chrome-curve.command` |
| save the tabs you have open as the focus set | Dock app `Save Curve Tabs`, or `scripts/chrome-curve.command --save` (writes `workbench/tabs.html`) |
| reopen that set | launch normally, or `--saved`; it opens the one local page |
| the default focus pair | `--default` (the lab and the book gallery) |
| one link in the light browser | `curve-open <url>` (`~/bin`, on PATH) — also takes `catenary.html` |
| your real Chrome while the light one runs | `chrome-main [url]` (`~/bin`) |
| a link in this chat | click it; it goes to the default browser (main Chrome) |

- Both Dock apps are in `~/Applications` and only hand off to the repo launcher:
  `Curve Lab Browser` opens the saved-tabs page, `Save Curve Tabs` runs `--save`
  and notifies (a .app has no terminal). The save app's snapshot excludes the
  saved-tabs page itself.
- The saved-tabs page is generated and ignored by git; the URL snapshot is in
  `~/.config/curve-lab/tabs.json`. Saving reads the light profile's debugging
  port (9224), so an instance started before the port was added must be
  relaunched once.
- The Dock's Chrome tile activates **whichever instance is running**, because
  macOS identifies the app by bundle, not by `--user-data-dir`. With the light
  profile up, that tile brings the light window forward. `chrome-main` is the
  way round it.
- **Do not run both.** Memory is additive: 2026-11-04 measured main Chrome at
  3362 MB/31 procs plus the light one at 667 MB/12 procs, 2.3 GB of swap on an
  8 GB machine. Quit the light one when the work is done.
- **`!command` works in the OpenCode prompt** — it runs as a shell command. Two
  early attempts failed because text had been prefixed before the `!`
  (`curve-open $ !curve-open …`), not because the prefix is unsupported; the
  bare `!curve-open https://example.com` is the form that works.
- Chrome settings that keep a stray launch cheap: `chrome://settings/onStartup`
  → *Open the New Tab page*, `chrome://settings/performance` → Memory Saver on,
  `chrome://settings/system` → background apps off.

## Invariants

- **Exact means Fraction.** Anything claiming exactness is computed in
  `fractions.Fraction` and asserted integral before it is drawn.
- **Every percentage is an error**, as a share of a stated reference. Where a
  number is not an error, say so in words.
- **A curve is cheap exactly when it has a singularity** — a node, cusp or
  triple point. Smooth curves (squircle, heart) are not rational and cannot be
  made exact.
- **One grid per curve** for now; the grid is a factorisation problem, not a
  size problem.
- **Enumerate the source, do not recall it.** When a page claims a catalogue,
  diff the page against the tables that own it (`generators.NAMED`,
  `heart_forms.FORMS`, `curve_lab.presets`) and render from them. We once
  shipped a limaçon labelled "bean" while the exact bean sat in the table.
  A curve drawn from memory is a bug, even when it looks right.
- **Say where a thing fails.** Three figures on `hearts.html` are recorded as
  broken rather than tuned to look acceptable.

## Already settled — do not redo

- `from_pairs` agrees with `from_hermite`; the half-angle bug is fixed.
- Degree is `n = deg h + 2 max(deg u, deg v) + 1`; quartics and sextics need `h`.
- The square-discriminant route gives 0 of 17,168 hits on the rung ladder. Dead.
- PH does not buy integer milestones; `mⁿ` is the floor and PH costs 3 or 15.
- One clothoid cannot do G2 (Bertolazzi–Frego); two or three can.
- Clothoid chains cannot cross a cusp; the roulettes keep 9–63% error.
- The bean, pear, piriform, trifolium and cruciform are rational and exact; the
  heart and the squircle are not.
- The 3-4-5 ladder is fine to 3125: 350 rungs, median gap 0.14°.
- A log spiral's constant-width offset is **not** a log spiral; the angle drift
  grows with d/r. Its exact partner is scaled *and* rotated, so the width grows
  with the radius — the only exact variable-width stem we have.
- A parabola's parallel is **not** a parabola; the involute of its evolute is
  exactly the parallel family, which proves rather than denies it.
- In the p-triple plane, fixed a and fixed b are hyperbolae whose integer points
  are factorisations; fixed m is a parabola, not a hyperbola.
- Several grids can share one design: they compose by lcm (1, 1/5, 1/25 → 25).
  Per-span grids cost 5^k: fine to six spans, unusable by twelve.
- The Euclid family chain is integer at scale 1 and C1 everywhere; its curvature
  exponent drifts to -4/3, so it is a generalised Euler spiral in the limit.
- A PH curve's offset is exact and rational: `O = C + d·(−y', x')/σ`, in
  `curve_lab/ph_offset.py`. On `integer-105` the first interior lattice hit is
  **grid 3360 at t = 1/2** (32× the pitch 105); the rails share that grid only
  at **d = 41/1120**. The curve is not symmetric, so its midpoint is a branch
  station, not a mirror line. Cubics are the export step, not the working form.

## Open

- **Integer Bézier:** exact cubic and G2/Piece work is done; the n=2 triangle
  chain, ribbon width and the full cubic catalogue are open. Levien is
  background.

- The heart half (Fig. 3/4 on `hearts.html`) drifts at 11.7% — the sample path
  has a 0.5-unit jump at the lobe tip, which is where the error comes from.
- Double tangency: the model is rotation *plus* placement; no solution yet.
- The Gerono leaf: the double-tangent line is right, the arc choice is not.
- **Offsets are drawn nowhere.** Every curve here will need an offset set, and
  the page only asserts "rational, exact" in a table. The PH integer curve now
  has its exact rail (`integer-ph-rail.html`); the conics, LACs and sampled
  curves are still unbuilt. The tiers decide it: PH
  curves offset exactly, rational quartics need fitting, sampled curves can only
  be fitted from samples. Nothing has been pushed through `curve_lab/offsets.py`
  yet, so we do not know which of the twenty-one are safe to give a width.
- **Plant-form arc.** `goals.md`: stalk → two-sided offsets → flower / seagrass
  / cone terminal (R = 2 × offset) → integer-lattice growth marks → branches
  (lower bigger than upper) → ornament-forms. No bare tip.
