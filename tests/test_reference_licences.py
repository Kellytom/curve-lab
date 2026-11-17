"""Every tracked reference image names its source and licence.

The public tree is the point: an image without a licence record is the one thing
that cannot be fixed after publishing. The manifests are the record; this test
fails when an image is added without one.
"""

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg")
MANIFESTS = ("reference/manifest.json", "reference/fleur/svg/manifest.json")


def records():
    covered = {}
    for manifest in MANIFESTS:
        path = ROOT / manifest
        if not path.exists():
            continue
        for row in json.loads(path.read_text(encoding="utf-8")):
            name = (row.get("file") or "").replace("reference/", "")
            if name:
                covered[name] = row
    return covered


class ReferenceLicenceTest(unittest.TestCase):
    def test_every_tracked_image_has_a_licence_record(self):
        tracked = subprocess.run(["git", "ls-files", "reference"],
                                 cwd=ROOT, capture_output=True, text=True).stdout.split()
        images = [name.replace("reference/", "") for name in tracked
                  if name.lower().endswith(IMAGE_SUFFIXES)]
        self.assertTrue(images, "no tracked reference images found")
        covered = records()
        missing = [name for name in images if name not in covered]
        self.assertEqual([], missing, f"no licence record for: {missing}")

    def test_every_record_states_a_licence_and_a_page(self):
        for name, row in records().items():
            self.assertTrue(row.get("licence"), f"{name}: no licence")
            self.assertTrue(row.get("page"), f"{name}: no source page")


if __name__ == "__main__":
    unittest.main()
