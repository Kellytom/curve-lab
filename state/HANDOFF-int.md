# curve-lab handoff

**Updated:** 2026-11-19
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
  (`SPEC.md`, `app/src/content/docs/docs/project.md`, `goals.md`, `app/src/content/docs/docs/philosophy.md`). `/fhandoff`
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
  p=±0.5 reference plates stay in the LAC group.  Doc: `archive/notes/FLOWERS-int.md`.
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
  `app/src/content/docs/docs/integer-cubic.md`; `tests/test_pyth_cubic.py`,
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
  curves; see `app/src/content/docs/docs/pythagorean-families.md`.
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
  `97e83d5`. Rule and caveats: `app/src/content/docs/docs/fidelity.md`.
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
- **Docs:** `app/src/content/docs/docs/handover.md` is the durable reference;
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
  filleted run can be a normal `Design`. Docs: `app/src/content/docs/docs/junction.md`; tests:
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
  `pythagorean-spiral/app/src/content/docs/docs/handover.md`).
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
  Docs: `app/src/content/docs/docs/clearance.md`; tests: `tests/test_clearance.py`.
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
  `app/src/content/docs/docs/hub.md` explains it, including the one rule: **run `hub.py` after any
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
- **`app/src/content/docs/docs/ph-integer.md` + its HTML twin.** The corrected rewrite of the
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
of their own (`app/src/content/docs/docs/primal.md`), gated on a finished framework: twenty fleur
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
| `app/src/content/docs/docs/fidelity.md` | **the accepted 1.4–1.6% accuracy budget** and its metrics |
| `curve_lab/terminals.py` | `butt`, `point`, `arc`, `round`, `taper` cap geometry |
| `tests/test_piece.py` | piece model, mirror, round-trip tests |
| `tests/test_terminals.py` | each terminal, extension, fold and width rejection |
| `scripts/piece_sandbox.py` | builds `workbench/piece-model.html` |
| `app/src/content/docs/docs/review.md` | senior review: page model, PDF, outline, ids, CI |
| `app/src/content/docs/docs/philosophy.md` | what a glyph is: parts, full lines, sections, joints |
| `app/src/content/docs/docs/primal.md` | primal ornaments: the four elements, their gate and order |
| `workbench/piece-model.html` | W01/W02 visual proof: traces, rails, mirror, terminal strip |
| `Dockerfile` | thin app image; starts FROM the engine base |
| `engine/Dockerfile` | engine base: C++ build + Python runtime + `.so` |
| `cloudbuild.engine.yaml` | build and push the engine base |
| `.gcloudignore` | small app-only Cloud Build upload |
| `.gcloudignore.engine` | engine-base build context |
| `scripts/check-parity.py` | local/remote parity smoke test |
| `tests/test_web.py` | web API tests |
| `tests/test_auth.py` | token auth and rate-limit tests |
| `app/src/content/docs/docs/handover.md` | durable handover |
| `docs/HANDOVER.html` | HTML mirror |
| `docs/BACKLOG-int.md` | execution detail for W01–W26 |
| `workbench/ornament-board.html` | visual board: 85 plates, 26 work, 11 decisions |
| `workbench/fleur-studies.html` | subpage: the twenty fleur studies, P01–P20 |
| `scripts/board/` | board generator, template, extractors and README |
| `next-fhandoff-int.md` | two-line focused pointer |
| `archive/notes/FLOWERS-int.md` | the four-stem flowers sheet: mm units, Euler flowers, JSON/Node split, stem library |
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
- **W05 storey 02, the pillar** (`workbench/storey-pillar.html`): plinth,
  torus, entasised shaft from two mirrored integer-controlled cubics (waist
  16.39 at y = 27.4 on a 15 → 9 taper), capital and an axis drawn as a ray.
  Width comes from the profile, so no parallel offset is claimed. **387 tests,
  1 skipped; recheck 34/34.**
- `c = 1000` = 158 primitive triples / 316 arm pairs. c = 500 gives 160 S
  curves and keeps the interior range within 1°; c = 200 gives 64.
- **382 tests, 1 skipped; recheck 33/33.** Context hit the 70% warning after
  this block (71.7%), so the hour was not filled: the next block should start
  from a fresh session.

## Current truth — 2026-11-06

- **Previous action landed:** W05 storey 02, the pillar; and the session went on
  to the showcase dot work. The pillar still holds (`workbench/storey-pillar.html`,
  `tests/test_storey_pillar.py`).
- **Local:** 200 on `:8003` (checked). **Remote:** no `.run.app` URL recorded;
  status unknown (carried 2026-11-05).
- **Tests:** 390, 1 skipped — run this session after the last code change.
  **recheck 35/35.**
- **Git:** clean at `73199e8`. Showcase **393 panels · 4.9 MB**; 37 sections,
  numbers unique and sequential.
- **Dots:** one finder, `scripts/dot_chain.dot_finder` — even spacing, both
  ends of every open curve, no duplicates. Audited on the built page:
  **13,409 dots, 0 off the ink, 0 unmarked open ends.** The 24-mark cap is a
  checkbox on the showcase, off by default.
- **Dot solver:** `workbench/dot-solver.html` + `scripts/check-dots.py`, 6/6
  cases. Image exception scoped to that sub-focus in `AGENTS.md`.
- **Integer cubics:** hits are the p-triangle joins; the q³ ladder (3/3/5/5/9/11/29)
  is on the catalogue page, with a 1× / 125× pair showing 3 → 9.
- **Risks:** 13a's sharpest step is still the p-triple turn at a node — its fix
  is the spine's arcs, not a spline; the board lightbox grid is in page units,
  not design units; the chord is fitted, not lattice-built, so a dot is a
  projected join rather than an exact integer point.
- **Current state (2026-11-08, handoff):** local server **200**; remote not
  probed (no deploy this session — carried 2026-11-06). Tests: full suite
  **72 modules OK**, 1 skipped, run this session after the last code change;
  **recheck 46/46**. Git: clean before the handoff commits, branch level with
  origin after the push; showcase **500 figures, 179 rows**; notes page ~11 MB
  because every note now carries its figure's SVG. The elastica start-point fix
  (κ = 0, not κ = m) is committed as `c7ec892`.
- **Next move:** build the sequence-curve family (see `TODO.md`): segment
  lengths from factorials and triangular sums with right-angle turns, and the
  symmetric closure schedule. Not started: context hit 72% when it was asked.
- **Tried and rejected:** starting the elastica at κ = m — κ′ = 0 there, so the
  integrator never leaves the turning point and the "curve" is a circle; start
  at the inflection. (2026-11-08)
- **Context:** 72.2% of 1M, 321 active min, 490 turns, WARN; timer cleared at
  the cap (this session's record: 60.01m, cap, 2026-11-07 01:35). Tally: 9
  sessions, median 52.6m, mean 45.0m, total 404.7m. Wall clock beyond the cap:
  the clock is a budget, not a quota; the work stopped on the context rule.
- **Panels refined (2026-11-08):** elastica now m = 2.2, 3.0, 3.8 (the m = 1.2
  member was a circle and is gone); the sinusoidal circle (n = 1) moved to the
  notes as the family's definition; the n = −½ parabola is drawn on a finite
  arc (0.55 of its range) so it no longer reads as a line; the quintic Hermite
  panel is now an S with varied tangents and accelerations, still G2. 500
  figures, 179 rows.
- **Families split, SVGs in notes, c423 G2 (2026-11-08):** the six families are
  now six sections, one curve per figure (19 panels; showcase 501 figures,
  180 rows). Every note now carries its figure's SVG inline, so a panel can be
  copied straight into Inkscape/Glyphs (notes page ~11 MB). c423 is the
  yin-yang rebuilt as four quintic Hermite spans, G2 at the three interior
  knots. GitHub: repo renamed **curve-lab**, remote over SSH/443 with a
  repo-scoped deploy key; AGENTS.md now says commit per action, push at every
  handoff, leave CI green.
- **Offsets by name (2026-11-07):** companions on **8e** (the squircle-of-eight
  Eulers, as one composite pair: 2 paths) and on the cusped/closed stem cards
  **c119, c120, c122, c126–135, c138, c140, c141, c143, c146** (per piece: 4–16
  paths each). The two-arc terminal is `curve_lab/plant.py::cone_terminal`
  (R = 2×offset, tip at √3·offset) — the next thing to work with.
- **Unresolved audit (2026-11-07):** swept HANDOFF/TASKS/BACKBURNER/goals. Added
  to `state/UNRESOLVED-int.md`: Stage III's four serif outlines (not wired), the
  uncertain combined curves, BACKBURNER B02 (Euler spiral → cubic fit), spiro
  as a G2 alternative, the ambiguity in "full cubic catalogue" (316/632 exist),
  and the canonical fleur (a form, not a curve). Features excluded on purpose.
- **All-of-it pass (2026-11-07):** kappa in NAMED; biarcs page (equal-radius,
  G1, R = √2−1); **Drawn pairs · 2** (Lissajous, yin-yang); qAC + discrete LAC
  page (c = 0 check 5e-5); Beta-splines written up in `app/src/content/docs/docs/junction.md` as a
  join option, not built. `state/UNRESOLVED-int.md` holds σ/τ, quartic
  Catmull–Rom and propeller for the operator's links. 482 figures; recheck
  45/45; 71 modules.
- **Research pass (2026-11-07):** kappa curve added to NAMED (29 named, 27
  exact; milestone scale 6.7e9 — exact but a ten-digit grid); Lissajous and the
  yin-yang boundary added as **Drawn pairs · 2**; `state/UNRESOLVED-int.md`
  holds σ-curve, τ-curve, quartic Catmull–Rom and propeller curve, waiting on
  the operator's links.
- **Arches and pillars (2026-11-07):** `workbench/arches-pillars.html`. One
  section mirrored about the centreline: if the halves meet inward it is an
  arch, if they branch outward it is a capital. Eight showcase sections,
  placed both ways and measured: three arches (cycloid 3.9° off vertical,
  astroid 8.5°, integer cubic 16.2°) and three capitals (squircle 11.6°,
  Euler steep 14.1°, log spiral 49.0°); two fit neither. Goals updated with
  the architectural branch; the next step is a whole bay.
- **Pell d, and constant width (2026-11-07):** `pell.py` now carries d = 2, 3,
  5, 6 (squares excluded). `reuleaux.py` adds the Reuleaux triangle three ways:
  exact 60° arcs (width 1), Bézier handles at 60° (radial error 2.4e-5), and the
  Pell 13/15 copy (closure gap 5.6e-4) — the demonstration that √3 is not a
  p-triple angle. recheck **39/39**.
- **Page structure (2026-11-07):** section 19's three spine panels, the reach
  chart (20c) and the fit-error chart (21c) moved to the notes page, where they
  render as illustrations with no back-link; the 19 text stays as the intro
  note. Composition and Primal moved to the end, before Rays. Showcase now 460
  figures, 163 rows.
- **Gen-Arch (2026-11-06/07):** `workbench/gen-arch.html` and a showcase family.
  Gen-Arch is r = a + b·φ^(1/c): c = −2 lituus, −1 hyperbolic, 1 Archimedean,
  2 Fermat. The radial of a LA curve is Gen-Arch with c = α − 1 (Salvi 2026),
  measured to 2e-16 on α = −2, −1, 2, 3. Three dials, now kept apart:
  α = LCH slope (κ ∝ s^(−1/α)), repo **p = −1/α**, c = α − 1 = −1/p − 1.
  **Correction:** C70's `p = 3` is α = −1/3, not α = 3; the stem cuts are
  relabelled `p = …`, never `α`. 465 showcase figures; recheck **38/38**.
- **Two figures (2026-11-06):** `workbench/discrete-clothoid.html` — equal chords,
  turns Δθ_k ∝ k quantised to p-triple angles; fitted exponent **1.001**, max
  error **0.31°** against a **1.35°** ladder gap; rational nodes at a 44-digit
  scale. `workbench/pyth-plane.html` — new **Fig. P4**: the evolute of y = x² is
  (−4t³, 3t² + ½), i.e. 27x² = 16(y − ½)³, with integer-t points; the copied
  27x² = 4(y − 2)³ is a different semicubical. recheck **37/37**.
- **Pell / √2 (2026-11-06):** `workbench/pell.html` — x² − 2y² = 1, the
  doubling law (x,y) → (x²+2y², 2xy), 3/2 → 17/12 → 577/408, and the addition
  law giving 99/70 from (3,2)·(17,12). Error is exactly 1/(2√2 y²); the page
  plots it log–log against the law. `scripts/pell.py`, `tests/test_pell.py`;
  recheck now **36/36**. The hub has a showcase link at the top.
- **Inventory, not sampler (2026-11-06):** the showcase gained a family of the
  cuts a stem is actually taken from — half a parabola, one hyperbola wing,
  **every one of the 31 recovered LAC spines cut at 90° and 130° of turn**
  (62 panels), and two Euler S spans (+30°→−30°, and at the 3/4 slope). 66
  panels; turns measured on the polylines: LAC 90.3–90.7° and 130.5–131.5°,
  S join 30.0° / peak 37.5° / end −29.6°. Showcase now 461 figures. The notes
  page carries a standalone explanation ("fig-spine-345") with no back-link,
  so notes can be prose as well as one-per-figure. Still missing from the
  inventory: the integer-lattice conics with Pythagorean slopes (pyth-plane),
  and the Pell page is queued.
- **Curve census (2026-11-06):** `semicubical` (Neile's parabola, y² = x³, the
  evolute of a parabola) is now in `NAMED` — 26 named, 24 exact, scales (3, 27)
  — so it also gained a stem card (178) and two showcase figures (395 total).
  Hit totals moved with it: 126 → 927. `tests/test_curve_census.py` now
  declares every curve outside `NAMED` (transcendental, conics, hearts) with
  its home and reason, so none can sit silently outside again.
- **Next move:** offsets / complementary side curves either side of every
  single-curve example — **done 2026-11-06**: `panel()` draws ±5% companions on
  every curve example (308 panels, 692 companion paths), one pair per drawn
  piece, and labels the rule (`fitted` 293, `exact` 13, `not an offset` 2). A
  curve is one curve even in pieces: hyperbola branches, lemniscate loops, cusp
  splits, and the Conversions ideal + quantised pair all qualify. Exempt: the
  three charts (3c, 19b, 20c) and the Rays panel. Reference: displayed Fig. 1a =
  key `0a`, the log spiral. The rule has its own line at y−32 so captions are
  not truncated. Test:
  `test_every_single_curve_panel_carries_companions`; `hub.py` must follow
  `showcase.py` or the page loses its bar (recheck 34/35).
- **Tried and rejected:** 3-4-5 turns for 13a at display scale — 36.87° reads as
  a kink; the 4.41° triple on the 3125 ladder is used instead. (2026-11-06)
- **Tried and rejected:** projecting dots off arbitrary grid crossings — the
  spacing was irregular by construction and left bare stretches. (2026-11-06)
- **Context:** 530k of 1M, 282 active min, 490 turns, ok; clock 106.4 min on
  the last record, tally median 35.9, mean 43.1, total 344.7 over 8.

## G3 work — 2026-11-08, updated 2026-11-09

The G3 showcase is now cubic-only: `workbench/g3-showcase.html` carries five
four-point spans per curve (the quintic G3 representation collapsed to cubics),
which is what Inkscape and the glyph pipeline need. The original quintic page
is preserved as `workbench/quintic-showcase.html`, titled “Quintic Béziers
every join G3”. The catalogue and the extend-and-cut page are unchanged and
still use the quintic conveyor; the cubic page is the glyph-facing view.


`workbench/g3-showcase.html` now uses quintic Bézier spans; every join is
measured G3 (position, tangent, curvature, curvature-rate). The bell is the
five-span interpolation the four-cubic attempt could not make G3. The cubic
curves collapse to cubics, carried as elevated quintics; the lattice cubic is
integer at ×6250. `workbench/g3-catalogue.html` attempts 232 candidates: the 29 named
curves, 24 heart forms, 21 integer cubics, 4 presets, 4 primals, 31 LAC spines,
90 Stage II spines and 19 other families. 160 are admitted (the circle is admitted but left to the notes page),
35 rejected with measured reasons (cusp, singular, or over 5% of the curve size). The curvature-rate formula was
corrected to `cross(r', r''')`; the old extra term is gone.

Next: fit the sampled hearts/squircle through a smooth polyline; then bring the
45° integer frame from the early bell notes onto the quintic bell and search for
integer points on the quintic controls. The extend-and-cut terminal is built:
`workbench/g3-cut.html` fits past a station, splits the span, keeps the left
chain and reports the cut deviation and G3 defect.

## 2026-11-09 — sequence curves landed; G3 catalogue at 166/232

- `workbench/sequence-curves.html`: five right-angle panels — factorials
  (4!…1!), triangular sums (T₄…T₁), the symmetric closure for n=4 and n=6, and
  the factorial closure. Every vertex is an integer.
- The closure `1,2,…,n,−n,…,−1` returns to the origin exactly: the return
  repeats each chord in reverse with the opposite sign, so the displacement
  cancels pairwise. `scripts/sequence_curves.py`,
  `tests/test_sequence_curves.py`, recheck 51/51.
- G3 status: the catalogue admits **166 of 232 (71.6%)**; target 186. The
  astroid is admitted as four smooth arcs, and the cubic showcase has cusp and
  deviation sections at the bottom. The remaining failures are 66: cusp/singular
  arcs still unsplit, and deviation over 5%.
- **Local:** 200 on `:8003`. **Remote:** unknown — only the placeholder
  `<your-service>.run.app` is recorded. **Tests:** 493 pass, 1 skipped
  (2026-11-09). **Git:** action committed; handoff commits follow.
- **Next move:** raise the G3 catalogue to the 80% target, 186 of 232, by
  splitting the remaining cusp/singular curves into smooth arcs and tightening
  the deviation cases, without relaxing the body-join gate.

Tried and rejected: the plain square-turn `1..n,-n..-1` schedule for general n
— only n=3 and n=4 close, so the page uses the signed reverse-chord return
instead. Invented C2/Catmull–Rom comparison curves — not from the original
showcase, replaced by astroid/oids/hearts. The equal-aspect `Frame` on the
acceleration graph — collapsed a 0–1 x-range against ±7 y into a strip; fixed
with independent x/y scales. (2026-11-09)

## 2026-11-11 — PH gallery; PHH/PPH pinned to 2D

- **Previous action did not land.** The 2026-11-09 handoff targeted the G3
  catalogue at 186/232 (80%). It was not done; the next-fhandoff was stale.
  `recheck` now reports **154 admitted, 78 rejected** of 232. The focus has
  moved to PH; the G3 80% target is not current.
- `workbench/ph-families.html` is the nine-card static PH gallery, generated
  by `scripts/ph_families.py`. It now has a **Plain English** panel at the
  bottom and a test (`tests/test_ph_families.py`). The cubic card is still the
  C-shaped arc; the full nodal Tschirnhausen alpha is the next fix.
- **Definitions are 2D only**: PH = polynomial Pythagorean-hodograph curve;
  **PHH = PH Hermite** (PH quintic interpolant through two points with
  prescribed tangents); **PPH = piecewise PH** (PH spans joined with
  continuity). The spatial/helix reading is out.
- **The 116 count did not reproduce.** Current `\bPH\b`: 32 docs-only; 18 in
  `PH-INTEGER.md`/`INTEGER-CUBIC.md`/`FLOWERS-int.md`; 196 docs+scripts. The
  generated `app/src/content/docs/docs/ph-integer.md` was created at `b2e56cf` with 12 and never
  116. Reconcile the note's pattern/snapshot or mark it stale.
- **Local:** `:8003/health` returns **404** (server not serving that route or
  not up). **Remote:** Cloud Run unknown; no URL recorded. **GitHub:** `main`
  pushed to `561bbf8`; CI run `42972105138` was not confirmed green; the watch
  was abandoned. **Tests:** 542 pass, 1 skipped (run 2026-11-11 on the
  `561bbf8` tree; carried after commit). **Recheck:** 54/54 at `561bbf8`.
- **Next move:** complete the 2D PH/PHH/PPH examination in
  `workbench/ph-families.html`; see `next-fhandoff-int.md`.
- **Tried and rejected:** the G3 80% target — stale and not attempted in this
  session; current 154/232. The 116 PH count — not reproducible with `\bPH\b`;
  reconcile or mark stale. (2026-11-11)

## 2026-11-11 — the PH ladder page, PHH/PPH pinned

**The occurrence audit is settled.** The operator's 116 is reproducible as
`git grep -o -E '\bPH' HEAD -- '*.md' | wc -l` at commit `8f26aa7`: it is a
*prefix* count (PH, PHH, PPH, PH-families). The exact token `\bPH\b` gives 90
over `*.md`, 32 over `docs/` (with the generated HTML twin) and 18 over
`docs/*.md`. The note is not stale; the pattern is now written on the page.

**`workbench/ph-families.html` rebuilt** by `scripts/ph_families.py`:
definitions of PH / PHH / PPH in one block (2D only); the audit; thirteen rungs
from the cubic to n = 8 plus the rational circle, each with more than one
example and all four quadrants; the full nodal Tschirnhausen alpha with the
C-segment marked; the integer scale/hit table at m = 4; a live explainer
(generators, grid m, quadrants, d, break PH) in
`workbench/ph-families-app.js`, whose BigInt scale is tested against
`generators.PHCurve.scale`; and the PHH/PPH panel.

**New geometry:** `curve_lab/ph_hermite.py`. PHH is the PH quintic through two
points with prescribed tangents — endpoint hit exactly by the quadratic in `b`,
`2b² + 3(a+c)b + (3a² + ac + 3c² − 15Δ) = 0`, with the declared speed rule
`|a| = |c| = √|Δ|`. PPH is the C² continuation: the next span's `a` is the
previous `c` and its `b` is set by the previous end slope, so the join is exact
by construction; the page reports |Δz|, |Δz′|, |Δz″|, |Δκ| all zero.

**Tests:** `tests/test_ph_hermite.py` (14) and `tests/test_ph_families_app.py`
(JS scale vs Python). Recheck carries the claim. Suite green; 55/55.

**Not built (on the page):** the general five-parameter PH quintic family, the
classical PHH magnitude rule, a general C² PPH solve (five conditions per join),
the PH quintic transition curve, rational PH beyond the circle, the general
n = 7/8 families, and anything in 3D.

## 2026-11-11 (later) — the page finished, the names corrected, iteration cut

**The page is complete.** `workbench/ph-families.html` carries Figs 1–16 (the
rungs, the integer cubic, the rational circle), 17–19 (the ladder), 20 (the live
figure), the m = 10 section (Figs 21–25, 27–35 — 154 milestones over the same
fourteen rungs), Fig. 26 (the six-span split), C6 and C61 (fitted rails) and H1
(PH–Hermite/PPH). Exports: `workbench/integer-curves.svg` and
`workbench/tschirnhausen-stem.svg`, every coordinate an integer, guarded by
`tests/test_ph_families.py`.

**Vocabulary, corrected against the literature.** The interpolant is
**PH–Hermite**, not PHH: in CAGD *PHH* is the **PHH-Bézier** approximation of a
hyperbolic **H-Bézier**. **PPH** is Piecewise Pythagorean-Hodograph, as the
literature has it. The page quotes both sources and gives the construction per
degree: cubic `b = (−a ± √(3(4Δ − a²)))/2` (checked 1.8e-15), quintic
`2b² + 3(a+c)b + (3a² + ac + 3c² − 15Δ) = 0`. *Milestone* is the word for
`t = k/m`; *station* already means one-coordinate-integer in
`app/src/content/docs/docs/philosophy.md`, so it is not used for these.

**Numbers that can be quoted.** The alpha `18y² = x(x−6)²` has integer points
`(18k², ±6k(3k²−1))` plus the node `(6,0)` — four in `t ∈ [−4,4]`. At `h = 3`
its controls are integers and ten points fall in the same window. The showcase's
lattice marks are now only true integer points (699 of them, carrying
`data-x`/`data-y`, checked by `tests/test_exploration_pages.py`); the old
evenly spaced arc-length dots are gone.

**Iteration.** `scripts/test.py` runs one module per process: default set
86.6 s → 42.6 s, `--full` ~110 s → ~95 s, whose floor is `test_fleur_sets`
alone. `scripts/pagecache.py` skips a page whose inputs are unchanged:
ph-families 4.4 s → 0.23 s, showcase 67 s → 0.19 s, g3 pages 35 s → 0.47 s
(`--force` rebuilds; cache in `state/build-cache.json`, gitignored).

**Green at this commit:** suite 577 tests OK, 1 skipped (parallel runner,
2026-11-11); recheck 55/55 (2026-11-11); remote not checked (no deploy).

**Tried and rejected:** the per-import dependency walk in `pagecache.py` — 0.7 s
per call and it can still miss a dependency, so it was replaced by hashing
`curve_lab/` and `scripts/` whole; the ten-module SERIAL list in `test.py` —
it made the parallel run slower than serial, since only the two modules that
rewrite `stem-library.html` actually compete.

**Next:** the operator's alternative route to integer points on the Tschirnhausen
by Pythagorean-triangle construction. They asked for it eventually to live in
its own directory and said **not to set the directory up yet**, so the first step
is the rule in prose, not code.

**2026-11-11 — session clock retired.** The wall clock came out of the workflow:
the memory pressure behind it was Chrome, not OpenCode's context, so it measured
the wrong thing. `scripts/timer.js` and `scripts/notify.js` moved to
`legacy/timer/` (`ROOT` and the chime path fixed after the move; `--check` still
answers). `AGENTS.md`, `/fhandon` and `/fhandoff` no longer start or report a
clock. `state/timers.jsonl` stays as history. `scripts/ctx.py` is the only
measurement now. Superseded: the "Session timer" section of TODO.md, and the
elapsed/tally fields in earlier handoff blocks.

**2026-11-11 — integer-hit chain: verified, and the focus rules loosened.** The
discrete triangle chain is built and checked, in `tph_tri_chain/` and not in
`curve_lab/`: `chain.py` (exact Fractions), `glyph.py` (SVG in cells),
`sandbox.py` (page), `t1.js` (d3 figure), vendored d3 7.9.2, `RESULTS.md` and
`results.html`. Verified: the curve meets the integer lattice only at t in 3Z
plus the waist at t = ±√3; pitch is q³, or 4q³ when the step width's top number
is odd; at twelve triangles the pitch is 108 at t=4, 256 at t=3, 500 at 12/5;
every vertex is an integer point, and the curve misses by T³/(12N²).

Rules changed this session, all recorded in `legacy/agent-rules-retired.md`:
instructions accumulate (AGENTS.md); the handoff file is a default, not the
priority of record; "add no code until the rule is written" retired; "held / do
not wire in" retired; the image ban replaced by a 150 KB / 1000 px limit, and
verified by reading back a 93 KB PNG.

Recheck 55/55. The single failure found was `workbench/todo.html` missing its hub
bar after regeneration — re-run `scripts/todo.py` then `scripts/hub.py`, in that
order, whenever TODO.md changes. Tests: 577 OK, carried from earlier today; the
suite was not touched this session. Local probe: `/health` returned 404, not
investigated. Remote: not checked, and no Cloud Run URL is recorded here.

Tried and rejected: two raw half-chains concatenated for the glyph — the nose
lands 1/64 off and the tips disagree (+1536 against −1528), so the right half is
mirrored instead. Also rejected: named HTML entities in SVG (XML refuses them and
the image goes blank); 3125 as a grid at twelve triangles (it needs step width
2/5, so t = 24/5); decimals in tables (they hide whether a point is rational);
and a 156k context window (it is 1M).

**Scope, next few sessions: `tph_tri_chain/` only.** Nothing outside it is in
play — not W01–W04, not `curve_lab/`, not the quintic pass. The thread runs until
the comparison below is fair, one action per session:

1. Fig. T1 labels, so the figure can be read (the current block).
2. One source of truth: either retire `RESULTS.md` / `results.html` or convert
   them to exact fractions. Two documents that disagree is the failure mode.
3. The like-for-like table on the sandbox page: midpoint against straight joins,
   same triangle count, exact values, with the length comparison written as
   fractions and square roots rather than decimals.
4. Stop. At that point the method can be compared on its merits.

"Finished" for this thread means: one page, exact throughout, legible figure, and
an SVG export in integer cells that Inkscape opens without rescaling.

**2026-11-11 — Fig. T1 labels fixed (item 1 of the tph_tri_chain thread).**
`tph_tri_chain/t1.js` now puts each vertex label in a left or right column, runs
a one-dimensional spread per column (gap 2), and draws a leader line for a
displaced label (3 of 25). The two tips label inward, the nose labels right, and
A–D sit above their rings with a paper halo. The canvas is 980 × 820 at a
uniform 0.25 px per cell, with an in-figure title, both axis labels, and a
15 px two-row legend. Measured, not eyeballed: `node tph_tri_chain/audit_t1.mjs`
prints 25 labels, 0 label overlaps, 0 letter-vs-ring overlaps, 0 overlaps among
all 76 text boxes, 0 boxes outside the figure, and 25/25 vertex pairs matching
`chain.py`. `tph_tri_chain/out/t1.png` is 980 × 822, 85.5 KB. The operator has
not yet looked at it; the visual call is theirs. Next in the thread is item 2
(one source of truth for `RESULTS.md` / `results.html`).

**2026-11-11 — iteration gate slimmed.** `scripts/test.py --slim` runs ten
engine modules (model, piece, clearance, fillet, junction, section, grammar,
pyth_triples, pyth_cubic, todo) in 3.1 s with no page built; it is a smoke
gate, not the commit gate. `node tph_tri_chain/audit_t1.mjs` now falls back to
the page on disk when :8003 is down, so the T1 audit never needs the server.
The two together take 5.7 s: `.venv/bin/python scripts/test.py --slim && node
tph_tri_chain/audit_t1.mjs`. The default set (40 s) and `--full` are unchanged.

**2026-11-11 — the thread rotated to the algebraic orientation.** The operator
was right: the standard Tschirnhausen (and this repo's own alpha form
18y² = x(x−6)²) has the loop along x, and the PH form (t − t³/3, t²) stood it
up. `chain.py` now carries x = t², y = t − t³/3, so 9y² = x(x−3)² exactly; the
exact coordinate is now x (x′ = 2t is linear) and the drift is in y. The mirror
in `t1_block`, `glyph.py` and the audit is in y, not x. Every derived artefact
was regenerated: sandbox tables and prose, `RESULTS.md` / `results.html`,
`out/lattice-t3.svg` / `.csv`, `out/midpoint.svg` (Fig. T2 transposed: B is
"x is exact", C is "y drifts"), and `out/t1.png`. All ten memo checks in
`chain.py` pass, and `make_results.py` reports 0 failures. The audit prints 25
labels, 0 overlaps, 25/25 pairs against `chain.py`; `out/t1.png` is 729 × 982,
86.8 KB. The visual call on the rotated figures is the operator's.

**2026-11-11 — TQ(k) page built.** `workbench/ph-quintic-lattice.html`
(`scripts/ph_quintic_lattice.py`) carries the Tschirnhausen-type PH quintic:
primitive, polynomial, `w = k(t²−1) + i`, so `y` is a cubic and only `x` is
fifth-degree. The hit period is periodic mod 15 — `15|k` gives every integer t
at scale 5, `3|k` gives 5ℤ at scale 5, `5|k` gives 3ℤ at scale 15, neither gives
15ℤ at scale 15 — so there is no ceiling on k, only k² growth in the control
numbers. TQ(15) is the headline (every integer t; controls 0…595 at scale 5;
arc 121 at t=1, 123005 at t=5); TQ(3) is the small-controls member (hits at
5ℤ). Every unit piece, reparametrised, is a quintic Bézier with integer
controls at scale 5, so the cuts are exact and the lengths are rational.
`tests/test_ph_quintic_lattice.py` (8 tests) checks the identity, the periods,
the piece controls, the lengths and the degree-5 chain grid (442,368, drift 31).
The page is in the manifest (80 pages) and links to `ph-families.html` and the
tph_tri_chain sandbox. Suite 84 modules, green; the page figure has 0 text
overlaps and 0 boxes outside its 940×500 viewBox.

**2026-11-11 — TQ page: six figures, k = 75, and one persistent headless Chrome.**
`workbench/ph-quintic-lattice.html` now carries six figures: the family
(TQ(3)/TQ(15)/TQ(75) side by side), TQ(75) in all four quadrants, the zoom on
the S and the inflection at (0,0), the three cut pieces, the grid-cost bars
(256 vs 442,368 vs 5, log), and x(t)/y(t) with the stops. k = 75 is the
headline: every integer t, grid 5, first piece controls (0, 5624, 11248, 14997,
14996, 14995) / (0, −150, −300, −425, −500, −500), arc 3001 at t = 1 and
3,075,005 at t = 5. The member table now says "every integer t / every 3rd /
every 5th / every 15th", counts the hits in t = 0…5, and drops the ℤ notation.
Browser work now attaches to one persistent headless shell on :9223
(`chrome-headless-shell`, no window, no Dock icon); `audit_t1.mjs` connects
over CDP and never launches a second Chrome. All six figures: 0 text overlaps,
0 boxes outside the viewBox. 8 tests, slim suite green.

## 2026-11-13 — PH curves at degree 6 and 7 (septic sandbox)

The quintic theory is settled and unchanged. The new work lives in
`workbench/ph-septic-sandbox.html` (panels A-D, generated by
`scripts/ph_septic_sandbox.py` from `scripts/ph_septic_panels.js`):

- **A**: general degree-7 polynomial, 14 sliders.
- **B**: PH septic, eight speed numbers, curve and chord terms side by side,
  solver for right angles and closure, named curves (half-heart, flourish-a,
  flourish-b, lazy-s-2), save + paste + download JSON.
- **C**: G2 Hermite interpolation (two points, two tangents, two curvatures),
  Levenberg-Marquardt over the eight speeds, residual 0.0000.
- **D**: 40 sample curves from small integer speeds, two per row.

Exact machinery: `scripts/ph_quintic_metrics.py` (bend, pitch, inflection,
closest, diagnostics at any degree), `scripts/ph_quintic_hits.py` (stops, exact
gcd, near misses), `scripts/ph_math.js` (one copy of the page maths).

`lazy-s-2` is the simple-number classic so far: speed (2, -3, 3, 0.5) /
(2, -12, 12, -0.5), bend 1.736, pitch 70.

Open: the CI run from the last push (`gh run list -L 1`), and the six TODO
items under "PH curves at degree 6 and 7".

## 2026-11-13 (late) — sandbox layout, two-slider speeds

Landed and pushed: `2e71f09` fine + decade slider on every speed (the solver
could exceed ±16 and the display disagreed), `3089156` sliders stacked and
full-width with the buttons under the images, `77029a3` the t^k label beside the
input. Local server 200; `check-ph-page.mjs` green (7 readouts). Tests carried:
649 tests from the last full run, 2026-11-12 (no code under web/, curve_lab/,
tests/ changed since). CI: runs 43347946554 / 43348118205 were in flight at the
earlier handoff; the only known failure was the review-doc check importing
`markdown`, fixed in 70262d4 / 84ff0b7.

Tried and rejected: widening the sample search to [-3,3] exhaustively — 2.5M
candidates at ~64 ops each timed out; [-2,2] plus a random [-4,4] sweep is the
working recipe.

## 2026-11-13 (later) — gallery D promoted to named curves

`scripts/septic_curves.py` now carries twelve named curves: the four shaped by
hand (half-heart, flourish-a, flourish-b, lazy-s-2) plus eight promoted from
gallery D, one per measured signature — small-loop, tight-loop, shallow-turn,
narrow-arch, vertical-s, tight-hook, straight-start, long-sweep. Each keeps its
gallery speeds unchanged; `test_the_promoted_curves_keep_their_gallery_numbers`
pins every stored metric to its sample's.

`workbench/septic-curves.json` and `workbench/ph-septic-sandbox.html` were
regenerated and `scripts/hub.py` run. In the browser: 12 named buttons render,
clicking **tight-loop** loads its speeds and reads bend 2.082 / pitch 210 /
inflection 0.441 / closest 0.197, no page errors. `check-ph-page.mjs` prints OK
(7 readouts, 6 save buttons). Test module 9 tests OK; default suite 91 modules
green, exit 0. Committed locally; not pushed in this action.

Tried and rejected: naming the curves by eye from the panels — the selection
comes from measured signatures instead (self-crossings by segment test at 1200
samples; bend/pitch/inflection/closest from `ph_quintic_metrics`), so each name
states a number. Rejected "hairpin" for the 180° shallow turn: the word already
means a turned terminal in `app/src/content/docs/docs/philosophy.md`.

## 2026-11-13 (later still) — the sandbox box bug, and the classic curve

Two defects reported from use, both fixed and committed:

- **Typing ate the sign and the decimal point.** `input` fired on every
  keystroke, and `syncBCell` wrote the field back; a partial entry ("-", "0.")
  reads as empty in a number input, so `-1` became `1` and `79.301` became
  `301`. Now a field is never written back while it is the source, and empty or
  non-finite text is ignored. `check-ph-page.mjs` retypes the default speeds key
  by key and fails if anything moves — proved by running it against the old
  handler (FAIL: `-3 -> 3`, `0.3 -> 30`).
- **The boxes clipped long numbers.** Panel B's speed boxes are now
  `field-sizing: content` (min 96, max 176 px), the decade slider is a fixed
  64 px, and the fine slider keeps the rest; measured at 1200/900/390 px with
  `-14997.123456` typed: no clipping, panel B inside the page. Panel A is
  untouched; the page's pre-existing horizontal overflow at 900/390 (104/614 px)
  is unchanged and is panel A's, not this fix's.
- **The formula block now prints the eight speeds** as well as x(t)/y(t), since
  the boxes take the speed numbers and the polynomial is what is displayed.

**The classic curve is exactly PH.** Speeds x `(2, -5, 6, 0)`, y
`(4, -20, 20, -2)` reproduce `bend 3.011 | pitch 105 | inflection 0.505 |
closest 1.068`, degree 7 (x 7, y 6), and the position polynomial character for
character (controls integer at 105). The earlier paste (bend 30.134) is not PH:
its z' is not a perfect square (residual 0.111 at t^4..t^6), so no eight speeds
reproduce it; the nearest square root gives bend 29.857, pitch 1.05e14.

**Two curves pinned from the operator's pastes:** `integer-105` above, and
`integer-70` — x `(2, -3, 3, 3)`, y `(2, -12, 12, 1)`, bend 1.290, pitch 70
(controls integer at 70; 1.143 -> 80). Both are exact, not replicas.

**The chord box, reworked into a comparison.** The old single box listed seven
vectors with a numeric column and read badly. It is now two boxes beside the
plot, on one scale: **B1** chains the terms head to tail in two shapes (blue
quintic T0-T4, red septic-only T5-T6) and rings where the quintic ends; **B2**
is a signed bar chart — position on a common zero baseline, not angle and
radius, because a sign is read from side and size from length (Cleveland's
ranking: position beats length, length beats angle/area). Each term is two bars,
x in ink and y in brown, on rows t^1..t^7, with the septic-only rows t^6-t^7 on
a tint. A compass/rose version was drafted and dropped: it reads worse for
signed values once the terms stop being parallel.

The plot, B1 and B2 sit in one row at 1200 px (449/281/281), fold to two rows at
1000 and one at 700; the chord viewBox is 400x460 with 18/17 px text so it stays
readable at a third of the width. Measured at 1200/1000/700: 0 text overlaps,
0 text outside either box. The numbers are printed in a line under the row
(`#b-terms-values`), not stacked inside the figure.

**A live JSON box.** `#b-json` is a read-only textarea under the paste row that
always holds the current curve in the shape `workbench/septic-curves.json` and
the paste box both take: name, speedX, speedY, bend, pitch, inflection,
closest, degree. It carries the name of the clicked curve and falls back to
"curve" after a hand edit. Proved by cutting it into the paste box: "1 curve
loaded", same readout.

**The size slider is a magnitude.** It spanned -16..16, so a zero mantissa sat
exactly half way across, which read as "set to middle" when the value was
nothing. It now spans 0..10 (the mantissa's own range, so it no longer snaps on
release) and keeps the sign already in the box: zero is at the left end, and
dragging `-2` to 7 gives `-7`. Typing a minus still sets the sign.

`scripts/shot.mjs` takes an optional CSS selector as a seventh argument and
shoots just that element: `node scripts/shot.mjs <url> <out.png> 1040 900
viewport .trio` gives the three boxes in one 954x300, 30 KB image.

## 2026-11-13 — is the septic more productive than the quintic? Measured

Four deterministic experiments, no sweeps (about 12 solver runs total):

1. **Full closure is degenerate.** `bend = arc/|chord|`, so `|C| = 0` gives an
   infinite bend. Every exactly-closed septic the solver produced is a tight
   coil (bend 1e5-1e6), not a shape. The curves worth keeping sit at 20-33%
   openness (`H` 0.222, `G` 0.218, `loop-105` 0.240, `double-loop` 0.290,
   `integer-105` 0.332); `classic-30` at 0.033 gives bend 30. Closure is a dial,
   and the tidy step is what pulls the curve back into the usable band.
2. **The third degree is load-bearing.** Dropping `t^3` from the same numbers:
   `loop-105` 1 crossing -> 0, `G` 1 -> 0 (bend rises to 21.2), `H` stays 0,
   `double-loop` stays 1. The two extra knobs are what hold loops at moderate
   openness.
3. **Automated tidy is the fragile part.** Holding a target openness is one
   equation in two unknowns; snapping the rest to integers and solving moved the
   last coefficient by 0.3-1.3 and the pitch from 1e9 to 1e11. The hand tidy is
   doing real stabilising work.
4. **No new curves by symmetry.** Swap, mirror-x, mirror-y and point-reflection
   of the nine named curves produced no new two-crossing shape. `double-loop`
   came from the close walk, not from symmetry.

Verdict: the septic is the better *search space* (loops survive), the cubic and
quintic the better *output space* (degree 7 controls are not what Inkscape
wants). A "close to a chosen openness" dial is the one control that follows from
this; the plain close button stays as it is.

**2026-11-13 — the operator's method, and the low-pitch field.** The walk is:
put the speeds near 50, vary one or two, press `close chord` (or `close to …`),
then tidy. That is the process behind `H`, `G`, `Cap-C`, `cap-T`, `fish-1`,
`drop`, `drop-2`, `double-knot`, `heart-2`.

Every named curve now also carries a low-pitch form in
`workbench/septic-curves.json`: `speedXLow`, `speedYLow`, `pitchLow`,
`closestLow`. Scaling all eight speeds leaves bend and inflection untouched and
scales `closest`, so the same shape can sit on a coarser grid; the fields are
chosen by lowest pitch over a fixed set of terminating-decimal scales
(`scripts/septic_curves.py`, `SCALES`). It is a second field, never a
replacement: names such as `loop-105` and `integer-70` state the original pitch,
so replacing would make them false. **`half-heart` is exempt** — the heart is a
recognised figure and its decimals are the accepted statement of it.

Measured: 26 of 27 non-exempt curves can be written lower; the floors are 7, 14
and 21, set by the `1/(k+1)` factors, not by the speeds. Every low form was
checked to keep the parent's bend and inflection to 1e-6 and to carry the pitch
its stored numbers actually produce.

## 2026-11-13 — the nth sandbox: degree 11, fitted curves, a gallery

**Landed.** `workbench/ph-nth-sandbox.html` (part 1) and `workbench/ph-nth-sandbox-2.html`
(part 2), generated by `scripts/ph_nth_sandbox.py` and `ph_nth_sandbox2.py` from
`scripts/ph_nth_panels.js`. Part 1 carries exact curves; part 2 carries 80 showcase paths
fitted to degree-11 PH speeds (`scripts/ph_fit_showcase.py --write 80`), each with its
source path stored, so a cell opens original (left) against fitted (right).

Controls on both pages: close chord, close-to with an openness dial, lift a quintic, a
coarsest-grid button, character offsets (per-side strength, bow/S/taper profile, end
shear), a rational tail hook, arc terminals on either end, a -45 view, a JSON box, and
save/rename/delete/transfer with duplicate-name confirmation.

**What this session proved, measured.** The number on the page called *grid* is the
integer scale `1/N` at which every position coefficient is an integer: integer speeds
always give `N | 27720 = lcm(1..11)`; at degree 13 the constant is `360360`; decimals
break the rule because `w` is squared. A hook stored as magnitude and angle is irrational
and blows the grid to 1e14; stored as a rational pair `(dx, dy)` it can even lower it.
Monomial speed coefficients are ill-conditioned: 0.1% on `t^3` moves the fitted curve 38%
of its size, so rounding the numbers cannot simplify a fitted curve.

**Local:** 200 on `:8003`. **Remote:** no `.run.app` URL recorded, not probed (carried
2026-11-13, no deploy this session). **Tests:** full suite 97 modules green, `recheck`
55/55 (2026-11-13). **Git:** `ea969b8`, clean apart from this block.

**Risks.** The 3-figure "simplified" column is not shape-preserving — it is evidence of
the conditioning problem, not a tool. Saved curves live in `localStorage`, so a different
browser sees only the seeds. Part 2's fits are labelled `fitted` with their rms; nothing
there is claimed exact.

**Next move:** part 3 at degree 13 (`SPEED_DEGREE = 6`, 14 speed boxes, position degree
13), the natural test for cursive `m / v / w / u`.

Tried and rejected: rounding monomial speeds to three figures — the curve moved by 0.02
to 208 times its size; a polar hook (magnitude and angle) — irrational, grid 3.5e14;
refitting at degree 3 as a "rough grade" — collapsed or diverged on the LAC curves.

**Context:** 72.9% of 1M, 331 active min, 557 turns, WARN — the session stopped
adding work at the warning, not at the cap.

## 2026-11-13 (night) — the ladder, the pair, and what the formula can carry

The sandbox grew from one rung to five, gained a second curve, and the curve
family was measured against the log-aesthetic law. Everything below is checked
by a script in the repo, not remembered.

**Built.** The degree ladder (`11, 13, 15, 17, 19` — 12 to 20 speed numbers) with
a slider and a sign flip on every number; the complementary curve in 40% grey
with its own sliders, a crossing count and marked meetings; placement as a 3x3
affine matrix per curve in the saved record (`curve-lab.double-knot/1`), plus a
`turn` rule about the spine's centre because a centroid-rotation matrix would be
wrong the moment the numbers change; a `t from` / `t to` window with no clamp; a
`place the end` Newton solve on the top pair; an inflection count against the
ceiling `2k - 1`; and the explanation panel (arithmetic ladder, product grid,
length triangles, which-box-does-what, start-heading compass, Fig. E1-E4).

**Tools.** `ph_crossings.py` (self and pair crossings), `ph_find.py` (random
search on the two counts, `--write` to `workbench/found-curves.json`, which the
gallery fetches), `ph_root_family.py` (letter strokes by root position),
`lac_generate.py` (exact LAC spines from `(p, turn)`), `lac_fit.py` (is this an
LAC?), `ph_carry.py` (can the PH formula carry a target curve?), `lac_rosettes.py`
and `node_curves.py`.

**Findings worth not losing.**
- Position degree is always odd (`2k + 1`), so **12, 14 and 16 cannot occur**.
- The grid ceiling is `lcm(1..d)`: 11 -> 27,720; **13 and 15 both 360,360**;
  17 -> 12,252,240; 19 -> 232,792,560. Degree 15 is the cheap rung above 11.
- **Symmetry comes from roots placed symmetrically about `t = 1/2`.** `wave3` is
  roots `1/6, 1/2, 5/6`; `wave5` adds `1/3, 2/3`. A random search never finds
  these; the root walk does, and it found 183 symmetric curves in one pass.
- **The involute is an LAC at `p = 2`, exactly**: `rho = t`, `s = t^2/2`, so
  `rho^2 = 2s`. The circle is `p = 0`, the Euler `p = -1`, the log spiral
  `p = 1` (self-similar: scale 2 came back as 2.0002 and a turn of 39.63 deg
  against the predicted `ln 2 = 39.72`).
- **The PH formula carries any smooth target; the degree is the accuracy dial.**
  At `k = 9`: involute 3e-5, catenary 0, Euler 0, log spiral 0 of the size.
  The LAC law is the specification, the PH formula the representation.
- **Node curves are not LACs** (residuals 0.06 to 0.78): rolling circles,
  lemniscates, piriform, roses, strophoid, trisectrix, the sandbox cusps. They are
  joins. Even the recovered involute plate (Stage II Fig. 14 spine 4) is drawn 3%
  off the ideal.
- **Crossings with the horizontal flip are 0 for symmetric curves.** The lace
  comes from rotated copies about the centroid: `wave3` crosses 20 times at 180
  deg, 19 at 90.
- Fitted transcendental curves have no grid: `1/18,018,000,000,000`. Shapes only.

**Bugs fixed, all found by cross-checking two implementations.** The pitch and
`curve_polynomials` dropped the y terms when the x row was shorter (pitch read 1
instead of 14); the vectorised crossing count paired segment *i* with *i* (8
where the drawing crosses 3); numpy was an undeclared dependency, now pinned in
`requirements.txt` and installed by CI; a `t from` of 0 piled 350 duplicate points
on the origin; a duplicated control block left two of every id.

**Risks.** Fitted curves are shapes, not exact PH curves, and their grids are
useless. The gallery thumbnail is 200x150, so a spiral reads as a thick line
there; judge on the main plot. Saved curves live in `localStorage`.

**Next move.** Write the notes-page section (specification vs representation, with
both tables), then decide whether the 183 symmetric-root curves beyond `wave3`
are worth a page: the best so far is `x [1,0,0,0] y [-4,33,-75,50]` at 12
meetings with its 180-degree copy.

**Context:** 62.5% of 1M, 359 active min, 528 turns, verdict ok. **Git:** `b0bb749`.

## 2026-11-13 (night, status at handoff)

**The previous action did not land, and should not.** `next-fhandoff-int.md` asked
for part 3 at degree 13 (`scripts/ph_nth_sandbox3.py`, 14 boxes). That work was
superseded in the session above by the **degree ladder**: rungs at 11, 13, 15, 17
and 19 inside the one page, so a separate part-3 page was never built and is not
wanted. The next handoff says so instead of repeating it.

**Current truth.**
- **Local:** 200 on `:8003` (probed 2026-11-13).
- **Remote:** no `.run.app` URL recorded; the probe returned 000. Carried from
  2026-11-13, no deploy this session.
- **Tests:** carried, 100 modules green from `scripts/test.py --full` on
  2026-11-13; `web/`, `curve_lab/`, `csrc/` and `tests/` are unchanged since HEAD,
  so nothing was re-run.
- **Claims:** `scripts/recheck.py` 55/55 on 2026-11-13, `state/ACHIEVEMENTS-int.md`
  unchanged.
- **Git:** clean after this block except `state/sessions.jsonl` (the ctx log).

Tried and rejected: a random search for knot-like curves over small-integer speed
rows (scripts/ph_similar.py, 1500 draws) — it found zero symmetric curves, because
symmetry comes from roots placed symmetrically about t = 1/2 and a random draw
almost never lands there; the root walk replaced it and found 183 in one pass. Also
rejected: judging every node curve by the LAC law — most are not LACs.

**Next move:** the notes-page section, specification versus representation, with
both tables.

## 2026-13-11 (session) — new curves from the symmetric root walk

**Landed.** `scripts/ph_root_search.py` walks every mirror-closed root set up to a
chosen speed degree and denominator, over symmetric x rows only (a constant and
`c·t(1−t)`), and measures each curve. Symmetry about `t = 1/2` is an exact equation
on the coefficients, so random small-integer rows never land on it (1,500 draws, 0
hits); choosing the roots and multiplying out makes it true by construction.

**At speed degree 5** (12 speed numbers, the degree-11 rung): 57 curves pass the
shape filter. `wave3` comes back at the top of the degree-3 walk with 20 meetings
at 180° and 19 at 90°, which is the hand-found number, so the walk is calibrated on
a known case before it is trusted on new ones.

**15 curves landed** in `workbench/found-curves.json` (the gallery fetches it at
load, so no rebuild): three laces at roots 1/8, 1/10 and 1/12 with three roots at
1/2, giving 8, 8 and 10 self-crossings and 16, 12 and 14 meetings with their
half-turn copies. That beats `knot-6`'s six crossings from a four-number row.
Best: `lace-1of8-3`, bend 1.39, grid 1/1155, 8 self-crossings. Names state the
construction, e.g. `wave-1of4-1of3-1` = pairs 1/4 and 1/3 plus one root at 1/2.

**Proved.** `tests/test_ph_root_search.py` (7): mirrored roots give `q(1−t) = ±q(t)`
exactly, `wave3` is exactly `72(t−1/6)(t−1/2)(t−5/6)`, three non-symmetric rows all
fail. `tests/test_ph_root_found.py` (6): every stored row rebuilds from its own
name, is symmetric in integers, and its bend/pitch/inflections match a fresh
measurement. Suite 98 modules green; `check-nth-page.mjs` OK (gallery of 71, the
lace loads its rows). Commit `9158204`, pushed, CI run `43557627848` green.

**Screenshots** for the operator: `$TMPDIR/lace-1of8-3.png`, `$TMPDIR/lace-1of12-3.png`
(407×334, 10 and 13 KB). Not read by the model.

Tried and rejected: naming by the smallest pair only — `wave-1of4-1-2` came out for
a row with two pairs, which the name denied; now every pair is in the name and the
test checks it. Appending without a guard against the existing seeds — `wave5`'s own
y row turned up as a find; `write_found` now skips a row proportional to a seed's.

**Next:** the same exhaustive walk at speed degree 7 (16 numbers, ~45 min of compute)
and degree 9; then the notes-page section still owed (specification vs representation).

## 2026-11-14 — mirror-safe tweaks, and the register that keeps them

**Built.** The experimental page replaces its complementary curve with a "Tweak
the primary curve, mirror kept" panel: a size box and one button per balanced
pattern. Measured at size 0.2, every pattern holds the mirror gap at 0.0000 at
both step 1 and step ½, and the primary curve redraws at once.

The patterns, as additions at the given powers: `x: t1,t2 = -1,+1`;
`x: t2..t4 = +1,-2,+1`; `x: t3..t6 = +1,-3,+3,-1`; `y: t1..t3 = -1,+3,-2`;
`y: t2..t5 = -1,+4,-5,+2`. The y row needs the three-number form because it reads
as its own negative from the far end. The operator's own `+0.1/-0.1` habit is the
first row.

**Two faults found by use, both fixed and guarded:** the multiply by
`1 + size(t - t²)` was trimming the top two powers, and those are exactly the
terms that balance the change — hence "it goes lopsided"; and undo crashed after
a tweak had grown the rung, because a restored row was shorter than the boxes.
Both now have browser checks in `scripts/check-nth-page.mjs`, register rows 14
and 15.

**Also landed:** `scripts/register.py` runs the whole register — the fast
fixed-fault checks plus the browser gate — starting the server itself and
reporting a could-not-run as a non-zero outcome, so a skip is never a pass. Its
first run found three defects, all fixed. The data format is
`curve-lab.curves/2`: terms carry their power, measured numbers are labelled, and
`workbench/found-curves.json` validates before it is written.

**Focus now:** making new curves with the tweak panel and adding them to the
front of the experimental page's found curves, which now sorts newest first.

## 2026-11-14 (session) — the sandbox, the register, and what the curves can do

**The previous action did not land.** `next-fhandoff-int.md` asked for the notes-page
section on specification vs representation (membership and carry tables). It was not
done; this session worked on the sandbox pages instead. The front matter of
`ph-nth-serif-notes.html` was not regenerated with those tables.

**Built.** The experimental sandbox now has: a flat-spot ruler whose numbers stack per
copy (click the number to add, shift-click to remove), an explicit `fill from the dots`,
a fraction size box, and a `Tweak the primary curve, mirror kept` panel with balanced
patterns for the x row (`t1,t2`; `t2..t4`; `t3..t6`) and the y row (`t1..t3 = -1,+3,-2`;
`t2..t5`), plus a multiply of both rows by `1 + size(t - t^2)`. Measured: every pattern
holds the mirror at 0.0000, and the sizes are binary-exact only — a size of 1/3 took the
grid from 3,465 to 8.7e13.

**Measured, and these are the numbers worth keeping.** Legs shorten by moving the outer
flat spots inward (88% → 42% → 12%), not by cutting `t`: these curves' crossings span
t 0.02 to 0.98, and the largest exact span below the whole curve is 0.879. Half powers
are a dial, not a field: 0 of 400 random half-power rows made a knot, but one term at
`t^1/2` took a curve from 6 crossings to 9. A share of the coefficient is the cheap
lever: 1/4 of the 16 pair took the grid 3,465 → 693. Base pairs whose magnitude is a
multiple of five (`15`, `20`, `30`) give grid 693.

**Data.** `workbench/found-curves.json` is `curve-lab.curves/2`: `name`, `terms` (power
beside each value), `measured`, `provenance`, and optionally `truncation`. 169 records,
67 of them truncated by arc length (20% off each end). Every stored bend and grid
re-derives from its own terms. Records now carry `step`, so a curve made at ½ reloads at
½; absent means whole powers.

**Register.** `scripts/register.py` runs the fast fixed-fault checks and the browser gate
as one command, starting the server itself; a could-not-run exits non-zero rather than
being counted a pass. 17 rows. Green at this commit.

**Local:** 200 on `:8003`. **Remote:** no `.run.app` URL recorded; not probed, no deploy
this session (carried 2026-11-13). **Tests:** `scripts/test.py` green at `8f168c3` — 101
modules, no failures (119.6 s). Two reds were carried in and fixed: `test_ph_root_found.py`
read `speedX`/`bend`/`pitch` after `workbench/found-curves.json` became
`curve-lab.curves/2` (172 errors), and the experimental page's gallery test demanded no
gallery on a page that has one. Both guards are reversed rather than deleted (register rows
19, 20). **Git:** `8f168c3`, not pushed (no internet this session).

**Risks, in the order they will bite.** (1) The drawing is coalesced into one animation
frame, so any test or script that clicks and then immediately reads the DOM sees the previous
frame — the gate needs a 120 ms settle, which is why it once reported the rails failing. That
is a behaviour change, not a bug, and it will look like a bug to whoever writes the next
check. (2) Pan and zoom move the viewBox only: 20 pans in 473 ms, and the polyline stays at
700 points, so zoom no longer raises sampling — the earlier "jagged at high zoom" fix is moot
and sampling cannot be raised by zooming. (3) Open, unfixed: the pan sliders are coarse (one
step is one model unit, and these curves are a few units across); thumbnails of browser-saved
curves cannot be reproduced headlessly because localStorage is invisible to a headless run;
the three knot-cutting controls are parked on `ph-nth-exp-notes.html` and the truncation
decision (fitter consumes it, or the field goes) is still open in `TODO.md`. (4) There is no
d3 on the sandbox pages — they write SVG by hand, and d3 is vendored only in `tph_tri_chain/`;
if "standard across the project" was a request rather than a question, that is a deliberate
refactor and its own action, not a one-line change.

**Next move:** start the Bézier fitting step on one stored curve, with the span plan and
the deviation measured rather than eyeballed.

Tried and rejected: cutting legs in `t` (window, arc-length cut, exact sub-span rebuild,
integer-hit cut) — the crossings span the curve, and a half-power row is not a polynomial
in `t`, so no span shorter than the whole holds the knot; the three controls are parked on
`ph-nth-exp-notes.html`. Also rejected: tweak sizes of 1/3 or 1/7 (binary-inexact, grid
explodes), and coefficient-wise multiplication by `t(1-t)` (must be a polynomial product,
otherwise the mirror breaks).

**Context:** the operator reports 77% used. `scripts/ctx.py --log` reports 2.7% for
session `ses_e230985b1ffe`, which is not this conversation's id (`ses_e27b9fc53ffe`), so
the meter is not tracking this session — carried as ambiguous rather than trusted.

## 2026-11-14, 847bb1e — the specification/representation section

The focused action came true. `scripts/ph_nth_serif_notes.py` now emits a
"Specification and representation" section at the top of
`workbench/ph-nth-serif-notes.html`, and it says the thing in words: the
log-aesthetic law says what the curve must be (a specification), the PH formula
says how it is drawn (a representation), and neither implies the other — the
Euler spiral and the log spiral meet the law and are not polynomial, so no degree
carries them exactly.

Table 1 is membership of the family (circle p = 0, Euler p = −1, log spiral p = 1,
involute p = 2), computed by `lac_fit.best_power`, the same function
`lac_fit.py --classics` prints. The circle's row reads 0.1 because the scan skips
0; the page says why. Table 2 is the degree-`k` PH carry at k = 3, 5, 7, 9,
computed by `ph_carry`. Neither table is typed in:
`test_the_carry_table_is_computed_not_typed` recomputes cells and the page must
match to five places. Figures 1 and 2 are now numbered inside the figure, and the
two tables are numbered with captions.

Register row 18: the reproduce checks on `ph-nth-sandbox.html` and
`ph-nth-sandbox-2.html` compared the build stamp, so they failed whenever the
minute rolled over — a red suite with nothing changed. Both now drop the stamp
line before comparing.

## 2026-11-14, ec4ae68 — the flat-spot ruler, doubled

The ruler read 0 to 1 across the box, so every fraction crowded into the left
half and 1/19 and 1/20 were 2.6 px apart. It now runs **0 to 1/2 across the
whole width**, with a **second strip under it from 1 to 1/2** that names the
mirrors — 18/19 sits directly under 1/19 at 10.53%, so a spot and its partner
line up. Denominators reach 20 and now include 17 and 19.

Labels pack by their own width over six rows, so all 64 keep their names; the
gap between 1/19 and 1/20 is 6.4 px on a 1030 px page (it was 2.6 px). Only the
lower strip places spots — the upper is a read-out. Four pages inline
`scripts/ph_nth_panels.js` and all four were regenerated (11th, 11th-2,
sandbox, sandbox-2, exp).

## 2026-11-14, 1e677c0 — seven families above the found curves

The experimental page now opens with the seven families the operator named:
one outer flat spot, its mirror and three copies at 1/2 — `1/15` to `1/9`. Each
is five spots, so a `t^5` row. A button writes the spots into the field and
presses the same "fill from the dots" the operator presses (at step 1, so six
numbers land in six boxes), then scrolls to the strip. A rule separates them from
the found gallery, which stays below for later.

Measured by clicking each one: bend 1.148, 1.192, 1.250, 1.328, 1.431, 1.571,
1.772 for 1/15, 1/14, 1/13, 1/12, 1/11, 1/10, 1/9; grids 1/154, 1/231, 1/1386,
1/77, 1/42, 1/693, 1/22.

The tweak panel was rebuilt the same day (`4aedfdb`): one dropdown of the five
patterns, four press-buttons (-5, -1, +1, +5), undo, and "widen the ink" at s = 1,
5, 13, 39. The share-of-the-pair dial is gone — inert on the families, and its
divisors do not divide the common pairs (25, 36). The total-change line clears on
a family load, a gallery load, a fill, a step change and a typed number.

Two faults fixed at `7609051`. The readout said "grid n/a: fractional powers" with
no fractional power in use: `recipeMetrics` fell back to the numeric path whenever
the step was not 1. A row whose half boxes are empty is folded back to whole powers
(and padded, or a constant x row cut the powers off the squared row) and measured
exactly; a real half-power term still reports n/a. And the gallery and the speed
grid used `1fr`, which floors at content width, so a long cell pushed the page past
the window and the found curves ran off the right edge — both are
`repeat(2, minmax(0, 1fr))` now, measured clean at 900–1280 px.

**Next move:** not set by this session; the operator runs `/fhandoff`. Both carried
reds are gone (rows 19 and 20) and the experimental page keeps its gallery by the
operator's call. The serif notes section landed at `847bb1e`.

## 2026-11-16, 1b8774e — handoff

**Did the previous action land? No.** The block of 2026-11-14 asked for the Bézier fitting
step and named `scripts/bezier_fit.py` and `tests/test_bezier_fit.py`; neither file exists.
The session that followed worked on the page instead, so the action is still open and is the
next move below, unchanged.

**Local:** 200 on `:8003`. **Remote:** `000` — no `.run.app` URL recorded, not probed
(carried 2026-11-13; nothing deployed this session). **Tests:** carried — 101 modules green
at `1b8774e`, the last full `scripts/test.py` run this session; nothing under `web/`,
`curve_lab/`, `csrc/` or `tests/` has changed since. **Register:** `tests.test_regressions`
green, run now (14 tests). **Git:** clean at `1b8774e` except this block.

**What changed this session.** Pages: the serif notes section (`847bb1e`); a second
symmetric ruler, fold-into-whole-powers so a whole-power row on a step of ½ reports its grid,
a gallery split into Symmetric/Asymmetric by a 1 % mirror test, `copy this one` for saved
records, a manual focus (`focus` in the record), and the "possible families" section
(`7ac5852`). Data: `curves/` holds ten curves, each `curve.json` + `notes.md`, with figures
drawn from the flat spots and y stretched by a printed factor. Review page:
`workbench/curve-figures.html` — ten rows, page view beside factored view, accept/reject,
decisions returned as JSON. **None of those decisions has been made yet.**

**Risks, in the order they will bite.** (1) The census families draw as slivers because
`p = 1` against `q` of 10⁸; that is the shape, not a renderer fault, and the fix is a
balanced family, not a picture. (2) The context meter is retired (AGENTS.md, 2026-11-16): its
share did not match the session, so no percentage is quoted here. (3) The drawing is
coalesced into one animation frame, so a test that clicks and reads the DOM needs a beat.
(4) `curves/*/figure.png` are withdrawn where the page draws a line; `figure-exact.png` is
the only picture for those.

**Next move:** start the Bézier fitting step — fit `wide-knot-x20` with cubic spans, print the
span count and the maximum deviation as a share of the curve's size, and do the same for two
more stored curves.

**Context:** meter retired 2026-11-16 and not quoted. `scripts/ctx.py --log` reports 394
active minutes and 558 turns for this session; those are reported, not judged.

Tried and rejected: rescaling the row to fix the drawing — dividing by its peak gave a
10^-15-wide curve (scaling `w` scales the curve by its square) and 1/sqrt(peak) still degraded
a curve that draws unscaled at peak 2.7e5; the cause is cancellation, and the factored form
was the answer. Tried and rejected: a size threshold as a predictor of which rows the page
miscounts — it did not pick out the five that failed.

## 2026-11-16, senior review of the codebase

Asked for as a review; recorded here so it is not carried in someone's head.

**Sizes, measured.** Engine (`curve_lab/`, `web/`) 7,862 lines. Generators (`scripts/`) 55,899.
Generated pages (`workbench/`) 53,967 lines across 95 pages. Tests 9,092 lines, 105 modules.
Commits 821. The engine is small; the generators are seven times its size and the HTML they write
is as large again. That ratio is the finding: the product is 95 generated pages written as Python
strings.

**What is genuinely good.** Exact arithmetic as a stated invariant, not an aspiration. A bug
register with a test per row (`state/REGRESSIONS-int.md`, 20 rows). Pages generated, never
hand-edited. Written memory that lets a session start in minutes. 105 test modules.

**Five things to fix, in value order.**

1. **The numeric core exists three times and disagrees with itself.** `pitch` lives in
   `ph_math.js`, `ph_quintic_metrics.py` and four scripts written this session. They agree in exact
   arithmetic and disagree in doubles: the page said grid 1/5,148 where the exact answer is 1/36,
   with identical rows. That divergence is the cause of most of 2026-11-16's confusion. One
   reference implementation, exact, exported for the page to consume.
2. **Three figure pipelines, created this session.** `curves/<slug>/figure.png` (page capture or
   exact drawing), `workbench/figures/*.png` (169 HUD captures), and `figure-exact.png`/`.svg`
   beside the first. One curve, one picture, one path, one script; the gallery reads that path.
3. **The ad-hoc verification should be a test.** `scripts/curve_png_all.mjs` compares the page's
   grid and bend with the record's for every curve. Nothing in `tests/` does, which is why a stale
   stash and a wrong step both reached the operator. That check belongs in the suite.
4. **Tests assert strings and counts, not behaviour.** The clean-up broke tests demanding more than
   100 records and a named curve's flat spots. Every literal count (60, 109, 169, 50 markers) is a
   test that will fail for the right reason eventually. Derive expectations from data; assert DOM
   structure rather than substrings.
5. **3,846 lines of `ph_nth_panels.js` inlined into 100 pages** — 384,600 duplicated lines, and the
   reason one edit dirties 100 pages and eight generators. Serve it as a static file, or accept
   that "one page, one generator" implies one copy of the engine and stop inlining.

**Smaller observations.** Files over 1,800 lines that are 80 % HTML (`g3_showcase.py`,
`ph_families.py`) want template files, which would give escaping (a curve name containing a quote
can break a page), highlighting and readable diffs. `ctx.py` is retired but still present; it
belongs in `legacy/`. `family-census.json` is 1.2 MB of derived data: committed, good, but say in
one line where it comes from and that the sweep takes twelve minutes. The register tracks faults,
not absences — it has no row for "nothing compares page numbers with record numbers".

**Advice for the next session:** not more features. One action — make the page consume exact
precomputed numbers, and add the test that compares them. That is the difference between a lab that
finds curves and a lab that trusts its own display.

## 2026-11-16 (end), handoff

**Did the previous action land? No.** The block still asks for the Bézier fitting step and names
`scripts/bezier_fit.py` and `tests/test_bezier_fit.py`; neither exists. Unchanged and still next.

**Local:** 200 on `:8003`. **Remote:** `000`, no `.run.app` URL recorded, not probed (carried
2026-11-13). **Tests:** carried — 101 modules green at `7ed8afb`, the last full `scripts/test.py` run
this session; nothing under `web/`, `curve_lab/`, `csrc/` or `tests/` changed since. **Register:**
green, run now. **Git:** `1795a8e`, plus this block and the two operator screenshots moved to
`docs/evidence/`.

**What changed since the review block.** The tweak explanation moved to the notes page (the panel
keeps a title and a link); the gallery gained star and up/down ordering with a JSON box; the
clean-up list from the operator was applied — 109 curves to `workbench/moved-curves.json` and
`workbench/moved-curves.html`, 60 left in `found-curves.json`, numbered Fig. 1 to 60 with 54
symmetric and 6 asymmetric.

**Risks, in the order they will bite.** (1) The numeric core still exists three times and the page's
own arithmetic disagrees with the exact answer on large rows — the review's first item, still open.
(2) Three figure pipelines exist. (3) The gallery's star order and moved list live in the browser
until the JSON comes back. (4) Tests still assert literal counts, so the next data change breaks
them for the right reason.

**Next move:** the Bézier fitting step, unchanged.

**Context:** meter retired 2026-11-16 and not quoted; `ctx.py` reports 560 active minutes, 723
turns, verdict WARN — reported, not judged. The session is long by choice.

Tried and rejected: rescaling the row to fix the drawing (10^-15 curve at 1/peak; 1/sqrt(peak)
degraded a curve that draws unscaled) — the cause was cancellation, the answer was the factored
form. Tried and rejected: a coefficient-size threshold as a predictor of which rows the page
miscounts — it did not pick out the five that failed. Tried and rejected: hiding moved curves at
load — the late re-render brought them back; the fix is to apply the archive inside every render.

## 2026-11-16 (final), handoff

**Did the previous action land? No.** `scripts/bezier_fit.py` still does not exist, so the Bézier
fitting step is unchanged and remains the next move.

**Local:** 200 on `:8003`. **Remote:** `000`, no `.run.app` URL recorded, not probed (carried
2026-11-13). **Tests:** carried — 101 modules green at `faf8546`, the last full run this session;
nothing under `web/`, `curve_lab/`, `csrc/` or `tests/` changed since. **Register:** green, run now.
**Reading list:** `scripts/reading_counts.py --check` passes; counts current. **Git:** clean at
`faf8546`.

**What changed since the review block.** The gallery gained star and up/down ordering with a JSON
box; the operator's clean-up was applied (109 curves to `workbench/moved-curves.json` and
`workbench/moved-curves.html`, 60 left, Fig. 1–60, 54 symmetric and 6 asymmetric); the tweak
explanation moved to the notes page; the reading list got a refresh script, a `/fhandoff` step and
three rows for this session's files; and the browser-only state now has one-press export
(`operator-list.json`: saved curves, moved list, star order), verified with seeded data.

**Risks, in the order they will bite.** (1) The numeric core still exists three times and the page's
arithmetic disagrees with the exact answer on large rows — the review's first item. (2) Three figure
pipelines exist. (3) Saved curves, the moved list and the star order live only in the browser until
`export everything` is pressed. (4) Tests still assert literal counts, so the next data change will
break them for the right reason.

**Next move:** the Bézier fitting step, unchanged.

**Context:** meter retired 2026-11-16 and not quoted; `ctx.py` reports the numbers above, verdict
WARN, session long by choice.

Tried and rejected: rescaling the row to fix the drawing (10^-15 curve at 1/peak; 1/sqrt(peak)
degraded a curve that draws unscaled) — cancellation was the cause, the factored form the answer.
Tried and rejected: a coefficient-size threshold to predict which rows the page miscounts — it did
not pick out the five that failed. Tried and rejected: hiding moved curves only at load — the late
re-render brought them back; the fix is to apply the archive inside every render. Tried and
rejected: quoting the page's own grid on large rows — it is wrong in doubles (1/5,148 against an
exact 1/36 on identical rows), so the record is the authority.

## 2026-11-16 (later) — the senior review, in its own words

Recorded 2026-11-16, at the operator's request: "include all that in the handoff."
The summary of this review sits earlier in this file, under "2026-11-16, senior
review of the codebase". This block carries the review's own words, so a later
session reads the argument rather than a paraphrase. Provenance: one senior-dev
pass, DeepSeek V4.1 Flash 1017, 7 min 5 s.

**Where it stands.** The review landed at `1795a8e`; its four highest-value items
became rows in `TODO.md`. The three handoffs after it (`5b12485`, `296ba50`,
`82d85c0`) all kept the Bézier fitting step as the next move, so the review's
advice has not been actioned yet. The fifth item, on tests asserting counts,
never became a row.

### The shape of it

| area | measured |
|---|---|
| engine (`curve_lab/`, `web/`) | 7,862 lines |
| generators (`scripts/`) | 55,899 lines |
| generated pages (`workbench/`) | 53,967 lines across 95 pages |
| tests | 9,092 lines, 105 modules |
| commits | 821 |

The engine is small and the generators are seven times its size. That ratio is
the whole story: the HTML is the product and it is written as Python strings.

### What is genuinely good

- Exact arithmetic is a stated invariant, not a hope: `Fraction`, whole rows,
  exact arc as a polynomial integral.
- A bug register with tests (`state/REGRESSIONS-int.md`, 20 rows). That is rarer
  than it should be.
- Pages are generated, never hand-edited — the one rule that keeps 95 pages
  honest.
- Written memory: LTMemory, HANDOFF, TODO, READING — a new session can start in
  minutes.
- 105 test modules for a research lab is real discipline.

### Five things I would fix, in value order

1. **The numeric core exists three times and disagrees with itself.**
   `pitch` is implemented in `ph_math.js`, `ph_quintic_metrics.py`, and four
   scripts added that day. They agree in exact arithmetic and disagree in
   doubles: the page said grid 1/5,148 where the exact answer is 1/36, with
   identical rows. That single divergence caused most of that afternoon. One
   reference implementation (Python, exact), exported as data the page consumes,
   kills the whole class.
2. **Three parallel figure pipelines — the reviewer's doing, that day.**
   `curves/<slug>/figure.png` (page capture or exact drawing),
   `workbench/figures/*.png` (169 HUD captures), plus `figure-exact.png`/`.svg`
   beside the first. One curve should have one picture, one path, one script,
   and the gallery should read that path.
3. **The verification written ad hoc should be a test.**
   `scripts/curve_png_all.mjs` checks the page's grid equals the record's for
   every curve. Nothing in `tests/` does that, which is why a stale-stash bug and
   a wrong-step bug both survived to the operator. That check belongs in the
   suite.
4. **Tests assert strings and counts, not behaviour.** That day's clean-up broke
   tests that demanded more than 100 records and a named curve's flat spots.
   Every literal count (60, 109, 169, the 50 markers) is a test that will fail
   for the right reason eventually. Derive expectations from the data; assert
   DOM structure, not substrings.
5. **3,846 lines of `ph_nth_panels.js` inlined into 100 pages.** That is 384,600
   lines of duplicated JavaScript in the repository, and it is why an edit to one
   file lights up 100 dirty pages and 8 failing generators at once. Either serve
   it as a static file, or accept that "one page, one generator" implies "one
   copy of the engine" and stop inlining.

### Smaller observations

- `scripts/` has files over 1,800 lines that are 80 % HTML (`g3_showcase.py`,
  `ph_families.py`). Template files would give escaping, syntax highlighting and
  readable diffs. Right now a name containing a quote can break a page — that
  risk was hit with curve names.
- `ctx.py` is retired but still on disk; fine, but it should move to `legacy/` so
  nobody wires it back up.
- `family-census.json` is 1.2 MB of derived data committed. Good — but it should
  say in one line where it comes from and how long the sweep takes, so no one
  regenerates it blindly (12 minutes).
- The register has 20 rows; two faults that day were found by the operator, not
  by it. The register tracks faults; it does not yet track absences like "no test
  compares page numbers with record numbers".

### What I would advise for the next session

Not more features. One action: make the page consume exact precomputed numbers,
and add the test that compares them. That is the difference between a lab that
finds curves and a lab that trusts its own display.

## 2026-11-17 (night) — the exact core, the lost buttons, and the stale crossing counts

**Did the previous action land? No.** `next-fhandoff-int.md` still asks for the Bézier
fitting step and `scripts/bezier_fit.py` does not exist. The operator parked it in words:
"we need the curves and the engine to be complete before we go cubic bezier."

**Local:** 200 on `:8003`. **Remote:** `000`, carried from 2026-11-13, not probed.
**Tests:** 106 modules green at `26d8a3c` (`scripts/test.py`, 86.6 s). **Register:** 24 rows,
green. **Git:** clean at `26d8a3c` plus this block. **Tag:** `page-works-2026-11-16` at
`f24301f` — a page whose rails draw, whose side-curve controls exist and whose buttons hold
every stored curve.

**What landed, in the order it was asked for.**

1. **One exact numeric core.** `curve_lab/measure.py` holds grid, bend, arc, inflections,
   closest in `Fraction`; `scripts/ph_quintic_metrics.py` is a facade over it. The page prints
   a stored curve's numbers from its record, labelled "(exact, from the record)", while the
   loaded rows are untouched. `loop-13-15-17-mid-1` reproduced exactly: record 36, page 5,148.
2. **The saved-curve buttons.** `workbench/operator-list.json` holds 179 curves built from the
   stored records by `scripts/operator_list.py`; a browser with no list is seeded from it, so
   the B panel shows 212 buttons instead of 33. A failed read can no longer become a write:
   backup + mirror on every save, repair on load, `undo the last change`, `restore a list`.
   `scripts/check-saved.mjs` proves six of those, including a pair record.
3. **The gallery carries every stored curve** — 60 found, 109 moved, 10 kept — and the
   experimental page keeps the complementary-curve box (it used to cut it out of its own
   build, which is why the side-curve button could not exist there).
4. **`Look closer`** is its own section: the optical controls no longer sit among the ones
   that change the numbers.
5. **`scripts/build-pages.py`** rebuilds all eight pages that inline the shared JavaScript;
   `tests/test_page_assets.py` fails when a page is older than the shared file. This is the
   fault that made a correct rails control look dead.
6. **Crossings are one number again: crossing pairs.** 100 stored counts predated the
   parameter-pair dedupe. `scripts/crossing_audit.py` recomputes, `--write` restores,
   `tests/test_crossings.py` guards. `lace-1of10-1of5-3` is 5 pairs at 3 places.
7. **`scripts/reading_counts.py`** was blind to numbered rows; it now refreshes Tier 0 and
   `tests/test_reading_counts.py` guards it. `/fhandon`'s stale 846-line note and its retired
   no-image rule are corrected, and `READING-int.md` now says the opening message adds to
   Tier 0 and never replaces it.

**Risks, in the order they will bite.** (1) Every page still inlines `ph_math.js` and
`ph_nth_panels.js`; the build script and the drift test catch a forgotten rebuild, but the
review's item 5 — serve one copy — removes the class. (2) Three figure pipelines still exist;
collapsing them needs the operator to say whether the review page's factored views survive.
(3) Tests still assert literal counts (60, 109, 169, 50). (4) Saved curves, the moved list and
the star order live in the browser until exported.

**Next move:** the two-arc cone terminal — one arc from each rail end, radius
`R = 2 × offset`, tangent at the base and meeting at the centreline tip, with the
arc centres stated. The `cone` already in `curve_lab/terminals.py` is a width law,
not this construction, so the new one needs its own name. It is goals.md work item
2 and it finishes the terminal layer the review left alone.

**Context:** meter retired 2026-11-16 and not quoted. Session long by choice; the operator
asked for the night.

Tried and rejected: testing against a fresh browser profile while the operator works in the
light one — it proved the source and not the page, and a stale inline copy looked like a dead
control. Tried and rejected: comparing inlined JavaScript byte for byte — some generators
substitute inside the copy on purpose; the build-time test is the honest check. Tried and
rejected: clustering crossings by position to report "meeting places" — the count then
depends on scale, so it is not a property of the curve.

## 2026-11-17 (later) — S1 landed: the cone terminal, both modes

**Did the previous action land? Yes.** S1 of `state/PLAN-int.md` is done: the
engine function, the symmetric mode, the proof page and the tests.

**Local:** 200 on `:8003` (probed at handoff). **Remote:** `000`, carried from
2026-11-13, not probed. **Tests:** 108 modules green, carried from `7362b32`
(`scripts/test.py`, 83.4 s, 2026-11-17) — nothing under `web/`, `curve_lab/`,
`csrc/` or `tests/` differs from HEAD since. **Register:** 14 tests, green, run
now. **Git:** clean at `cb63932` except the session log.

**What landed.**
- `curve_lab/terminals.py`: `cone_terminal()` — two 60° arcs, `R = 2 × half`, each
  centred on the *opposite* rail's end, meeting at `√3 × half`; `symmetric=True`
  with `centre` and `tangent` snaps the rail ends to a mirror pair and puts the
  tip on the centreline, reporting `shift` and `axis_twist`. Eleven tests.
- Two bugs the tests did not catch, found by looking at the page: the tip's
  perpendicular was not normalised, and the second arc left the tip along the
  incoming tangent (a loop at the point). Both fixed; both visible only in the
  rendered figure. Lesson: draw the figure and look at it.
- `workbench/cone-terminal.html`: Fig. C1a default (tip off the stroke, 8.53°
  twist) and C1b symmetric (tip on the centreline, 12.000 snapped).
- The false "engine has no image input" rule is gone from every file; images are
  450 KB / 3000 px. Context-budget instructions are gone; DESIGN records why.

**Risks.** (1) The default cap still leans on a curved spine; symmetric mode is
the answer and the caller must pass the spine's tangent. (2) The figure is drawn
from straight rails; a curved spine's joins are not shown. (3) Page not yet in
the hub manifest.

**Next move:** S2 — the integer cubic's exact PH offset rail beside the Levien
fit on the same curve.

Tried and rejected: reporting a suite result from `tail -4` — it hides the
`FAILED` blocks above the summary, and I twice called a red tree green; grep for
`FAILED` or read the whole summary. Tried and rejected: comparing the inlined
panels byte for byte — some generators substitute inside the copy on purpose, so
the build-time check is the honest one. Tried and rejected: clustering crossings
by position to report "meeting places" — the count then depends on the figure's
scale and is not a property of the curve. Tried and rejected: verifying in a
fresh browser profile while the operator works in the light one — it proves the
source, not the page.

## 2026-11-17 (later) — S2 landed: the exact PH rail, the lattice grid, a mirror candidate

**Did the previous action land? Yes.** S2 of `state/PLAN-int.md`: `integer-105`'s
exact rail beside the Levien fit, plus the lattice grid the action asked for.

**Local:** 200 on `:8003` (probed at the session start). **Remote:** not pushed —
the operator's rule is no internet unless asked. **Tests:** 109 modules green
(`scripts/test.py`, 84 s, 4 skipped without `--full`). **Register:** 14 green.
**Git:** `da3e8f5`, clean except this block and the session log.

**What landed.**
- `curve_lab/ph_offset.py`: the exact PH offset as a ratio of two polynomials,
  `O = C + d·(−y', x')/σ`. Exact `Fraction` points, `lattice_scale`,
  `first_interior_hit`, `hits_at_scale`, and a float sampler for fits/drawings.
  No Bézier control data: cubics are the export step.
- `scripts/integer_ph_rail.py` + `workbench/integer-ph-rail.html` (manifest and
  hub entry). `integer-105`: pitch 105 gives **2** lattice points; the first
  interior hit is **t = 1/2, grid 3360** (32× the pitch); the rails share that
  grid only at **d = 41/1120** (normal (40/41, −9/41)), and at d = 3/100 the
  rail needs **688,800**. The station translates to (0, 4130) with the rails at
  (120, 4103) and (−120, 4157). It is **not** a mirror: half-turn gap 37%,
  mirror gap 49%, tangent 12.7° off vertical, x = 0 met four times.
- The fit is measured (45 spans, 9.2e-6 = 4.4e-6 of the 2.068 size) and printed
  as a number, not drawn.
- **Mirror candidate, not adopted:** `u = 1`, `v = (2t − 1)²`. Half-turn gap
  0.000, tangent at the midpoint exactly horizontal, y axis crosses once.
  Grid 15: midpoint (6, 5) → (0, 5) after a shift of −2/5; rails at d = 1/15
  give (0, 6) and (0, 4); the +rail's first interior hit is **grid 5**.
- `tests/test_integer_ph_rail.py` (14 tests): normal equations in `Fraction`,
  pinned polynomials, the grid numbers, the station, the label-swap guard, the
  candidate. Recheck claim added; DESIGN, TODO and LTMemory updated.

**Risks.** (1) Adopting the candidate changes the primary curve. (2) The lattice
search is t = k/q up to q = 200 — not a proof against an irrational-parameter
hit. (3) A rail hits the lattice only when d is chosen for the normal there.

**Next move:** the operator's choice — keep `integer-105` (exact rail, no mirror
axis) or adopt the symmetric candidate (exact rail and mirror axis). Otherwise
S3, the `Section` wiring.

Rejected: reading the page's speed pair as the derivative (that made the curve
look non-PH; it is PH because the pages write `C' = (u² − v², 2uv)`); giving the
rail Bézier control data (two negative weights, a 3.0e27 denominator, and a
Bézier form the operator asked to defer); drawing the cubic fit; calling the
four-crossing midpoint line a mirror.

## 2026-11-17 (end of the long session) — JS core, book plates, the lab; real curves next

**Did the previous action land? Yes.** S2 landed, then the JS exact core, the
book plates and the square/rectangle lab.

**Local:** 200 on `:8003`. **Remote:** not pushed — no internet unless asked.
**Tests:** 111 Python modules and 18 JS tests green; register green; recheck
56/56 at the run before the lab work. **Git:** clean at this commit.

**What landed.**
- **S2:** `curve_lab/ph_offset.py` and `scripts/integer_ph_rail.py`; the exact
  rail for `integer-105`, the first interior lattice hit at **grid 3360**
  (t = 1/2), the rails sharing it only at **d = 41/1120**, and the symmetric
  candidate `u = 1, v = (2t − 1)²` at grid 15.
- **JS core:** `workbench/exact.js`, `poly_exact.js`, `ph_offset.js`, 18 tests
  pinned to the Python numbers; `scripts/test.py` runs `node --test`;
  `state/PORT-int.md` sets the boundary (browser JS, Node for tests, Python
  where it is debugged).
- **Book plates:** `book/` with six symmetric plates, 300 dpi, tight crop,
  white, no text, two-column gallery; `scripts/plate_export.py`,
  `plate_curves.py`, `plate_png.mjs`, `png_dpi.py`; 7 tests.
- **The lab:** `workbench/square-frame.html`, `workbench/square_lab.js`,
  `curve_lab/square_assembly.py`. The leg bisects the 90° corner; the curve is
  placed on one edge and mirrored/quarter-turned for the other three; the frame
  takes counts across and down and an a/b pattern; the leaf is curve a below
  and flipped b above. Measured: arch/arch tips 90°/90°, S/arch 90°/0°.
  1 pt stroke floor at 1–4 in.
- **Records:** founder's log has a Current focus, the plan marks S2, the next
  action is B7.

**Risks.** (1) The lab still offers the four sandbox cubics; B7 is the fix.
(2) The book waits; the set and trim size are not chosen. (3) The JS port is
partial: the rail lab, crossings and grid remain Python. (4) The leaf's tip
pair must match before a leaf goes in the book.

**Next move:** B7 — real curves in the lab, normalised to the chord.

Tried and rejected: the four sandbox cubics as the lab's curve set (they are
placeholders); lace plates (|d·κ| = 735, no visible rail); a second
implementation of a page; Node as a build dependency; calling a station a
mirror.

## 2026-11-17 (final) — the plate path is JS

The book plates and the central designs now run in JS: `workbench/plate_math.js`
(the spine, the character rails, the caps that close the ribbon, and
cross/leaf/arch/frame) and `scripts/plates_export.mjs` (SVG, 300 dpi PNG,
gallery). The Python plate files are deleted — `plate_curves.py`,
`plate_designs.py`, `plate_export.py`, `plate_png.mjs`, `png_dpi.py` and
`tests/test_plate_export.py` — so there is one implementation, not two.

`tests/js/plates.test.js` guards the maths and the files: 6 tests; the gate now
runs 24 JS tests. The gallery has two framed symmetric designs (cross, leaf) above the 27 single
curves; the arch is a single plate and a lab form, because a natural-leg arch
frame overlaps itself. Every character rail is closed at its ends.

B7 then moved the lab onto the same data and maths: the curve set is inlined
and checked (empty, count, zeros), and the four sandbox cubics and
`square_lab.js` are gone.

**Stars and the picker.** The lab stars a design to `localStorage`, downloads
`starred.json`; the exporter adds those plates under **Framed Quintic symmetric
figures** above **Simple framed symmetric central figures** and the singles. A
picker at the foot of the lab shows all 28 curves with their rails and symmetry;
click to load one. **Next:** B8, the chain form.

## 2026-11-17 (later still) — B7 landed: the lab on the real curves

The lab now loads the saved set and draws with `workbench/plate_math.js`: the
curve, its character rails, the closed ends, and cross/leaf/arch/frame. The four
sandbox cubics and `workbench/square_lab.js` are deleted. The curve data is
**inlined into the page** (no fetch, no load wait), and the single arch is the
default. Controls: curve a/b, form, counts, a/b pattern, leg or natural legs,
print size, fill, alternate, frame.

Tests: 6 page tests and 15 JS tests. **Stars and the picker.** The lab stars a design to `localStorage`, downloads
`starred.json`; the exporter adds those plates under **Framed Quintic symmetric
figures** above **Simple framed symmetric central figures** and the singles. A
picker at the foot of the lab shows all 28 curves with their rails and symmetry;
click to load one. **Next:** B8, the chain form.

## 2026-11-17 (Astro) — the app is Astro; the lab and its save are live

**Decision:** the operator chose Astro for the final app. No React; local file
support; it must run on Next and other servers.

**Running:** `app/` with Astro **5.18.2** + `@astrojs/node` **9.5.5** on
**:4321**. Astro 7 refused this machine's Node 22.4.1 (it wants >=22.23.4);
Astro 5 accepts it. A global Astro 5.18.2 is installed. The old grid-8 project
is on 4.15.

**What works.** The lab page imports the shared `workbench/plate_math.js` and
`workbench/real-curves.json` (Vite fs.allow to the repo root). A star stores the
current design in localStorage; **save to workbench** posts to `/api/stars` and
writes `workbench/starred.json` through `app/src/lib/stars.js` — plain Node,
validated ids, temp file + rename. The download stays as the fallback. A browser
run verified: 88 cards, star, save, file on disk.

**Tests:** 4 save tests in `app/tests/stars.test.mjs`, now in the gate with the
17 JS tests; 110 Python modules.

**Not yet:** the book gallery and the other pages are still generated HTML. The
Python engine and the spline connector stay; A4 is the Node bridge.

**Network off** by the operator: no installs or fetches from here. `zod` is the
one runtime addition; `@astrojs/check` and Prettier were removed (incompatible
in this install, unrepairable offline). `npm run build` and `npm test` are the
app gate.

**Next:** A2, port the book gallery into Astro; then pages on touch.

## 2026-11-17 (fhandoff) — A2 did not land; the app and the gate are current

**Did the previous action land? No.** The previous next action was A2, the book
gallery into Astro. `app/src/pages/` holds only `index.astro` and the `api/`
route, and `book/index.html` is still the generated page. This block restates
A2; it does not invent a new action.

**Local:** 200 on `:8003` and on `:4321` (probed now). **Remote:** `000`, not
pushed, carried (last checked 2026-11-17; no deploy this session). **Tests:**
108 Python modules and 21 JS/app tests, carried from the run before the handoff
commit; the tree is clean, so nothing under `web/`, `curve_lab/`, `csrc/` or
`tests/` moved. **Register:** green (run now). **Git:** clean at `96aea81`.

**Changed since the last block.** The default gate now sends the two 42 s
sandbox page modules to `--full`: **69 s** here on a loaded 4-core machine, from
91 s; `--slim` is about 2 s. The Astro page has navigation, the gallery has a
deliberate empty state for stars, and the save payload is parsed with zod.
`@astrojs/check` and Prettier were removed (ESM/require error; missing native
binding) and are unrepairable with the network off; `npm run build` and
`npm test` are the app gate.

**Risks.** (1) The gate is still 69 s here with 59 Chrome/node processes; an
incremental runner is the real fix. (2) Astro 7 waits on Node >=22.23.4; this
machine is 22.4.1. (3) The old generated pages remain until ported. (4) The
Python engine and the spline connector stay; A4 is the Node bridge.

**Next move:** A2 — the book gallery into Astro.

Tried and rejected: `@astrojs/check` — `ERR_REQUIRE_ESM` from the language
server in this install; Prettier + `prettier-plugin-astro` — no native binding;
Astro 7 — Node 22.4.1 below its floor; further installs — the operator stopped
the network.

**After the handoff (2026-11-17):** the light browser now opens one local
saved-tabs page, `workbench/tabs.html`, listing only the focus tabs;
`scripts/chrome-curve.command --save` writes it, `--saved` opens it, and
`--default` opens the focus pair. `071ae33`; see LTMemory §Browsers and links.
The git line above (`96aea81`) predates this commit; the next `/fhandoff`
rewrites the block.

## 2026-11-17 (A2) — the book gallery is the Astro page at /book

**Did the action land? Yes.** `app/src/pages/book.astro` renders three sections
in the operator's order: the plates starred in the lab (`workbench/starred.json`),
the cross and leaf (`book/plates.json`), then the 27 singles. `app/src/lib/gallery.js`
reads both files on every request, so a saved star appears without a rebuild; the
caption for each card comes from `workbench/plate_compose.js`, the compose call
the exporter now shares instead of owning. PNGs are served by
`app/src/pages/api/plate/[id].js` from `book/plates/` (id checked against the
plate-name pattern, path checked against the plate directory), so 5.8 MB is not
copied into the app. `book/index.html` is deleted and `scripts/plates_export.mjs`
no longer writes it; it still writes SVG, PNG and `render.html`.

**Proof.** Built server on :4399: `/book` 200, 29 `<img>` (2 designs + 27
singles), captions identical to the retired page ("cross · 3×3 frame ·
new-symmetric · character rails · curve half-turn"); `/api/plate/cross-frame-1-t-exp-c-0201`
200 `image/png` 463,827 bytes; a traversal id gets 400. With a temporary
`starred.json` (`u-bowl-arch-1-t-exp-c-0301`) the star appears under Framed
Quintic symmetric figures, ledger reads "1 starred", and its card says the PNG is
not exported yet — then the temporary file was removed. `npm test` 11 pass,
`npm run build` green, `scripts/test.py` 108 modules + 28 JS tests green.
7 new app tests in `app/tests/gallery.test.mjs`; the plates test now fails if
`book/index.html` returns.

**Tried and rejected.** Requiring `../workbench/plate_compose.js` by relative
path — the Astro build moves `gallery.js` into `dist/server/chunks/`, so the
require resolved there and every page was a 500. Fixed by requiring the absolute
path under the resolved repo root.

**One file left alone.** A fresh export rewrote `book/plates/involute-fit-1-t-exp-c-0116.png`
(127,615 → 128,140 bytes, same 3000×2447). The composer is identical before and
after this action, so this is the current Chrome rasterising that thin spine-only
plate differently from the 13:23 export; the PNG was restored to keep the commit
scoped. Worth re-exporting deliberately, not as a side effect.

**Git:** `7fd71ad`, local only — no push (the operator has not asked).

**Next move:** A3, port pages on touch: each moved workbench page is deleted from
its generator in the same commit, and the shared maths stays one file.

## 2026-11-17 (hub) — `/` is the hub; the lab moved to `/lab`

**Landed.** `app/src/pages/index.astro` is a scrollable hub of **100 live
cards**: the lab and book gallery first, then the 86 manifest pages under the
manifest's own four intents (curve 64, terminal 2, strand 6, sheet 12), then 12
workbench pages the manifest does not name (PH sandboxes, cone-terminal,
flowers, curve-figures and the rest). `app/src/lib/pages.js` builds that list
from `workbench/manifest.json` plus the folder; `app/src/pages/pages/[...file].js`
serves `workbench/<file>` with a path check, so a preview is always the current
generated page. The shell is the admin-dashboard layout (sticky sidebar, top
bar, card grid) in curve-lab's cream, gold and Georgia; the Flowbite Astro
admin dashboard (MIT) is credited in `app/README.md` for the layout only — no
Tailwind or template code is used. The lab moved to `/lab`; `/book`'s lab link
follows.

**Proof.** Built server: `/`, `/lab`, `/book` 200; 100 `<iframe>`; sidebar
anchors `#app #curve #terminal #strand #sheet #unlisted`;
`/pages/ph-nth-sandbox.html` 200, `/pages/ph_math.js` 200 `text/javascript`;
`/pages/../astro.config.mjs` 404. Rendered at 1400 px: cards, captions and the
lab/book frames (the lab's 3.52 × 2.54 in readout and the book's two designs)
draw correctly. 4 hub tests (every manifest page shown once, every disk HTML
listed, app pages lead, page wiring); 15 app tests, 108 Python modules and 32 JS
tests green. `e9effbe`.

**Four senior fixes after the first render.** The book's empty state pointed at
`/` (now the hub) instead of `/lab`; `galleryRoot` was doing two jobs and is now
`repoRoot`; `buildHub` computed a `counts` object nobody read; the template had
no credit line.

**Known cost.** 100 iframes make a 26,438 px page. `loading="lazy"` holds the
offscreen ones back, but scrolling far loads many pages with their own JS. On
this 8 GB machine that is the Chrome pressure the project already knows; if it
bites, the fix is a "load previews" switch per section, not fewer pages in the
list.

**Next:** how the phone sees the site — LAN (`npm run dev -- --host`, then
`http://172.17.5.202:4321`), or a Cloudflare quick tunnel with
`vite.server.allowedHosts`. Hosting (Netlify/Pages) waits on the public task,
because `/pages/**`, `/api/plate/**` and `/book` all read the repo from disk.

## 2026-11-17 (tunnel, services) — the phone gets in without a terminal

**Landed.** `cloudflared 2026.11.1` at `~/bin/cloudflared` (prebuilt; Homebrew
was compiling Go and was stopped). `app/src/content/docs/docs/tunnel.md` + generated twin: quick
tunnel, named tunnel with the no-zone dead end written down, get in/get out,
symptom table. `scripts/tunnel.sh` for the named tunnel; `scripts/service.sh`
for what is running now: two LaunchAgents (`com.curvelab.app`,
`com.curvelab.tunnel`) that start at login and restart on death, so neither
process belongs to a terminal or an agent session.

**Proof.** Killed the app's pid: `launchd` gave a new pid, port back in ~14 s,
`/` 200. Restarted the tunnel: new quick address
`https://retention-staying-fence-empire.trycloudflare.com`, 200 from here.
`scripts/service.sh status` prints both states, the local code and the phone's.

**Found on the way.** Probing a quick URL the instant it is printed caches an
NXDOMAIN on this Mac, so `curl` says "Could not resolve host" while the tunnel
answers 200 when pinned to its IP. `status` now distinguishes the two, and the
run book says `sudo killall -HUP mDNSResponder`.

**Residual, stated plainly.** Not hosting: sleep, shutdown or logout ends the
URL, and a quick tunnel takes a new name each restart (`scripts/service.sh
url`). A named tunnel ends the second problem once a domain is on the Cloudflare
account; the account has no zone, so `cloudflared tunnel login` cannot complete.

**Git:** `1edec6c`, local only.

## 2026-11-17 (S4) — 179 stored curves, 0 gaps

**Landed.** `scripts/curve_audit.py` prints one row per curve in
`workbench/operator-list.json` (179) with five fields: grid, crossing-pair count,
picture, note, page. Grid, picture and page were already complete. The crossing
count was missing on 59 records and is now recomputed by the router
(`stable_crossings`); `--write` fills it into the record that owns it
(`found-curves.json`, `moved-curves.json`, or `curves/<name>/curve.json`), never
into the generated list. Notes come from the record, the folder's `notes.md`, or
a derived line from the roots it was built from, marked `(derived)`.
`tests/test_curve_audit.py` fails when the count is not 179/0.

**One bug found while reading the output, not the data:** a crossing count of
**0** was being reported as a gap; `wave-1of4-2` really has no crossings. The
check now treats only `None`/`""` as missing.

**Public prep, same session.** All 16 tracked reference images now carry a
licence record (the three fleur PNGs point at the SVG they were rendered from),
`tests/test_reference_licences.py` guards it, and the history scan found no secret
value — three key-shaped hits, all the secret's name in deploy docs.

## 2026-11-17 (curve finder) — the family, the loops, and what solving buys

**The stored finds are PH curves with a recovered generator.** `lace-1of8-3`'s
`v` row is exactly `(t−1/8)(t−7/8)(t−1/2)³ × 512` and `u = 1 − 2t + 2t²`; the
odd/even sign alternation the operator remembered comes from multiplying those
roots out. So the lace family is one mirrored pair plus a middle count, and the
pair position is the single interesting number.

**Properness is not "no loops".** A loop is a finite failure of injectivity, so
a self-intersecting curve is still proper; `curve_lab/reduction.py` catches only
covers. Crossings need `z(t)=z(s)` solved, not a segment scan (the first scan
reported fifty crossings on a straight line by counting collinear pairs).

**The parametric family `x = Q − P, y = Q + P` (P odd, Q even)** is the useful
design space: mirror about `y = x` is free; `Q = 0` gives exactly the line
`y = −x`, so the even coefficients are the shape and the odd ones redistribute
the parameter; the curve meets the axis where `P = 0`, and its tangent is 45°
where `P' = 0`. Crossings are **solved**: `Q(t₁)=Q(t₂)`, `P(t₁)=P(t₂)` are two
linear equations. Eight solved crossings are on `/finder`, ranked cusp-free by
branch angle (best 61°, family limits); `cross+45deg at t=1/4` also forces the
tangent at one branch to be parallel to the axis.

**Weighted derivative balance** (`Σ w_k z⁽ᵏ⁾(t₀) = 0`) is linear and splits into
P and Q. As an identity it forces a constant curve (since `(I−D)T = z'`); at a
point it is a usable condition. Weight profile decides how motion is spent:
`2⁻ᵏ` and `1/k²` give speed ratios up to 120, while `1/(2ᵏk!)` flattens it to
about 6. One condition per degree over-determines and zeroes coefficients; the
**minimum-norm** solution keeps every degree alive.

**Instruments:** `curve_lab/features.py` (flats, inflections, symmetry, bend),
`curve_lab/nodes.py` (resultant crossing solver, unproven), `curve_lab/reduction.py`
(covers). `/finder` stars to `workbench/finder-stars.json` with a backup.
Known gap: curvature peaks report cusps (κ 440–747) without saying so.

## 2026-11-18 (Tschirnhausen) — the old work was exact; the elevation is parked

`tph_tri_chain/RESULTS.md` already answered the rational question: with
`x = t²`, `y = t − t³/3`, integer hits are exactly the multiples of 3 and other
rational stops are exact at a stated pitch. The node is at `t = ±√3` and stays
irrational. Not an approximation — a different (and larger) result than a
rational node would have been.

`scripts/tschirnhausen.py` adds the degree-elevation experiment: the cubic
elevates to degree 7 identically (verified), and a solved handle move puts a
crossing at `t = ±1` (±0.007) and `t = ±½` (±0.123). The drawn results are
slivers, because one handle cannot bend an elevated septic near its ends; that is
recorded in `TODO.md` as parked, with the PH cost stated on the cards.

## 2026-11-18 (connectable curves) — mobile arcs and ends-first, both exact

`scripts/mobile_arcs.py` cuts the mobile between two rational parameters: the
endpoints and end tangents are exact fractions printed on each card, and
`arc −1 to 1` turns exactly −90.0° across the arc. `scripts/ends_first.py` builds
a degree-7 curve from position, tangent and second derivative at both ends
(twelve conditions, two free coefficients per coordinate), then spends the free
coefficients on a crossing at t = 1/4 and 3/4 — verified exact on all three cases.

Grid check under the operator's rule (ratios from 2, 3, 4, 5): a mobile on those
keeps grids of 5, 10, 15 and 50. `5-12-13` and `8-15-17` tilts introduce 13 and
17 and the grids jump to 4250 and 13260 — exact, but no longer simple, so the
default tilts are 3-4-5 only.

Known weakness, in TODO: the ends-first cards are shallow because the end
curvatures given are ±1; that input is the lever, not the solve.

## 2026-11-18 (finder page) — ids, starred first, best picked

Every curve now carries a stable `id` (`family-<sha1(definition)[:8]>`), assigned
by `finder_store.save_family`, so a star survives regeneration. The page renders
three blocks: **Starred** (by id, at the top), **Best so far** (13 curves marked
`featured`, one or two per new method), then the rest by family. Stars are stored
by id with name, family and definition; the save carries a base hash and is
refused with 409 if the file moved. 61 curves, build and 23 app tests green.

## 2026-11-18 (symmetry) — 45° and x-axis answered, labelled, featured

Every stored curve (318: finder families, the 60 finds, the 109 moved, the 88 in
the lab) was tested against 14 rational mirror axes and the half turn.
`scripts/symmetry_audit.py` does it with numpy in 14 s.

**45° (y = x): 30 curves.** The whole `Q/P` family and its loops — exact by
construction, `x(−t) = y(t)`.
**x axis: 13 curves.** The limaçons, the mobiles, the rational roses and the
Tschirnhausen base.
Vertical 167, half turn 83, y = −x 4. Oblique: **one** hit, `3-4-5, crossed` at
slope 1/2 (gap 0.0044) — an ellipse about its own tilted major axis, not an
ornament axis. No 3/4 mirror exists, as the operator suspected.

`finder_store.mark_symmetry` writes the measured gap onto each card as a flag
("mirror y=x (gap 0.0000)"), so a regeneration keeps it. The page's featured set
is balanced: four for y = x, six for the x axis, four chainable pieces.

The sandbox page (`phNthSymmetry`) tests **only** the vertical axis; that is why
these cases were open there.

## 2026-11-18 (close) — records, rotations, and the tree is clean

**Landed since the last block.** Every finder curve carries a `record`: kind,
formula, variables, grid and a sandbox verdict (`scripts/curve_record_view.py`).
Tschirnhausen is off the board. The sandbox's finder section carries only the 5
starred curves. A new section on the sandbox page, *Rational rotation: a mirror
you can turn*, shows the vertical mirror and the same curve turned by
`q = 1/2, 1/3, 1/4, 1/5` — axes `−3/4, −4/3, −15/8, −12/5` — with the 45° attempt
drawn from floats and labelled not exact. One loadable PH curve with whole rows
(`u = 2 − t − 2t²`, `v = 1 + 2t − t²`, mirror slope −3/4 at gap 0.000000) sits at
the top of a new **Symmetric** section on the finder.

**Why 45° is impossible on the grid.** Rotating a PH curve multiplies its *speed*
by `e^{iθ/2}`; the rows stay rational only when `tan(θ/2)` is rational. p-triple
angles pass (`3-4-5`: `tan = 1/2`, rows whole after `√5`); 45° fails
(`tan 22.5° = √2 − 1`). Recorded in `state/DESIGN-int.md`.

**Measured state.** Local `:4321` 200. Register green. App tests 23/23 (carried
from this session's runs). Python suite 114 modules (carried, code dirs
unchanged). Recheck 65/65 (carried from the run after `hub.py` restored the
missing bar). Remote: repo private, anonymous fetch 404 (carried 2026-11-18).
Git clean at `ce9875b` before this block's commit.

**Risks.** (1) The rose `k=4` card stores only half a turn (t ∈ [−1,1]), so the
page cannot show the diagonal symmetry the algebra proves; closed curves need a
full-turn sampling. (2) The finder's symmetry test now scales tolerance with
sampling density, which fixes closed curves but makes the flag threshold
curve-dependent — worth stating on the page. (3) No finder curve loads in the
sandbox except the new PH one; the kind counts are 29 position, 25 rational, 1 PH.

**Next move:** Sprint 1 of `state/SPRINT-int.md` — the grid bill for all 56
curves.

Tried and rejected: the ends-first generator as a shape source — six end
conditions leave the top powers free, the crossing correction then plunges the
curve far outside its chord (x −20 on a 2-unit span) and it draws as a sliver; a
better basis (Bernstein with local handles) is needed, recorded in TODO.
Rotating a PH curve by 45° — needs `√2`, so no rational rows exist.
Tschirnhausen — classic but adds nothing; off the board.

## 2026-11-19 — the data layer, Astro 7, and the naming desk

- **Node 24.22.3** from the official tarball at `~/node24` (Homebrew cannot build
  it on macOS 12); it is on PATH. **Astro 7.4.13**, Starlight 0.43.1, adapter 11.
  The app's fast tests are 13 in about 2 s; the rendering tests are `test:full`.
- **SQLite through Prisma is the record**: names, importance, rotation, pieces,
  border uid, stars, plate stars, users and sandbox saves are rows. The database
  is gitignored; `workbench/curve-registry.json` is the seed. The migration
  proved 262 curves, 262 notes, 262 sets.
- **Backups**: `.backup` snapshots on dev start, before a build and before a
  migration, integrity-checked, the last 20 in `state/backups/db`; `npm run
  backup` and `npm run restore`; WAL on.
- **GitHub is the off-site copy** for the exports: `scripts/sync-data.sh` runs
  every five minutes from a LaunchAgent.
- **Pages**: `/illuminations` 241 figures (50 found, the picked finder curves,
  3 roses, all of B); `/figures` 262 bordered PNGs with the border margin;
  `/names` the 212 chosen curves; `/finder-candidates` the 50 unstarred pool.
- **Next**: finish the naming, then the pictures. Sprint 1 (the grid bill) is
  parked behind them.
- **Open**: stars are keyed by name (aliases keep a rename safe; a uid foreign
  key is the proper model); there is no automated database test; the polyline
  frame maths is a second copy; 2 dependency alerts remain.

### Session close — 2026-11-19

- **Landed:** SQLite through Prisma as the record; automatic snapshots and a
  five-minute GitHub sync of the exports; Astro 7.4.13 on Node 24.22.3 with the
  fast app tests (13 in about 2 s); the handoff, `fhandon` and `focus` commands
  matched to the tree; the memory freshness test in the fast gate.
- **Next:** the 212 names on `/names`, then the pictures.
- **Tried and rejected:** `brew install node@24` — macOS 12 is Tier 3, no
  bottles, and it broke the existing `icu4c` link; the official tarball at
  `~/node24` is the working path.

## 2026-11-19 — the app shell, the finder's stars, the naming desk

- **One header on every page** (`app/src/components/AppNav.astro`,
  `app/public/vendor/app-shell.css`): brand, draft mark, "this page is the X",
  and a menu that does not link to the page you are on. Skip link to
  `main#main`; the theme's colours only. `app/scripts/check-pages.mjs` checks
  all 12 pages.
- **`/illuminations` stopped inlining 238 SVGs**: 82,689,119 bytes → 307,907
  bytes, 0.96 s → 0.069 s. Each figure is `/illuminations/fig-N.svg`, cached
  for a week with an ETag, loaded lazily; the build is memoised by data mtime.
- **The finder's star click was throwing** (`title is not defined`), so a star
  was never added and never saved. Fixed; un-starring now names its removal.
  Stars are one per curve (`app/src/lib/star-list.js`), and sections cannot
  overlap (`app/src/lib/finder-sections.js`) — the source of the 5 duplicate
  cards.
- **The naming desk** can save a name that is only its construction ("amper",
  "knot-6"); ten of the 212 rows could not be saved before. Drafts are stored
  only when the box differs from the saved name.
- **Measured:** 12 pages 200 with one header; `/finder` 56 cards, 0 duplicates;
  `/figures` 262 PNGs; `/illuminations` 238 figures; app tests 21/21; the
  register 14/14; `check-names` 212 rows, save survives a reload; `check-stars`
  round trip leaves the server at its 6 stars.
- **Data intact:** the three saved names from the check (`c-0091`
  `loop-t1of2-3of4`, `c-0094` `cross-small-knot`, `c-0101` `cross-2-loops-45`)
  are in the database with their 01:01 and 01:37 timestamps, and `/names`
  renders them at the top by importance.
- **Next:** the operator inspects the 12 pages; then the naming of the 212, then
  the pictures. Sprint 1 stays parked behind them.

### Session close (later, 2026-11-19) — the static gate, and names that stay visible

- **TypeScript and ESLint are the gate.** `npm --prefix app run check` runs
  `astro check` then `eslint`; both are clean (0 errors, 0 warnings; 33 implicit
  `any` hints). The first run found 42 errors, all in page scripts.
- **Page logic moved out of the pages**: `app/src/scripts/names-desk.js`,
  `finder-stars.js`, `illuminations.js` (lab already imported its own). A page
  script is now one import.
- **The saved name always wins over a browser draft.** `draftState` (tested) drops
  a draft older than the record; empty drafts are not drafts. `/names` prints
  "saved <time>" per row. Verified in a browser: a stale draft is discarded and
  `c-0094` shows `small-knot` with "saved 2026-11-19 01:01".
- **Measured:** `npm run check` clean; app tests 28/28; `check-pages` 12 pages;
  `check-names` 212 rows; `check-stars` 6 stars before and after; the register
  green (14 tests).
- **Next:** the operator names the 212; then the pictures; Sprint 1 stays parked.

## 2026-11-19 — the measured set, the rails, and two new variants in flight

- **Every curve is measured.** `CurveMetric` (one row per curve): grid, bend,
  arc, chord, inflections, closest, crossing pairs, meeting points, bbox, area,
  curvature median, three symmetry gaps, and `method` exact/sampled — 206 exact,
  56 sampled. `scripts/analyse_curves.py` computes, `load-analysis.mjs` writes
  through Prisma. `state/SIMILARITY-int.md` gives every curve's three nearest
  neighbours and the **77 empty cells** of (crossings x inflections): the search
  list for curves that do not exist yet.
- **The border is a band, everywhere.** The motif's amplitude is capped at 30%
  of its chord; the per-curve whack-a-mole is gone and `c-0037`/`c-0038` came
  right on their own. Stored per curve: `perSide`, `borderTurn`, `border_uid`.
- **Character offsets are data**: `offsets`, `widthPct`, `plus`, `minus`,
  `profile`; the rails are drawn and their band filled, in the centre and on the
  border. Every frame has an A plate and a `-B` twin; 180 PNGs.
- **The leaf is two curves** (curve + its mirror across the chord through the
  feet), filled pale: the first two-tone glyph. Weights were split (2.6 central,
  1.4 border) and the tone deepened on the operator's account of the halo.
- **Recovery parity and job ownership**: `scripts/recover.sh` (check/backup/
  restore, naming what a restore overwrites), `Session` and `Job` rows, and
  `scripts/jobs.mjs` refusing a claim that overlaps an active one.
- **The message bus** (`bus/`): HTTP + JSON over SQLite, durable, ordered,
  at-least-once, long-poll; first traffic sent and acknowledged.
- **The map**: `state/EXPLORATION-int.md` — the pendulum mobile, Gaussian
  transforms, tweaks as rows, rails everywhere, tails, the review, the empty
  cells. `state/DESIGN-TODO-int.md` ranks the 262 curves by open design task
  (164 want a corner *stop*, 67 suit a rotated corner, 64 show a seam crossing).
- **The essay**: "The logic of beauty" is in the README, on the hub, and in the
  philosophy page.
- **In flight**: variants **C** (corner rule) and **D** (C + tangent seam +
  50%/9% proportion), each with a paragraph per A/B/C/D block; the print export
  (`scripts/book_export.mjs`) exists and is paused until the plates are judged.

### The hour's sandboxes — 2026-11-19

- **`/sandbox`**: the visual adder — every term of a polynomial drawn alone,
  three across with a plus, the sum large at the same scale; five families,
  including `x − x³ + x⁵ − x⁷`. And **`z = b i`**: even terms give x, odd give y,
  signs rotate; the odd-only case is shown as the degenerate vertical line it is.
  Data from `scripts/sandbox_curves.py`, a registered format; the page is in the
  nav and in the page check (13 pages).
- **`scripts/where-is-my-phone.sh`**: Shortcuts first, a message second, Find My
  third; the number lives in `~/.config/curve-lab/phone`, never in the repo. The
  operator reports Messages is not working on this Mac, so the Shortcut is the
  real route when it exists.
- **Measured on the imaginary idea**: odd-only is a point in x; one even term
  opens it (grid 90090, 0 inflections, bend 1.009 — almost straight). The
  substitution makes wings and tails, not knots.

### Focus realigned — let the prime mover drive new families (2026-11-19)

- **The standing direction is the prime mover** (`state/PRIME-MOVER-int.md`): a
  pair `PMx, PMy` travelling the unit circle over `PM ∈ [−2π, 2π]`, walked by
  p-triples from `(25, 0)` to `(24, ±7)`, the two directions distinct sets. A
  fixed triple never closes at 2π (Niven); the three routes are written down.
- **Seven new curves entered the collection, starred:** six looped integer
  Béziers (`bezier-loop-1..6`, whole controls, 2–3 crossings each) and one
  mobile `k = 8/3` at equal radii. Registry 269 curves, 269 sets, notes equal;
  `check-db` green; figures rendered.
- **What was tried and did not pay:** coupler curves (5 of 900 looped, none more
  than twice), parity symmetry over `t ∈ [−1,1]` (symmetry, almost no crossings),
  the two-pair root sweep (flat ghosts — crossings in a microscopic fold), the
  Chebyshev Lissajous family (known, parked by the operator).
- **The one change of hands:** DeepSeek2 owns git from now; DeepSeek1 decides,
  reviews and writes the handoff.

### The circle taken out — the prime mover's method (2026-11-19, late)

- **The typo hunt is over; the page is green.** Defaults are the thin triple `(56, 783, 785)`
  with quadrants I and IV ticked (a check fails if either slips); Fig. 1–4 headings carry the
  triple, the mode and the station count; figures are numbered in page order 1–8; Fig. 9
  follows them.
- **The method is settled and written down** (`state/DESIGN-int.md`): a circular part is a
  constant on the walk, so it is invisible; removing a radial part cannot reshape a
  parametric curve (it only re-stations it by `t = Y/(1+X)`); a linkage rosette is exact only
  when its closure discriminant is a rational square, and the parallelogram family is the one
  that qualifies (60 sets, 20 directions).
- **Built and proven:** `scripts/circle_split.py` (four implementations, all identities exact
  in `Fraction`), `scripts/circle_plots.py` + `app/src/lib/plot-figure.js` (Fig. 9: seven
  panels, axes, grid, 15 px legends, cubic Bézier chains), `scripts/linkage_exact.py`
  (closure rule + search), tests for all three.
- **The database:** `c-0270 lens-56-783-785`, `c-0271 four-fold-56-783-785`, and the three
  named lace curves renamed to `lace-2-eight-3`, `lace-balloon-3`, `lace-arch-x-1` (aliases
  kept). Registry 271, sets 271, notes 271; `check-db` green; figures rendered.
- **Faults fixed with guards:** the figure index was overwritten by a partial run (regression
  37, merge + index test); the closure test divided by an irrational distance and reported
  every linkage as impossible (regression 38, rational line-and-circle test).
- **Spec is a checklist now:** 73 items, 64 ticked, 9 open, rendered as checkboxes at
  `/spec/prime-mover.html`; the generated pages carry a source hash and `tests/test_spec_pages.py`
  fails when one is stale.
- **Tried and rejected:** a foundry over odd polynomial maps (`scripts/curve_foundry.py`) —
  the top-scoring curves were flat lenses with no crossings, no better than the astroid
  already stored; the lace sweep to new `p` values (1/7, 1/9, 1/14…) — flat folds, not new
  character; splitting the parametric circle at the constant term `P(0)` — every lace curve
  starts at the origin, so `P(0) = 0` and the split is empty. The mean split replaced it.

### The reform entered as a record — 2026-11-19

- **`c-0272 lace-2-eight-3-circle-parameter`** is in the registry and the database
  (272 curves, 272 sets, 272 notes; `node app/scripts/check-db.mjs` green), `kind: path`,
  `base_uid: c-0028`, not starred.
- **It is the re-stationing, not `z·(P − C)/P`.** `P = x² + y²` is zero where the lace
  curve passes the origin, so the rule as written in §12 has poles there and cannot be a
  record. The stored curve is the same outline sampled at `t = Y/(1+X)`: 61 stations at
  `t = k/60`, each with its own exact rational circle point, and
  `C = 72796373224/42945377475 ≈ 1.6951` in the note. The decision is in `DESIGN-int`.
- **The proofs:** figure `app/public/figures/c-0272.png` (600 px, index merged, 272
  entries); row in `workbench/circle-split.json` under `reformed`; guard
  `tests/test_circle_split.py::test_way_4_the_reformed_curve_is_saved_as_its_own_record`
  fails without the row, the note's parameter or C, the figure, or an exact station.
- **Spec §15 box ticked** and `/spec/prime-mover.html` regenerated; the count line now
  reads 72 ticked, 10 open, recounted from the file (the old 64/9 had gone stale).
- **The tree carried another session's uncommitted work** (79 paths, including
  `tests/test_regressions.py` and the sandbox pages). This action staged only its own
  paths and did not touch those.

### Fig. 10, and the table the operator asked for — 2026-11-20

- **The stations now come from the driver's own table**, not a re-invented walk:
  `scripts/pm_reform_probe.py` writes `workbench/pm-reform.json` with `k`, `a`, `b` and the exact
  `X`, `Y`, both directions, the same rule as `driverRows()`.
- **`/prime-mover/` Fig. 10** draws the lens map on that table, then the same 21 stations through
  `z·(P − C)/P`: `C = 5004584177013258352947126468503097895474231/6071532165918824830441735684871673583984375`
  ≈ 0.82427. The reformation turns the plain lens into a four-petalled figure with a pinch at the
  origin.
- **Spec supersession:** §12's "cannot change the shape" holds for the re-stationing, not for the
  mean-`C` reform — `C` is the mean of `P`, so the reform always passes through the origin and
  the outline does change. Written in §12 and §15 in the same commit.
- **The guard:** `app/scripts/check-prime-mover-page.mjs` now checks Fig. 10 has two panels, both
  axes and a 15 px legend; Fig. 9's count stays at seven and Fig. 5's at six.
- **Not yet done:** the record for a *new* curve from this figure (A, then B/C/D). The figure is a
  probe on the page, not a stored curve.

### The hybrid desk — 2026-11-20

- **`/hybrids/`** is up: 343 cards, one per candidate of `x = C(t)^p, y = S(t)^q` with the
  middle-term polynomial of `(x+y)^n` used in 2D — colour (a tint) or radius (a scale).
  Each card has keep / later / reject; each decision is a `SandboxCurve` row, so a save
  cannot touch another card.
- **The figures are files**, not one page: `app/public/hybrid-figures/<id>.svg`, written by
  `scripts/hybrid_figures.py`; the list is `workbench/hybrids.json`.
- **Stations are one pass of the rational circle** (`t = u/(1−|u|)`, `u = i/100`): exact
  fractions, no sin, no cos. Crossings come from the router in the generator.
- **Contact sheets** for reading the whole family at once: `workbench/hybrid-sheets.html`
  (colour sheet + six radius sheets).
- **Guard:** `app/scripts/check-hybrids-page.mjs` — 343 cards, sampled figures load, two
  keeps survive a reload, no page errors. `/hybrids/` is in `check-pages` (17 pages).
- **Not done:** a kept candidate does not yet become a registry record; that is a separate
  step, and the operator decides which.

### Promotion, and the visible copy — 2026-11-20

- **`app/scripts/export-sandbox.mjs`** writes `workbench/sandbox-curves.json`: every
  `SandboxCurve` row, with a header naming each field. This is the visible copy the
  operator asked for; the sidechat adds the rest of the `data/` files.
- **`scripts/promote_hybrids.py`** turns each kept candidate into a registry record:
  uid, name `hybrid-<p>-<q>-<block>-<use>`, `params`, `formula`, exact `grid`, measures in
  the note, path. Proven end to end on `h-colour-5-3` (c-0273, check-db green, figure
  rendered), then removed, because the operator has not chosen yet.
- **`tests/test_hybrids.py`** guards the three drifts: a candidate without a formula, a
  figure missing from disk, a keep with no registry record.
- **The grid of a promoted hybrid is large** (561 digits for 199 stations); it is stored
  exactly in `grid` and its station rule is in `params`, because the lcm is the honest
  number and a rounded one would be a lie.
