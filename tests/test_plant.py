import math
import unittest

from curve_lab import plant as P


class PlantGeometryTest(unittest.TestCase):
    def test_cone_terminal(self):
        c = P.cone_terminal((0.0, 0.0), (0.0, 1.0), 0.5)
        self.assertAlmostEqual(c["radius"], 1.0)
        self.assertAlmostEqual(c["extension"], math.sqrt(3.0) * 0.5)
        self.assertAlmostEqual(c["tip"][0], 0.0)
        self.assertAlmostEqual(c["tip"][1], math.sqrt(3.0) * 0.5)
        a, b = c["rails"]
        self.assertAlmostEqual(a[0], -0.5)
        self.assertAlmostEqual(b[0], 0.5)
        self.assertAlmostEqual(c["left"][0][0], a[0], places=9)
        self.assertAlmostEqual(c["left"][0][1], a[1], places=9)
        self.assertAlmostEqual(c["right"][0][0], b[0], places=9)
        self.assertAlmostEqual(c["left"][-1][0], c["tip"][0], places=9)
        self.assertAlmostEqual(c["left"][-1][1], c["tip"][1], places=9)
        self.assertAlmostEqual(c["right"][-1][0], c["tip"][0], places=9)

    def test_seagrass_and_flower(self):
        blades = P.seagrass((0.0, 0.0), (0.0, 1.0), 0.5)
        self.assertEqual(len(blades), 3)
        for blade in blades:
            self.assertGreater(len(blade), 8)
        flower = P.flower((0.0, 0.0), (0.0, 1.0), 0.5)
        self.assertGreater(len(flower), 50)
        self.assertAlmostEqual(flower[0][0], flower[-1][0], places=9)
        self.assertAlmostEqual(flower[0][1], flower[-1][1], places=9)

    def test_lattice_hits_and_pyramid(self):
        line = [(0.0, float(i)) for i in range(5)]
        hits = P.lattice_hits(line, 1.0)
        self.assertEqual([h["value"] for h in hits], [0.0, 1.0, 2.0, 3.0, 4.0])
        tri = P.pyramid((0.0, 2.0), (0.0, 1.0), (-1.0, 0.0), (0.2, 0.4))
        self.assertEqual(len(tri), 3)
        self.assertLess(tri[0][1], 2.0)
        self.assertGreater(tri[1][1], 2.0)
        self.assertLess(tri[2][0], 0.0)


if __name__ == "__main__":
    unittest.main()
