"""Read every workbench dataset through the one loader, and say what is there.

    .venv/bin/python scripts/data_audit.py

Each file must parse, be an object, and declare the format the registry expects.
A failure names the file and the reason, so the fix is not a hunt. This is the
check behind `state/DATA-int.md`.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab.datafile import FORMATS, OPTIONAL, DataFileError, load  # noqa: E402

WORKBENCH = ROOT / "workbench"


def rows_of(data) -> int:
    for key in ("curves", "plates", "rows", "pages", "stems", "spans"):
        if isinstance(data.get(key), list):
            return len(data[key])
    if isinstance(data.get("count"), int):
        return data["count"]
    return 0


def main() -> int:
    problems = []
    printed = 0
    for name, fmt in sorted(FORMATS.items()):
        path = WORKBENCH / name
        if name in OPTIONAL and not path.exists():
            print(f"{name:32} {fmt:34} absent (cache, gitignored)")
            continue
        try:
            data = load(path, fmt)
        except DataFileError as error:
            problems.append(str(error))
            print(f"{name:32} FAIL")
            continue
        rows = rows_of(data)
        bytes_ = path.stat().st_size
        print(f"{name:32} {fmt:34} {rows:>6} rows {bytes_ / 1024:>8.1f} KB")
        printed += 1

    on_disk = sorted(path.name for path in WORKBENCH.glob("*.json"))
    for name in on_disk:
        if name not in FORMATS:
            problems.append(f"{name}: on disk but not in the registry (curve_lab/datafile.py)")

    optional = ", ".join(sorted(OPTIONAL))
    print(f"\n{printed} of {len(FORMATS)} datasets read; {len(on_disk)} JSON files on disk")
    print(f"optional caches (gitignored, may be absent): {optional}")
    if problems:
        for problem in problems:
            print(f"  {problem}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
