# curve-lab — agent notes

Instructions accumulate. The operator's latest message is authoritative, and a
new emphasis adds to the work rather than replacing what came before. Read what
the work needs, not only what the handoff names.

## Plain English, always

Write in plain English: short sentences, everyday words, one idea per sentence.
Jargon is allowed only when it is the name of something real in the project
(`pitch`, `Pythagorean`, `PH`) and then it is defined in the same breath.

- Say what a number measures and in what unit: "grid 1/27720", "bend 2.259
  (arc over chord)", not "pitch 27720".
- No filler verbs: use "use", "show", "make", "fix" instead of "utilise",
  "leverage", "facilitate".
- No sales words: "robust", "seamless", "powerful", "nice" — say what it does.
- If a sentence needs a diagram to parse, rewrite it. If a term has two
  meanings in the project, name both.
- The operator may not be a mathematician: explain the result in words first,
  the formula second.

## Achievements are logged, not remembered

Hours go into fixing a fault, and a fault fixed twice is a process failure. So:

- **`state/REGRESSIONS-int.md` is the register** of every fault that cost real
  work, with the test that guards it. It is Tier 0: read it before changing a
  control, not after breaking one.
- **A fix and its register row land in the same commit.** A fix without a test is
  not finished. The test goes in `tests/test_regressions.py`, named after the
  fault, with the operator's own words in the docstring.
- **Nothing is deleted from the register** because a change made it awkward. If a
  test fails and the new behaviour is right, amend the row in that same commit
  and write why.
- **Run it at every boundary:** `.venv/bin/python -m unittest tests.test_regressions`
  (a tenth of a second). `/fhandon` runs it before the action, `/fhandoff`
  before writing the block.
- **Settled decisions go in `state/DESIGN-int.md`**, with the reason, so the same
  argument is not had twice. Published numbers go in `state/ACHIEVEMENTS-int.md`
  via `scripts/recheck.py`.

## Start cheap

0. **`state/READING-int.md`** — the authoritative reading list (its line counts are refreshed by `scripts/reading_counts.py`, which `/fhandoff` runs): what to load, in
   what order, at what cost, and what never to load. Follow it; do not invent a
   reading order. If an action needs a file that is not on it, add the row.

   Read **`senior-dev.md`** (twelve rules, one page) before the action, on every
   focus command. It is the working standard, not a process.

Tier 0 of that list, in short: `LTMemory-int.md` (map, invariants, settled),
`next-fhandoff-int.md` (the one action), `state/HANDOFF-int.md` (**tail only** —
current truth), `TODO.md` (checklist), `goals.md` (the arc),
`state/ACHIEVEMENTS-int.md` (what is proved, and `scripts/recheck.py`).

Tier 1 — **the scope anchor**, read when direction or a grade is in question:
`SPEC.md`, `docs/PROJECT.md`, `goals.md`, `docs/PHILOSOPHY.md`. Scope in one
line, so it is never absent: exact integer and rational curves on one grid; the
deliverable is a grammar of plant-forms that becomes the ornament grammar, not a
gallery of drawings.

Then, per action only: `state/BACKLOG-int.md` (the W-label detail, and nothing
else), `workbench/ornament-board.html` (visual order and labels; generated — do
not edit by hand).

Do **not** read `docs/HANDOVER.md` unless the action needs durable
architecture/deploy/security detail. It is deliberately long. Do not read
`vendor/`, `out/caps/*.svg`, or the `ornaments` repository unless the action is
extraction or comparison. Generated pages may be read: reading the built page
is how a claim about the page is checked.

## Focus (2026-10-26)

The DeepSeek order: **W01 piece model** → **W02 terminals** → **W03 fleur
grammar** → **W04 twenty parameter sets**, then the primal studies (fire,
water, earth, air — see `docs/PRIMAL.md`), then the archetypal ornaments. The
plant-form → ornament-form arc is in `goals.md`; the focused next action is
still the offset catalogue. Auth and render limits are live; accounts/roles are
later. Keep the public URL private.

## Degree: cubic first — quintic only when the curve needs it

A curve goes to Inkscape or a glyph editor as **four-point cubic spans**. Try a
cubic chain first. A quintic (six-point) span is allowed only when no cubic chain
can meet the G3 gate and the deviation tolerance. The **lead** carries only the
few curves that need it — about **five to ten**, and each one says why the cubic
attempt failed. The same showcase page also carries the **full gallery** below, so
one page gives the overall view. Quintic spans may appear in the side construction
panels as the working view. The full fallback index may also exist on
`workbench/g3-handover.html`.

## Naming — descriptive, unique, one meaning per name

A reader should never have to ask which `c`. The rule applies to code, page text
and documentation alike.

- **JavaScript/TypeScript:** `camelCase`. Nouns for values (`bendRatio`,
  `lineIntercept`, `speedYLinear`), verbs for functions (`buildRecipePanel`,
  `drawCurve`). Single letters only as loop indices (`i`, `j`, `k`).
- **DOM ids and CSS classes:** `kebab-case`, prefixed by the figure
  (`q9-plot`, `q9-controls`, `q9-readout`). A number/slider pair is `<id>` and
  `<id>-slider`.
- **Python:** `snake_case`, already the house style.
- **Math symbols stay on the page** (`λ`, `u₀`, `k`, `c`), but every one gets a
  descriptive code name, and the page says both when they could be confused —
  Q9's `c` is `lineIntercept`, Q7's is the constant term of `v`.

## Files that matter

| Path | Purpose |
|---|---|
| `web/server.py` | stdlib server, auth, rate limit, `/api/render` |
| `curve_lab/model.py` | `Design` and `Segment` |
| `curve_lab/measure.py` | **the one exact core**: grid, bend, arc, inflections, closest in `Fraction` |
| `scripts/build-pages.py` | rebuilds the eight pages that load the shared JS, then the hub |
| `scripts/exact_numbers.py` | audits every record's grid and bend against `curve_lab/measure.py` |
| `scripts/crossing_audit.py` | audits every record's crossing-pair count |
| `scripts/operator_list.py` | writes `workbench/operator-list.json` from the stored records |
| `scripts/check-saved.mjs` | the saved-curve buttons: seed, repair, undo, load (headless) |
| `scripts/check-rails.mjs` | rails draws and the complementary controls exist (headless) |
| `workbench/ph_math.js`, `workbench/ph_nth_panels.js` | the shared page JS, written once by `build-pages.py`; pages load them |
| `curve_lab/piece.py` | `Piece`, `Trace`, multi-trace render (W01) |
| `curve_lab/clearance.py` | min-gap and crossing report; `piece_clearance()` |
| `curve_lab/fillet.py` | tangent-arc fillet at a corner (`corner_fillet`) |
| `curve_lab/junction.py` | `Junction`: branch + trunk + declared merge |
| `curve_lab/grammar.py` | fleur study 01 ported from the old grammar |
| `curve_lab/contact.py` | `Contact`: a declared legal touch |
| `curve_lab/section.py` | `Section`: one station across a full line |
| `curve_lab/bundle.py` | `Bundle`: the design box — full lines that must not touch |
| `curve_lab/primal.py` | earth, water, air, fire: one grammar each |
| `curve_lab/svg.py` | SVG writer; `document(..., groups=...)` |
| `curve_lab/presets.py` | bracket, ogee, petal, S-curve |
| `scripts/board/` | board generator + template + extractors (edit these, not `workbench/*.html`) |
| `tests/` | 305 tests; run the whole suite |
| `docs/REVIEW.md` | architecture/print review — act after the current work |
| `docs/PHILOSOPHY.md` | the design philosophy: glyph, full line, sections, joints |
| `goals.md` | the long arc: plant-forms → ornament-forms; offsets, endings, lattice growth marks, branches |
| `docs/PRIMAL.md` | primal ornaments (fire, water, earth, air) and their gate |
| `docs/G3-showcase-docs.md` | how the G3 showcase is built; the HTML twin is generated by `scripts/g3_showcase_doc.py` |
| `state/G3-FIXES-int.md` | the tracked figure fixes, the colour rule and their proofs |
| `reference/principles.json` | principle cards: gesture, 3 numbers, not-this |
| `reference/` | attributed reference images + manifest (measurement only) |
| `docs/CLEARANCE.md` | the clearance/crossing rule and its limits |
| `docs/JUNCTION.md` | junctions: vocabulary, fillet, what comes next |
| `workbench/spirals/` | recovered Stage II + LAC spines and their parity report |
| `workbench/` | the working pages, one generator each; these become the app's input pages |
| `pythagorean-spiral/` | the exact spine layer — central to the curve work, not a spike; not yet imported by the package |
| `state/DESIGN-int.md` | settled design decisions, with the reason; read before changing a control |
| `state/REGRESSIONS-int.md` | fixed faults, each with the test that keeps it fixed |
| `state/HANDOFF-int.md` | current truth |
| `state/DOT-SOLVER-int.md` | the dot-solver sub-focus and its image exception |
| `next-fhandoff-int.md` | one action |
| `state/PLAN-int.md` | the rolling queue of the next sessions; edited at every handoff |
| `senior-dev.md` | twelve working rules; read on every focus command |
| `state/parked-focus-int.md` | parked directions, newest first; `/fstart <direction>` pushes, `/fstart return` pops |

## Commands

Start the one server if it is not already up (this is idempotent — it says
"already serving" and exits):

```sh
.venv/bin/python scripts/serve.py            # http://127.0.0.1:8003
```

```sh
.venv/bin/python -m unittest discover tests
.venv/bin/python -m unittest tests.test_regressions   # the fixed-bug register, ~0.1 s
.venv/bin/python scripts/test.py --slim          # tight loop: engine only, ~3 s
.venv/bin/python scripts/test.py                 # commit gate, ~40 s
.venv/bin/python scripts/test.py --browser       # the gate plus the headless page checks
.venv/bin/python scripts/test.py --full          # before a push
.venv/bin/python scripts/build-pages.py          # rebuild every page that loads the shared JS
.venv/bin/python scripts/exact_numbers.py        # audit stored grid/bend; --write repairs
.venv/bin/python scripts/crossing_audit.py       # audit stored crossing counts; --write repairs
.venv/bin/python scripts/operator_list.py        # rebuild the button list from the records
node tph_tri_chain/audit_t1.mjs                  # Fig. T1: label audit, ~2 s
.venv/bin/mkdocs serve                          # the docs book, live on :8000
.venv/bin/mkdocs build                          # static output into site/
.venv/bin/python web/server.py                  # local, open on 127.0.0.1
node scripts/check-ph-page.mjs                  # gallery readouts in a headless browser
node scripts/board/build-board.mjs              # regenerate both board pages
.venv/bin/python scripts/g3_showcase_doc.py      # refresh the G3 showcase doc + HTML twin
.venv/bin/python scripts/g3_cubic_native.py      # the cubic-native side list
.venv/bin/python scripts/g3_gate.py              # strict / source / near-G3 tiers
.venv/bin/python scripts/ph_families.py           # PH family gallery, degree by degree
node scripts/check-web.mjs                      # when it exists: layout gate
```

Deploy is thin (~30 s):

```sh
gcloud run deploy clothoid-web --source . --region us-central1 \
  --allow-unauthenticated --memory 512Mi --cpu 1 --concurrency 2 \
  --min-instances 0 --max-instances 1 --timeout 60 --port 8080 \
  --set-env-vars HOST=0.0.0.0,CLOTHOID_RATE_PER_MIN=60,CLOTHOID_RATE_BURST=20 \
  --set-secrets CLOTHOID_TOKEN=clothoid-token:latest --quiet
```

## GitHub — run it like a normal developer

- **No internet unless the operator says so.** No fetch, no push, no `gh`, no remote
  probe. Work from the files on disk and say what you ran.
- **No CI unless the operator says so.** Do not run `gh run watch`, do not poll
  `gh run list`, do not wait for a workflow. Make the push, report it in one
  line, and leave the run alone.
- **Anything on GitHub that takes more than a minute needs approval first.**
  Say what it is and how long it takes, then wait for a yes.
- **Commit per action** when its `Proves:` line is satisfied and the suite is
  green. A finished action left uncommitted is the one thing a crash or a
  `git checkout` can destroy.
- **Push after every green block, not only at handoff.** The remote is the
  backup: a red or stale remote is worse than a local commit. If a push turns
  the `native` workflow red, fix or revert before starting the next task.
- **Push `main` at every handoff.** Do not end a session with green local
  commits GitHub has not seen. Before pushing: `scripts/test.py --full` and
  `scripts/recheck.py` must pass; then `git push origin main`; then
  `gh run list -L 1` and confirm the `native` workflow is green. Leave the
  remote green — fix or revert a red build immediately.
- **Never force-push `main`.** Stage the paths the action touched.
- **The remote is `Kellytom/curve-lab` (private).** The old `clothoid-lab`
  name redirects; do not use it in links or commands.
- **Auth is the `gh` keyring.** Never print, paste or commit a token.
- **A push is not a deploy.** Cloud Run deploys stay explicit and separate.

## Guardrails

- One task at a time, at the scope the operator set; verify, commit, stop.
- Never edit `docs/ornament-board.html` or `docs/fleur-studies.html` by hand.
  Change `scripts/board/build-board.mjs` or `board-template.html`, then rebuild.
- Never touch `out/play-template.svg`.
- Do not change `vendor/`; caps are baked into the app image.
- **No context budget is enforced here (2026-11-17).** The 2026-11-16 meter measured
  OpenCode while the actual pressure was Chrome holding memory, so it has been retired
  and every instruction that constrained context use is gone. The operator monitors and
  decides how long a session runs. The one rule that stays is about honesty, not memory:
  never report a narrowed result as complete — "complete" needs a diff or a test.
- **Catalogue pages are generated from the source tables**, never drawn from
  memory. Diff the page against `generators.NAMED` and `heart_forms.FORMS`
  before claiming completeness; `recheck` fails when one is missing.
- The auth token is at `~/.config/<app>/token` and in Secret Manager.
  Never print it, commit it, or put it in a URL.
- Auth is HTTP Basic on everything except `/health`; `/healthz` is intercepted
  by Google's frontend.
- Browser checks: headless Chrome on CDP port 9223, never the Review pane.
- **Images are allowed, under 150 KB and 1000 px per file.** The old "engine has no
  image input" rule was deprecated 2026-11-16: it applied to large files. A raster to be
  looked at goes in under both limits, checked with `file` or `sips -g pixelWidth
  -g pixelHeight` first, and downscaled with `sips -Z 900` when it is not. SVG is text and has no limit. Generated figures are
  made to fit: export under 150 KB and 1000 px on the long side. Verified
  2026-11-11: an 880 x 620, 93 KB PNG of Fig. T1 read back without error, so the
  limit is the real constraint, not the format.
- **Exception — the dot-solver subproject only** (`state/DOT-SOLVER-int.md`):
  images it generates may be sent back for diagnosis. The operator authorises
  it per session and runs `/fhandoff` then `/fhandon` first, so a freeze costs
  one step. Scope: only images the solver produced, only in this sub-focus.
  If the engine rejects one, say so at once and start a fresh session instead
  of retrying in place.

## Figures

- Label every figure **inside the figure**, not only in a caption: a figure
  number or letter (for example `Fig. 1`, `Fig. C1`, `Fig. G1`), a title naming
  the curve/case, x and y axis labels, units when they matter, a legend for the
  marks (source, handles, points, rails), and the key endpoint or coordinate
  values.
- A caption is an explanation, not a substitute for axis and series labels.
- Use the full width of the figure box. Size the canvas/SVG from the data or
  grid aspect instead of leaving large side margins; a narrow drawing in a wide
  box is a layout error.
- Label integer control points with their names and coordinates, and enlarge
  the figure until those labels are legible. An integer result is not visible
  if the reader cannot read the integers.
- Legend type must stay readable at full width: at least 15px (about 11pt), which is 2pt larger than the 12px floor. Do not shrink a legend to fit; move it or wrap it.
- This applies to generated workbench SVGs, docs figures, and board panels.
  If a figure deliberately suppresses axes, it still needs a title and a legend.
- Check the rendered figure at full width before committing; labels must not
  overlap the curve or each other.
- Exports stay under 150 KB and 1000 px on the long side, so they can be looked at.

## Reading discipline

- Probe once with a single shell call; grep before reading; do not re-read a
  file already in context.
- Prefer `git diff --stat` and targeted `sed` over whole-file reads.
- If a file is over ~200 lines, read the section the action names, not the file.
- Stop when the action is done; do not explore adjacent work.
