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

## Start cheap

0. **`state/READING-int.md`** — the authoritative reading list: what to load, in
   what order, at what cost, and what never to load. Follow it; do not invent a
   reading order. If an action needs a file that is not on it, add the row.

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
`vendor/`, `out/caps/*.svg`, the generated board HTML, or the `ornaments`
repository unless the action is extraction or comparison.

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
| `state/HANDOFF-int.md` | current truth |
| `state/DOT-SOLVER-int.md` | the dot-solver sub-focus and its image exception |
| `next-fhandoff-int.md` | one action |

## Commands

Start the one server if it is not already up (this is idempotent — it says
"already serving" and exits):

```sh
.venv/bin/python scripts/serve.py            # http://127.0.0.1:8003
```

```sh
.venv/bin/python -m unittest discover tests
.venv/bin/python scripts/test.py --slim          # tight loop: engine only, ~3 s
.venv/bin/python scripts/test.py                 # commit gate, ~40 s
.venv/bin/python scripts/test.py --full          # before a push
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
- **Measure context, don't feel it:** `python scripts/ctx.py` (1M window). Warn
  at 70%, stop at 85% — then /fhandoff. It also prints active minutes and turns,
  but they are reported, not judged: the store shows no error-rate rise with
  long sessions, so no time threshold is claimed. `--log` appends to
  `state/sessions.jsonl`; `--tally` shows the last record per session; `--watch
  N` beeps at 70% and 85%. Never narrow the task
  silently; "complete" needs a diff or a test.
- **Catalogue pages are generated from the source tables**, never drawn from
  memory. Diff the page against `generators.NAMED` and `heart_forms.FORMS`
  before claiming completeness; `recheck` fails when one is missing.
- The auth token is at `~/.config/<app>/token` and in Secret Manager.
  Never print it, commit it, or put it in a URL.
- Auth is HTTP Basic on everything except `/health`; `/healthz` is intercepted
  by Google's frontend.
- Browser checks: headless Chrome on CDP port 9223, never the Review pane.
- **Images, if any: 150 KB and 1000 px per file.** A raster to be looked at
  goes in under both limits, checked with `file` or `sips -g pixelWidth
  -g pixelHeight` first. SVG is text and has no limit. Generated figures are
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

## Context discipline

- **The window is 1,000,000 tokens.** `scripts/ctx.py` is configured correctly;
  do not retune `DEFAULT_WINDOW` from a recollection or a guess. 85% of one
  million is the stop point, and a session at 17% has room.
- Probe once with a single shell call; grep before reading; do not re-read a
  file already in context.
- Prefer `git diff --stat` and targeted `sed` over whole-file reads.
- If a file is over ~200 lines, read the section the action names, not the file.
- Stop when the action is done; do not explore adjacent work.
