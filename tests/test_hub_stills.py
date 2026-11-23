"""The hub's stills are as new as the pages they show.

The hub opens each window as a screenshot and loads the live page when reached. A still that
shows an older look is a wrong picture, and nothing on the page can tell. This fails when a
still is missing, or older than the source that draws its page.

Refresh the stills with `node scripts/hub_shots.mjs` (the app must be on 127.0.0.1:4321).

The source list is short on purpose: the four app pages the hub shows, the shared header and
shell, and the two scripts that do their drawing. It is a staleness alarm, not a build graph.
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STILLS = ROOT / "app" / "public" / "hub"
WINDOWS = ["lab", "book", "ph-nth-sandbox", "finder"]
SOURCES = [
    "app/src/pages/lab.astro",
    "app/src/pages/book.astro",
    "app/src/pages/ph-nth-sandbox.astro",
    "app/src/pages/finder.astro",
    "app/src/components/AppNav.astro",
    "app/public/vendor/app-shell.css",
    "app/src/scripts/lab.js",
    "app/src/scripts/finder.js",
]
# a second of slack: a still written in the same second as the source is not stale
SLACK = 1.0


class HubStillsTest(unittest.TestCase):
    def test_every_window_has_a_still(self):
        for key in WINDOWS:
            file = STILLS / f"{key}.png"
            self.assertTrue(file.is_file(), f"{key}.png is missing — run node scripts/hub_shots.mjs")
            self.assertGreater(file.stat().st_size, 10_000, f"{key}.png is too small to be a page")

    def test_the_stills_are_not_older_than_the_page_sources(self):
        newest = max(
            (ROOT / name).stat().st_mtime for name in SOURCES if (ROOT / name).is_file())
        stale = [
            key for key in WINDOWS
            if not (STILLS / f"{key}.png").is_file()
            or (STILLS / f"{key}.png").stat().st_mtime + SLACK < newest
        ]
        self.assertEqual(stale, [],
                         f"stale stills: {stale} — run node scripts/hub_shots.mjs")


if __name__ == "__main__":
    unittest.main()
