"""Keep the counts block in the G3 showcase document true.

    .venv/bin/python scripts/g3_showcase_doc.py --check
    .venv/bin/python scripts/g3_showcase_doc.py

The page is Starlight content now; this script does not build HTML. It reads the
catalogue and the showcase page, and rewrites the counts table between the
`counts` markers, or fails when it is stale.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import g3_showcase as S  # noqa: E402

MD = ROOT / "app" / "src" / "content" / "docs" / "docs" / "g3-showcase-docs.md"


def _git(*args):
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT, text=True,
            stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _counts():
    cat = json.loads((ROOT / "workbench" / "g3-catalogue.json").read_text())
    rows = cat["curves"]
    hand = json.loads((ROOT / "workbench" / "g3-handover.json").read_text())
    page = (ROOT / "workbench" / "g3-showcase.html").read_text()
    figures = len(re.findall(r"<h[23]>Fig\.\s*\d+", page))
    complete = hand["counts"]["complete"]
    try:
        cusp_part = page.split('id="cusp-family"')[1]
        cusp_part = cusp_part.split('id="deviation"')[0]
        cusp = len(re.findall(r"<h3>Fig\.", cusp_part))
        dev_part = page.split('id="deviation"')[1]
        dev = len(re.findall(r"<h3>Fig\.", dev_part))
    except Exception:
        cusp = dev = "—"
    return {
        "candidates": len(rows),
        "admitted": sum(1 for r in rows if r.get("admitted")),
        "complete": complete,
        "smooth": hand["counts"]["smooth"],
        "declared": hand["counts"]["declared"],
        "cubic_native": sum(1 for r in rows
                            if r.get("native") == "cubic-native"),
        "figures": figures,
        "lead": figures - complete,
        "gallery": complete,
        "quintic": len(S.QUINTIC_KEYS),
        "cusp": cusp,
        "dev": dev,
    }


def _counts_table(c):
    rows = [
        ("candidates attempted", c["candidates"]),
        ("admitted", c["admitted"]),
        ("G3-complete", c["complete"]),
        ("smooth handover", c["smooth"]),
        ("complete with a declared feature", c["declared"]),
        ("cubic-native rows", c["cubic_native"]),
        ("figures on the showcase", c["figures"]),
        ("lead figures (cubic + quintic + cusp + deviation)", c["lead"]),
        ("gallery figures", c["gallery"]),
        ("quintic-required lead", c["quintic"]),
        ("cusp cards", c["cusp"]),
        ("deviation cards", c["dev"]),
    ]
    body = "\n".join(f"| {a} | {b} |" for a, b in rows)
    return "| | |\n|---|---|\n" + body


def _replace(md, name, body):
    pattern = re.compile(
        rf"<!-- {name}:start -->.*?<!-- {name}:end -->", re.S)
    return pattern.sub(
        f"<!-- {name}:start -->\n{body}\n<!-- {name}:end -->", md)


def _check():
    md = MD.read_text(encoding="utf-8")
    expected = _counts_table(_counts())
    if expected not in md:
        print("stale: the counts block does not match the catalogue/showcase.\n"
              "Run .venv/bin/python scripts/g3_showcase_doc.py")
        return 1
    return 0


def build():
    md = MD.read_text(encoding="utf-8")
    counts = _counts()
    updated = (f"Updated {date.today().isoformat()} · commit "
               f"`{_git('rev-parse', '--short', 'HEAD') or '—'}`")
    md = _replace(md, "updated", updated)
    md = _replace(md, "counts", _counts_table(counts))
    MD.write_text(md, encoding="utf-8")
    print(MD)
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(_check())
    sys.exit(build())
