"""One row per stored curve, five fields, and no gaps left unseen.

    .venv/bin/python scripts/curve_audit.py            # report; exit 1 on a gap
    .venv/bin/python scripts/curve_audit.py --write    # compute missing crossing counts

The set is `workbench/operator-list.json` (the list the page's buttons use).
Each row must carry:

    grid       from the record, or its measured block
    crossings  the crossing-pair count; computed by scripts/ph_crossings.py
    picture    workbench/figures/<name>.png or curves/<name>/figure.png
    note       the record's own note, the folder's notes.md, or a derived line
               from the roots it was built from (marked "derived")
    page       the workbench page that shows it, from where the record came

`--write` fills only the crossing count: it is the one field that can be
recomputed exactly from the stored speeds. A derived note says it is derived;
nothing is invented as prose.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from curve_lab.datafile import load  # noqa: E402
from ph_crossings import stable_crossings  # noqa: E402

WB = ROOT / "workbench"
LIST = WB / "operator-list.json"
FOUND = WB / "found-curves.json"
MOVED = WB / "moved-curves.json"
FIGURES = WB / "figures"
CURVES = ROOT / "curves"

PAGES = {
    "found": "/workbench/ph-nth-sandbox-2.html",
    "moved": "/workbench/moved-curves.html",
}
FOLDER_PAGE = "/workbench/curve-figures.html"


def sources():
    found = {c["name"]: ("found", c) for c in load(FOUND)["curves"]}
    moved = {c["name"]: ("moved", c) for c in load(MOVED)["curves"]}
    folders = {}
    for path in sorted(CURVES.glob("*/curve.json")):
        record = load(path)
        folders[record["name"]] = ("folder", record)
    return {**found, **moved, **folders}


def measured(record):
    return record.get("measured") or {}


def crossing_count(kind, record):
    if kind == "folder":
        return record.get("crossings")
    self_count = measured(record).get("self")
    return self_count if isinstance(self_count, int) else None


def derived_note(kind, record):
    provenance = record.get("provenance") or {}
    roots = provenance.get("roots")
    if not roots:
        return None
    bits = [f"roots {roots}"]
    if provenance.get("batch"):
        bits.append(f"{provenance['batch']} batch")
    return " · ".join(bits) + " (derived)"


def note_for(kind, record):
    if record.get("note"):
        return record["note"]
    if kind == "folder":
        path = CURVES / record["name"] / "notes.md"
        if path.exists() and path.stat().st_size:
            return "notes.md"
    return derived_note(kind, record)


def picture_for(name):
    figure = FIGURES / f"{name}.png"
    if figure.exists():
        return str(figure.relative_to(ROOT))
    folder = CURVES / name / "figure.png"
    if folder.exists():
        return str(folder.relative_to(ROOT))
    return None


def page_for(kind):
    return FOLDER_PAGE if kind == "folder" else PAGES.get(kind, "/workbench/workbench.html")


def write_crossing(kind, record, count):
    if kind == "folder":
        path = CURVES / record["name"] / "curve.json"
        data = load(path)
        data["crossings"] = count
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        return
    path = FOUND if kind == "found" else MOVED
    data = load(path)
    for row in data["curves"]:
        if row["name"] == record["name"]:
            row.setdefault("measured", {})["self"] = count
            break
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv):
    write = "--write" in argv
    rows = load(LIST)["saved"]
    where = sources()
    gaps = []
    written = 0

    print(f"{'curve':28} {'grid':>8} {'cross':>6} {'picture':7} {'note':5} page")
    for row in rows:
        name = row["name"]
        kind, record = where.get(name, ("unknown", {}))
        grid = row.get("grid") or measured(record).get("grid")
        count = crossing_count(kind, record)
        if count is None and write and row.get("speedX") and row.get("speedY"):
            count = stable_crossings(row["speedX"], row["speedY"])
            write_crossing(kind, record, count)
            written += 1
        picture = picture_for(name)
        note = note_for(kind, record)
        page = page_for(kind)
        # 0 is a real crossing count, so only None and "" are gaps.
        missing = [label for label, value in
                   (("grid", grid), ("crossings", count), ("picture", picture),
                    ("note", note), ("page", page)) if value is None or value == ""]
        if missing:
            gaps.append((name, missing))
        print(f"{name:28} {str(grid or '-'):>8} {str(count if count is not None else '-'):>6} "
              f"{'yes' if picture else 'MISS':7} {'yes' if note else 'MISS':5} {page}")

    print(f"\n{len(rows)} curves · {len(gaps)} with a gap · {written} crossing counts written")
    if gaps:
        for name, missing in gaps[:20]:
            print(f"  {name}: {', '.join(missing)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
