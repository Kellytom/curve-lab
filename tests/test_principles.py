import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = json.loads((ROOT / "reference" / "principles.json").read_text())
MANIFEST = json.loads((ROOT / "reference" / "manifest.json").read_text())


class TestCards(unittest.TestCase):
    def test_every_card_is_complete(self):
        self.assertEqual(len(CARDS), 8)
        ids = [c["id"] for c in CARDS]
        self.assertEqual(len(ids), len(set(ids)))
        for card in CARDS:
            self.assertIn(card["class"], {"primal", "archetype"})
            self.assertGreater(len(card["gesture"].split()), 20, card["id"])
            self.assertEqual(len(card["numbers"]), 3, card["id"])
            self.assertGreaterEqual(len(card["not_this"]), 2, card["id"])

    def test_primal_ids_are_the_four(self):
        primal = {c["id"] for c in CARDS if c["class"] == "primal"}
        self.assertEqual(primal, {"earth", "water", "air", "fire"})

    def test_every_card_has_a_real_reference(self):
        subjects = {row["subject"] for row in MANIFEST}
        for card in CARDS:
            self.assertIn(card["id"], subjects)
            files = [row["file"] for row in MANIFEST if row["subject"] == card["id"]]
            self.assertGreaterEqual(len(files), 1)
            for name in files:
                path = ROOT / "reference" / name
                self.assertTrue(path.is_file(), name)
                self.assertGreater(path.stat().st_size, 1000, name)

    def test_page_matches_the_cards(self):
        page = (ROOT / "docs" / "principles.html").read_text()
        for card in CARDS:
            self.assertIn(card["name"], page)
            self.assertIn(card["gesture"], page)


if __name__ == "__main__":
    unittest.main()
