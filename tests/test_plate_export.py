"""Guards the book plates: names, tight crop, white ground, no text, 300 dpi."""

import json
import re
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import plate_curves  # noqa: E402
from png_dpi import read_dpi  # noqa: E402

BOOK = ROOT / "book"
NAME = re.compile(r"^([a-z0-9][a-z0-9-]*)-([0-9]+)-t-exp-c-([0-9]{4})$")


def png_size(path):
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise AssertionError(f"{path} is not a PNG")
    return struct.unpack(">II", data[16:24])


class BookPlateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((BOOK / "plates.json").read_text())
        cls.plates = cls.manifest["plates"]
        cls.gallery = (BOOK / "index.html").read_text(encoding="utf-8")

    def test_every_name_is_descriptor_variant_marker_serial(self):
        serials = set()
        for plate in self.plates:
            match = NAME.match(plate["id"])
            self.assertIsNotNone(match, plate["id"])
            descriptor, variant, serial = match.groups()
            self.assertEqual(descriptor, plate["descriptor"])
            self.assertEqual(int(variant), int(plate["variant"]))
            self.assertNotIn(serial, serials)
            serials.add(serial)

    def test_every_plate_has_a_svg_and_a_png_at_the_declared_size(self):
        long_side = self.manifest["longSide"]
        for plate in self.plates:
            svg = (BOOK / "svg" / f"{plate['id']}.svg").read_text()
            png = BOOK / "plates" / f"{plate['id']}.png"
            self.assertTrue(png.exists(), plate["id"])
            width = int(re.search(r'width="(\d+)"', svg).group(1))
            height = int(re.search(r'height="(\d+)"', svg).group(1))
            self.assertEqual(max(width, height), long_side)
            self.assertEqual(png_size(png), (width, height))

    def test_the_image_is_white_and_carries_no_text(self):
        for plate in self.plates:
            svg = (BOOK / "svg" / f"{plate['id']}.svg").read_text()
            self.assertIn('fill="#ffffff"', svg)
            self.assertNotIn("<text", svg)
            self.assertNotIn("<title", svg)

    def test_the_curve_fills_the_frame_and_is_not_clipped(self):
        margin = round(0.012 * self.manifest["longSide"])
        for plate in self.plates:
            svg = (BOOK / "svg" / f"{plate['id']}.svg").read_text()
            width = int(re.search(r'width="(\d+)"', svg).group(1))
            height = int(re.search(r'height="(\d+)"', svg).group(1))
            xs, ys = [], []
            for points in re.findall(r'points="([^"]+)"', svg):
                for pair in points.split():
                    x, y = pair.split(",")
                    xs.append(float(x))
                    ys.append(float(y))
            self.assertGreaterEqual(min(xs), margin - 1.5, plate["id"])
            self.assertGreaterEqual(min(ys), margin - 1.5, plate["id"])
            self.assertLessEqual(max(xs), width - margin + 1.5, plate["id"])
            self.assertLessEqual(max(ys), height - margin + 1.5, plate["id"])
            fill_x = (max(xs) - min(xs)) / (width - 2 * margin)
            fill_y = (max(ys) - min(ys)) / (height - 2 * margin)
            self.assertGreater(max(fill_x, fill_y), 0.99, plate["id"])

    def test_every_png_carries_300_dpi(self):
        for plate in self.plates:
            png = BOOK / "plates" / f"{plate['id']}.png"
            self.assertEqual(read_dpi(png), 300, plate["id"])

    def test_the_gallery_is_plain(self):
        self.assertNotIn("<input", self.gallery.lower())
        self.assertNotIn("<form", self.gallery.lower())
        self.assertEqual(self.gallery.count("<img "), len(self.plates))
        for plate in self.plates:
            self.assertIn(plate["id"], self.gallery)
            self.assertIn(f'src="plates/{plate["id"]}.png"', self.gallery)

    def test_the_curves_are_the_saved_set(self):
        data = json.loads((ROOT / "workbench" / "real-curves.json").read_text())
        names = {row["name"] for row in data["curves"]}
        ids = {plate["id"] for plate in self.plates}
        for plate in self.plates:
            self.assertEqual(plate["kind"], "seed")
            self.assertIn(plate["name"], names)
        for retired in ("swan-1-t-exp-c-0001", "sweep-1-t-exp-c-0002"):
            self.assertNotIn(retired, ids)

    def test_no_rail_folds(self):
        for plate in self.plates:
            data = plate_curves.load(plate)
            if data["rails"]:
                self.assertLess(data["fold"], 0.9, plate["id"])
                self.assertIn("character rails", data["note"])
            else:
                self.assertIn("spine only", data["note"], plate["id"])


if __name__ == "__main__":
    unittest.main()
