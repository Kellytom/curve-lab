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

## Fixed and measured, but not yet in the fast suite

These have browser-level proof in `scripts/check-nth-page.mjs` (which needs a
headless browser), so they are named here rather than duplicated:

- the flat-spot strip: click to add, click a dot to remove one copy (three clicks
  at ½ give a count of 3);
- the suggestion list fills the known row `[-8, 129, -663, 1522, -1620, 648]`;
- typing in a speed box keeps its sign and its decimal point;
- the gallery loads a curve into the sandbox with the rows it was saved with.

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
