# curve-lab — agent notes

Keep the context small. Read only what the current action names.

## Start cheap

0. `LTMemory-int.md` — the map, the invariants and what is already settled.
1. `next-fhandoff-int.md` — the one action.
2. `goals.md` — the long arc: plant-forms → ornament-forms.
3. `state/HANDOFF-int.md` — current truth. Stop there unless it points onward.
   `state/ACHIEVEMENTS-int.md` is the list of what is proved, with the command that
   re-derives each one (`scripts/recheck.py`).
4. `state/BACKLOG-int.md` — the W-label detail for the action, and nothing else.
5. `workbench/ornament-board.html` — visual order and labels (generated; do not
   edit by hand).

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
| `tests/` | 277 tests; run the whole suite |
| `docs/REVIEW.md` | architecture/print review — act after the current work |
| `docs/PHILOSOPHY.md` | the design philosophy: glyph, full line, sections, joints |
| `goals.md` | the long arc: plant-forms → ornament-forms; offsets, endings, lattice growth marks, branches |
| `docs/PRIMAL.md` | primal ornaments (fire, water, earth, air) and their gate |
| `reference/principles.json` | principle cards: gesture, 3 numbers, not-this |
| `reference/` | attributed reference images + manifest (measurement only) |
| `docs/CLEARANCE.md` | the clearance/crossing rule and its limits |
| `docs/JUNCTION.md` | junctions: vocabulary, fillet, what comes next |
| `workbench/spirals/` | recovered Stage II + LAC spines and their parity report |
| `workbench/` | the working pages, one generator each; these become the app's input pages |
| `pythagorean-spiral/` | the exact spine layer — central to the curve work, not a spike; not yet imported by the package |
| `state/HANDOFF-int.md` | current truth |
| `next-fhandoff-int.md` | one action |

## Commands

Start the one server if it is not already up (this is idempotent — it says
"already serving" and exits):

```sh
.venv/bin/python scripts/serve.py            # http://127.0.0.1:8003
```

```sh
.venv/bin/python -m unittest discover tests
.venv/bin/mkdocs serve                          # the docs book, live on :8000
.venv/bin/mkdocs build                          # static output into site/
.venv/bin/python web/server.py                  # local, open on 127.0.0.1
node scripts/board/build-board.mjs              # regenerate both board pages
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

## Guardrails

- One focused action at a time; verify, commit, stop.
- Never edit `docs/ornament-board.html` or `docs/fleur-studies.html` by hand.
  Change `scripts/board/build-board.mjs` or `board-template.html`, then rebuild.
- Never touch `out/play-template.svg`.
- Do not change `vendor/`; caps are baked into the app image.
- The auth token is at `~/.config/<app>/token` and in Secret Manager.
  Never print it, commit it, or put it in a URL.
- Auth is HTTP Basic on everything except `/health`; `/healthz` is intercepted
  by Google's frontend.
- Browser checks: headless Chrome on CDP port 9223, never the Review pane.

## Figures

- Label every figure **inside the figure**, not only in a caption: a figure
  number or letter (for example `Fig. 1`, `Fig. C1`, `Fig. G1`), a title naming
  the curve/case, x and y axis labels, units when they matter, a legend for the
  marks (source, handles, points, rails), and the key endpoint or coordinate
  values.
- A caption is an explanation, not a substitute for axis and series labels.
- This applies to generated workbench SVGs, docs figures, and board panels.
  If a figure deliberately suppresses axes, it still needs a title and a legend.
- Check the rendered figure at full width before committing; labels must not
  overlap the curve or each other.

## Context discipline

- Probe once with a single shell call; grep before reading; do not re-read a
  file already in context.
- Prefer `git diff --stat` and targeted `sed` over whole-file reads.
- If a file is over ~200 lines, read the section the action names, not the file.
- Stop when the action is done; do not explore adjacent work.
