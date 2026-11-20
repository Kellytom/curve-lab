"""A spec page must match the markdown it was generated from.

The fault this guards (2026-11-19): the operator asked where the HTML for
`state/SPEC-prime-mover-int.md` was, and it was an hour stale, because nothing rebuilds
the pages when the markdown changes. Each generated page now carries the hash of its
source, so a stale page fails here instead of being discovered by eye.
"""

import hashlib
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = ROOT / "app" / "public" / "spec"
SOURCES = [
    ROOT / "state" / "SPEC-prime-mover-int.md",
    ROOT / "state" / "SPEC-css-int.md",
    ROOT / "state" / "SPEC-stage-two-int.md",
    ROOT / "state" / "PROBLEMS-prime-mover-int.md",
    ROOT / "state" / "PROBLEMS-css-int.md",
    ROOT / "state" / "PROBLEMS-stage-two-int.md",
    ROOT / "state" / "NOTES-prime-mover-gaussian.md",
]


def slug(path: Path) -> str:
    """The generator's own rule: SPEC-x-int -> x.html, PROBLEMS-x-int -> x-problems.html."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("spec_page", ROOT / "scripts" / "spec_page.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.slug(path)


class SpecPages(unittest.TestCase):
    def test_every_generated_page_matches_its_source(self):
        missing = []
        stale = []
        for source in SOURCES:
            page = SPEC_DIR / f"{slug(source)}.html"
            if not page.exists():
                missing.append(page.name)
                continue
            text = source.read_text(encoding="utf-8")
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            found = re.search(r'name="spec-source-hash" content="([a-f0-9]+)"', page.read_text())
            if not found or found.group(1) != digest:
                stale.append(page.name)
        self.assertEqual(missing, [], "spec pages missing: run scripts/spec_page.py --all")
        self.assertEqual(stale, [], "spec pages stale: run scripts/spec_page.py --all")


if __name__ == "__main__":
    unittest.main()
