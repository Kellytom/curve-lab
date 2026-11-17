"""Give every workbench JSON file a declared format, and keep it that way.

    .venv/bin/python scripts/data_format.py --check   # exit 1 if any file is unstamped
    .venv/bin/python scripts/data_format.py --write   # stamp the ones that lack it

The editor is surgical: the `format` line is inserted after the opening brace, so
the rest of the file keeps its own indentation and the diff is one line. Nothing
else is reordered or reformatted.

The table below is the registry. `state/DATA-int.md` is the same list for a
reader; a test keeps the two in step.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
from curve_lab.datafile import FORMATS, OPTIONAL  # noqa: E402

WORKBENCH = ROOT / "workbench"



def current_format(text: str):
    """The top-level format, or None. A list-shaped file is never stamped."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return False
    if not isinstance(data, dict):
        return False
    return data.get("format") or None


def stamp(text: str, fmt: str) -> str:
    """Insert the format line after the opening brace, preserving indentation."""
    brace = text.index("{")
    match = re.search(r"\n(\s+)\"", text)
    indent = match.group(1) if match else "  "
    stamped = text[: brace + 1] + f'\n{indent}"format": "{fmt}",' + text[brace + 1:]
    json.loads(stamped)  # refuse to write something that does not parse
    return stamped


def survey() -> list[dict]:
    rows = []
    for path in sorted(WORKBENCH.glob("*.json")):
        name = path.name
        text = path.read_text(encoding="utf-8")
        rows.append({
            "name": name,
            "path": path,
            "format": current_format(text),
            "wanted": FORMATS.get(name),
            "text": text,
        })
    return rows


def main(argv: list[str]) -> int:
    write = "--write" in argv
    rows = survey()
    problems = []

    for row in rows:
        if row["wanted"] is None:
            problems.append(f"{row['name']}: not in the registry (add it to FORMATS)")
            continue
        if row["format"] is False:
            problems.append(f"{row['name']}: not a JSON object")
            continue
        if not row["format"]:
            if write:
                row["path"].write_text(stamp(row["text"], row["wanted"]), encoding="utf-8")
                print(f"stamped {row['name']} → {row['wanted']}")
            else:
                problems.append(f"{row['name']}: no format (run --write)")
        elif row["format"] != row["wanted"]:
            problems.append(
                f"{row['name']}: format {row['format']} but the registry says {row['wanted']}")

    extra = set(FORMATS) - {row["name"] for row in rows} - OPTIONAL
    for name in sorted(extra):
        problems.append(f"{name}: in the registry but not on disk")

    print(f"{len(rows)} data files, {len(rows) - len(problems)} stamped as registered")
    if problems and not write:
        for problem in problems:
            print(f"  {problem}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
