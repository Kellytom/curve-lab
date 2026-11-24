"""Fixed bugs, each with the check that keeps it fixed.

A bug that was fixed once and is discovered again is a process failure, not bad
luck. Every user-visible fault that took real work to fix gets a test here, named
after the fault, and a row in `state/REGRESSIONS-int.md`. The rule: fix and test
land in the same commit, and nothing in here is deleted because a change made it
awkward — an awkward test is the point.

These checks read the generators and the built pages rather than driving a
browser, so they run in the fast suite. Browser-level proof lives in
`scripts/check-nth-page.mjs` and `scripts/phase1_checks` style gates.
"""

import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import curve_records as R  # noqa: E402

PANELS = ROOT / "scripts" / "ph_nth_panels.js"
TEMPLATE = ROOT / "scripts" / "ph_nth_sandbox.py"
EXP = ROOT / "scripts" / "ph_nth_sandbox_exp.py"
FOUND = ROOT / "workbench" / "found-curves.json"
PAGE2 = ROOT / "workbench" / "ph-nth-sandbox-2.html"


class TestRegressions(unittest.TestCase):
    def test_the_half_power_boxes_are_never_removed_by_the_starter(self):
        """2026-11-14: the default curve loading at step 1 deleted every 1/2 box."""
        source = EXP.read_text()
        start = source.index("starter = (")
        starter = source[start:source.index("</body></html>", start)]
        self.assertIn("step.value = '0.5'", starter)
        self.assertNotIn("step.value = '1'", starter)

    def test_a_power_lands_in_its_own_box_not_the_next_one(self):
        """2026-11-14: rows were written straight in, so a whole-power curve at
        step 1/2 sat in the half-power boxes and drew the wrong curve."""
        (x, y), refused = R.rows_for_step([R.term(0, 1, -8), R.term(1, 0, 129), R.term(2, 0, -663)], 0.5)
        self.assertEqual(refused, [])
        self.assertEqual(y, [-8, 0, 129, 0, -663])

    def test_stored_curves_keep_terms_and_drop_flat_rows(self):
        """2026-11-14: two sources of truth (row position and power) disagreed."""
        document = R.read(FOUND)
        self.assertEqual(R.validate(document), [])
        for curve in document["curves"]:
            self.assertNotIn("speedX", curve)
            self.assertNotIn("speedY", curve)

    def test_the_build_stamp_sits_at_the_foot_and_is_current(self):
        """2026-11-14: a stale page looked like a broken page."""
        template = TEMPLATE.read_text()
        self.assertIn('<p class="small mono" id="n-build">build __BUILD__</p>', template)
        self.assertIn("def stamped(page)", template)

    def test_every_speed_number_still_has_two_sliders(self):
        """2026-11-14: the decade slider went missing, leaving one slider per number."""
        panels = PANELS.read_text()
        self.assertIn("decade.className = \"decade\"", panels)
        self.assertIn("pair.append(number, fine, decade, flip, scales)", panels)

    def test_the_ladder_still_reaches_thirty_numbers(self):
        """2026-11-14: halving the step halved the top power until the rows doubled."""
        template = TEMPLATE.read_text()
        self.assertIn('data-speed-degree="14"', template)
        self.assertIn("degree 29", template)

    def test_an_open_gallery_cell_draws_one_curve_only(self):
        """2026-11-14: a found curve was drawn twice, thumbnail plus panel."""
        template = TEMPLATE.read_text()
        self.assertIn(".gallery figure.open>svg{display:none}", template)

    def test_the_knotlike_section_still_opens_with_the_operators_curves(self):
        """2026-11-14: position-based ordering re-shuffled the section on its own."""
        page = PAGE2.read_text()
        names = json.loads(re.search(r"window\.phNthKnots = (\[.*?\]);", page, re.S).group(1))
        self.assertEqual(names[:7], ["wave3", "knot", "bud", "knot-2", "hersheys copy",
                                     "wave-1of7-1of5-1-bow9"] + names[6:7])

    def test_the_ordering_rules_name_curves_rather_than_positions(self):
        """2026-11-14: adding one curve shifted every number and re-ordered the page."""
        source = (ROOT / "scripts" / "ph_nth_sandbox2.py").read_text()
        self.assertIn('DEMOTE = ("wave5"', source)
        self.assertIn('AFTER = "wave-1of3-2"', source)

    def test_a_fractional_step_reports_no_grid_and_no_inflection_count(self):
        """2026-11-14: the page claimed a grid that does not exist off whole powers."""
        self.assertIn("grid n/a: fractional powers", PANELS.read_text())
        self.assertIn("inflections n/a: fractional powers", PANELS.read_text())

    def test_the_readout_still_reports_knot_and_leg_shares(self):
        """2026-11-14: 'make the knot bigger' had no number to steer by."""
        self.assertIn("knot ${knotShare}% legs ${legShare}%", PANELS.read_text())

    def test_the_nudge_buttons_offer_only_whole_steps(self):
        """2026-11-14: a size of 1/3 took the grid from 3,465 to 8.7e13, because a
        third cannot be written exactly in machine arithmetic.

        Amended the same day on the operator's call: the free-text size field and
        the share-of-the-pair dial are gone, replaced by one dropdown of patterns
        and four press-buttons. A fraction cannot be typed at all now, so the
        hazard is gone by construction rather than by an offered list. The widened
        ink is refitted to whole numbers at the same degree, so it cannot move the
        grid either.
        """
        source = EXP.read_text()
        self.assertNotIn('id="n-tweak-size"', source)
        self.assertNotIn("n-tweak-divisor", source)
        for step in ('data-step="-5"', 'data-step="-1"', 'data-step="1"', 'data-step="5"'):
            with self.subTest(step=step):
                self.assertIn(step, source)
        for spread in ('<option value="3"', '<option value="8"', '<option value="13"'):
            with self.subTest(spread=spread):
                self.assertIn(spread, source)

    def test_the_flat_spots_fill_whole_power_boxes(self):
        """2026-11-14: pressing fill at step 1/2 wrote the knot into the half-power
        boxes, so the button drew a different curve from the one it named."""
        panels = PANELS.read_text()
        fill = panels[panels.index("function fillFromFlatSpots()"):]
        fill = fill[:fill.index("writeCells();")]
        self.assertIn("rowsFromTerms(terms)", fill)
        self.assertNotIn("padRow([bow.d, bow.n, -bow.n], count)", fill)

    def test_loading_a_curve_does_not_change_the_exponent_step(self):
        """2026-11-14: loading used to reset the step, silently changing the curve."""
        panels = PANELS.read_text()
        load = panels[panels.index("window.phNthLoad = item =>"):panels.index("window.phNthLoad = item =>") + 400]
        self.assertNotIn("phPowerStep = 1", load)

    def test_the_figure_index_names_every_registry_curve(self):
        """2026-11-19: "the gallery is empty" — `curve_pngs.mjs --only` wrote the
        index from the two curves it had just drawn, so 270 entries vanished.

        The script now merges; this reads the two files so a partial run cannot
        quietly shrink the gallery again.
        """
        registry = json.loads((ROOT / "workbench" / "curve-registry.json").read_text())
        index = json.loads((ROOT / "app" / "public" / "figures" / "index.json").read_text())
        wanted = {record["uid"] for record in registry["curves"]}
        indexed = {meta["uid"] for meta in index["curves"]}
        self.assertEqual(sorted(wanted - indexed), [], "registry curves with no figure")

    def test_the_plates_are_not_parallel_curves(self):
        """2026-11-20, the operator: "I CANT BELIEVE WE ARE DEALING WITH PARALLEL
        CURVE". They were right twice: the plate read a decision file that no longer
        existed, and its row builder carried a duplicate `character:` key whose second
        copy set plus and minus to 0 — a plain parallel offset — whatever the desk said.

        The law now lives in `scripts/lib/plate-row.mjs`, and its own test measures the
        two rails: the guarded side must widen along the curve, the other must not move
        much, and zero character must be the only parallel case.
        """
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not on PATH")
        run = subprocess.run(
            [node, "--test", str(ROOT / "tests" / "js" / "plate-row.test.mjs")],
            capture_output=True, text=True, cwd=ROOT,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)



class PlateGapTest(unittest.TestCase):
    """2026-11-22, the operator: "half are too thin and half are too thick ... you should
    have algorithms to figure that out already and fix it before i even see it. right?
    check the thickness".

    The preset was a fixed number, so a curve the fold guard bound drew a hairline and a
    curve it did not drew a slab. The preset is now a measured 2 % drawn gap, solved per
    run; this runs the plate-gap check over every preset curve in the registry.
    """

    def test_every_preset_plate_draws_the_target_gap(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not on PATH")
        run = subprocess.run(
            [node, "--test", str(ROOT / "tests" / "js" / "plate-gap.test.mjs")],
            capture_output=True, text=True, cwd=ROOT,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


class PlateRailCrossingTest(unittest.TestCase):
    """2026-11-23, the operator: "letting each rail cross itself at a tight turn, marking
    every crossing with a red dot, hiding the small loop as an invisible span, and recording
    the spans in book/print/rail-holes.json."

    The inside cap and the roundSpikes bevel are withdrawn, so the rail is the asked offset at
    every station and folds through itself where the curve turns tight. This runs the three
    probed curves (c-0046, c-0065, c-0273) and checks the drawn dot and the recorded span,
    not the count, which changes with the width.
    """

    def test_each_probed_curve_crosses_and_records_a_span(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not on PATH")
        run = subprocess.run(
            [node, "--test", str(ROOT / "tests" / "js" / "plate-holes.test.mjs")],
            capture_output=True, text=True, cwd=ROOT,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


class SidePillarTest(unittest.TestCase):
    """2026-11-23, found in the build, not by the operator: the side-pillar figure drew one bow
    across the page with its labels at the edges.

    The path strings are model units (x around ±150, y up); they were written into the SVG as if
    they were already SVG coordinates, so nothing was offset or flipped, and the Q control point
    ignored the pillar's axis. This runs the page's own tests: each line stays beside its axis,
    the first paint on the page puts it there, the labels sit in the empty field, and the swell
    can never make the shaft wider than its foot.
    """

    def test_each_pillar_stays_beside_its_axis(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not on PATH")
        run = subprocess.run(
            [node, "--test", str(ROOT / "tests" / "js" / "side-pillars.test.js")],
            capture_output=True, text=True, cwd=ROOT,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


class BranchDrawTest(unittest.TestCase):
    """2026-11-23: "the multi-branch records c-0416 (cruciform) and c-0418 (absx-gerono) draw as
    fragments."

    Two faults, one rule. The tune page joined c-0416's four arms with chords, and the figure
    page read them as spine + two rails and filled the jump as a blob. `PLATE.branchesOf` is the
    one rule: stored branches first, else a path splits on a jump over a quarter of its size.
    """

    def test_a_branch_record_is_drawn_as_branches(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not on PATH")
        for name in ("plate-branches.test.mjs", "figure-branches.test.mjs"):
            run = subprocess.run(
                [node, "--test", str(ROOT / "tests" / "js" / name)],
                capture_output=True, text=True, cwd=ROOT,
            )
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


class OrnamentWriterTest(unittest.TestCase):
    """2026-11-22, the operator: "i cant see how many curves to do because the page
    keeps refreshing constantly."

    The launch agent re-ran `npm run dev` every ten seconds; it failed on Node 22, but
    its `predev` step still ran the ornament writer, which deleted the folder and rewrote
    all 371 SVGs each time. The dev server watches that folder, so every open page reloaded
    on the same ten-second beat. The writer now leaves an unchanged file alone, inode and
    mtime included, and prunes only files whose curve has left the registry.
    """

    def test_an_unchanged_ornament_is_not_rewritten(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not on PATH")
        run = subprocess.run(
            [node, "--test", str(ROOT / "tests" / "js" / "write-if-changed.test.mjs")],
            capture_output=True, text=True, cwd=ROOT,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_the_ornament_writer_does_not_wipe_its_folder(self):
        source = (ROOT / "scripts" / "marginalia.mjs").read_text()
        self.assertNotIn("rmSync(OUT", source,
                         "wiping the folder rewrites every ornament and reloads every page")
        self.assertIn('from "./lib/write-if-changed.mjs"', source,
                      "the writer must use the tested write-if-changed rule")


class SpanWidthTraceTest(unittest.TestCase):
    """The desk records name their traces with the layer baked in ("ink/a") and
    carry a width; the constructor refused that combination ("a cubic span trace
    is a hairline"), so every saved desk piece was un-buildable through the
    normal model, and the rails-from-spans capability was unreachable. The
    refusal is removed; build_piece's pre-built path builds the rails and
    reports the fit error; the layer is not doubled when the name already
    carries it."""

    def test_a_span_trace_may_carry_a_width_and_build_its_rails(self):
        import json
        import subprocess
        from pathlib import Path as PathLib
        sys_path = str(PathLib(__file__).resolve().parents[1])
        program = """
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
"""
        run = subprocess.run([sys.executable, "-c", program], capture_output=True,
                             text=True, cwd=sys_path)
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)


class RepeatedAskTest(unittest.TestCase):
    def test_every_operator_ask_is_written_down_and_closed_honestly(self):
        """The operator, 2026-11-23: "i should not have to repeat myself", after asking
        for a way to save the cut curves two or three times. Each session read the code
        and fixed something adjacent, because the ask was only in the chat. The register
        is `state/ASKS-int.md`, read at Tier 0; this check fails when a row has no
        verbatim ask, a fixed row names no real commit or file, or an open row names no
        next step."""
        run = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_asks.py")],
                             capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)


class SaidRollTest(unittest.TestCase):
    def test_the_said_rolls_hold_every_message_with_proof(self):
        """The operator, 2026-11-23: "check http://127.0.0.1:4321/said/ on a regular basis and
        make a rolling checklist from it in md and then prove that you did the work and check
        it off." Both chats have a file and a roll: `data/said.json` →
        `state/SAID-CHECKLIST-int.md` for the main chat, `data/said-deep2.json` →
        `state/SAID-DEEP2-CHECKLIST-int.md` for sidechat. Each check fails when a message has
        no row, a row's words differ from the message, or a `done` row names no real commit or
        file. Local only, like the history."""
        checked = 0
        for who in ("me", "deep2"):
            said = ROOT / "data" / f"said{'' if who == 'me' else '-deep2'}.json"
            roll = ROOT / "state" / f"SAID{'' if who == 'me' else '-DEEP2'}-CHECKLIST-int.md"
            if not said.exists() or not roll.exists():
                continue
            run = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "said_checklist.py"), "--who", who],
                capture_output=True, text=True, cwd=ROOT)
            self.assertEqual(0, run.returncode, run.stdout + run.stderr)
            checked += 1
        if not checked:
            self.skipTest("the /said/ histories and their rolls are local only")


class CurveFlagsTest(unittest.TestCase):
    def test_every_curve_has_a_status_and_its_png_follows_the_flag(self):
        """The operator, 2026-11-23: "put a flag in the database for every curve that indicates
        whether its png should be git ignored... and then make sure they are", and "make sure
        even the temporary or in progress curves are in the database labeled as such". Three
        checks: every page curve is a Curve or Study row with a known status
        (`check_page_curves.mjs`), every plate and figure PNG is tracked exactly when its row
        says `pngIgnored: false` (`curve_pngs_git.mjs`), and the study rows are registered
        (`register_studies.mjs`)."""
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not on PATH")
        for script in ("register_studies.mjs", "curve_pngs_git.mjs", "check_page_curves.mjs"):
            run = subprocess.run([node, str(ROOT / "scripts" / script)],
                                 capture_output=True, text=True, cwd=ROOT)
            self.assertEqual(0, run.returncode, f"{script}:\n{run.stdout}{run.stderr}")


class GapsNamedTest(unittest.TestCase):
    def test_the_gaps_page_proposes_only_curves_that_are_actually_named(self):
        """2026-11-23, found in the build: `curve_gaps.mjs` took every `dict(key=...)` block in
        `generators.py` as a named curve, so the speed-family examples "quartic" and "sextic"
        were listed as missing classical curves for years. Only the NAMED table (blocks with an
        equation) counts."""
        import generators as G  # noqa: E402
        known = {spec["key"] for spec in G.NAMED}
        page = json.loads((ROOT / "app" / "src" / "data" / "extra-curves.json").read_text())
        for curve in page["missingNamed"]:
            self.assertIn(curve["key"], known, f"{curve['key']} is not a NAMED curve")
        for curve in page["addedOnRequest"]:
            self.assertIn(curve["uid"], {row["uid"] for row in json.loads(
                (ROOT / "workbench" / "curve-registry.json").read_text())["curves"]})


class RegistryRebuildTest(unittest.TestCase):
    def test_the_registry_rebuild_refuses_to_drop_curated_rows(self):
        """2026-11-23, from the TODO: `scripts/curve_registry.py` rebuilds and renumbers the
        registry from its sources, so it would lose the seven curated finds (c-0263..c-0269)
        and every record added by hand. It now refuses and names the difference unless
        --force; this runs the real --write and requires the file to be untouched."""
        path = ROOT / "workbench" / "curve-registry.json"
        before = path.read_bytes()
        run = subprocess.run([sys.executable, str(ROOT / "scripts" / "curve_registry.py"),
                              "--write"], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(2, run.returncode, run.stdout + run.stderr)
        self.assertIn("refusing to write", run.stdout + run.stderr)
        self.assertEqual(before, path.read_bytes(), "the registry was written anyway")


class BookPlateTest(unittest.TestCase):
    def test_every_curve_has_a_3000_px_300_dpi_plate(self):
        """book/README.md: a 3000 px long side (10 in at 300 dpi) and a 300 dpi pHYs. The check
        reads each PNG header; a curve with no plate, a short plate or a plate without the dpi
        fails, because the book is drawn from all of them."""
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not on PATH")
        run = subprocess.run([node, str(ROOT / "scripts" / "check_book_plates.mjs")],
                             capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)


class MaxCurvatureTest(unittest.TestCase):
    def test_the_sharpest_bend_is_computed_and_not_a_placeholder(self):
        """2026-11-23, found in the build: `maxCurvature` read 0.0 on all 403 curves — a
        documented placeholder ("0 when not yet computed") that looked like data and was
        compared by nothing. The function existed but was never called. It is now the sharpest
        bend times the curve's size, and null past 1e6 where a cusp's polyline number would be
        the sampling, not the curve."""
        rows = json.loads((ROOT / "workbench" / "curve-analysis.json").read_text())["curves"]
        values = [row.get("maxCurvature") for row in rows]
        numeric = [value for value in values if isinstance(value, (int, float))]
        self.assertGreater(len(numeric), len(values) * 3 // 4, "most curves must have a reading")
        self.assertGreater(len({round(value, 3) for value in numeric}), 50,
                           "a constant placeholder has one value, not fifty")


class DataReadmeCountsTest(unittest.TestCase):
    def test_the_row_counts_in_the_data_readme_are_the_files_own(self):
        """2026-11-23: four headings in `data/README.md` were stale — curves.json said 272 rows
        when it held 403, metrics.json 262 when it held 403. A count in a table is read as a
        fact, so it is checked against the file."""
        import re
        text = (ROOT / "data" / "README.md").read_text()
        checked = 0
        for match in re.finditer(r"### `([^`]+)` — ([\d,]+) rows", text):
            name = match.group(1)
            stated = int(match.group(2).replace(",", ""))
            path = ROOT / "data" / name
            if not path.exists():
                continue
            data = json.loads(path.read_text())
            rows = data.get("curves") or data.get("candidates") or data.get("rows") or []
            if not isinstance(rows, list) or not rows:
                continue
            self.assertEqual(stated, len(rows), f"data/README.md says {name} has {stated} rows")
            checked += 1
        self.assertGreaterEqual(checked, 4, "the counts stopped being readable")


class RenderLockTest(unittest.TestCase):
    def test_two_renders_never_write_the_index_at_once(self):
        """2026-11-23: the save renders in a detached child, so two quick saves can overlap and
        each would merge the same index from a stale read — the fault register 29 records. The
        lock directory serialises them; this runs the node test that holds two jobs open."""
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not on PATH")
        run = subprocess.run(
            [node, "--test", str(ROOT / "tests" / "js" / "render-lock.test.mjs")],
            capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)


class RootLabTest(unittest.TestCase):
    def test_the_second_pair_and_the_x_row_keep_the_curve_symmetric(self):
        """2026-11-23, from the TODO: the root lab "needs a second pair and a variable x row
        before it can find anything". The test pins the maths: v is anti-symmetric about t = ½
        and u symmetric, so the curve mirrors about x = x(1)/2; a second pair adds two roots to
        v and none to u; B = 0 still mirrors."""
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not on PATH")
        run = subprocess.run(
            [node, "--test", str(ROOT / "tests" / "js" / "root-lab.test.mjs")],
            capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)


class TrimCurveTest(unittest.TestCase):
    def test_a_leg_cut_keeps_the_stations_between_the_fractions(self):
        """The operator, 2026-11-24: "cutting the legs off the curves using rational fractions of
        t". t = 0 is the first station, t = 1 the last; a cut given as p/q keeps the stations
        between the two cuts, drops the legs, and puts the two cut points exactly on the
        fractions. A decimal is refused on purpose."""
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not on PATH")
        run = subprocess.run(
            [node, "--test", str(ROOT / "tests" / "js" / "trim-curve.test.ts")],
            capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)


class DevServerHostTest(unittest.TestCase):
    def test_the_dev_server_answers_on_ipv4_loopback(self):
        """Every browser check failed with `net::ERR_CONNECTION_REFUSED at
        http://127.0.0.1:4321/` while `curl localhost:4321` answered: a fresh
        `npm --prefix app run dev` bound Astro's `localhost` (IPv6 ::1) only, so
        every documented 127.0.0.1 link and every check that uses it was refused.
        The dev script must name the IPv4 loopback."""
        package = json.loads((ROOT / "app" / "package.json").read_text())
        self.assertIn("--host 127.0.0.1", package["scripts"]["dev"])


class SideCurveOffsetTest(unittest.TestCase):
    def test_the_offset_curves_are_equal_on_both_sides(self):
        """The operator, 2026-11-21: "it looks like you just took the original curve and scaled
        it... the offset curves should look the same on both sides of the curve, not thin on the
        right and wide on the left... if the difference at the end is 10x 10y, then move the
        starting position by 5 x and 5 y to balance." The two sides take one strength (the
        average of plus and minus); the profile is zero at both ends, so the start and end gaps
        are equal. The next session moves the curve's starting point where they are not."""
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not on PATH")
        run = subprocess.run(
            [node, "--test", str(ROOT / "tests" / "js" / "plate-offset.test.mjs")],
            capture_output=True, text=True, cwd=ROOT,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
