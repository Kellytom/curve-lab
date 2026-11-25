/**
 * Fixed bugs, each with the check that keeps it fixed.
 *
 * This is the TypeScript twin of `tests/test_regressions.py`, ported 2026-11-24 so the
 * register runs on the same runtime as the pages. Every row keeps its Python name, its
 * mechanism and the operator's own words. The modules a row calls that are still Python
 * (`curve_records`, `generators`, `check_asks.py`, `said_checklist.py`,
 * `curve_registry.py`) stay Python until their own ports, and are run as subprocesses.
 *
 * A bug that was fixed once and discovered again is a process failure, not bad luck.
 * Every user-visible fault that took real work to fix gets a row here, named after the
 * fault. Nothing in here is deleted because a change made it awkward — an awkward test
 * is the point.
 *
 * Run: node --test tests/test_regressions.ts
 */
import { describe, test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const PANELS = "scripts/ph_nth_panels.js";
const TEMPLATE = "scripts/ph_nth_sandbox.py";
const EXP = "scripts/ph_nth_sandbox_exp.py";
const FOUND = "workbench/found-curves.json";
const PAGE2 = "workbench/ph-nth-sandbox-2.html";

const read = (rel: string): string => readFileSync(path.join(ROOT, rel), "utf8");
const readJson = (rel: string): any => JSON.parse(read(rel));

/** The Node the app runs on: `~/node24` first, else the one running this file. */
function node24(): string {
  const preferred = path.join(homedir(), "node24", "bin", "node");
  return existsSync(preferred) ? preferred : process.execPath;
}

/** The Python the project's own scripts run on. */
function python(): string {
  const venv = path.join(ROOT, ".venv", "bin", "python");
  return existsSync(venv) ? venv : "python3";
}

function run(command: string, args: string[]) {
  const result = spawnSync(command, args, { cwd: ROOT, encoding: "utf8" });
  return { code: result.status ?? 1, out: result.stdout ?? "", err: result.stderr ?? "" };
}

/** A row whose subject is still Python: run it there and read its exit code. */
function py(program: string) {
  return run(python(), ["-c", program]);
}

/** A row that guards a browser-side test: run it under Node and require a pass. */
function nodeTest(rel: string) {
  const result = run(node24(), ["--test", path.join(ROOT, rel)]);
  assert.equal(result.code, 0, result.out + result.err);
}

/** Python's `str.index` raises on a missing marker; slicing from -1 must not pass here. */
function at(text: string, marker: string, from = 0): number {
  const found = text.indexOf(marker, from);
  assert.notEqual(found, -1, `marker not found: ${marker}`);
  return found;
}

function includes(text: string, needle: string) {
  assert.ok(text.includes(needle), `expected to find: ${needle}`);
}

function omits(text: string, needle: string, why?: string) {
  assert.ok(!text.includes(needle), why ?? `expected not to find: ${needle}`);
}

/** Python truthiness for the `or` chain in the data README check: `[]` and `{}` fall through. */
function pythonTruthy(value: unknown): boolean {
  if (Array.isArray(value)) return value.length > 0;
  if (value && typeof value === "object") return Object.keys(value).length > 0;
  return Boolean(value);
}

/** Python's `round()` rounds a half to even; `Math.round` does not. */
function roundHalfEven(value: number, digits: number): number {
  const scale = 10 ** digits;
  const scaled = value * scale;
  const floor = Math.floor(scaled);
  const rest = scaled - floor;
  if (rest > 0.5) return (floor + 1) / scale;
  if (rest < 0.5) return floor / scale;
  return (floor % 2 === 0 ? floor : floor + 1) / scale;
}

describe("TestRegressions", () => {
  test("test_the_half_power_boxes_are_never_removed_by_the_starter", () => {
    // 2026-11-14: the default curve loading at step 1 deleted every 1/2 box.
    const source = read(EXP);
    const start = at(source, "starter = (");
    const starter = source.slice(start, at(source, "</body></html>", start));
    includes(starter, "step.value = '0.5'");
    omits(starter, "step.value = '1'");
  });

  test("test_a_power_lands_in_its_own_box_not_the_next_one", () => {
    // 2026-11-14: rows were written straight in, so a whole-power curve at
    // step 1/2 sat in the half-power boxes and drew the wrong curve.
    const result = py(`
import json, sys
sys.path.insert(0, 'scripts')
import curve_records as R
(x, y), refused = R.rows_for_step([R.term(0, 1, -8), R.term(1, 0, 129), R.term(2, 0, -663)], 0.5)
print(json.dumps({"x": x, "y": y, "refused": refused}))
`);
    assert.equal(result.code, 0, result.out + result.err);
    const got = JSON.parse(result.out.trim());
    assert.deepEqual(got.refused, []);
    assert.deepEqual(got.y, [-8, 0, 129, 0, -663]);
  });

  test("test_stored_curves_keep_terms_and_drop_flat_rows", () => {
    // 2026-11-14: two sources of truth (row position and power) disagreed.
    const result = py(`
import json, sys
sys.path.insert(0, 'scripts')
import curve_records as R
document = R.read('${FOUND}')
print(json.dumps({"errors": R.validate(document)}))
`);
    assert.equal(result.code, 0, result.out + result.err);
    assert.deepEqual(JSON.parse(result.out.trim()).errors, []);
    for (const curve of readJson(FOUND).curves as any[]) {
      assert.ok(!("speedX" in curve), "a stored curve keeps terms, not a flat row");
      assert.ok(!("speedY" in curve), "a stored curve keeps terms, not a flat row");
    }
  });

  test("test_the_build_stamp_sits_at_the_foot_and_is_current", () => {
    // 2026-11-14: a stale page looked like a broken page.
    const template = read(TEMPLATE);
    includes(template, '<p class="small mono" id="n-build">build __BUILD__</p>');
    includes(template, "def stamped(page)");
  });

  test("test_every_speed_number_still_has_two_sliders", () => {
    // 2026-11-14: the decade slider went missing, leaving one slider per number.
    const panels = read(PANELS);
    includes(panels, 'decade.className = "decade"');
    includes(panels, "pair.append(number, fine, decade, flip, scales)");
  });

  test("test_the_ladder_still_reaches_thirty_numbers", () => {
    // 2026-11-14: halving the step halved the top power until the rows doubled.
    const template = read(TEMPLATE);
    includes(template, 'data-speed-degree="14"');
    includes(template, "degree 29");
  });

  test("test_an_open_gallery_cell_draws_one_curve_only", () => {
    // 2026-11-14: a found curve was drawn twice, thumbnail plus panel.
    includes(read(TEMPLATE), ".gallery figure.open>svg{display:none}");
  });

  test("test_the_knotlike_section_still_opens_with_the_operators_curves", () => {
    // 2026-11-14: position-based ordering re-shuffled the section on its own.
    const page = read(PAGE2);
    const match = /window\.phNthKnots = (\[[\s\S]*?\]);/.exec(page);
    assert.ok(match, "the knot list is on the page");
    const names: string[] = JSON.parse(match[1]);
    assert.deepEqual(names.slice(0, 7), [
      "wave3", "knot", "bud", "knot-2", "hersheys copy",
      "wave-1of7-1of5-1-bow9", names[6],
    ]);
  });

  test("test_the_ordering_rules_name_curves_rather_than_positions", () => {
    // 2026-11-14: adding one curve shifted every number and re-ordered the page.
    const source = read("scripts/ph_nth_sandbox2.py");
    includes(source, 'DEMOTE = ("wave5"');
    includes(source, 'AFTER = "wave-1of3-2"');
  });

  test("test_a_fractional_step_reports_no_grid_and_no_inflection_count", () => {
    // 2026-11-14: the page claimed a grid that does not exist off whole powers.
    const panels = read(PANELS);
    includes(panels, "grid n/a: fractional powers");
    includes(panels, "inflections n/a: fractional powers");
  });

  test("test_the_readout_still_reports_knot_and_leg_shares", () => {
    // 2026-11-14: 'make the knot bigger' had no number to steer by.
    includes(read(PANELS), "knot ${knotShare}% legs ${legShare}%");
  });

  test("test_the_nudge_buttons_offer_only_whole_steps", () => {
    // 2026-11-14: a size of 1/3 took the grid from 3,465 to 8.7e13, because a
    // third cannot be written exactly in machine arithmetic.
    //
    // Amended the same day on the operator's call: the free-text size field and
    // the share-of-the-pair dial are gone, replaced by one dropdown of patterns
    // and four press-buttons. A fraction cannot be typed at all now, so the
    // hazard is gone by construction rather than by an offered list. The widened
    // ink is refitted to whole numbers at the same degree, so it cannot move the
    // grid either.
    const source = read(EXP);
    omits(source, 'id="n-tweak-size"');
    omits(source, "n-tweak-divisor");
    for (const step of ['data-step="-5"', 'data-step="-1"', 'data-step="1"', 'data-step="5"']) {
      includes(source, step);
    }
    for (const spread of ['<option value="3"', '<option value="8"', '<option value="13"']) {
      includes(source, spread);
    }
  });

  test("test_the_flat_spots_fill_whole_power_boxes", () => {
    // 2026-11-14: pressing fill at step 1/2 wrote the knot into the half-power
    // boxes, so the button drew a different curve from the one it named.
    const panels = read(PANELS);
    const fill = panels.slice(at(panels, "function fillFromFlatSpots()"));
    const body = fill.slice(0, at(fill, "writeCells();"));
    includes(body, "rowsFromTerms(terms)");
    omits(body, "padRow([bow.d, bow.n, -bow.n], count)");
  });

  test("test_loading_a_curve_does_not_change_the_exponent_step", () => {
    // 2026-11-14: loading used to reset the step, silently changing the curve.
    const panels = read(PANELS);
    const start = at(panels, "window.phNthLoad = item =>");
    omits(panels.slice(start, start + 400), "phPowerStep = 1");
  });

  test("test_the_figure_index_names_every_registry_curve", () => {
    // 2026-11-19: "the gallery is empty" — `curve_pngs.mjs --only` wrote the
    // index from the two curves it had just drawn, so 270 entries vanished.
    //
    // The script now merges; this reads the two files so a partial run cannot
    // quietly shrink the gallery again.
    const registry = readJson("workbench/curve-registry.json");
    const index = readJson("app/public/figures/index.json");
    const wanted: string[] = registry.curves.map((record: any) => record.uid);
    const indexed = new Set<string>(index.curves.map((meta: any) => meta.uid));
    const missing = wanted.filter((uid) => !indexed.has(uid)).sort();
    assert.deepEqual(missing, [], "registry curves with no figure");
  });

  test("test_the_plates_are_not_parallel_curves", () => {
    // 2026-11-20, the operator: "I CANT BELIEVE WE ARE DEALING WITH PARALLEL
    // CURVE". They were right twice: the plate read a decision file that no longer
    // existed, and its row builder carried a duplicate `character:` key whose second
    // copy set plus and minus to 0 — a plain parallel offset — whatever the desk said.
    //
    // The law now lives in `scripts/lib/plate-row.mjs`, and its own test measures the
    // two rails: the guarded side must widen along the curve, the other must not move
    // much, and zero character must be the only parallel case.
    nodeTest("tests/js/plate-row.test.mjs");
  });
});

describe("PlateGapTest", () => {
  // 2026-11-22, the operator: "half are too thin and half are too thick ... you should
  // have algorithms to figure that out already and fix it before i even see it. right?
  // check the thickness".
  //
  // The preset was a fixed number, so a curve the fold guard bound drew a hairline and a
  // curve it did not drew a slab. The preset is now a measured 2 % drawn gap, solved per
  // run; this runs the plate-gap check over every preset curve in the registry.
  test("test_every_preset_plate_draws_the_target_gap", () => {
    nodeTest("tests/js/plate-gap.test.mjs");
  });
});

describe("PlateRailCrossingTest", () => {
  // 2026-11-23, the operator: "letting each rail cross itself at a tight turn, marking
  // every crossing with a red dot, hiding the small loop as an invisible span, and recording
  // the spans in book/print/rail-holes.json."
  //
  // The inside cap and the roundSpikes bevel are withdrawn, so the rail is the asked offset at
  // every station and folds through itself where the curve turns tight. This runs the three
  // probed curves (c-0046, c-0065, c-0273) and checks the drawn dot and the recorded span,
  // not the count, which changes with the width.
  test("test_each_probed_curve_crosses_and_records_a_span", () => {
    nodeTest("tests/js/plate-holes.test.mjs");
  });
});

describe("SidePillarTest", () => {
  // 2026-11-23, found in the build, not by the operator: the side-pillar figure drew one bow
  // across the page with its labels at the edges.
  //
  // The path strings are model units (x around ±150, y up); they were written into the SVG as if
  // they were already SVG coordinates, so nothing was offset or flipped, and the Q control point
  // ignored the pillar's axis. This runs the page's own tests: each line stays beside its axis,
  // the first paint on the page puts it there, the labels sit in the empty field, and the swell
  // can never make the shaft wider than its foot.
  test("test_each_pillar_stays_beside_its_axis", () => {
    nodeTest("tests/js/side-pillars.test.js");
  });
});

describe("BranchDrawTest", () => {
  // 2026-11-23: "the multi-branch records c-0416 (cruciform) and c-0418 (absx-gerono) draw as
  // fragments."
  //
  // Two faults, one rule. The tune page joined c-0416's four arms with chords, and the figure
  // page read them as spine + two rails and filled the jump as a blob. `PLATE.branchesOf` is the
  // one rule: stored branches first, else a path splits on a jump over a quarter of its size.
  test("test_a_branch_record_is_drawn_as_branches", () => {
    for (const name of ["plate-branches.test.mjs", "figure-branches.test.mjs"]) {
      nodeTest(path.join("tests/js", name));
    }
  });
});

describe("OrnamentWriterTest", () => {
  // 2026-11-22, the operator: "i cant see how many curves to do because the page
  // keeps refreshing constantly."
  //
  // The launch agent re-ran `npm run dev` every ten seconds; it failed on Node 22, but
  // its `predev` step still ran the ornament writer, which deleted the folder and rewrote
  // all 371 SVGs each time. The dev server watches that folder, so every open page reloaded
  // on the same ten-second beat. The writer now leaves an unchanged file alone, inode and
  // mtime included, and prunes only files whose curve has left the registry.
  test("test_an_unchanged_ornament_is_not_rewritten", () => {
    nodeTest("tests/js/write-if-changed.test.mjs");
  });

  test("test_the_ornament_writer_does_not_wipe_its_folder", () => {
    const source = read("scripts/marginalia.mjs");
    omits(source, "rmSync(OUT",
      "wiping the folder rewrites every ornament and reloads every page");
    assert.ok(source.includes('from "./lib/write-if-changed.mjs"'),
      "the writer must use the tested write-if-changed rule");
  });
});

describe("SpanWidthTraceTest", () => {
  // The desk records name their traces with the layer baked in ("ink/a") and
  // carry a width; the constructor refused that combination ("a cubic span trace
  // is a hairline"), so every saved desk piece was un-buildable through the
  // normal model, and the rails-from-spans capability was unreachable. The
  // refusal is removed; build_piece's pre-built path builds the rails and
  // reports the fit error; the layer is not doubled when the name already
  // carries it.
  test("test_a_span_trace_may_carry_a_width_and_build_its_rails", () => {
    const program = `
import json, sys
sys.path.insert(0, '.')
from curve_lab.model import Design, Segment
from curve_lab.piece import Piece, Trace, build_piece
def ribbon(x, y, length=60.0, angle=0.0, kd=0.0, kappa0=0.005):
    return Design(name="ribbon", segments=[Segment(kd=kd, length=length, kappa0=kappa0)],
                  anchor={"x": x, "y": y, "angle": angle})
groups0, _ = build_piece(Piece(name="src", stroke=0.6, traces=[
    Trace("a", ribbon(0, 0, kd=0.01, kappa0=0.005), width=3.0)]), tol=0.02)
spine_spans = [dict(s) for s in groups0[0].spans]
piece = Piece(name="desk", stroke=0.6, traces=[
    Trace("ink/a", spans=[dict(s) for s in spine_spans], width=3.0,
          terminals=("round", "point"))])
groups, info = build_piece(piece, tol=0.02)
roles = [g.role for g in groups]
assert roles.count("rail") == 2, roles
assert roles.count("cap") == 2, roles
assert roles.count("spine") == 1, roles
assert info["fit_ok"], info["traces"]
assert groups[0].name == "ink/a start round", groups[0].name
assert next(g for g in groups if g.role == "rail").instance == "ink/a"
print("ok")
`;
    const result = run(python(), ["-c", program]);
    assert.equal(result.code, 0, result.out + result.err);
  });
});

describe("RepeatedAskTest", () => {
  test("test_every_operator_ask_is_written_down_and_closed_honestly", () => {
    // The operator, 2026-11-23: "i should not have to repeat myself", after asking
    // for a way to save the cut curves two or three times. Each session read the code
    // and fixed something adjacent, because the ask was only in the chat. The register
    // is `state/ASKS-int.md`, read at Tier 0; this check fails when a row has no
    // verbatim ask, a fixed row names no real commit or file, or an open row names no
    // next step.
    const result = run(python(), [path.join(ROOT, "scripts", "check_asks.py")]);
    assert.equal(result.code, 0, result.out + result.err);
  });
});

describe("SaidRollTest", () => {
  test("test_the_said_rolls_hold_every_message_with_proof", (t) => {
    // The operator, 2026-11-23: "check http://127.0.0.1:4321/said/ on a regular basis and
    // make a rolling checklist from it in md and then prove that you did the work and check
    // it off." Both chats have a file and a roll: `data/said.json` →
    // `state/SAID-CHECKLIST-int.md` for the main chat, `data/said-deep2.json` →
    // `state/SAID-DEEP2-CHECKLIST-int.md` for sidechat. Each check fails when a message has
    // no row, a row's words differ from the message, or a `done` row names no real commit or
    // file. Local only, like the history.
    let checked = 0;
    for (const who of ["me", "deep2"]) {
      const said = path.join(ROOT, "data", who === "me" ? "said.json" : "said-deep2.json");
      const roll = path.join(ROOT, "state",
        who === "me" ? "SAID-CHECKLIST-int.md" : "SAID-DEEP2-CHECKLIST-int.md");
      if (!existsSync(said) || !existsSync(roll)) continue;
      const result = run(python(), [path.join(ROOT, "scripts", "said_checklist.py"), "--who", who]);
      assert.equal(result.code, 0, result.out + result.err);
      checked += 1;
    }
    if (!checked) t.skip("the /said/ histories and their rolls are local only");
  });
});

describe("CurveFlagsTest", () => {
  test("test_every_curve_has_a_status_and_its_png_follows_the_flag", () => {
    // The operator, 2026-11-23: "put a flag in the database for every curve that indicates
    // whether its png should be git ignored... and then make sure they are", and "make sure
    // even the temporary or in progress curves are in the database labeled as such". Three
    // checks: every page curve is a Curve or Study row with a known status
    // (`check_page_curves.mjs`), every plate and figure PNG is tracked exactly when its row
    // says `pngIgnored: false` (`curve_pngs_git.mjs`), and the study rows are registered
    // (`register_studies.mjs`).
    for (const script of ["register_studies.mjs", "curve_pngs_git.mjs", "check_page_curves.mjs"]) {
      const result = run(node24(), [path.join(ROOT, "scripts", script)]);
      assert.equal(result.code, 0, `${script}:\n${result.out}${result.err}`);
    }
  });
});

describe("GapsNamedTest", () => {
  test("test_the_gaps_page_proposes_only_curves_that_are_actually_named", () => {
    // 2026-11-23, found in the build: `curve_gaps.mjs` took every `dict(key=...)` block in
    // `generators.py` as a named curve, so the speed-family examples "quartic" and "sextic"
    // were listed as missing classical curves for years. Only the NAMED table (blocks with an
    // equation) counts.
    const result = py(`
import json, sys
sys.path.insert(0, 'scripts')
import generators as G
print(json.dumps([spec["key"] for spec in G.NAMED]))
`);
    assert.equal(result.code, 0, result.out + result.err);
    const known = new Set<string>(JSON.parse(result.out.trim()));
    const page = readJson("app/src/data/extra-curves.json");
    for (const curve of page.missingNamed as any[]) {
      assert.ok(known.has(curve.key), `${curve.key} is not a NAMED curve`);
    }
    const uids = new Set<string>(
      readJson("workbench/curve-registry.json").curves.map((row: any) => row.uid));
    for (const curve of page.addedOnRequest as any[]) {
      assert.ok(uids.has(curve.uid), `${curve.uid} is not in the registry`);
    }
  });
});

describe("RegistryRebuildTest", () => {
  test("test_the_registry_rebuild_refuses_to_drop_curated_rows", () => {
    // 2026-11-23, from the TODO: `scripts/curve_registry.py` rebuilds and renumbers the
    // registry from its sources, so it would lose the seven curated finds (c-0263..c-0269)
    // and every record added by hand. It now refuses and names the difference unless
    // --force; this runs the real --write and requires the file to be untouched.
    const file = path.join(ROOT, "workbench", "curve-registry.json");
    const before = readFileSync(file);
    const result = run(python(), [path.join(ROOT, "scripts", "curve_registry.py"), "--write"]);
    assert.equal(result.code, 2, result.out + result.err);
    includes(result.out + result.err, "refusing to write");
    assert.ok(before.equals(readFileSync(file)), "the registry was written anyway");
  });
});

describe("BookPlateTest", () => {
  test("test_every_curve_has_a_3000_px_300_dpi_plate", () => {
    // book/README.md: a 3000 px long side (10 in at 300 dpi) and a 300 dpi pHYs. The check
    // reads each PNG header; a curve with no plate, a short plate or a plate without the dpi
    // fails, because the book is drawn from all of them.
    const result = run(node24(), [path.join(ROOT, "scripts", "check_book_plates.mjs")]);
    assert.equal(result.code, 0, result.out + result.err);
  });
});

describe("MaxCurvatureTest", () => {
  test("test_the_sharpest_bend_is_computed_and_not_a_placeholder", () => {
    // 2026-11-23, found in the build: `maxCurvature` read 0.0 on all 403 curves — a
    // documented placeholder ("0 when not yet computed") that looked like data and was
    // compared by nothing. The function existed but was never called. It is now the sharpest
    // bend times the curve's size, and null past 1e6 where a cusp's polyline number would be
    // the sampling, not the curve.
    const rows: any[] = readJson("workbench/curve-analysis.json").curves;
    const values = rows.map((row) => row.maxCurvature);
    const numeric = values.filter((value) => typeof value === "number");
    assert.ok(numeric.length > Math.floor((values.length * 3) / 4),
      "most curves must have a reading");
    const distinct = new Set(numeric.map((value) => roundHalfEven(value, 3)));
    assert.ok(distinct.size > 50, "a constant placeholder has one value, not fifty");
  });
});

describe("DataReadmeCountsTest", () => {
  test("test_the_row_counts_in_the_data_readme_are_the_files_own", () => {
    // 2026-11-23: four headings in `data/README.md` were stale — curves.json said 272 rows
    // when it held 403, metrics.json 262 when it held 403. A count in a table is read as a
    // fact, so it is checked against the file.
    const text = read("data/README.md");
    let checked = 0;
    for (const match of text.matchAll(/### `([^`]+)` — ([\d,]+) rows/g)) {
      const name = match[1];
      const stated = Number(match[2].replace(/,/g, ""));
      const rel = path.join("data", name);
      if (!existsSync(path.join(ROOT, rel))) continue;
      const data = readJson(rel);
      const rows = [data.curves, data.candidates, data.rows].find(pythonTruthy) ?? [];
      if (!Array.isArray(rows) || rows.length === 0) continue;
      assert.equal(stated, rows.length, `data/README.md says ${name} has ${stated} rows`);
      checked += 1;
    }
    assert.ok(checked >= 4, "the counts stopped being readable");
  });
});

describe("RenderLockTest", () => {
  test("test_two_renders_never_write_the_index_at_once", () => {
    // 2026-11-23: the save renders in a detached child, so two quick saves can overlap and
    // each would merge the same index from a stale read — the fault register 29 records. The
    // lock directory serialises them; this runs the node test that holds two jobs open.
    nodeTest("tests/js/render-lock.test.mjs");
  });
});

describe("RootLabTest", () => {
  test("test_the_second_pair_and_the_x_row_keep_the_curve_symmetric", () => {
    // 2026-11-23, from the TODO: the root lab "needs a second pair and a variable x row
    // before it can find anything". The test pins the maths: v is anti-symmetric about t = ½
    // and u symmetric, so the curve mirrors about x = x(1)/2; a second pair adds two roots to
    // v and none to u; B = 0 still mirrors.
    nodeTest("tests/js/root-lab.test.mjs");
  });
});

describe("TrimCurveTest", () => {
  test("test_a_leg_cut_keeps_the_stations_between_the_fractions", () => {
    // The operator, 2026-11-24: "cutting the legs off the curves using rational fractions of
    // t". t = 0 is the first station, t = 1 the last; a cut given as p/q keeps the stations
    // between the two cuts, drops the legs, and puts the two cut points exactly on the
    // fractions. A decimal is refused on purpose.
    nodeTest("tests/js/trim-curve.test.ts");
  });
});

describe("DevServerHostTest", () => {
  test("test_the_dev_server_answers_on_ipv4_loopback", () => {
    // Every browser check failed with `net::ERR_CONNECTION_REFUSED at
    // http://127.0.0.1:4321/` while `curl localhost:4321` answered: a fresh
    // `npm --prefix app run dev` bound Astro's `localhost` (IPv6 ::1) only, so
    // every documented 127.0.0.1 link and every check that uses it was refused.
    // The dev script must name the IPv4 loopback.
    const packageJson = readJson("app/package.json");
    assert.ok(packageJson.scripts.dev.includes("--host 127.0.0.1"),
      "the dev script must name the IPv4 loopback");
  });
});

describe("SideCurveOffsetTest", () => {
  test("test_the_offset_curves_are_equal_on_both_sides", () => {
    // The operator, 2026-11-21: "it looks like you just took the original curve and scaled
    // it... the offset curves should look the same on both sides of the curve, not thin on the
    // right and wide on the left... if the difference at the end is 10x 10y, then move the
    // starting position by 5 x and 5 y to balance." The two sides take one strength (the
    // average of plus and minus); the profile is zero at both ends, so the start and end gaps
    // are equal. The next session moves the curve's starting point where they are not.
    nodeTest("tests/js/plate-offset.test.mjs");
  });
});
