# REGRESSIONS-int — fixed bugs, and the check that keeps them fixed

A bug fixed twice is a process failure. This file is the register: one row per
fault that cost real work, the test that now guards it, and the date it was
fixed. The tests live in `tests/test_regressions.py` and run in the fast suite.

**The rule, for every session:**

1. **Never delete a row or its test** because a change made it awkward. That is
   the moment the test is earning its keep.
2. **A fix and its row land in the same commit.** A fix without a test is not
   finished.
3. **If a test fails and the new behaviour is right**, the row is amended in the
   same commit, with the reason written down — never silently.
4. Before a handoff: `.venv/bin/python -m unittest tests.test_regressions`.

## The register

| # | date | the fault, as the operator saw it | the check | what it protects |
|---|---|---|---|---|
| 1 | 2026-11-14 | "when I refresh, it defaults to an incorrect curve because the values get put directly, not in the correct whole power boxes" | `test_a_power_lands_in_its_own_box_not_the_next_one` | power→box placement in `curve_records.rows_for_step` |
| 2 | 2026-11-14 | "why don't I see any .5 roots? you messed something up" | `test_the_half_power_boxes_are_never_removed_by_the_starter` | the experimental page always opens at step ½ |
| 3 | 2026-11-14 | rows and powers disagreed; two sources of truth | `test_stored_curves_keep_terms_and_drop_flat_rows` | the `curve-lab.curves/2` format |
| 4 | 2026-11-14 | "is this the page I am looking at?" — stale copies looked like broken pages | `test_the_build_stamp_sits_at_the_foot_and_is_current` | the footer build stamp |
| 5 | 2026-11-14 | "there should be about double the number of sliders" — the decade slider vanished | `test_every_speed_number_still_has_two_sliders` | mantissa + decade per number |
| 6 | 2026-11-14 | step ½ could not reach `t^7` | `test_the_ladder_still_reaches_thirty_numbers` | the 30-number ladder |
| 7 | 2026-11-14 | "it shows the curve, and then the curve again in a box" | `test_an_open_gallery_cell_draws_one_curve_only` | one figure per open cell |
| 8 | 2026-11-14 | "figures 1-6 are obviously wrong" — the section re-shuffled itself | `test_the_knotlike_section_still_opens_with_the_operators_curves` | the operator's six first |
| 9 | 2026-11-14 | position-based ordering drifted when a curve was added | `test_the_ordering_rules_name_curves_rather_than_positions` | order stated by name |
| 10 | 2026-11-14 | a grid and inflection count claimed for fractional powers | `test_a_fractional_step_reports_no_grid_and_no_inflection_count` | honest readouts |
| 11 | 2026-11-14 | no number to steer "make the knot bigger" by | `test_the_readout_still_reports_knot_and_leg_shares` | knot/leg shares |
| 12 | 2026-11-14 | loading a curve silently changed the exponent step | `test_loading_a_curve_does_not_change_the_exponent_step` | the step belongs to the operator |
| 13 | 2026-11-14 | "Build from flat spots is putting the numbers in the wrong boxes when I click the button" | `test_the_flat_spots_fill_whole_power_boxes` | the fill places coefficients by power |
| 14 | 2026-11-14 | "both rows: 1 + size(t - t2)" went lopsided | `check-nth-page.mjs` (exp page: gap stays 0.0000) | the product keeps its tail instead of trimming it |
| 15 | 2026-11-14 | undo after a rung grew crashed a box | `check-nth-page.mjs` (exp page: undo runs clean) | restored rows are padded to the boxes that exist |
| 16 | 2026-11-14 | "a fraction like 1/4 ... .1 doesnt seem like the way" — 1/3 blew the grid to 8.7e13 | `test_the_tweak_sizes_are_binary_exact_only` | only binary-exact sizes are offered |
| 17 | 2026-11-14 | "fix these buttons so they never lose data" — a lower rung deleted the higher numbers | `check-nth-page.mjs` (rung round trip keeps 777) | rung changes stash coefficients instead of deleting them |
| 18 | 2026-11-14 | the suite went red on `ph-nth-sandbox.html` with nothing changed: the reproduce check compared the build stamp, so it failed whenever the minute rolled over | `test_the_generator_reproduces_the_page` (compares after dropping the `n-build` line) | the rebuild check tests the page, not the clock |
| 19 | 2026-11-14 | 172 errors in `test_ph_root_found.py` for hours: the test read `speedX`/`bend`/`pitch` while `found-curves.json` had become `curve-lab.curves/2` with `terms`/`measured` | `test_the_walk_landed_something` (asserts the format) and the rows rebuilt from `terms` | the found-curves checks follow the file format, so a format change cannot silently orphan them |
| 20 | 2026-11-14 | "the page should have a gallery" — the experimental page had one, and its test still demanded none, so the suite stayed red | `test_the_page_keeps_the_gallery` | the experimental page keeps its gallery; the reversed guard is written in the test's docstring |
| 21 | 2026-11-16 | "grid 1/5,148 against the record's 1/36, with identical rows" — the page's doubles squared a row of 10^8 (1.06e16, past 2^53) and counted the grid 143 times too big | `test_exact_numbers.py`: `test_every_stored_curve_agrees_with_the_exact_core`, `test_the_large_row_keeps_grid_36_not_the_page_5148`, `test_the_page_squares_the_same_row_wrong_and_is_told_not_to` | one exact core (`curve_lab/measure.py`), the record as the authority for a stored curve, and the page printing the record's number while its rows are untouched |
| 22 | 2026-11-16 | "the list said HANDOFF was 2,226 lines when it was 2,353, and the counter said 'counts already right'" — the row pattern expected the file name second, so every numbered Tier 0 row was skipped | `tests/test_reading_counts.py`: `test_a_numbered_row_is_one_the_counter_recognises`, `test_the_pairing_has_no_stale_count_left` | the reading list's counts, and the counter that must refresh them |
| 23 | 2026-11-16 | "how can you lose all those curves when we werent even touching that code" — a damaged read became an empty list, and the next save wrote one curve over all of them | `scripts/check-saved.mjs` (six browser checks: seeding, repair from backup, no wipe after a bad read, load from a restored button, a pair record) and `tests/test_operator_list.py` (the list on disk is current and complete) | the saved-curve buttons: no write after a failed read, a backup and mirror on every save, and a file to seed a reset browser |
| 24 | 2026-11-16 | the page said `crosses itself 5` for `lace-1of10-1of5-3` and the record said 4 — the stored numbers predated the parameter-pair dedupe | `tests/test_crossings.py`: every record matches the router, the triple point counts as three pairs, and the count is scale-free | 100 stale crossing counts, and the one definition they now share |

| 25 | 2026-11-19 | "all the names I typed are lost" — the desk's script threw on a duplicate `let timer`, so Save never ran | `app/scripts/check-names.mjs` (212 rows, every one composes a name; a save survives a reload) and `app/tests/name-parts.test.mjs` | the desk save path, including a name that is only its construction |
| 26 | 2026-11-19 | "save failed: duplicate curve" — the file keyed by name, the page by id, and the merge kept both | `app/tests/finder-stars.test.mjs` (duplicate merge) | star identity |
| 27 | 2026-11-19 | a backup was written 0 bytes and still said "integrity ok" | `scripts/backup-db.mjs` checks the row count as well as the integrity | backups |
| 28 | 2026-11-19 | the notes mirror was stale: 2 rows against 262 in the database | `scripts/check-db.mjs` and the save path writing the mirror | the readable fallback |

| 29 | 2026-11-19 | "the finder starred curves don't show" — a browser with 2 stars saved, and the server deleted the other 4 | `app/scripts/check-stars.mjs`: 56 cards, no duplicate card, starring saves, un-starring names its removal, and the server's count is unchanged | a save adds; a removal must be named in `removed` |
| 30 | 2026-11-19 | "/lab has no margins" — the page lost its `<main>` wrapper, so the max-width and padding never applied | `app/scripts/check-pages.mjs`: every page has `main#main`, one header, the draft mark and no self-link | every page's layout |
| 31 | 2026-11-19 | "24 starred curves, but many are duplicates" — a mirrored curve that was also featured was built into both "Symmetric" and "Best so far", so 5 cards existed twice | `app/tests/finder-sections.test.mjs`: no curve is in two sections | the finder's section order |
| 32 | 2026-11-19 | a star click threw `ReferenceError: title is not defined` before the list was written, so nothing was added and nothing was saved | `app/scripts/check-stars.mjs` | the finder's star button |
| 33 | 2026-11-19 | ten of the 212 chosen curves could not be saved: a name that is only its construction ("amper", "swan", "knot-6") composed to an empty string and Save refused | `app/tests/name-parts.test.mjs` and `app/scripts/check-names.mjs` (0 rows without a name) | the naming desk |
| 34 | 2026-11-19 | "the names I saved are gone, again" — an old draft in the browser still sat in the box, so the saved name was hidden | `app/tests/name-parts.test.mjs` (`draftState`: an old draft never hides a newer save) and `app/scripts/check-names.mjs` | the naming desk's saved-name display |
| 35 | 2026-11-19 | "/illuminations is 500" — after the rails and fills, a figure held more points than `Math.min(...xs)` can take, and 238 figures in one request threw `Maximum call stack size exceeded` | `app/scripts/check-pages.mjs` (all 12 pages, 200 and one header) and `state/FRAMES-int.md` for the richer paths | the figure writer's bbox |
| 36 | 2026-11-19 | "something is broken… you have some restriction making you not do the job" — the grid demo had been patched a dozen times by string replacement: two helpers that only returned `pad`, three checkboxes wired to nothing, a `picked` value written and never read, and comments describing code that had moved | `app/scripts/check-prime-mover-page.mjs` (alternating shapes, exact driver rows, computed guard, wave dot count, no dead controls) | the grid demo page, and the habit that made it |

## Fixed and measured, but not yet in the fast suite

These have browser-level proof in `scripts/check-nth-page.mjs` (which needs a
headless browser), so they are named here rather than duplicated:

- the flat-spot strip: click to add, click a dot to remove one copy (three clicks
  at ½ give a count of 3);
- the suggestion list fills the known row `[-8, 129, -663, 1522, -1620, 648]`;
- typing in a speed box keeps its sign and its decimal point;
- the gallery loads a curve into the sandbox with the rows it was saved with;
- the saved-curve buttons survive a damaged value and a browser reset
  (`scripts/check-saved.mjs`: six checks, seeded from `workbench/operator-list.json`).

## Known open faults

- `cut and rebuild` (arc length) falls back to the whole curve on every curve
  tried: the span needed is longer than the largest exact square below 1, so
  only the whole span keeps the numbers exact. It reports this rather than
  cutting silently.
- `rebuild without the legs` is exact and verified against a Python reference,
  but the crossings on these curves span nearly all of `t`, so it usually has
  nothing to remove.
- The percentage-of-`t` control added earlier is superseded and inert; the
  markup is gone, the handler remains harmless.
| 37 | 2026-11-19 | "the gallery is empty" behind a partial figure run: `curve_pngs.mjs --only` wrote `index.json` from the two curves it had drawn, so 270 entries vanished and every other cell lost its figure | `tests/test_regressions.py` (`test_the_figure_index_names_every_registry_curve`: the index names every registry uid) and the merge in `scripts/curve_pngs.mjs` | the figure index |
| 38 | 2026-11-19 | the exact-linkage test said "no linkage closes rationally" for every link set, including the parallelogram that plainly does | `tests/test_linkage_exact.py` (parallelogram closes at every station; the joint meets both circle conditions; a general crank-rocker does not) | the rosette linkage rule |
| 39 | 2026-11-20 | "I CANT BELIEVE WE ARE DEALING WITH PARALLEL CURVE" — and the operator was right twice. (a) `print_plates.mjs` read `workbench/sandbox-curves.json`, which a later commit moved to `data/sandbox-curves.json`, and treated the missing file as "no desk values": every plate silently used 6 % / plus 2 / minus 2. (b) the row builder had a **duplicate `character:` key**; the second copy set plus and minus to 0, so the rail was `±d·normal` — a parallel offset by construction — whatever the desk said. (c) the save step called `app/scripts/export-sandbox.mjs`, which does not exist, so a tune wrote the database and never reached the plate. | `tests/test_regressions.py` (`test_the_plates_are_not_parallel_curves`, which runs `tests/js/plate-row.test.mjs`): the desk's plus/minus must reach the row, the guarded rail must widen along the curve while the other barely moves, and zero character must be the only parallel case | the one law for a plate's four values (`scripts/lib/plate-row.mjs`: note → desk row → defaults), and one copy of the decisions (`data/sandbox-curves.json`) |
| 40 | 2026-11-20 | `/tune/c-0001` said "the rows are too large for the rail routine; spine only" and drew nothing — a confident caption over a blank picture | `scripts/check-tune-lab.mjs` (waits for `#lab-preview svg`; a blank preview fails, and so does a message that invents a cause) | the tuning preview: the page must draw, and must not name a reason the code does not measure. Cause: `(await import(path)).default` is `undefined` under Vite for a CommonJS file outside `app/`, and the `catch` covered it |
| 41 | 2026-11-21 | "we might have 5 different versions from one spine, and that is good" — the only save was one row, replaced in full, so a chosen name and construction were lost and a second version could not exist | `app/tests/desk-tune.test.mjs` (save keeps fields; a new curve is a record with the next letter uid; collisions by name, alias and uid) and the desk checks in `scripts/check-tune-lab.mjs` (a name field, both save buttons, the family list) | the desk's rows: one row per curve, many curves per spine, and a name is a key |
| 42 | 2026-11-21 | "try different lower values for the percentage... the width jumps all around" — two causes. (a) the fold guard halved the width in powers of two, so raising the slider could narrow the band (`c-0002`: 2.2 % became 1.15 % at the next step). (b) after that was fixed, the server's first paint still used the old guard from a cached `require`, so the band jumped from 1.5 % to 2.29 % on the first touch | `tests/js/plate-guard.test.mjs` (no drop while the width rises from 0.5 % to 8 %; the cut must be the largest width that does not fold) and `scripts/check-tune-lab.mjs` (the first paint and the live redraw must report the same used width and draw the same picture) | the fold guard cut once to the largest safe width, and one maths file shared by the server and the client |
| 43 | 2026-11-21 | "add the usual 'saved' indicator. it only saves sometimes" — a save was a full form post that waited for the plate render, with no state beside the button, so a slow save looked like no save and a second click could write twice | `scripts/check-tune-lab.mjs` (a refused save says `not saved` beside the buttons and re-enables them) | the save's own state: saving, saved, or the server's refusal, beside the button |
| 44 | 2026-11-21 | "please fix underlying graph" — `c-0088`–`c-0143` drew as staircases: the registry copied each sampled outline with `round(px, 2)`, coarser than the step between samples on a curve of size 1–3, so a smooth parabola (`c-0143`) came out as axis-aligned steps | `tests/test_registry_paths.py` (every sampled outline must match its finder source to 1e-6; `c-0143` must have under 10 % axis-aligned steps) | the stored drawing's precision; identity may round, the outline may not |
| 45 | 2026-11-21 | the path records printed blobs and spikes (`c-0273`) or the spine only: the path rail's fold cap moved one station at a time, so the distance jumped 4 % of the curve's size and the edge made 105 sharp turns | `tests/js/plate-path.test.mjs` (`c-0273`: two rails, neither crosses the spine, no step over 1 % of size, under 30 sharp turns) and `scripts/check-tune-lab.mjs` (a stored path draws a band in the lab) | the path rail's continuous cap: one character law, the 0.5 × radius rule, applied as a ceiling that cannot step |
| 46 | 2026-11-21 | "how am i supposed to name it? desk io" and "the suggested name is in the box, but is greyed out and i cant save it" — the new-curve field held only a placeholder, so the button refused an empty name; a half-landed edit then made the page 500 | `scripts/check-tune-lab.mjs` (the box starts with a real free name; clearing it says "type a name" in place and re-enables the buttons) | the new-curve name: a real default, an editable value, and a refusal with a reason |
| 47 | 2026-11-21 | "it seems like you are ignoring that. didnt i say put the curves with stars? ... that is why we need the explanation below the curve" — `/plates` listed all 371 records, including 1-star and unrated ones, with no reason for any | `app/tests/provenance.test.mjs` (2 stars kept, 1 and 0 out, a variant joins a kept parent; the sentence names the rating or parent and the saved note) and the page prints it | the plates page shows the curator's choice and states its provenance |

## 90 · the span-trace width refusal blocked the desk records — removed

**Fault.** The `Trace` constructor refused a span trace that carried a width
("a cubic span trace is a hairline; width is not supported"), while the tune
desk's saved records carry exactly that (spans + width), and
`build_piece`'s pre-built path is written to build rails from it. Every saved
desk piece was un-buildable through the normal model, and the
rails-from-spans capability was unreachable. Also: `build_piece` doubled the
layer when the trace name already carried it (`ink/ink/a`).

**Fix.** The refusal is removed (`curve_lab/piece.py`); the pre-built path
builds the rails with the fitted parallels and reports the fit error in the
piece info (`fit_ok`), so the approximation is stated. The layer is not
doubled when the trace name already carries it. The TypeScript port follows
(`app/src/lib/piece.ts`).

**Test.** `tests/test_regressions.py :: SpanWidthTraceTest` — a span trace
with a width builds two rails, two caps (round start, point end) and the
spine, the fit is under tolerance, and the cap name is not double-prefixed.
| 48 | 2026-11-21 | every browser check failed with `net::ERR_CONNECTION_REFUSED at http://127.0.0.1:4321/` while `curl localhost:4321` answered; a fresh `npm --prefix app run dev` bound Astro's `localhost` (IPv6 ::1) only, so every documented 127.0.0.1 link and every check using it was refused | `tests/test_regressions.py` (`test_the_dev_server_answers_on_ipv4_loopback`: the dev script names 127.0.0.1) | the dev server's host is explicit, and it is the address the links and checks use |
| 49 | 2026-11-21 | `/ph-nth-sandbox/` threw `Cannot read properties of undefined (reading 'length')`, intermittently, in the framed gallery: a saved record can be a **pair** with the name on its primary, so the pair entered the list with no name and the numberer called `uidOf(undefined)` | `scripts/check-pages.mjs` (every route records a `pageerror`, and `/ph-nth-sandbox/` is in its list; the fix was also probed with a seeded nameless pair) | saved records are flattened to their primary before they reach the gallery, and a nameless record is dropped rather than counted |
| 50 | 2026-11-21 | "6% is way too much, look at the first two curves i did for a better preset level" and "tiny or no offset for others": the note migration wrote 0 into width, plus and minus for untouched curves, and the note won over the desk row, so those plates drew a 0 % band (plus = minus = 0 is a parallel offset); the default was still 1.5 % | `tests/js/plate-row.test.mjs` (the preset is 1 % / 2.5 / 0.1, the first two curves; a placeholder zero in a note falls through to the desk row) | note → desk → defaults, with a zero note treated as unset; the preset is the first two tuned curves |
| 51 | 2026-11-21 | "the ones where the rails are wrong need work too": at `c-0001`'s preset (1 %, plus 2.5) the widest rail reached **1.28 ×** the fold limit, because the guard capped the base width and then added the character bow; the rail crossed at the loop | `tests/js/plate-guard.test.mjs` (`c-0001 at the operator's preset keeps a band and does not fold at the loop`: used 0.7 %, fold ≤ 0.9, the next 0.01 % folds) | the guard measures the station-wise offset × curvature **including the bow**, not the base width × peak curvature |
| 52 | 2026-11-21 | "it looks to me like you went backwards with c-0275 to 368", then "i didnt ask for spines only. i asked for clean curves like the first two": the preset on stored paths first drew a tangle, then the path zero was read as spine-only; either way half the review was wrong, and the plate PNG batch took ten minutes for 371 | `tests/js/plate-row.test.mjs` (a stored path with a zero **or missing** width takes the preset; a saved width wins) and `node scripts/print_plates.mjs --svg-only` (all 371 SVGs in **10.8 s**) | one preset for every curve that has no saved width; the SVG is the plate and the review's card; the 300 dpi PNG is a separate, slow export |
| 53 | 2026-11-21 | "c-0273 to whatever are wrong wrong wrong ... give the offset curves as they should be": the stored paths and the row plates were drawn with a character offset, which tangle on a loop and collapse to the spine at a cusp; `docs/SIDE-CURVES.md` §1 and §5: a side curve is the same construction with one parameter shifted, **never** a parallel offset | `tests/test_regressions.py` (`test_the_side_curves_are_the_construction_partners`, running `tests/js/plate-partner.test.mjs`: stored paths scale linearly, rows scale the position by the speed scale squared, the origin is fixed, the right is inside the left) | every plate's side curves are the construction partners: the rows squared, the stored paths linear; the character rail law remains the tune page's ||| 54 | 2026-11-21 | the reduce desk printed "proven miss bound: 0.00 %, actual miss: 108 %, always ≤ the bound" — three claims that cannot all be true; the integral of the squared speed rows was a running sum (`out[i+1] = out[i] + c/(i+1)`) instead of the antiderivative, and the squared rows were built only over the speed rows' length instead of the full convolution, so every degree, bound and verdict the desk ever printed was computed on a wrong polynomial (c-0260's true position degree is 23, not 25; its true single-piece truncation miss is ~3 %, not 29 %) | `app/tests/chebyshev.test.mjs` (the exact bound pinned to the Fraction reference for c-0260 at 1, 2 and 4 pieces; the measured miss asserted ≤ the proven bound; a collapsed reduced form refused) and `app/src/lib/reduction/chebyshev.ts` (the bound is a Fraction basis change, no float touches it) | the exact bound comes from an exact basis change, the desk refuses its verdict when a self-check fails, and numbers on the page are plain integers or decimals, never an exponent |
