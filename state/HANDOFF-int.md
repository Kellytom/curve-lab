# curve-lab handoff

**Updated:** 2026-11-04
**Use `/fhandon` to resume, `/fhandoff` to refresh this file.** The commands are
project-scoped: open OpenCode in this repository to use them. They are not
global and do not appear in `grid-8` or `ornaments`.

## If you are reading this first

Read `LTMemory-int.md` before this file. Then run, once each:

```sh
.venv/bin/python scripts/serve.py     # idempotent; http://127.0.0.1:8003
.venv/bin/python scripts/recheck.py   # 14/14 proves nothing has slipped
```

## Objective

Turn curve-lab into a usable design tool with exact clothoid geometry, a
200 × 250 mm sheet, +y up, and class I/II cap families. A local MVP and a public
remote MVP now exist.

## Birds-eye view — 2026-11-04

- **Exact integer cubic family:** finished, documented and tested. Pythagorean
  triples give integer controls; the 3-4-5 base and ten triples are mapped.
- **G2:** the mirror chain passes all ten triples; the scale-1 asymmetric pair
  is exact; a G1 fallback is recorded. The editor is a probe, not a solver.
- **Piece/Trace:** cubic spans now travel through the actual model. The pair and
  the C–A–B chain both render and pass clearance, with declared G2 contacts.
- **Pythagorean field:** the workbench plots rays, all fixed-Euclid-`n` and
  fixed-Euclid-`m` families in the bound, the Fässler `N≈1450` cluster, the
  `n=20` 800 band, and the `n=2` 43.6°→4.0° sweep. A 500 box has 22 downward
  fixed-`m` curves and 15 right-opening fixed-`n` curves.
- **Open:** the n=2 chain is rendered (integer C1, rational G2 only); ribbon
  width and a fitted offset are the next model gaps; the full cubic catalogue
  is not built.
- **Levien:** background only. The fitted parallel Bézier remains a fitted
  option; there is no active Levien exact-integer route.
- **Process (2026-11-04):** `state/READING-int.md` is now the reading authority —
  Tier 0 is ~750 lines and no source, Tier 1 is the scope anchor
  (`SPEC.md`, `docs/PROJECT.md`, `goals.md`, `docs/PHILOSOPHY.md`). `/fhandoff`
  requires a `Proves:` finish line, a rejected-path line and a `TODO.md` tick;
  `/fhandon` commits its own work and backgrounds the server start. The next
  block was written under the new contract.

## Current state

- **Local app:** `http://127.0.0.1:8000/` — probe 2026-11-02: responds **404 at
  `/`** (up, but no index at the root path). Start with
  `.venv/bin/python web/server.py`. Auth is unset locally; the deployment
  requires the token.
- **Workbench server:** ONE process, `scripts/serve.py` on **8003** — probe
  2026-11-04: **200** at `/workbench/workbench.html`; `/health` is **404** because
  this is the static workbench server, not the app. Redirects a bare page name
  (`/catenary.html`) to `/workbench/catenary.html`. Starting it twice is safe.
- **Docs book:** `http://127.0.0.1:8020`, `mkdocs serve`, strict clean. Neither
  the book nor the workbench is deployed.
- **Remote:** carried from 2026-10-30, not probed this session (the URL is
  redacted in this file, so there is nothing to curl). `https://<your-service>.run.app` — Cloud Run,
  project `<your-gcp-project>`, region `us-central1`, service
  `clothoid-web`, revision `clothoid-web-00006-zrx` (carried). HTTP **401
  without the token** at 2026-10-30 (probe); a thin app deploy takes
  ~30 s.
- **Access:** HTTP Basic with a shared token; every route except `/health`.
  Token in Secret Manager `clothoid-token`, local copy
  `~/.config/<app>/token` (outside the repo). `/api/render` is limited to
  60/min, burst 20, per client address; excess is 429 with `Retry-After`.
- **Remote limits:** min `0`, max `1`, 1 vCPU, 512 MiB, concurrency `2`,
  60 s timeout. The Cloud Run IAM policy still allows unauthenticated ingress;
  the application token is the gate.
- **Build split (done):** engine base `clothoid-engine:2026-10-26` built in
  6m43s and pushed; the thin app deploy took 30 s (revision
  `clothoid-web-00004-nwx`, commit `eb67f4c`). App deploys now upload ~100
  files and skip the C++ compiler.
- **Budget:** `$1/month` alert (`curve-lab guardrail`) at 50/90/100%; alerts
  do not stop spend. Re-confirmed against billing account
  `<your-billing-account>` at 2026-10-25 23:45 UTC (carried).
- **Parity:** carried — all seven comparisons passed at 2026-10-26 00:02 UTC
  (not re-run in the handoff).
- **Local tests:** **305 pass** (1 skipped), carried from the full run
  2026-11-04; no code under `web/`, `curve_lab/`, `csrc/` or `tests/` differs
  from HEAD, so this handoff did not rerun them.
- **Git/probe (2026-11-04):** HEAD `d269afa`; the only worktree entries are four
  untracked user files (`IMG_2832.JPG`, `IMG_4668.JPG`,
  `reference/fire/IMG_4238.JPG`, `state/monitor.log`). Nothing tracked is dirty.
- **Risks carried:** remote URL is redacted, so remote is carried from
  2026-10-30 at **401 without token**, not probed; parity is its own check; the
  n=2 chain is rendered but has no width yet.
- **Flowers sheet and stem library (2026-11-03):** `workbench/flowers.html` is
  the 8.5 × 11 print sheet — a sextic, b quintic, c cubic and d r5 clothoid in
  gold squircle vases, mm rulers, with 18 mm Euler-interpolated flowers
  (cardioid/trifolium/quadrifolium/astroid) at the tips.  `workbench/stem-library.html`
  is the 177-card labelled catalogue (S01–S109 and S118–S157 single stems; halves
  S166–S167 rotated 150°/90° CW; SM1–SM26 multiple stems, internal S110–S117 and
  S158–S177; 4 presets, 25 named, Euler 45/90, 3 spiral-turns, 31 LAC spines,
  4 full gestures + 2 halves, 80 combination cards (70 pairs + 10 doubles), 16 LAC plants + the SM17
  fractional p=1/4–1 series, the SM18 p=1/4–3 combined fan, and the SM19–SM22
  end-spacing studies — equal tip arc, simple fractions, log, Fibonacci-like —
  and the SM23–SM26 integer studies, including the 25- and 5-grid sequences
  that land exactly on n = 3125).  The boundary
  p=±0.5 stems are dropped from SM5/SM6, SM7/SM8, SM9, SM11, SM13–SM16; the
  p=±0.5 reference plates stay in the LAC group.  Doc: `docs/FLOWERS-int.md`.
- **Plant-form / ornament-form arc (2026-11-03):** `goals.md` is the long arc:
  stalk → two-sided offsets (2 × offset + breathing room) → flower, seagrass or
  cone terminal (two arcs R = 2 × offset meeting at the centreline) → marks at
  the integer-lattice hits (a pyramid on each rail) → branches with smaller
  curves, lower bigger than upper → ornament-forms. No bare tip. The focused
  next action is the integer n=2 triangle chain; the offset catalogue follows.
- **Focused todo (2026-11-03):** `TODO.md` — the expanded heart-forms page is
  already the 15-card set (`41f3d8c`); `hearts.html` now links to it so its five
  clothoid-heart figures are not read as the whole list.  The clothoid cut
  already has the full ± table contact Fig. 5 at 38.5° CW (`73b56a6`); a
  regression test now guards it.  The measured table gap is **0.00002** at
  40,000 chords; the request's 0.0003 is not reproduced.
- **Integer cubic family (2026-11-03):** `workbench/integer-cubic.html` is the
  dedicated page for the exact Pythagorean construction: for `a²+b²=c²`,
  `P0=(0,0)`, `P1=(a,−b)`, `P2=(2c−a,b)`, `P3=(2c,0)`; chord `2c`, arms `c`,
  tangent `−atan2(b,a)`. The 3-4-5 base is `(0,0) → (3,−4) → (7,4) → (10,0)`;
  ten triples and the 3125 slopes are on the page. `curve_lab/pyth_cubic.py`;
  `docs/INTEGER-CUBIC.md`; `tests/test_pyth_cubic.py`,
  `tests/test_integer_cubic.py`. This is not the Euler fit.
- **Integer G2 probe (2026-11-03):** `workbench/integer-g2.html` — mirror the
  symmetric cubic across each endpoint tangent, scale by the hypotenuse, and
  the three-piece chain has exact G2 at both interior joins. All ten triples
  pass; `curve_lab/pyth_g2.py`, `tests/test_pyth_g2.py`. Fig. G2 adds a scale-1
  asymmetric pair (tangent `(4,−3)`, curvature `−6/5`) and a G1 fallback with a
  measured curvature jump. This is not a general asymmetric solver.
- **G2 drag probe (2026-11-04):** `workbench/integer-g2-editor.html` starts at
  the exact scale-1 pair and reports live G1/G2/tangent/curvature/integer status
  when a point is dragged. Snapping is not a G2 solver; exact reset restores the
  pair.
- **G2 Piece/Trace (2026-11-04):** `workbench/integer-g2-piece.html` carries
  the scale-1 pair as actual `Trace(spans=...)` objects; SVG and
  `piece_clearance()` run directly on cubic spans, with the G2 join declared as
  a contact. `Piece` report: clearance ok, 0 violations, 1 allowed crossing.
- **G2 chain Piece/Trace (2026-11-04):** the same page now carries the C–A–B
  chain as three cubic-span traces and two declared contacts. Both reports are
  clearance-ok with 0 violations and 0 warnings; pair has 1 allowed crossing,
  chain has 2.
- **Pythagorean field plot (2026-11-04):** `workbench/pythagorean-families.html`
  plots all triples `c≤3500`, scaling rays, all fixed-Euclid-`n`/`m` families in
  the bound, the Fässler `N≈1450` cluster and the highlighted `n=20` 800 band;
  the `n=2` sweep runs from `(20,21,29)` at 43.60° to `(3245,228,3253)` at 4.02°.
  A 500 box has 22 downward fixed-`m` curves and 15 right-opening fixed-`n`
  curves; see `docs/PYTHAGOREAN-FAMILIES.md`.
- **n=2 triple-tangent chain (2026-11-04, this session):** the sweep is now a
  rendered curve. `curve_lab/pyth_chain.py` builds 52 integer cubic spans from
  53 arm vectors: `D_k = 2(T_k+T_{k+1})`, `P0..P3 = N_k, N_k+T_k, N_{k+1}-T_{k+1},
  N_{k+1}`. Every control point is an integer and every join has the *same
  derivative vector* `3T_k` on both sides, so the chain is C1 exactly. Curvature
  jumps 6.2% (median) / 26.1% (max) of the larger side — near-G2, not G2.
  Fig. C1 (first five triples, four spans) and Fig. C2 (all 52 spans) are on the
  page, with a table of tangents and nodes. `tests/test_pyth_chain.py` (14).
  **G2 is reachable and not integral:** per-node handle lengths `h_k` keep C1
  and reduce curvature continuity to `C_k(S-h_k) = C_{k+1}(S-h_{k+2})`, a
  two-step linear recurrence that drives all 51 joins to exactly zero — but the
  common denominator has 84 digits, so there is no usable integer grid. Integer
  C1 and exact G2 are different currencies here.
- **The sweep's law (2026-11-04):** the arm angle is algebraic, not logarithmic:
  `θ(m)=atan(2nm/(m²−n²)) ≈ 2n/m` (for n=2, `θ·m → 229.2°`; power fit
  `m^-0.988`, `R²=0.9999`). Along the chain `|κ| ∝ s^-1.238` (`R²=0.993`) — a
  spiral that is none of clothoid (`s^+1`), log spiral (`s^-1`) or circle.
- **Chain editor (2026-11-04, this session):** `workbench/pythagorean-chain-editor.html`
  is live — sliders for `n`, the `m` range, the step `S` and the handle rule,
  a per-node G2 toggle, and a grid-extent guesstimate printed before drawing
  (`S for a 200,000-wide sheet: …`). Registered in `manifest.json`, built by
  `scripts/pyth_chain_editor.py`. Every number is recomputed in the browser from
  the same rules as `curve_lab/pyth_chain.py`.
- **Width measured (2026-11-04, this session):** Fig. C3. The smallest radius of
  curvature on the n=2 chain is **269** against a length of 246,000, so the legal
  offset is ~0.1% of the length: this is a **spine, not a stem**. Rails exist
  while `d < 1/|κ|`; at 2.2× the radius the rail inverts at the tight end.
- **`n` is a tightness dial (2026-11-04, this session):** Fig. C4, same 4°–44°
  band. Minimum radius **58 → 269 → 5,291** for `n=1,2,5`; curvature jump
  **12.4% → 5.0%** median; the law softens `κ ∝ s^-1.24 → s^-1.06`. Small `n`
  gives the tight, stem-like curve.
- **Ten primitive seeds (2026-11-04, this session):** `pyth_triples.primitives(10)`
  and a table on the families page — the ten smallest primitive triples with
  their `(m,n)`, angle, family `n`, spans and min radius. 3-4-5 is `(2,1)` →
  family `n=1`, radius 58: the natural first stem.
- **Offset catalogue (2026-11-03):** `workbench/stem-library-offset.html`,
  OffS1–OffS12, generated by `scripts/stem_offset_library.py`.  Six formulaic
  cards, three parallel conics (**parallel parabola/ellipse/hyperbola**), two
  LAC chain rails, and a two-stalk card; every card carries the ±d rails and
  the 2d separation.  **Levien's fitted cubic-Bézier parallel** is implemented
  in `curve_lab/parallel_bezier.py` and shown beside exact PH and the LAC rail;
  it reports fit error, cusps and clamps and is never called exact.  Tests:
  `tests/test_stem_offset_library.py`.  The next layer is endings.
- **Plant-form proof (2026-11-03):** `workbench/plant-forms.html` — one stalk
  with two rails, the **cone terminal** (two arcs R = 2 × offset meeting at the
  centreline), seagrass and flower detail endings, pyramid growth marks on both
  rails at the integer-grid hits, and three branches (lower bigger than upper,
  each with an ending).  Geometry in `curve_lab/plant.py`; generator
  `scripts/plant_forms.py`; tests `tests/test_plant.py` and
  `tests/test_plant_forms.py`.  The next layer is ornament-forms.
- **Backburner (2026-11-03):** `state/BACKBURNER-int.md` — B01 parks
  bounding parabolas (curve/curve intersection, boolean path ops; artifact
  `workbench/bounding-parabola.html`) until a real intersection need appears.
  B02 records the 2021 Euler-spiral → cubic handle-parabola rule as a candidate
  fitted option: chord-normalized left `x = 1/3 - (3/4)y²`, right
  `x = 2/3 + (3/4)y²`, handles at the tangent intersections; `O(n^5)`.
  B03 (2026-11-04) parks the machine-refresh problem: swap residue must be
  measured (`sysctl vm.swapusage`, `memory_pressure`, `ps`) before blaming it,
  and no browser is to be held open between screenshots.
- **Levien integer sandbox (2026-11-03):** `workbench/levien-integer.html` +
  `scripts/levien_integer.py` — parabola, y=x²/2, y=x²/4 and one integer cubic;
  source, exact normal rails, Levien cubic fit, integer lattice and near-integer
  hit counts.  Parabola sources have the known integer points; exact rails are
  sparse; Levien remains PASS as fit / FAIL as exact integer.  The page is the
  viewing tool for choosing the reverse-engineering variables.
- **Euler-section proof (2026-11-03):** `workbench/euler-sections.html` +
  `curve_lab/euler_polygon.py` + `scripts/euler_sections.py` — six smooth C
  sections — cycloid, astroid, semicubical, tractrix, heart, squircle, and one
  branch section each of bicorn, nodal, Tschirnhausen and piriform 2× — as exact
  p-triple polygons, rational miter rails, and cubic seams.  The exact polygon
  is A−; the ideal C curve stays C; the converted section is B.  Heart is
  refined to 0.076; the looped branch sections have node/loop splits.  Levien
  integer snapping: PASS as fitted, FAIL as an exact integer route.
- **C-family p-triple route (2026-11-03):** the p-triple spine is the solved
  plan route — exact rational Euler polygon, rational miter rails
  (`ribbon.rails`), cubic drawing with measured margin.  The C families
  (cycloid, astroid/hypocycloid, semicubical, tractrix, heart/squircle,
  looped/cusped rationals) are converted by choosing a triangle angle,
  quantizing the turn schedule, splitting at cusps, building the `Spiral`,
  offsetting, and drawing cubics.  The direct `build_rail` probe is a separate
  engine path, not the base plan.  `TODO.md` now carries the achievement ledger
  and this workstream.
- **Todo twin and grades (2026-11-03):** `TODO.md` is the focused checklist;
  `workbench/todo.html` is its generated read-only twin (`scripts/todo.py`,
  progress bar and grade matrix).  The provisional grades: **A** lines/arcs,
  PH, Pythagorean, cone; **B** LAC/Euler/log spiral, conics, rational
  non-cusped, catenary, general cubic/Levien; **C** cycloid/astroid/
  semicubical/tractrix/heart/squircle/cusped-looped rational.  **C is not a
  deletion:** those families are kept as ending/flower material and are
  converted with the p-triple Euler route; the p-triple conversion is the next
  action.  **Modulated width** (the former Stage IV) is
  **Advanced, not D**: variable width, not a parallel offset, and not a side
  issue; it gets its own proof after the ornament grammar.  The Levien integer probe found real-valued control points
  on an integer cubic; exact integer routes remain PH/arcs/Pythagorean.
- **Bring-up coverage (2026-11-03):** `goals.md` now carries the parallel/offset
  and integer inventory. First gaps: the offset catalogue and the parallel
  conics — **parallel parabola**, ellipse, hyperbola; the evolute page shows the
  evolute, not a parallel-parabola card/rail. LAC and Stage II are wired as
  sources; Stage III is terminals/straight spines and the former Stage IV is now **Modulated width**, explicitly
  non-parallel.  **Modulated width** (the former Stage IV) is the **advanced
  width-modulation track**, now at `workbench/modulated-width.html`; not a side
  issue and not a parallel-offset source. PH offsets are exact but
  not yet catalogued. The offset tiers are: exact PH/arcs; exact-in-family log
  spiral and circle involute; **Levien's fitted cubic-Bézier parallel**
  (`reference/external/parallel-beziers.html`, O(n⁶), not exact); the LAC/chain
  rail; and sampled curves. The offset catalogue and the plant-form proof are now built;
  the focused next action is ornament-forms.
- **Evolute parallel sandbox (2026-11-03):** `workbench/lac-parallel.html` +
  `lac-parallel.js` — the LAC base and the classical families (cycloid,
  epi/hypocycloid, ellipse→astroid, astroid, circle involute, catenary→tractrix,
  parabola→semicubical, PH cubic), the evolute `E=C+ρN`, and the exact
  two-sided offsets `P_d=C+dN` (the same family as the involutes of E between
  evolute cusps); family/α/k/b selects and `?family=&alpha=&d=`; a full-evolute
  inset sits under the fitted base/offset frame.  Hub now 26 pages.
- **Spine tests:** 143 pass at the 2026-10-30 run (139 plus four placement
  tests).
- **Promotion gate 1–3 (2026-10-30, this session):** `curve_lab/spine.py`
  reads a `pythagorean_spiral` chain through its own cubic spans and returns an
  ordinary `Design`/`Trace`/`Piece`; every fitted join lands on a chain anchor
  (worst 2e-14 units). `design_from_spans` now carries a span-to-span tangent
  jump as a segment `corner` (the apsis case), which it previously dropped.
  `scripts/spine_sheet.py` writes `workbench/spine-sheet.html`: a curl plus a forked
  branch on 200 × 250 mm through `svg.document`, with a declared contact at the
  fork (`merged` 1, 0 violations; the same gap fails without the contact).
  Tests: `tests/test_spine.py` (10). **Gate 4 is met under the operator's
  fidelity rule**: worst span-end drift at most 1.6% of study height; the chain
  study at 0.5° measures **1.29%**. Commits `3f7a603`, `413dc86`, `5ef5359`,
  `97e83d5`. Rule and caveats: `docs/FIDELITY.md`.
- **Git:** HEAD `cf5fcb6` (2026-11-02). Tree clean; untracked are three
  photographs (`IMG_2832.JPG`, `IMG_4668.JPG`, `reference/fire/IMG_4238.JPG`)
  and `state/monitor.log`, which is a log and stays untracked.
- **Untracked user file:** `out/play-template.svg`; leave it alone.
- **Layout (2026-10-31, this is the thing to know):** the generated pages moved
  out of `docs/` into **`workbench/`** — 16 pages, one generator each in
  `scripts/`, plus `spirals/`, `terminals/` and the three.js vendor copy. The
  five state files moved to **`state/`** (`HANDOFF`, `BACKLOG`, `SESSIONS`,
  `WORK`, `STATUS`); this file now lives at `state/HANDOFF-int.md`, not
  `docs/HANDOFF-int.md`. `docs/` is prose only: 22 markdown including `index.md` and
  `README.md`, plus `HANDOVER.html`.
- **Docs book:** `mkdocs.yml` at the repo root builds `docs/` into `site/` with
  the material theme and `strict: true`. `mkdocs` and `mkdocs-material` are
  pinned in `requirements-dev.txt`; `site/` is ignored. The state files are not
  in the book, on purpose.
- **Docs:** `docs/HANDOVER.md` is the durable reference;
  `docs/HANDOVER.html` is its browser mirror.
- **Public docs (2026-10-29):** `github.com/Kellytom/clothoid-docs`, site
  `kellytom.github.io/clothoid-docs/` — the Markdown, generated HTML, spine
  package, examples and context pages, with photographs and deployment
  identifiers removed. Built by MkDocs Material; sitemap, robots and
  `llms.txt` present. Pushed to `baf0bca` on 2026-10-30.
- **Joins (2026-10-30):** all 150 terminals carry `anchor` and `heading`
  (`43e3fc6`); `attach.py` places a cap on a terminal seam (gap 0, reach median
  0.98 of the cut) and a recovered end on a chain node (gap 0) (`79819ea`).
- **Veil (2026-10-30):** the v1/v3 experiment is reverted; the operator's
  two-version gate (v2 lighter than v1, both solved to the 85 per cent peak) is
  green again. `pythagorean-spiral/docs/veil3d.html` remains a three.js study
  with clustered puffs and an additive-light slider (`c00183f`), not product.

## 2026-11-02 — the curve day

One long session, almost entirely on the `generators` page and the mirror-to-
tangency construction. Everything below is committed.

- **`workbench/generators.html`** — 23 named curves, 21 exact, each checked
  against its own equation by `tests/test_named_curves.py`. Bean, pear,
  piriform, trifolium, bow, cruciform and both lemniscates are rational and
  exact; the heart (genus 4) and the squircle (genus 3) are not. The
  cruciform's exact arm now runs `u ∈ [1/5, 4/5]`, so the four mirrors read as
  a cross; the control scale stays **1250** (milestones 1,081,080).
- **The rule the page teaches**: a curve is cheap exactly when it has a
  singularity to run a line through.
- **Integer hits** are a factorisation problem, not a size problem. Bean: 4
  hits at grids 12, 48 and 156 alike; 16 at 273. Under 3125 the twenty-one
  exact curves go from 114 hits at their control scales to 843 at their best.
- **`workbench/euler-match.html`** — every exact curve rebuilt as an Euler
  polygon, one clothoid, and a chain of clothoid spans. One clothoid fails
  (35–72%) because a single linear-curvature law cannot follow a sign change;
  spans work at 0.44–1.1%. Cusps defeat all of them (9–63%), as the literature
  says they must.
- **`workbench/hearts.html`** — a unit clothoid rotated until it kisses the y
  axis, then mirrored. Fig. 1 and 2 are good. Fig. 3/4 now close on the lobe
  tip `(1.139028, 0.545330)`, where the two y-roots merge (`8y³−y²−1 = 0`,
  `x² = 1+y²`); the Euler polygon is 32 chords at **0.73%** of size with both
  ends within 0.003 units of the axis. The clothoid-span chain needs 32 spans
  for 1.44% (4 spans 8.21%) — that is now the open reading, not the sample
  path. Fig. 5 joins the two halves back into the whole heart; the ink halves
  share the cleft and the bottom, and the Euler halves meet within 0.005 units.
  The double-tangent table measures the closest two vertical-tangent contacts
  of one arc: 0.079 at 2 turns, 0.022 at 4, 0.0069 at 8, 0.0023 at 16 — it only
  tends to zero, so a finite arc has no exact double tangent.
- **`workbench/clothoid-cut.html`** (new, this session) — the eye is
  `(±√π/2, ±√π/2)`, the equal-arc cut is at the origin on the line between
  them, and the minimum-width box of one half is **0.898** at 150.5° (full pair
  **0.984** at 128.5°). The box edges are the two parallel support/tangent
  lines: a double normal, not a double tangent. Generator
  `scripts/clothoid_cut.py`; added to the hub.
- **`workbench/heart-forms.html`** (new, this session) — five heart curves to
  their true extent: Beutel sextic, cardioid (`r = 1+sin θ`, the one rational
  member), the `|x|^(2/3)` heart, the Fourier Valentine, and the polar heart
  after MathWorld. Generator `scripts/heart_forms.py`; test
  `tests/test_heart_forms.py` (5 forms, 5 figures). A catalogue, not a fit;
  the hub is now 22 pages.
- **`workbench/euler-square.html`** — eight arcs, curvature a tent, a tight
  square with G2 everywhere.
- **`reference/external/parallel-beziers.html`** — Raph Levien on offsetting a
  cubic, saved with attribution; the honest comparison for PH's exact offsets.
- **Rename**: the package is `curve_lab`, the directory `~/developer/curve-lab`,
  and internal documents carry `-int` for a future `-ext` twin. The **deployed**
  names are still `clothoid-*` on purpose.

## Queued after the heart fix

**Offsets.** The generators page claims "offset: rational, exact" in a table and
never draws one. That is the largest untouched idea in the curve work: every
stroke, ribbon and `Bundle` in the project is an offset. The tiers decide the
answer — PH curves offset exactly, rational quartics need fitting, sampled
curves can only be fitted from samples — so the deliverable is one figure and
one number per curve: offset by a stated distance, re-fit at the same degree,
report the error. `reference/external/parallel-beziers.html` is the fitting side
of that comparison, and `curve_lab/offsets.py` is where it lands.

## What changed this session

- Added `web/` MVP: stdlib HTTP server, static page, JSON editor, SVG preview,
  report, presets/caps, SVG/JSON download.
- Added `Dockerfile` with Debian C++ build and `python:3.12-slim` runtime.
- Added `.dockerignore`, `.gcloudignore`, `tests/test_web.py`, `web/README.md`.
- Deployed the container to Cloud Run via Cloud Build.
- Set min 0 / max 1, concurrency 2, 1 vCPU / 512 MiB, 60 s timeout.
- Created the $1 budget alert.
- Added project-scoped, focused `/fhandoff` and `/fhandon` commands, modelled
  on the existing `handoff`/`handon` pattern in `grid-8` and `ornaments`.
- Added `scripts/check-parity.py`, which compares the local and remote served
  assets, presets/caps, SVG and report. It passes.
- Opened the local and remote apps in Chrome tabs as the shared starting base.
- Added a **global** `/focus` command (`~/.config/opencode/commands/focus.md`)
  that moves any session into this repo and surfaces `next-fhandoff-int.md` without
  starting work, so `/fhandon` is reachable after a restart from any directory.
  `/fhandon` and `/fhandoff` stay project-scoped on purpose: they are hard-wired
  to this repo and should not appear in `grid-8` or `ornaments`.
- Made `/fhandon` faster to follow: it now opens with one sentence naming the
  focused action, and it uses headless Chrome/CDP for browser checks instead of
  looking for the desktop Review pane or Safari.
- Hardened the phone layout in `web/static/style.css`: zero-minimum grid
  tracks, `min-width: 0` on selects/inputs/status, wrapping action buttons, and
  tighter 430px padding. Headless Chrome at 390 × 844 and 320 × 844 shows no
  overflow in any state (cap-14, `cap-pt-9`, all four presets, width error,
  report shown). The original clipping did **not** reproduce in Chromium, so
  the hardening targets intrinsic-width/Safari cases; confirm on a real phone.
- Deployed the CSS fix: revision `clothoid-web-00003-r4m`; remote measures
  390/390 at 390 × 844 with the same control geometry as local; parity passes.
- Phone check on the Samsung: right edge confirmed clean, 2026-10-26. The
  temporary tunnel was closed after the check.
- Split the image: added `engine/Dockerfile` (C++ build + runtime base),
  `cloudbuild.engine.yaml`, a thin app `Dockerfile` (FROM the engine base), and
  `.gcloudignore.engine`; app `.gcloudignore` now drops `vendor/`, `csrc/`, and
  `scripts/`. Engine base built in 6m43s; first thin deploy took 30 s
  (revision `clothoid-web-00004-nwx`); parity passed.
- Added shared-token access and quotas: HTTP Basic on every route except
  `/health`, token in Secret Manager `clothoid-token`, and a per-address
  render limit (60/min, burst 20). Deployed as revision
  `clothoid-web-00006-zrx`; 401 without the token, 200 with it. Added
  `tests/test_auth.py`.
- **W01 done:** added `curve_lab/piece.py` (`Piece`, `Trace`,
  `render_piece`), extended `svg.document(..., groups=...)` for several named
  traces, and added `tests/test_piece.py`. The visual proof is
  `workbench/piece-model.html`, generated by `scripts/piece_sandbox.py`: one ribbon
  half, its two rails, its mirror, and an unmirrored guide.
- **W02 taxonomy.** Terminal is the umbrella; **cap** is a subset that closes
  the end without turning the stroke past **120°** (a tunable project choice,
  not a law). Caps: `butt`, `point`, `arc`, `round`. Tapers: `taper`, `cone`,
  `bulb`. A hairpin and the old wrapped bulb turn past the limit: *turned
  terminals*, not caps, and not built yet. `bulb` in the code is the Stage II
  width-law taper, not the wrapped ornament bulb.
- **W02 reopened.** Seven terminals now: `butt`, `point`, `arc` (5 mm dome),
  `round` (half-width dome), `taper` (four half-widths), plus `bulb` and `cone`
  on the two width laws recovered from the ornaments `stage-two` page
  (`w = ½(t(3−3t+t²)+12t²(1−t)³)` and `w = ½(1−(1−t)³)`, both G2 at the join).
  The old five are still cap geometry at either end of a ribbon. `Trace.terminals = (start, end)`
  takes a kind, a pair or a dict and round-trips through JSON; `render_piece`
  writes one named path per cap, reports each end with kind, reach and fold, and
  rejects a terminal on a folded ribbon or a trace without a width. `butt` adds
  no geometry, so W01 output is unchanged. `svg.document(..., linecap=...)` lets
  the piece ink use `butt` caps while the single-design default stays `round`.
  `workbench/piece-model.html` gained the labelled terminal strip (seven rows).
- **Junction object:** `curve_lab/junction.py` — `Junction(corner,
  branch_end, trunk_end, radius, widths)`, `.build()` returns a `Piece`, a
  declared `Contact` and a report (angle, trim, arc length, G1 join, 1/r step),
  `.check()` returns the clearance report with the merge already declared.
  Tests: `tests/test_junction.py`.
- **Contacts are model data:** `Piece.contacts` round-trips through JSON and
  `piece_clearance()` uses it by default. `Contact` moved to
  `curve_lab/contact.py` to keep the import graph acyclic.
- **Junctions started:** `curve_lab/fillet.py` gives the tangent-arc fillet
  at a corner (`corner_fillet`), plus `fillet_span()` to trim two straight
  spans and insert the arc. It refuses a radius that does not fit, collinear
  edges and doubled-back edges. This is G1 by construction: curvature still
  jumps at the touch points, so a trunk needs the clothoid blend next.
  `arc_segment()` turns the fillet into a circular-arc `Segment` + anchor, so a
  filleted run can be a normal `Design`. Docs: `docs/JUNCTION.md`; tests:
  `tests/test_fillet.py`.
- **Principle cards:** `reference/principles.json` holds eight cards — four
  primals, four archetypes — each with a gesture paragraph, exactly three
  numbers and a "not this" list. `scripts/principles.py` rebuilds
  `workbench/principles.html`; images attach by subject from `reference/manifest.json`
  (never hard-coded), so links cannot rot. `tests/test_principles.py` validates
  the cards, the corpus and the rendered page. Each primal card also carries a
  `check` block, and the tests assert the rendered grammar against it: segment
  count, maximum segment turn, maximum corner and end terminal. The board header
  links the page.
- **Primal first slice:** `curve_lab/primal.py` has one canonical grammar per
  element — earth (terraces with corners, taper), water (sweep and reversal,
  round), air (billowing arcs, round), fire (Euler tongue with a point). Render:
  `scripts/primal.py` → `workbench/primal.html`; tests: `tests/test_primal.py`.
  These are ahead of the gate on purpose and are sketches, not the four studies.
- **Section and Bundle:** `curve_lab/section.py` gives the read model —
  `Section(s, spine, tangent, width, left, right)` sampled by arc length, with
  left = `(-t.y, t.x)`. `curve_lab/bundle.py` gives the design box: a named
  set of full lines with an internal clearance and a footprint (sheaf, fasces,
  capital, acanthus leaves, fleur halves). `Bundle.check()` measures members
  only; the box is for placement, not clipping.
- **W03 first slice:** `curve_lab/grammar.py` ports study 01 from
  `ornament_set.js` as clothoid segments — straight runs, circle arcs and the
  petal's Euler span exact — with `Segment.corner` carrying the tangent jumps the
  old chain allows. All 12 nodes match the original within **0.030 units** (its
  3125-lattice snap). `scripts/study_01.py` writes `workbench/fleur-study-01.html`
  with the drawing and the node table. Not done: per-stroke terminals, the
  declared centre-seam contact, and studies 02–20.
- **Spiral parity:** `scripts/check-spirals.py` fits one clothoid per recovered
  cubic span (endpoints + tangents) and measures the worst distance to the drawn
  curve. All 586 Stage II spans fit. Median error per chord: `line` 0.00%,
  `euler` 0.01% (worst 0.12%), `arc` 0.02%, `logaesthetic` 0.01% (worst 0.16%),
  `member` 0.03%, `reflected` 0.03%. `hyperbezier` diverges as it must: 35.8%
  median, worst 78× chord. Writes `workbench/spirals/parity.json`.
- **Spike exponent dial (2026-10-28):** `pythagorean-spiral` now takes
  `power` in `design.spiral/lobe/curl` — turns run `k**p`, the clothoid at
  p = 1 (frozen digest test proves the old curl bit for bit), and every
  integer p closes exactly because the reversal cancels the same integers.
  `--power` on the CLI. **Join/fork landed too:** `Spiral.knots()`, `fork()`
  (angle as triangle steps or quarter turns, never degrees) and `joined()`
  asserting exact point and vector equality; the explainer's branch figure is
  now drawn by them. **Rails landed too:** `ribbon.py` offsets a chain exactly
  (miter of rational lines) with a rational taper, and `docs/GALLERY.md` +
  `docs/gallery.html` put six studies on it -- catenary, drapery, Corinthian
  volute, violin scroll, acanthus, fleur-de-lis -- each a filled ribbon. The
  float hybrid landed (`hybrid.py`): exact plan, double ink, 20,000 chords in
  0.03 s, closure still exact; `docs/EXTREMES.md` tests a 90-degree leaf corner
  (exact cusp) and the angles the lattice can hit. **Placement started:**
  `place.py` rotates inside the rational group, fits a 200 x 250 page and emits
  integers; `docs/TRANSFER.md` carries the 36 caps onto the new curve (median
  0.44% gap) and reports that the 150 terminal ends have no frame stored. The
  cloud study is `pythagorean-spiral/docs/CLOUD.md` + `cloud.html`: a toned
  photograph and a toned fresco under four layers of exact ellipse billows;
  the edge filter is optical, the geometry is rational. The veil strength is
  solved from the artwork area (`solve_veil`): only the bottom layer covers the
  works, to 5 per cent total, and the upper layers keep their body and stay off
  the work. Settings in `pythagorean-spiral/docs/veil-settings.json`. The solve
  is analytic, so a rendered-contrast check is still wanted. 127 tests there. This is the exact **spine
  layer**, central to the curve work, not a spike — it is just not yet
  imported by `curve_lab` (promotion gate in
  `pythagorean-spiral/docs/HANDOVER.md`).
- **Span bridge:** `interpolate.design_from_spans(spans)` turns a recovered or
  grammar-produced cubic chain into a `Design`, one clothoid segment per span,
  marked G1. This is the entry point a W03 port consumes.
- **Spirals recovered:** `scripts/extract-spirals.py` pulls every `spine` path
  from the Stage II and LAC pages, keeps the page's own cubics and its
  `data-span` tag (`line`, `arc`, `euler`, `logaesthetic`, `reflected`,
  `hyperbezier`, `member`), and writes `workbench/spirals/stage-two.json` (20 plates,
  90 spines) and `workbench/spirals/lac.json` (31 plates, 31 spines) plus a gallery.
  Coordinates are page units with y down, recorded as found. Shared reading
  helpers now live in `scripts/recover.py`.
- **Clearance built:** `curve_lab/clearance.py` measures the minimum
  edge-to-edge gap between ink instances and lists crossings, allowing one only
  where a declared `Contact` covers it. Measurements carry a `2·tol` band, so
  the report says *violation*, *warning* or *pass* instead of pretending the
  last tenth of a millimetre is known. `render_piece()` was split into
  `build_piece()` + writer so drawing and measuring share one geometry build.
  Docs: `docs/CLEARANCE.md`; tests: `tests/test_clearance.py`.
- **Terminals recovered:** `scripts/extract-terminals.py` cuts the outline ends
  out of the two ornaments pages at their `L`/`Z` seams and writes
  `workbench/terminals/stage-two.json` (20 plates, 88 ends),
  `workbench/terminals/lac.json` (31 plates, 62 ends) and a gallery
  `workbench/terminals/index.html`. The taper fraction is measured by nearest
  distance between the rails, not assumed: the medians are 17 per cent on
  Stage II and 18 on the LAC page.
- Added `workbench/ornament-board.html`: **85 plates** (45 catalogue ornaments
  P21–P65, 27 class I caps P66–P92, 9 class II leaves P93–P101, 4 presets
  P102–P105), **26 work items** W01–W26 and **11 decisions** D01–D11. The
  twenty fleur studies (P01–P20) are the subpage `workbench/fleur-studies.html`,
  defaulted to “Needs work”. The board has a beginner glossary, plain-language
  briefs, editable text per card, DeepSeek-pick sorting, priority/stage,
  drag/↑↓, notes, localStorage and JSON/order export.
- **Spine imported (this session):** `curve_lab/spine.py` is the one-way
  bridge from `pythagorean_spiral` chains; `workbench/spine-sheet.html` is its visual
  proof (sheet, join, declared contact). Gate 4 and the session order are in
  `docs/SESSIONS-int.md`.
- **Sandbox and spiral turns (this session):** `workbench/sandbox.html` is the
  hand-written index of the working pages; `workbench/spiral-turns.html` measures how
  many times a clothoid winds in a 100 grid and when the windings merge (about
  1.2 turns from rest at r=15; 7.5 turns at a 1-unit gap when already winding),
  plus the page bounds r_min=2w and r_max=L/2.
- **Practical curve (this session):** `curve_lab/practical.py` fits one
  clothoid per structural run and emits **34 cubics** (36 with one pin) instead
  of 1,164, at 0.42 mm worst deviation; `workbench/practical-curve.html` compares the
  two and prints the serif `C/@/&/~` counts. **Pins** let a branch chosen on the
  exact curve become an exact vertex in the practical one (pin error 2e-7).
  Fixed `bezier.fit_chain`, which read the next segment's tangent at a boundary
  and inflated every cornered fit.

## Risks / open decisions

1. **Accounts and roles are still absent.** The shared token (W11) and the
   per-address render limit (W12) protect the URL, but there are no named users,
   saved designs or audit trail. Rotate the Secret Manager version if the token
   leaks.
2. **Cold starts** at min 0 are roughly 1–3 s. Do not pay for min 1 unless a
   demo needs it; set it back to 0.
3. **Free-tier usage.** Stay within the monthly Cloud Run/Cloud Build/Artifact
   Registry allowances; the budget alert is only a warning.
4. **Large deploys (fixed).** App deploys are thin and skip the C++ compiler;
   the engine base must be rebuilt only when `vendor/`, `csrc/`, or
   `scripts/build-native.sh` changes. The base tag is pinned to `2026-10-26`.
   The Debian build is deliberate: the Ubuntu 24.04 artifact needs glibc 2.38
   and will not run on Debian bookworm.
5. **Caps are baked in.** New `out/caps/*.json` files need an app deploy (thin),
   not an engine rebuild.
6. **No persistence/accounts.** Designs live in the browser and are not saved.
7. **Reference tree is dirty and growing.** Untriaged images sit at `reference/`
   root, `reference/1/` and `reference/hard/`; the last hash/dedupe pass was
   2026-10-27. Nothing there is committed except the measured references and
   READMEs.

## Veil rebuilt on turn chains (2026-10-29, this session)

- **Two versions, both live on `docs/cloud.html`.** *v1* is the original veil:
  the same ellipse composition, now with the veil factor on every layer (the
  drawing used to give it to `bank` alone while the report gave it to all, so
  the top went opaque while the numbers said 5 per cent). *v2* replaces each
  ellipse with a turn-chain ribbon. The page carries both figures, both strips
  and the numbers side by side.
- **v1 is restored faithfully, including its under-shading.** The cloud read by
  shading, not by outline: every billow and crown had a darker under-lobe and a
  cream top. Those strokes were outside the opacity model; they are now a
  `shade` / `light` layer like any other, so the measurement counts them.
  v1's measured flaw is the original one: top row mean **0.54**, worst 0.72.
- **v2 is turn chains.** `design.lobe` (turns `k**p`, then the same integers
  reversed) through `ribbon.outline` with a rational taper: a closed rational
  polygon with pointed ends. Power dial = layer: haze p1, bank p2, billow p2,
  crown p3. 90 lobes from 30 puffs. Top row mean **0.07**, worst 0.28.
- **One model.** `pythagorean_spiral/veil.py` owns the geometry and the
  composite; `scripts/cloud.py` draws exactly those polygons.
- **2b: four standard patterns,** two on top (where the cloud meets the image)
  and two below, sampled and gated in `tests/test_veil.py`. v2 passes, v1 fails
  — that difference is the finding, not a bug.
- **2c: the slider.** One uniform layer of one cloud colour over the same four
  patterns, with `?veil=0.42` to set it from the URL. The number the operator
  picks there is the target the veil should be solved to; the model is not the
  authority on a design number.
- **The operator's number is 80 per cent opacity** (chosen on the 2c slider,
  now ranged 0-100 and sitting at 80). Both versions are solved to that peak,
  so the comparison is about *where* the density lands, not how strong it is.
  v1: top row mean 0.43, worst 0.61 — over the image. v2: top row mean 0.09,
  worst 0.47 — the peak is in the sky above the works. Same transparency,
  different geometry.
- **The gate reads the row mean** (how much of the image is covered), with a
  looser allowance for a single bad corner: top mean ≤ 0.25 (worst ≤ 0.50),
  bottom mean ≤ 0.12 (worst ≤ 0.30). v2 passes, v1 fails on the top mean.
- 139 tests pass. `scripts/veil_test.py` writes both versions' numbers to
  `docs/veil-test.json`.

- **Pixel truth is now measured, and it agrees with the model.** The analytic
  model was predicting the browser's compositing a second time; that duplication
  is what let the report and the picture drift apart. `scripts/veil_measure.py`
  now renders the veil over a black field and a white field in headless Chrome
  and recovers alpha exactly, per channel, from `a = 1 - (Rw - Rb)/255` --
  independent of the composite colour, edges and overlaps included. ~26 s.
  Measured vs model at the same factors: v1 top mean 0.461 / 0.428, v2 top mean
  0.120 / 0.131, peaks 0.84-0.85 / 0.80. Agreement is within ~8 per cent, so the
  original failure was the drawing/model split, not the arithmetic.
- **Still half-wired:** `docs/veil-measured.json` exists and is correct, but
  §2b's table and `tests/test_veil.py` still read the model numbers. The one
  remaining step is to make the measured block the reported truth and keep the
  model as the design aid (the operator asked for both, not one).

## In flight (2026-11-01, uncommitted)

- **The input hub landed (this was the stated goal).** `workbench/manifest.json`
  is the only description of a page; `scripts/hub.py` reads it, pulls each
  page's **first `<svg>` as the thumbnail**, writes `workbench/workbench.html`,
  and injects a guarded one-line bar into all 17 pages. The hub opens with four
  plain-language decisions (curve / terminal / strand / sheet), one link each.
  `docs/HUB.md` explains it, including the one rule: **run `hub.py` after any
  page generator**, because a generator drops its bar.
- **Twenty-one named curves on the generators page**, each measured. Fourteen are
  exact, thin control scales and all: bean 12/273, bicorn 6/105, nodal 1/4,
  Tschirnhausen 1/27, bow 1/128, nephroid 5/1, astroid 5/1, epicycloid k=3 35/1,
  epicycloid k=5 231/1, trifolium 12/50, quadrifolium 15/125, cardioid 3/25,
  Bernoulli 4/41, Gerono 6/25, piriform 6/25. Sampled: squircle (smooth, genus
  3), heart (genus 4), pear (genus 2), cruciform (rational but unbounded).
  **The rule the table proves: a curve is cheap exactly when it has a
  singularity to run a line through.**
  `roulette(m, sign)` now builds the whole epi/hypocycloid family exactly
  (Chebyshev in `cos θ`, then `u = tan(θ/2)`), so any integer `k` is one call —
  `k = 1` cardioid, `k = 2` nephroid (epi) and the Tusi couple (hypo), `k = 3`
  deltoid, `k = 4` astroid.
  Corrections this session: `y²=x²(x+1)` is **not** Tschirnhausen (90° node vs
  60°); the piriform is the `x³` form, not `x⁴−x²y+y²` (which is empty); and the
  Bernoulli lemniscate **is** rational (genus 0 — its node at the origin plus the
  two circular points at infinity absorb the degree), contrary to an earlier
  guess in this file's own reasoning.
- **`docs/PH-INTEGER.md` + its HTML twin.** The corrected rewrite of the
  survey, generated by `scripts/ph_doc.py` from `loom`'s own arithmetic so the
  prose cannot drift. In the mkdocs nav under *The engine*. `mkdocs build`
  (strict) is clean. The twin is the same source through `markdown`, styled
  like `HANDOVER.html`; neither file is hand-edited.

- **`from_pairs` was wrong and is fixed.** It rotated Δ by *half* the tangent
  angle (`c0, s0 = u0/h0, v0/h0`) instead of the full one, so the fit only
  closed when the segment started at θ₀ = 0 — exactly the vertex case every
  card happens to use. It now doubles by Euclid. Verified against
  `from_hermite` on five catenary spans: agreement to 1e-14, where the worst
  disagreement before the fix was 4.0 units. No callers, so no page output
  moves; 239 tests pass. **This also means §C's "both versions agree to the
  last digit" was prose, not a check — if it is kept, make it a test.**
- **The discriminant, exactly.** With direction triples (integer `h`), the
  closure quadratic's discriminant is
  `N / (h₀⁴ h₁²)`, `N = Y² − 4Xb`, `X = b(P²−Q²) − 2aPQ`, `Y = bP − aQ`,
  `a = (Δx·u₀ + Δy·v₀)`, `b = (−Δx·v₀ + Δy·u₀)`, `P = u₀u₁+v₀v₁`,
  `Q = u₀v₁−v₀u₁` — all integers. So "rational square" is a perfect-square
  test on `N`, with no floats.
- **Measured, and it is a negative result.** Over the full 92-rung pythagorean
  ladder (`max_h=400`), for the four catenary chords of Fig. N, **0 of 17,168**
  non-negative discriminants are squares. Freeing the node finds squares, but
  `k` then carries a huge denominator (3401, 32399, 615581 in a three-segment
  trial), so the control points are rational, not lattice. **The square test
  buys exactness, not integers.** That is why Fig. K snaps, and the next step
  is to say so on the page rather than build the chain as if it did not.
- **`generators` (the new input method + sandbox).** `scripts/generators.py` →
  `workbench/generators.html` (renamed from `loom`). Input is the *generator*,
  not the curve:
  `z′ = h(u²−v², 2uv)` with degree fixed by `n = deg h + 2·max(deg u, deg v) + 1`
  (Farouki–Sakkalis). Even degrees (4, 6) exist **only** via the `h` factor —
  the pasted plan omitted it, which is why n=4 and n=6 looked unreachable.
  Everything is `Fraction`-exact; control points and milestones are asserted
  integral before the page is written. CLI: `--n --h --u --v --m`.
- **Named curves, and the tiers they prove.** `homog_bezier()` turns a rational
  parametrisation into an exact rational Bézier by substituting `t = s/(1−s)`.
  - bean `x⁴+x²y²+y⁴ = x(x²+y²)`: **rational, exact**, control scale 12,
    milestones clear at **273** (denominators 1, 91, 3, 91, 1).
  - bicorn `y²(1−x²) = (x²+2y−1)²`: **rational, exact**, two branches (the two
    horns meet at ±1,0), control scale 6, milestones 48.
  - pear `x² = y³(1−y)`: quartic, cusp at the origin, genus 2 — **not rational**.
  - heart `(x²+y²−1)³ = x²y³`: sextic with cusps at (±1,0) and (0,−1),
    genus 4 — **not rational, and not smooth** (an earlier draft of the page
    said smooth; `|∇F|` vanishes at all three cusps).
  - piriform `a⁴y² = b²x³(2a−x)`, at a=b=1 `y² = x³(2−x)`: **rational,
    exact**, control 6, milestones 25. (`x⁴−x²y+y² = 0` is empty — discriminant
    `−3x⁴`; `x⁴+x²y−y² = 0` factorises into two parabolas.)
  - nodal `y² = x²(x+1)`: **rational, exact**, node angle **90°** — a nodal
    cubic, but *not* a PH curve.
  - Tschirnhausen `27y² = (1−x)(8+x)²`: **rational, exact**, node angle **60°**
    — this is the cubic PH family itself (`r = a sec³(θ/3)`).
  - bow `x⁴ = x²y − y³`: **rational, exact**, triple point at the origin,
    genus 0, polynomial (`x = t−t³`, `y = t²−t⁴`), control scale 1.
- **The goal as stated 2026-11-01: unify every current input.** One central
  page, plain explanations, branching to the individual input pages. Not the
  twenty fleur studies.
- **RENAME DONE, locally, 2026-11-01.** Package is `curve_lab/`, directory is
  `~/developer/curve-lab`; imports, pyproject, Dockerfile, mkdocs site name,
  docs prose, page text, `.opencode` commands and the parity json all follow.
  Six commits, the last two being the package and the move; the session was
  moved with the directory so everything builds from the new root.
  **Still deployed under the old name, deliberately:** Cloud Run `clothoid-web`,
  secret `clothoid-token`, engine base `clothoid-engine`, budget alert.
  Renaming those mints a new service that bills next to the old one until it is
  deleted, and a renamed secret 401s the site if only one side moves. Keep
  "clothoid" wherever it means the *curve*; only the project name changed.
- **Correction to the "integer milestones are impossible" claim.** They are not:
  any finite set of rational parameters clears at the lcm of their
  denominators. What *is* impossible is the chat log's "infinitely many integer
  points on the curve" — a bounded curve meets the lattice finitely often.

## Next move

**Done (2026-11-02): the heart half closes at its lobe tip.** The tip is the
double root of the sextic in `y`: `f = 0` and `f_y = 0` give `x² = 1+y²` and
`8y³ − y² − 1 = 0`, so `(x, y) = (1.139028…, 0.545330…)`. The sampler now stops
there and closes both branches on it; the old `x = 1.105` limit left a 0.508
jump in a 3.63 arc. Euler: 32 chords, **0.73%** of size, both ends within
0.003 units of the axis. The span chain is the honest open reading: 32 spans
for 1.44%, 4 spans for 8.21%.

**Done (2026-11-02): the heart family catalogue.** Five forms on
`workbench/heart-forms.html`; only the cardioid is rational. The next single
action is to measure the five (aspect, fill, cusp count) against the reference
and fit one with a clothoid chain at the fidelity budget — read them against
the French curves, catenaries and clothoids before choosing. The mirrored-
clothoid join is now measured, not a guess: on one finite arc the two
vertical-tangent contacts only crowd toward the eye (the hearts table), and the
minimum-width box is a double *normal* (the clothoid-cut page), so neither
gives the join. A two-arc placement, or a different curve, is the open route.
Clouds from clothoid puffs use that same join.

What is left from this session, in order:

1. **The deployment still carries the old name.** `clothoid-web`,
   `clothoid-token`, `clothoid-engine`, the budget alert. Deciding to move them
   is the one thing that needs the operator: a renamed Cloud Run service is a
   new service billing beside the old one until deleted. Everything local is
   already `curve-lab`.
2. **`next-fhandoff-int.md` is stale** — it points at the chain above. Run
   `/fhandoff` to replace it.
3. **The hub wants one more pass**: four of the seventeen cards have no
   thumbnail because those pages build their figure in JavaScript. Giving each
   one static first SVG is a small job with a visible payoff.
4. **The branch is 110 commits ahead of `origin/main`.** Nothing is pushed.

The catenary thread itself is current: A–M are hodograph chains, the involute
(Fig. W) and the bouncing ball (Fig. X) are done, and every PH figure now carries
the reference curve and the triangles.

**The practical profile landed** (`workbench/practical-curve.html`): 34 cubics at
0.42 mm, with pins for branch points. Read `FIDELITY.md` before quoting any
count.

**The next real connection is the fill.** A ribbon width on a per-chord chain
crosses at every corner under the engine's rail builder; the filled shape is the
spine layer's miter job (`ribbon.outline`). Until that is wired, chain studies
are centre lines. After the fill: the canonical fleur, W04, the turned
terminals, and the primals in the order in `docs/SESSIONS-int.md`. The
plant-form arc after the offset page is in `goals.md`: endings (flower, seagrass,
cone terminal), lattice growth marks, then branches; no bare tip. The offset
page should show exact PH, Levien's fitted cubic-Bézier parallel, and the LAC
rail on the same source; the Levien method is a fitted option, not an exact
claim.

**Parked: the veil.** The measured column in §2b is unwired, the v1 caption
overstates what it is, and the three.js page is a study.

**Deferred, not dropped: the canonical fleur.** Build `fleur_canonical()` from the measured fleur
reference (`reference/fleur/png/metrics.json`: aspect 1.43, fill 0.17,
symmetry 0.83), with exact clothoid segments, the band as a `Bundle`, terminals
per stroke, the centre seam declared, and a silhouette render beside the
numbers. Old study 01 stays as history; do not conform the other nineteen
until the silhouette is approved.

**Superseded, kept for context: the junction object, then W03.** The fillet exists; what is missing is the
junction itself — a small object carrying the corner, the clearance that must
survive through the crotch, the fillet or clothoid blend, the taper, and the
declared contacts, with a report that gives the join grades and the gore. The
recovered spirals (`workbench/spirals/`) are its first test data: the S joints are
real joins that must come out G2 or be explained.

**Clearance and junction work**: a measured minimum gap between
strokes (the 5 mm local clearance), a crossing report that allows a crossing
only at a declared terminal, and a blend where a leaf meets a branch and a
branch meets the trunk.

**After W03/W04: the primal studies.** Fire, water, earth and air are a category
of their own (`docs/PRIMAL.md`), gated on a finished framework: twenty fleur
studies with node parity, turned terminals, junctions with measured gores,
`Section` as a first-class model, and a web route. Order within it is earth →
water → air → fire, because fire needs the turned terminals. The archetypes
(fleur, acanthus, palmette) follow the primals.

**W03 — fleur grammar.** Port the old half-stroke grammar from
`ornaments/assets/ornament_set.js` (foot, tail, band, petal, lance, with its
lines, 5ⁿ arcs and Euler spans) onto `Piece`/`Trace` from W01 and the terminals
from W02. First target **P01**, study 01, at its old parameter values; keep the
report (spans, joins, copy error, fold) and no fill. Then W04 the twenty sets.

## Tooling notes

- `--headless=new` hangs Chrome on this machine; `--headless=old` captures
  screenshots fine. Prefer DevTools Protocol over CLI flags for emulation and
  measurement.

## Important paths and commands

| Path | Purpose |
|---|---|
| `web/server.py` | stdlib server and `/api/render` |
| `web/static/` | MVP page, JS, CSS |
| `curve_lab/piece.py` | `Piece`/`Trace` multi-trace model and renderer |
| `curve_lab/spine.py` | the one-way bridge from `pythagorean_spiral` chains |
| `tests/test_spine.py` | chain import, sheet render and declared contact |
| `scripts/spine_sheet.py` | builds `workbench/spine-sheet.html` |
| `scripts/spine_study_probe.py` | measures a chain study's drift from P01 |
| `docs/SESSIONS-int.md` | proposed order for the next sessions, gate 4 first |
| `docs/FIDELITY.md` | **the accepted 1.4–1.6% accuracy budget** and its metrics |
| `curve_lab/terminals.py` | `butt`, `point`, `arc`, `round`, `taper` cap geometry |
| `tests/test_piece.py` | piece model, mirror, round-trip tests |
| `tests/test_terminals.py` | each terminal, extension, fold and width rejection |
| `scripts/piece_sandbox.py` | builds `workbench/piece-model.html` |
| `docs/REVIEW.md` | senior review: page model, PDF, outline, ids, CI |
| `docs/PHILOSOPHY.md` | what a glyph is: parts, full lines, sections, joints |
| `docs/PRIMAL.md` | primal ornaments: the four elements, their gate and order |
| `workbench/piece-model.html` | W01/W02 visual proof: traces, rails, mirror, terminal strip |
| `Dockerfile` | thin app image; starts FROM the engine base |
| `engine/Dockerfile` | engine base: C++ build + Python runtime + `.so` |
| `cloudbuild.engine.yaml` | build and push the engine base |
| `.gcloudignore` | small app-only Cloud Build upload |
| `.gcloudignore.engine` | engine-base build context |
| `scripts/check-parity.py` | local/remote parity smoke test |
| `tests/test_web.py` | web API tests |
| `tests/test_auth.py` | token auth and rate-limit tests |
| `docs/HANDOVER.md` | durable handover |
| `docs/HANDOVER.html` | HTML mirror |
| `docs/BACKLOG-int.md` | execution detail for W01–W26 |
| `workbench/ornament-board.html` | visual board: 85 plates, 26 work, 11 decisions |
| `workbench/fleur-studies.html` | subpage: the twenty fleur studies, P01–P20 |
| `scripts/board/` | board generator, template, extractors and README |
| `next-fhandoff-int.md` | two-line focused pointer |
| `docs/FLOWERS-int.md` | the four-stem flowers sheet: mm units, Euler flowers, JSON/Node split, stem library |
| `scripts/stems_print.py` · `.mjs` | flowers geometry → JSON, then the SVG renderer |
| `workbench/flowers.html` | the four-stem flower print sheet (8.5 × 11, mm) |
| `workbench/stem-library.html` | 177 labelled stems: S01–S109, S118–S157, S166–S167; SM1–SM26 |
| `TODO.md` | focused checklist: heart-forms link/test and clothoid-cut regression |
| `goals.md` | the long arc: plant-forms → ornament-forms; offsets, endings, lattice growth marks, branches |
| `workbench/lac-parallel.html` | evolute → parallel offsets sandbox (LAC and classical families) |
| `workbench/lac-parallel.js` | the family/evolute/offset geometry |
| `scripts/stem_library.py` | the stem-library generator |
| `.opencode/commands/fhandoff.md` | write the focused handoff |
| `.opencode/commands/fhandon.md` | resume from it |
| `~/.config/opencode/commands/focus.md` | global: move session here, show focus |

```sh
cd /Users/thomaskelly/developer/curve-lab
.venv/bin/python -m unittest discover tests
.venv/bin/python web/server.py
# with the local server up and the remote reachable:
.venv/bin/python scripts/check-parity.py
```

```sh
# engine base: only when vendor/, csrc/, or scripts/build-native.sh changes
gcloud builds submit --config cloudbuild.engine.yaml \
  --ignore-file=.gcloudignore.engine .

# app: every UI/Python change (thin upload, no C++ compile)
gcloud run deploy clothoid-web --source . --region us-central1 \
  --allow-unauthenticated --memory 512Mi --cpu 1 --concurrency 2 \
  --min-instances 0 --max-instances 1 --timeout 60 --port 8080 \
  --set-env-vars HOST=0.0.0.0 --quiet
```

## 2026-11-04 — names for the two routes

- **turn-exact** — `pythagorean-spiral/`: exact rational turns and nodes, rational
  miter rails; the drawn cubics are fitted (~1.4%).
- **Euclid family chains** — `curve_lab/pyth_chain.py`: tangents taken from a
  fixed-`n` family of Euclid's formula; integer nodes and control points at
  scale 1; the turns are C1-fitted and the rails are floating point.

Neither name claims a role: either route can be a stem, a spine or a chain.
`Euclid families` alone means the triple families (the field plot); the route is
`Euclid family chains`.

## 2026-11-04 — the chain's exponent is −4/3

`κ ∝ s^p` is the generalised Euler-spiral family (p = 1 clothoid, 0 circle,
−1 log spiral). The n=1 chain is not a power law at a finite band, but the
fitted p drifts to **−4/3**: −0.835 (m ≤ 6) → −1.222 (25) → −1.305 (100) →
−1.325 (400). The algebra gives it: θ ≈ 2n/m, dθ/dm ≈ −2n/m², s ∝ m³, so
κ ∝ s^(−4/3); n only scales the constant. It is a member of the family, not a
new species. Fig. Y on `workbench/pythagorean-chain-editor.html`.

## 2026-11-05 — three explorations opened

- **Log spiral** (`workbench/log-spiral.html`): a constant-width parallel is **not**
  a log spiral — the tangent-to-radius spread grows with d/r (0.21° at 0.02, 2.6°
  at 0.2). What is exact: scaling (width ∝ r, a self-similar taper) and the
  evolute (spread 0.000000°).
- **p-triple plane** (`workbench/pyth-plane.html`): in (m,n), a and b levels are
  hyperbolae whose integer points are factorisations; vertex curvature radius is
  √a. In (a,b), fixed m is a parabola opening sideways. The involute of a
  parabola's evolute is exactly its parallel family (error 2e-15) — and those
  parallels are not parabolas (fit residual ~21% of d).
- **Multi-grid** (`workbench/multi-grid.html`): parts may sit on different grids;
  the composite is the lcm (1, 1/5, 1/25 → 25). Per-span grids cost 5^k
  (15,625 at six spans, 244M at twelve).

## 2026-11-05 — the exact taper, and the log-spiral width corrected

- `curve_lab/taper.py`: the partner of `r = a e^(bθ)` is `k·P(θ+φ*)` — rotated as
  well as scaled; width `= ω(k,b)·r`. `tests/test_taper.py` guards ratio
  constancy (1e-9), the partner's being a log spiral, and the constant-offset
  drift.
- `workbench/tapered-stem.html`: rails ×1 and ×1.12, asymmetry **5.25%**,
  terminal seam **2.63%** of the offset. Exact rails, not offsets.
- Correction: the first log-spiral page used the far normal intersection
  (1.60·r); the nearest distance is **0.3409·r**. Fixed and tested.

## 2026-11-05 — the showcase, the catalogue rule, the meter

- `workbench/showcase.html`: 18 families, 55 numbered panels plus an unnumbered
  ray fan; every figure links to `showcase-notes.html` (its own section). The
  top of the page is the structure: exact parallels (log spiral, circle
  involute, the string construction), smooth Euler chains, the integer spine
  drawn as ink with a cut and a branch, LAC ribbons.
- `workbench/curves-all.html`: 25 named curves from `generators.NAMED` and 15
  hearts from `heart_forms.FORMS`, rendered by the repo's own code — the answer
  to the four invented silhouettes that had been standing in for them.
- `scripts/ctx.py`: context meter (`input + cache.read` against the 1M window),
  a tally in `state/sessions.jsonl`, and `--watch` that beeps at 70% and 85%.
  Duration and turns are reported, not judged.
- `recheck` now 21/21, including "every named curve and heart is rendered from
  its own table" — the check that makes the enumeration rule enforceable.

**Local:** 200 on :8003. **Remote:** no `.run.app` URL is recorded anywhere in
the docs, so remote status is **not known** — carried, and a gap worth closing.
**Tests:** 44 modules green, last run 2026-11-05 (this session). **Git:** clean
at the commit below.

**Next move:** the graded table has 23 PASS curves; three are drawn nowhere —
the 3-4-5 Pythagorean spiral, the seagrass ending, the modulated-width study.
The hyperbola is the fourth gap (family 9 shows parabola and ellipse only).
Take the 3-4-5 spiral first: it is the exact spine and the signature result.

Tried and rejected: drawing catalogue pages from memory — produced a limaçon
labelled "bean" while the exact bean sat in `generators.NAMED`; replaced by
table-driven rendering and a failing check. A 90-minute session timer — the
store shows long sessions with the *lowest* error rate (0.12 vs 0.47 per 100
turns), so duration is reported, not judged. (2026-11-05)

## 2026-11-05 — the 3-4-5 exact spine on the showcase

- `workbench/showcase.html` has family **20 · 3-4-5 exact spine** (ids
  `fig-19a`–`19c`, because the page's renumbering runs after the build):
  19a the 10-chord chain with all 11 integer nodes marked and
  `1+2+3+4+5-5-4-3-2-1 = 0` printed; 19b the cumulative turn plot returning
  to 0 and exiting east; 19c the rational rotation `(4x-3y, 3x+4y)/5`.
- The chain is built from `pythagorean-spiral/` itself (`spiral.load()` →
  `Spiral(Triple(3,4,5), 1)`), not re-derived in the script. Closure asserts
  `coeff == 0` and an axis-aligned heading; `integer_form()` gives the 11
  integer nodes at ×5¹⁵ = 30,517,578,125. The scale is a choice, not a
  property — node denominators are powers of the hypotenuse (AUDIT §2).
- Guards: `tests/test_exploration_pages.py::test_the_345_spiral_panel` plus
  updated row/id counts (19 rows, 1 four-row, 61 figure ids). `recheck`
  still **21/21**. Full suite: **1 pre-existing failure**, unrelated to this
  action — `tests/test_plant_forms.py::test_page_has_the_proof` expects 6
  `<svg>` in `workbench/plant-forms.html`; HEAD already has 7.
- Screenshot for the operator (not read by the model):
  `/tmp/curve-lab-345-spiral.png` (1120×900 viewport).
- Reading-list gap found and fixed in `state/READING-int.md`: the showcase
  generator/notes/test and the `pythagorean-spiral` package modules were not
  named. Next session should load them from the new Tier 2 row rather than
  search.

## 2026-11-05 — the four graded gaps are closed

- `workbench/showcase.html` now draws all four: the 3-4-5 exact spine
  (family 20), the **seagrass ending** (8d, `plant.seagrass`), the
  **modulated-width study** (4d, rails from `scripts/modulated_width.py`) and
  the **hyperbola** (9d, two branches plus asymptotes). Families 4, 8 and 9
  became four-across rows.
- The pre-existing `test_plant_forms` failure is fixed: the page has one
  full-width proof figure plus six cards, so the guard now counts 7, not 6.
  **Full suite green: 336 tests, 1 skipped.**
- `scripts/check-web.mjs` was tried and is not usable in this session: it
  expects the docs on :8002 and the app on :8000, both down; it is about the
  pythagorean-spiral docs pages, not the workbench.
- Commits: `560f67b` (gaps), `67c5879` (tidy guard), admin follows.
- **Next:** the first ornament proof from `goals.md` — one fleur using the
  plant-form grammar. `TODO.md` says so; `/fhandoff` should carry it.

## 2026-11-05 — catalogue completion after the gaps

Three more families, so the layers that finish a stroke and the rest of the
named table are drawn rather than only described:

- **21 · Terminals** — caps (butt, point, arc, round), tapers (taper, bulb,
  cone) built by `curve_lab/terminals.terminal_spans`, and a plot of
  `terminal_extension` in half-widths.
- **22 · Fitted parallels** — Levien's `fit_chain` on one cubic: fitted vs
  dense exact offset with the max error printed (1.8e-3 at tol 5e-3), a large
  offset with its cusp interval flagged, and error against tolerance. Always
  labelled fitted, never exact.
- **23 · The rest of the named table** — Tschirnhausen, bicorn and the nodal
  cubic, sampled from `generators.NAMED` via `homog_point`, not redrawn from
  memory.
- Page text now says panels run `a–d`. `todo.html` carries its hub bar.
- **Full suite green: 337 tests, 1 skipped. `recheck` 21/21.** Commits
  `dd3e84a`, `ad92e43`; admin follows.

## 2026-11-05 — the session clock is back

The operator restored the wall-clock timer that had been rejected as a session
limit. It is now a reporting device and a budget, not an error-rate argument:

- `scripts/timer.js` and `scripts/notify.js` copied from `ornaments/`; the
  `.timer.json` marker was already gitignored here. Start with
  `node scripts/timer.js 20m 60m "<label>"` in the background; `--check`
  reports elapsed/floor/cap; `--stop` clears it.
- Wired into `/focus` (global `~/.config/opencode/commands/focus.md`),
  `/fhandon` (step 0) and `/fhandoff` (report elapsed, then stop), and into
  `AGENTS.md` as a session-clock rule. `/fhandoff` now carries the wall clock
  beside the `ctx.py` numbers because they measure different things.
- Proved with a real start/check/stop (`0m elapsed`, marker cleared). No test
  suite entry: the tool is Node, guarded by the commands rather than unittest.
- **Stats:** start, floor, cap and stop now append JSON lines to
  `state/timers.jsonl` (override with `CURVE_LAB_TIMER_LOG` for scratch runs).
  `--tally` prints the last ten sessions and median/mean/total elapsed. The
  file is created empty here; the first real `/focus` or `/fhandon` writes the
  first record. `/fhandoff` runs check → stop → tally, pastes both numbers into
  the block, and commits the stats with the handoff.

## 2026-11-05 — the ornament proof track opened

The three named proofs in `TODO.md` are built, each from the module that owns
the geometry, each with its counts recomputed in the generator:

- **Fleur proof 01** (`workbench/fleur-proof.html`, `scripts/fleur_proof.py`):
  the grammar's 26 spans, rails at ±12.5, cone terminal R = 25 at the lance
  tip, a real branch off the band node with a seagrass ending, 16 integer
  nodes and two pyramid pairs.
- **Volute proof 01** (`workbench/volute-proof.html`): 33 chords on
  79-3120-3121, exact rational nodes, peak 765.8°, numeric rails at ±0.26 and
  a cone R = 0.52; seagrass branch off node 12.
- **Cruciform proof 01** (`workbench/cruciform-proof.html`): two `Junction`s
  (G1, r = 0.6, arc 0.9425, curvature step 1.667), two declared merges, seven
  `Section` stations, four cone terminals.
- **Ending fit pass** (`workbench/ending-fit.html`): all ten C sections from
  `euler_sections.SECTIONS` attached at 6 × offset; every one clears the rails
  by about the offset (min 0.50) and crosses only at the declared tip. The
  ending grades stand; no promotion.
- Guards: `tests/test_fleur_proof.py`, `test_volute_proof.py`,
  `test_cruciform_proof.py`, `test_ending_fit.py`; `scripts/check-proofs.mjs`
  is a Playwright layout gate for the four pages (4 × 3 viewports). `recheck`
  is now **25/25**. Full suite **349 tests, 1 skipped**.
- TODO review after the first proof: **no grade change**; the proofs exercise
  the ending/junction rules and do not add offset-table rows.
- Still open: the integer-lattice rule (grid-line crossings vs full integer
  points) and the modulated-width proof. Both are operator decisions/targets,
  not silently settled here.

## 2026-11-05 — the width track's proof, and the proof gate

- **Modulated width proof** (`workbench/modulated-width-proof.html`): the law
  w(u) = w0(1+64a u³(1−u)³) at a = 0.6, measured against a constant 2 × band.
  Ratio 1.600, seams exactly w0 at both ends, rail separation matches the law
  to 8.9e-16, 0.300 half-width deviation from the constant band, no rail
  self-intersection. This closes the Stage IV TODO item as a measurement, not
  a promotion.
- `scripts/check-proofs.mjs` is the layout gate for the five proof pages at
  1000/390/320 px; 15/15 pass. `recheck` **26/26**. Full suite **352 tests,
  1 skipped**.
- The clock is now also logging: `state/timers.jsonl` has the start/stop for
  this block, so the next `/fhandoff` can report wall time from data rather
  than memory. The 90-minute cap is still rejected; the clock is a budget, not
  an error-rate claim.

## 2026-11-05 — the grid page, and the grounding rule

- **`workbench/grid-explained.html`**: position and heading at every node are
  exact; the fraction is a **ruler** (52/25 = 52 ticks of a 1/25 ruler), not a
  drawing size; 1×62 and 2×31 sweep the same 90° with the same exact ruler; the
  grid is the **box**, not the path — a 270° chain is 79 × 79 with a 186-chord
  path, and the box stops growing after the vertical (90°) and horizontal
  (180°) turning points. 360° keeps the same box.
- The nuance: for a constant-radius circle the box is the **diameter** (the
  far side is −R); for an inward spiral the first turning points bound it; for
  an outward spiral the last turn sets it. "After vertical it curls in" is the
  inward case.
- **Grounding rule** added beside the three aspects: every design names a
  horizontal datum and a vertical element, visible or declared. Pages and
  recheck updated (32/32); the fleur, volute and cruciform state both.
- Full suite **369 tests, 1 skipped** at the last run; gate 21/21; recheck
  **32/32**.

## 2026-11-05 — the showcase is the catalogue

- `workbench/showcase.html` is now **476 panels in 165 rows of three**, with
  no four-across row. Seven table-driven families were added:
  25 named (`generators.NAMED`), 15 hearts (`heart_forms.FORMS`), 4 presets
  (`presets.PRESETS`), 4 conics, 10 Euler sections (`euler_sections.SECTIONS`),
  31 LAC spines (`workbench/spirals/lac.json`) and 316 integer cubics
  (`pyth_cubic.catalogue`).
- Every panel comes from its table; `scripts/showcase_catalogue.py` is the
  single list, and `showcase_notes.py` generates one note per panel from it.
- The duplicate hand-built named families were removed; the curated concept
  families remain. Tests require all 25 named `data-curve` keys and 476 unique
  ids; full suite **373 tests, 1 skipped**; recheck **32/32**.
- Page size 1.6 MB; the remaining large source is `stem-library` (177), not on
  the page.

## 2026-11-05 — flowers, French curves, leaves, C cubics

- Flowers family: **8e squircle of eight Euler spans** (45° each, fitted through
  endpoints and tangents) and **8f bicorn flower** (four quartic bicorns, 45°
  apart, eight cusps).
- New families: **French curves · 8** (three Euler spans each, curvature
  declared at the joins) and **Leaves · 8** (one section mirrored across its
  chord; the Euler span solved through two tangents is one of them).
- Integer **C** cubics: `case_c`/`catalogue_c` (P1=(a,b), P2=(2c−a,b)) — 316
  rows on `workbench/integer-cubic-catalogue.html`, separate from the S family.
- Showcase now **671 panels / 230 rows of three**. Cubic order is by
  control-polygon interior angle, shallow (88.7°) to sharp (46.3°).
- `c = 1000` is the hypotenuse limit: 158 primitive triples → 316 arm pairs.
  At c = 500: 80 triples / 160 curves, interior 46.8–88.2° (loses under 1°);
  at c = 200: 32 / 64, 48.0–87.0°.
- Full suite **378 tests, 1 skipped**; recheck **32/32**.

## 2026-11-05 — catalogue breadth, and the first W05 storey

- Showcase now **1010 panels / 345 rows of three**: added the whole 306-billow
  cloud and its six layers, the five drapery ribbons, the combined gallery
  (catenary, volute, violin, acanthus, fleur), the four primal grammars, and
  the 316 integer **C** cubics (by height) alongside the 316 S cubics.
- Flowers: 8e eight-Euler squircle, 8f four-bicorn flower.  French curves (8),
  leaves (8), stems (177).
- **W05 storey 01, the monstrance** (`workbench/storey-monstrance.html`):
  baseline, foot, stem with rails, head, host, 24 p-triple rays, cross; grounded
  and naming its three aspects.
- `c = 1000` = 158 primitive triples / 316 arm pairs. c = 500 gives 160 S
  curves and keeps the interior range within 1°; c = 200 gives 64.
- **382 tests, 1 skipped; recheck 33/33.** Context hit the 70% warning after
  this block (71.7%), so the hour was not filled: the next block should start
  from a fresh session.

## Current truth — 2026-11-05

- **Previous action landed:** the 3-4-5 showcase panel is present (`fig-19a`)
  and `showcase.html` is newer than the handoff that asked for it.
- **Local:** 200 on `:8003` (checked). **Remote:** no `.run.app` URL is
  recorded; status unknown (carried 2026-11-05).
- **Tests:** 382, 1 skipped (carried 2026-11-05; nothing under `web/`,
  `curve_lab/`, `csrc/` or `tests/` differs from `19c519b`). **recheck 33/33**
  (carried, same commit).
- **Git:** clean at `19c519b` except this handoff. Showcase **1010 panels /
  345 rows**, 4.9 MB.
- **Risks:** the page is large; `c = 1000` is still the default pending a total;
  the last block ended at the 70% context warning.
- **Next move:** W05 storey 02, the pillar.
- **Tried and rejected:** spending the hour at 70% context — it crosses the 85%
  stop, so the block was committed and stopped. (2026-11-05)
- **Context:** 72.5%, 183 active min, 502 turns, WARN; clock **16.99 min**,
  median 17.5, mean 23.6, total **118.2 min** over 5 records.

