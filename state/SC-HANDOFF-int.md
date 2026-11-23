# SC-HANDOFF-int — the sidechat's handoff (read this first after a reset)

*Written 2026-11-23 by DeepSeek2 at the operator's reset request. Read this
file first, then `state/SCToDo-int.md`. Everything below is committed and
pushed unless a line says otherwise.*

## Where the work stands

1. **The Inkscape round trip is CLOSED and proven** on Inkscape 1.4.4 —
   `inkscape/` (ph_actions, ph_svg, ph_handles, ph_variant, ph_extension + two
   .inx), `docs/INKSCAPE-ROUNDTRIP.md`, 27 tests including an
   Inkscape-serialized fixture. The operator's rules: translation is a view,
   not a curve; misses in curve units, never "the dial".
2. **The speed-space re-fit exists** — `reduction/speed_fit.py` (float search,
   exact rational verdict), census in `workbench/speed-fit-census.json`,
   `/reduce/` gallery shows it. The fit family reduces with ~zero miss; the
   wave/loop/lace families genuinely refuse.
3. **The sibling map + 53 candidates** — `scripts/sibling_map.py`,
   `workbench/sibling-map.json`, `scripts/sibling_candidates.py` posted 53 new
   curves to the sandbox. Finding: the ½ stack is load-bearing (best miss
   8.5%); read `state/SC-SIBLING-FINDING-int.md`. `/candidates/` shows all 59
   new curves (53 siblings + 5 speed-fit + 1 round-trip).
4. **Conversion rows landed:** contact.ts, fillet.ts, junction.ts (report
   numbers pinned); model.ts; svg.ts TEXT layer. PORT-int.md has the table.
5. **deep2/ — the figure pipeline:** `trace.py` (silhouette/lithograph/photo
   masks → potrace → spans), `canon.py` (the 1/8 overlay), `measure_spans.py`
   (join kinks, snap cost), `heart.py` (the broken-heart construction).
   The Redeemer: 35 spans, joins ≤7.7°, snap to 1/1000 costs ≤0.0005.
   Prior art: `archive/notes/prior-art-human-figure.md` (PH-for-ornament is
   published — Klár & Valasek 2011; the exact grid stays ours).
6. **The broken heart:** built, one S-seam sample looks right (both halves
   interlock on the same curve). **NOT yet on an HTML page** — the operator
   wants the attempts consolidated onto an EXISTING page (`/candidates/` is
   the natural home; `/extra-curves/` is DeepSeek1's).

## The operator's open asks (in order)

1. **Consolidate the heart attempts into an existing HTML page.** Samples
   ready in `deep2/out/heart-*.svg`; the good one is `heart-S seam, lateral
   0.18.svg` (rename to a slug when copying into `app/public/`).
2. **The human figure at the centre** — TODO.md carries the operator's words,
   the canon route, and the prior-art pointer.
3. **HTML page consolidation** — the operator said "we need to consolidate
   our html pages"; a survey of app pages vs workbench pages is unstarted.
4. The housekeeping: run `scripts/prepush.sh` (last known reds were
   DeepSeek1's: `side-tests.html` label, c-0398 slot, book manifest).

## Environment facts a fresh session must not rediscover

- Inkscape headless: `PYTHONPATH=/Applications/Inkscape.app/Contents/Resources/share/inkscape/extensions
  /Applications/Inkscape.app/Contents/Resources/bin/python3 ph_extension.py /tmp/blank.svg --mode=...`
- The .inx namespace must be `.../namespace/inkscape/extension`.
- DeepSeek1 is actively editing; the counters race (reading_counts) — refresh
  from a clean extraction before pushing.
- ruff is installed in the venv and configured in pyproject.toml; `deep2/` is
  clean under it.
- Attention sounds: global cli.json → `ding-high.wav`; sidechat launcher env
  (`OPENCODE_CLI_CONFIG_CONTENT`) → `ding-low.wav` (G4, volume 0.18).
- Compaction: sidechat.json has keep 24k, buffer 20%, background false,
  summaries by deepseek-v4-pro; `/precompact` writes state/PRE-COMPACT-int.md
  before a compaction.
