"""Write the operator's button list from the curves the repository actually holds.

    .venv/bin/python scripts/operator_list.py             # rewrite workbench/operator-list.json
    .venv/bin/python scripts/operator_list.py --dry-run   # report, write nothing

The page's `B | solve, save, take away` buttons hold the built-in seeds plus
whatever is in the browser under `ph-nth-curves`. That browser list is the only
copy of the operator's own saves, and it has been lost twice: once by a write
after a failed read, once by a browser reset. So the list is written here, from
the records on disk, and the page reads it back when the browser has no list of
its own.

Where the curves come from, in this order: `workbench/found-curves.json` (the
finds), `workbench/moved-curves.json` (the ones taken out of the gallery), and
`curves/<slug>/curve.json` (the ones with a folder). A name appears once; the
first source wins, as it does in the gallery.

`--merge <file>` adds a list the operator exported from the browser, keeping
every record in it even when the repository does not have that curve: an export
is the only surviving copy of a curve that was never written to disk.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "operator-list.json"
FOUND = ROOT / "workbench" / "found-curves.json"
MOVED = ROOT / "workbench" / "moved-curves.json"
CURVES = ROOT / "curves"
ARCHIVE = ROOT / "workbench" / "moved-curves.json"


def rows_of(record):
    """(speedX, speedY) from a record that stores terms or rows."""
    if isinstance(record.get("speedX"), list) and isinstance(record.get("speedY"), list):
        return record["speedX"], record["speedY"]
    terms = record.get("terms") or []
    if not terms:
        return [], []
    length = max(int(term["power"]) for term in terms) + 1
    speed_x = [0] * length
    speed_y = [0] * length
    for term in terms:
        power = int(term["power"])
        speed_x[power] = term.get("x", 0)
        speed_y[power] = term.get("y", 0)
    return speed_x, speed_y


def button_record(record, source):
    """One entry in the shape the saved buttons read."""
    speed_x, speed_y = rows_of(record)
    if not speed_x or not speed_y:
        return None
    entry = {
        "name": record["name"],
        "speedX": speed_x,
        "speedY": speed_y,
        "from": source,
    }
    if record.get("step") is not None:
        entry["step"] = record["step"]
    measured = record.get("measured") or {}
    grid = measured.get("grid", record.get("grid"))
    if grid is not None:
        entry["grid"] = grid
    return entry


def collect():
    """Every stored curve as a button, one per name, first source winning."""
    entries, seen = [], set()

    def add(record, source):
        name = record.get("name")
        if not name or name in seen:
            return
        entry = button_record(record, source)
        if entry:
            entries.append(entry)
            seen.add(name)

    if FOUND.exists():
        for record in json.loads(FOUND.read_text()).get("curves", []):
            add(record, "found")
    if MOVED.exists():
        for record in json.loads(MOVED.read_text()).get("curves", []):
            add(record, "moved")
    for path in sorted(CURVES.glob("*/curve.json")):
        add(json.loads(path.read_text()), "folder")
    return entries


def read_export(path):
    """A browser export: its saved, moved and starred lists, all optional."""
    payload = json.loads(Path(path).read_text())
    if isinstance(payload, list):
        payload = {"saved": payload}
    return payload


def main(argv):
    entries = collect()
    moved, starred = [], []
    merge = None
    if "--merge" in argv:
        merge = argv[argv.index("--merge") + 1]
    if merge:
        payload = read_export(merge)
        known = {entry["name"] for entry in entries}
        kept = 0
        for item in payload.get("saved", []):
            if item.get("name") and item["name"] not in known:
                entries.append(item)
                known.add(item["name"])
                kept += 1
        moved = payload.get("moved", [])
        starred = payload.get("starred", [])
        print(f"merged {kept} curve(s) the repository did not have, from {merge}")
    document = {
        "format": "curve-lab.operator-list/1",
        "note": ("Written by scripts/operator_list.py from the stored records. The page reads it "
                 "when the browser holds no list, so a reset cannot empty the buttons."),
        "count": len(entries),
        "saved": entries,
        "moved": moved,
        "starred": starred,
    }
    if "--dry-run" in argv:
        print(f"{len(entries)} buttons would be written")
        return 0
    OUT.write_text(json.dumps(document, indent=1) + "\n")
    print(f"{OUT.relative_to(ROOT)}: {len(entries)} curves in the buttons")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
