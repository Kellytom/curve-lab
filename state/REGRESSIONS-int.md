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

| 25 | 2026-11-19 | "all the names I typed are lost" — the desk's script threw on a duplicate `let timer`, so Save never ran | none yet: the API is tested (`app/tests/curve-notes.test.mjs`), the page is not | the desk save path |
| 26 | 2026-11-19 | "save failed: duplicate curve" — the file keyed by name, the page by id, and the merge kept both | `app/tests/finder-stars.test.mjs` (duplicate merge) | star identity |
| 27 | 2026-11-19 | a backup was written 0 bytes and still said "integrity ok" | `scripts/backup-db.mjs` checks the row count as well as the integrity | backups |
| 28 | 2026-11-19 | the notes mirror was stale: 2 rows against 262 in the database | `scripts/check-db.mjs` and the save path writing the mirror | the readable fallback |

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
