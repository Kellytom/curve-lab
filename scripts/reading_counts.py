"""Refresh the line counts in state/READING-int.md, so the list cannot go stale.

    .venv/bin/python scripts/reading_counts.py          # rewrite the numbers
    .venv/bin/python scripts/reading_counts.py --check  # exit 1 when they are wrong

The counts in that table are a cache of `wc -l`. Nothing refreshed them, so /fhandoff left them
years behind (`HANDOFF-int.md` was listed at 846 lines when it was 2,226). This rewrites every
`| `file` | number |` row it recognises and prints what changed.

Run at every /fhandoff, after the handoff block is written.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIST = ROOT / "state" / "READING-int.md"
ROW = re.compile(r"^\| (?:[0-9]+ \| )?[`]([^`]+)[`] \| ([0-9,]+) \|")


def main() -> int:
    check = "--check" in sys.argv
    text = LIST.read_text()
    lines = text.splitlines()
    changed = []
    for index, line in enumerate(lines):
        match = ROW.match(line)
        if not match:
            continue
        relative, listed = match.group(1), match.group(2)
        path = ROOT / relative
        if not path.exists():
            print(f"missing file on the list: {relative}")
            continue
        actual = len(path.read_text().splitlines())
        printed = f"{actual:,}" if "," in listed else str(actual)
        if printed == listed:
            continue
        changed.append((relative, listed, printed))
        lines[index] = line.replace(f"| {listed} |", f"| {printed} |", 1)
    if check:
        for relative, was, now in changed:
            print(f"stale: {relative} listed {was}, is {now}")
        return 1 if changed else 0
    if changed:
        LIST.write_text("\n".join(lines) + "\n")
    for relative, was, now in changed:
        print(f"{relative}: {was} -> {now}")
    print(f"{len(changed)} counts refreshed" if changed else "counts already right")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
