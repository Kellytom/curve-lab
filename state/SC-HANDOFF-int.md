# SC-HANDOFF-int — the sidechat's handoff (read this first after a reset)

*Refreshed 2026-11-23 at the operator's /shandoff, before a reset and a model
switch. Everything below is committed and pushed unless the line says
otherwise. Read this file first, then `state/SCToDo-int.md`.*

## 1. Where the work stands

1. **The Inkscape round trip — CLOSED, proven on Inkscape 1.4.4.** Files:
   `inkscape/ph_actions.py`, `ph_svg.py`, `ph_handles.py`, `ph_variant.py`,
   `ph_extension.py` + two `.inx`; doc `docs/INKSCAPE-ROUNDTRIP.md`; 27 tests
   incl. an Inkscape-serialized fixture (`tests/fixtures/`). Operator's laws:
   a translation is a view, not a curve; misses in curve units, never "the
   dial".
2. **The speed-space re-fit — works, census current.** Files
   `reduction/speed_fit.py`, `reduction/speed_fit_census.py`,
   `workbench/speed-fit-census.json`; 5 tests incl. own-degree recovery on a
   5e7-coefficient curve. Fit family reduces ~free; wave/loop/lace refuse.
3. **The sibling map + candidates — posted.** `scripts/sibling_map.py`,
   `workbench/sibling-map.json`, `scripts/sibling_candidates.py` (53 distinct
   new curves → sandbox). Finding: the ½ stack is load-bearing (best miss
   8.5 %) — `state/SC-SIBLING-FINDING-int.md`. `/candidates/` shows 59.
4. **Conversion rows — landed:** `contact.ts`, `fillet.ts`, `junction.ts`,
   `model.ts`, `svg.ts` (TEXT layer; `document()` stays Python). Row table in
   `state/PORT-int.md`. npm 100 pass.
5. **deep2/ — the figure pipeline.** `trace.py` (silhouette/lithograph/photo
   masks → potrace → spans), `canon.py`, `measure_spans.py`, `heart.py`.
   First conversion: the Redeemer, 35 spans, joins ≤7.7°, snap 1/1000 costs
   ≤0.0005. Prior art: `archive/notes/prior-art-human-figure.md`.
6. **The broken heart — construction done, samples approved pending.**
   Same seam in both halves; the balanced S-seam (A·sin 2πt) gives both
   pieces a matching lobe. `deep2/out/heart-S seam, lateral 0.18.svg` reads
   right. **NOT on an HTML page yet** (open ask 1).
7. **Attention sounds — done, operator said "good enough".** Sidechat tone:
   A2+A3+A4 mix, 1.6 s, volume 0.18, at
   `~/.config/opencode/sounds/ding-low.wav`, carried by the Side Chat
   launcher's `OPENCODE_CLI_CONFIG_CONTENT`; main session keeps the bright
   bell via global `cli.json`.
8. **The GLM AI-news task — written, ready to paste.**
   `deep2/notes/glm-ai-news-task.md` (plain-English rule included).
9. **Compaction setup — active.** `sidechat.json`: keep 24k, buffer 20 %,
   background false, summaries by deepseek-v4-pro. `/precompact` writes the
   in-flight note; `/shandoff` writes this file.

## 2. The operator's open asks, in order

1. **The heart attempts onto an existing HTML page, and consolidate our HTML
   pages.** Their words: "put the heart attempts into an existing html page.
   we need to consolidate our html pages." Open first: `app/src/pages/·`
   (`/candidates/` is ours; `/extra-curves/` is DeepSeek1's, generated from
   `app/src/data/extra-curves.json`). No new pages; consolidate existing.
2. **A human figure at the centre** (the Virgin, Christ, the two Hearts).
   Open first: `TODO.md` (their words, the canon route, prior art pointer);
   samples in `deep2/`.
3. **Run the GLM AI-news task** (file above) when the model is switched.
4. **Housekeeping:** `scripts/prepush.sh`; last known reds were DeepSeek1's
   (`side-tests.html` label, c-0398 slot, book manifest) — verify before
   pushing anything of ours.

## 3. Environment facts a fresh session must not rediscover

- Inkscape headless: `PYTHONPATH=/Applications/Inkscape.app/Contents/Resources/share/inkscape/extensions
  /Applications/Inkscape.app/Contents/Resources/bin/python3 ph_extension.py
  /tmp/blank.svg --mode=send|receive ...`. The `.inx` namespace must be
  `http://www.inkscape.org/namespace/inkscape/extension`.
- potrace is at `/usr/local/bin/potrace`; PIL/numpy/scipy are in `.venv`.
- ruff is installed and configured (`pyproject.toml`); `deep2/` is clean.
- DeepSeek1 edits state files live: the reading-counts cache races (refresh
  from a CLEAN EXTRACTION of HEAD before pushing); the mailbox heading
  format is `## YYYY-MM-DD HH:MM — subject` (a middle dot breaks the reader).
- Mailbox: never edit `archive/notes/deep-to-side.md`; append to
  `side-to-deep.md` after `---`.
- The dev server is DeepSeek1's (`localhost:4321`); `astro dev logs` has
  stderr. Never open pages for the operator; give links.

## 4. The one next action

**Put the broken-heart samples into `/candidates/`** as a "The broken heart"
section: copy `deep2/out/heart-straight.svg` and
`heart-S seam, lateral 0.18.svg` (renamed to slugs) into
`app/public/deep2/`, render them on the page with their labels and the
sample strengths, and link back to `deep2/heart.py`. Then run the gate and
push. Proves: the page shows the two drawings; `curl /candidates/` contains
the section; the gate is green apart from DeepSeek1's known reds.
