"""Guards the integer-cubic catalogue: counts, controls, signs, rotations."""

import unittest
from pathlib import Path

from curve_lab.pyth_cubic import (catalogue, catalogue_c, case, checks,
                                  interior_angle, representatives)
from curve_lab.pyth_triples import base_triples


class IntegerCubicCatalogueTest(unittest.TestCase):
    def setUp(self):
        self.rows = catalogue(1000)
        self.prims = [t for t in base_triples(1000) if t["k"] == 1]

    def test_counts_follow_the_triples(self):
        self.assertEqual(len(self.prims), 158)
        self.assertEqual(len(self.rows), 2 * len(self.prims))
        self.assertEqual(len(self.rows), 316)

    def test_every_row_is_integer_and_checked(self):
        for row in self.rows:
            self.assertTrue(checks(row), row["label"])
            self.assertEqual(row["chord"], 2 * row["c"])
            self.assertEqual(row["arm"], row["c"])
            for p in (row["p0"], row["p1"], row["p2"], row["p3"],
                      row["mirror_p1"], row["mirror_p2"], row["mirror_p3"],
                      *row["rotation_points"]):
                self.assertIsInstance(p[0], int, row["label"])
                self.assertIsInstance(p[1], int, row["label"])

    def test_the_3_4_5_rows(self):
        ab = next(r for r in self.rows
                  if r["label"] == "3-4-5" and r["order"] == "ab")
        self.assertEqual(ab["p1"], (3, -4))
        self.assertEqual(ab["p2"], (7, 4))
        self.assertEqual(ab["mirror_p1"], (3, 4))
        self.assertEqual(ab["rotation_points"][1], (25, 0))
        ba = next(r for r in self.rows
                  if r["label"] == "4-3-5" and r["order"] == "ba")
        self.assertEqual(ba["p1"], (4, -3))

    def test_the_c_cubics(self):
        rows = catalogue_c(1000)
        self.assertEqual(len(rows), 316)
        base = next(r for r in rows if r["label"] == "3-4-5 C"
                    and r["order"] == "ab")
        self.assertEqual(base["p1"], (3, 4))
        self.assertEqual(base["p2"], (7, 4))
        self.assertEqual(base["height"], 4)
        page = (Path(__file__).resolve().parents[1] / "workbench" /
                "integer-cubic-catalogue.html").read_text(encoding="utf-8")
        self.assertIn("The C cubics · 316", page)

    def test_the_page_states_the_counts(self):
        page = (Path(__file__).resolve().parents[1] / "workbench" /
                "integer-cubic-catalogue.html").read_text(encoding="utf-8")
        self.assertIn("158", page)
        self.assertIn("316", page)
        self.assertIn("632", page)
        self.assertIn("3-4-5", page)
        self.assertIn("Infinity:", page)
        self.assertEqual(page.count('<figure class="card">'), 26)


    def test_the_ladder_is_eleven_s_and_ten_c(self):
        reps = representatives()
        self.assertEqual(len(reps["s"]), 11)
        self.assertEqual(len(reps["c"]), 10)
        for rows, bins, val in (
                (reps["s"], reps["s_bins"], interior_angle),
                (reps["c"], reps["c_bins"],
                 lambda r: r["height"] / r["chord"])):
            for row, (lo, hi) in zip(rows, bins):
                self.assertGreaterEqual(val(row), lo)
                self.assertLessEqual(val(row), hi)
            self.assertEqual([lo for lo, _ in bins], sorted(lo for lo, _ in bins))

    def test_each_representative_is_the_smallest_c_in_its_bin(self):
        reps = representatives()
        families = (
            (reps["s"], reps["s_bins"], catalogue(reps["c_max"]),
             interior_angle),
            (reps["c"], reps["c_bins"], catalogue_c(reps["c_max"]),
             lambda r: r["height"] / r["chord"]),
        )
        for rows, bins, pool, val in families:
            for row, (lo, hi) in zip(rows, bins):
                inside = [r for r in pool if lo <= val(r) <= hi]
                self.assertTrue(inside)
                self.assertEqual(min(r["c"] for r in inside), row["c"])
                self.assertIn(row, inside)

    def test_the_showcase_is_the_ladder(self):
        page = (Path(__file__).resolve().parents[1] / "workbench" /
                "showcase.html").read_text(encoding="utf-8")
        self.assertIn("The integer cubics · 11", page)
        self.assertIn("The integer C cubics · 10", page)
        self.assertNotIn("The integer cubics · 316", page)
        self.assertEqual(page.count('class="fig"'), 395)


class ShowcaseOrderTest(unittest.TestCase):
    def test_the_cubics_run_shallow_to_sharp(self):
        import sys
        sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "scripts"))
        import showcase_catalogue as C
        rows = C.cubic_rows()
        self.assertEqual(len(rows), 11)
        turns = [C._cubic_turn(r) for r in rows]
        self.assertEqual(turns, sorted(turns))
        self.assertAlmostEqual(180.0 - turns[0], 85.601, 3)
        self.assertAlmostEqual(180.0 - turns[-1], 49.399, 3)

    def test_the_stem_library_is_on_the_page(self):
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
        import showcase_catalogue as C
        self.assertEqual(len(C.stem_panels()), 178)
        page = (Path(__file__).resolve().parents[1] / "workbench" /
                "showcase.html").read_text(encoding="utf-8")
        self.assertIn("The stem library · 178", page)
        self.assertIn("S01 ·", page)
        self.assertIn("SM1 ·", page)


if __name__ == "__main__":
    unittest.main()
