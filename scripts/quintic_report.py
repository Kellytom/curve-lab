#!/usr/bin/env python3
"""Quintic from Guide: the numbers the docs quote, computed here.

Two jobs:

  python scripts/quintic_report.py
      the table of cubic counts against measured miss, on two cages of known
      size, plus how long the fit takes. This is what `docs/QUINTIC-GUIDE.md`
      quotes; if the table and the doc disagree, the doc is wrong.

  python scripts/quintic_report.py --sheet workbench/quintic-guides
      run the INSTALLED extension over every .svg in that folder and print one
      row per curve, read back from the sidecar JSON the extension wrote. That
      is the end-to-end check: the numbers come from Inkscape's own Python,
      through the files the operator installs.

Run it with `.venv/bin/python` for the table (plain stdlib), or any Python 3
for `--sheet` (it shells out to Inkscape's bundled interpreter).
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inkscape import quintic_math as qm  # noqa: E402

WILD = [(20, 180), (160, 60), (260, 170), (360, 40), (390, 110), (320, 240)]
GENTLE = [(0, 100), (50, 60), (100, 50), (150, 50), (200, 60), (250, 100)]

WILD_SEGMENTS = [
    ((20, 180), (60, 80), (110, 20), (160, 60)),
    ((160, 60), (200, 90), (220, 180), (260, 170)),
    ((260, 170), (300, 160), (330, 90), (360, 40)),
    ((360, 40), (380, 10), (395, 60), (390, 110)),
    ((390, 110), (385, 160), (350, 200), (320, 240)),
]
FREEHAND_SEGMENTS = [
    ((20, 150), (40, 110), (70, 90), (100, 95)),
    ((100, 95), (130, 100), (150, 130), (180, 135)),
    ((180, 135), (210, 140), (230, 110), (260, 105)),
    ((260, 105), (290, 100), (310, 130), (340, 125)),
    ((340, 125), (370, 120), (390, 90), (410, 80)),
]

INSKAPE_PY = "/Applications/Inkscape.app/Contents/Resources/bin/python3"
INSKAPE_EXT = "/Applications/Inkscape.app/Contents/Resources/share/inkscape/extensions"
USER_EXT = Path.home() / "Library/Application Support/org.inkscape.Inkscape/config/inkscape/extensions"


def table():
    print("cubics | wild cage (400 px wide) | gentle cage (250 px wide)")
    print("-------|------------------------|------------------------")
    for segments in (2, 3, 4, 6, 8, 12, 16, 32):
        wild = qm.measure_max_error(WILD, qm.cubic_chain(WILD, segments))
        gentle = qm.measure_max_error(GENTLE, qm.cubic_chain(GENTLE, segments))
        print("%6d | %20.7f px | %20.7f px" % (segments, wild, gentle))
    print()
    print("fit to a tolerance (the extension's default, segments = 0):")
    for tol in (0.05, 0.01, 0.001):
        for name, cage in (("wild", WILD), ("gentle", GENTLE)):
            start = time.time()
            chain, err, used = qm.fit_to_tolerance(cage, tol)
            took = (time.time() - start) * 1000.0
            print("  %-6s tol %-6.3f -> %2d cubics, miss %.7f px, %4.0f ms"
                  % (name, tol, used, err, took))
    print()
    print("overshoot, interpolation through six points (unclamped):")
    for name, cage in (("wild", WILD), ("gentle", GENTLE)):
        control = qm.solve_through_samples(cage)
        print("  %-6s sticks out of the six points by %8.2f px"
              % (name, qm.overshoot(control, cage)))


def spans_table(dense_per_span=60):
    """The middle layer: how far the six-point curve is from the drawn stroke.

    Every figure here is drawn -> quintic, in px, on a dense arc-length sample of
    the stroke that is embedded in this file, so the extension is not needed.
    """
    print("stroke | mode | spans | drawn->quintic max | rms")
    print("---|---|---|---")
    for name, segments in (("wild 400 px", WILD_SEGMENTS),
                           ("freehand-like", FREEHAND_SEGMENTS)):
        for mode in ("even", "lsq"):
            for spans in (1, 2, 3, 4, 6):
                count = dense_per_span * spans
                dense = qm.samples_along(segments, [i / count for i in range(count + 1)])
                chunks = qm.split_samples(dense, spans)
                worst = 0.0
                rms_sum = 0.0
                for chunk in chunks:
                    control = (qm.fit_least_squares(chunk) if mode == "lsq"
                               else qm.solve_through_samples(qm.six_points_even(chunk)))
                    got_max, got_rms = qm.fit_report(control, chunk)
                    worst = max(worst, got_max)
                    rms_sum += got_rms * got_rms
                print("%s | %s | %d | %.3f px | %.3f px"
                      % (name, mode, spans, worst, (rms_sum / len(chunks)) ** 0.5))
    print()


def sheet(folder, mode="even", spans=1):
    """Run the installed extension over a folder and print one row per guide.

    Reads the CONTRACT file the extension writes (`curve-lab.quintic/1`), so the
    numbers come from the same artifact the other desk reads.
    """
    folder = Path(folder).expanduser()
    svgs = sorted(folder.glob("*.svg"))
    if not svgs:
        print("no .svg in %s" % folder)
        return 1
    print("| file | spans | cubics | drawn->quintic max | rms | proved bound | box |")
    print("|---|---|---|---|---|---|---|")
    worst = 0.0
    for svg in svgs:
        guide_id = None
        for el in ET.parse(str(svg)).iter():
            if el.tag.endswith("path") and el.get("id"):
                guide_id = el.get("id")
                break
        if guide_id is None:
            print("| %s | n/a | | | | | no path with an id |" % svg.name)
            continue
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, PYTHONPATH=INSKAPE_EXT,
                       CURVE_LAB_ROOT=str(ROOT))
            cmd = [INSKAPE_PY, str(USER_EXT / "quintic_guide.py"),
                   "--pointmode=" + mode, "--fullness=1", "--segments=0",
                   "--tolerance=0.01", "--spans=%d" % spans, "--id=" + guide_id,
                   "--keepguide=true", "--showpoints=false",
                   "--exportdir=" + tmp, "--clipboard=false", str(svg)]
            done = subprocess.run(cmd, env=env, capture_output=True, text=True)
            contract = next(Path(tmp).glob("*-quintic.json"), None)
            numbers = next(Path(tmp).glob("*-report.json"), None)
            if contract is None or numbers is None:
                lines = [l for l in done.stderr.strip().splitlines()
                         if "Quintic from Guide" in l and "wrote" not in l]
                first = (lines or ["no contract file written"])[-1]
                print("| %s | FAILED | | | | | %s |" % (svg.name, first))
                continue
            doc = json.loads(contract.read_text())
            rep = json.loads(numbers.read_text())
        spans_in = rep["spans"]
        cubics = sum(s["cubic_segments"] for s in spans_in)
        fit_max = max(s["drawn_to_quintic_max_px"] for s in spans_in)
        fit_rms = max(s["drawn_to_quintic_rms_px"] for s in spans_in)
        bound = max(s["quintic_to_chain_proved_bound_px"] for s in spans_in)
        box = "clamped" if any(s["clamped"] for s in spans_in) else (
            "overshoot" if any(s["overshoot_px"] > 0 for s in spans_in) else "inside")
        worst = max(worst, fit_max)
        print("| %s | %d | %d | %.3f px | %.3f px | %.5f px | %s |"
              % (svg.name, len(doc["curves"][0]["spans"]), cubics, fit_max, fit_rms,
                 bound, box))
    print()
    print("worst drawn->quintic miss over the sheet: %.3f px" % worst)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sheet", help="folder of .svg guides to run the installed extension over")
    ap.add_argument("--mode", default="even", choices=("even", "lsq", "cage-nodes", "cage-samples"))
    ap.add_argument("--spans", type=int, default=1)
    args = ap.parse_args()
    if args.sheet:
        return sheet(args.sheet, args.mode, args.spans)
    table()
    spans_table()
    return 0


if __name__ == "__main__":
    sys.exit(main())
