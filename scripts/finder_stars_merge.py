"""Merge an exported finder-stars.json into the workbench list.

    .venv/bin/python scripts/finder_stars_merge.py ~/Downloads/finder-stars.json
    .venv/bin/python scripts/finder_stars_merge.py FILE --write

The union is taken by name, so a star that is only in one list survives. The
current file is copied to workbench/backups before anything is written, and
nothing is written without --write. A failed read is an error, not an empty
list.
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "workbench" / "finder-stars.json"


def read_list(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"{path}: cannot read ({error})")
    if not isinstance(data, dict) or not isinstance(data.get("curves"), list):
        raise SystemExit(f"{path}: expected {{\"curves\": [...]}}")
    return data["curves"]


def key(star: dict) -> str:
    name = star.get("name")
    if not name:
        raise SystemExit(f"a star has no name: {star}")
    return str(name)


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__.strip())
        return 2
    incoming = Path(args[0]).expanduser()
    write = "--write" in argv

    current = read_list(TARGET) if TARGET.exists() else []
    extra = read_list(incoming)

    merged: dict[str, dict] = {key(star): star for star in current}
    added = 0
    for star in extra:
        if key(star) not in merged:
            merged[key(star)] = star
            added += 1

    print(f"current {len(current)} · incoming {len(extra)} · new {added} · merged {len(merged)}")
    if not added:
        print("nothing to add")
        return 0
    for star in merged.values():
        if key(star) not in {key(s) for s in current}:
            print(f"  + {key(star)}")
    if not write:
        print("dry run: add --write to keep the union")
        return 0

    backup = ROOT / "workbench" / "backups"
    backup.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().isoformat().replace(":", "-").replace(".", "-")
    if TARGET.exists():
        shutil.copy2(TARGET, backup / f"finder-stars-merge-{stamp}.json")
    payload = {"format": "curve-lab.finder-stars/1", "curves": list(merged.values())}
    TARGET.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {TARGET.relative_to(ROOT)} with {len(merged)} stars")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
