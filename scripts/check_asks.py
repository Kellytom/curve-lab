"""Check that the operator's asks are written down and closed honestly.

`state/ASKS-int.md` is the register: one row per ask, in the operator's words.
This check fails when a row cannot be trusted:

  - a row does not have the six columns;
  - the date is not YYYY-MM-DD;
  - the status is not open / fixed / dropped;
  - a fixed row names no commit and no file that exists;
  - an open row names no next step;
  - a dropped row does not say the operator dropped it;
  - a row has no note saying what happened or what blocked the first answer.

Run it from the repo root:

    .venv/bin/python scripts/check_asks.py

`RepeatedAskTest` in `tests/test_regressions.py` runs it with the register, so
a broken row fails the fast suite. The operator's words, 2026-11-23:
"i should not have to repeat myself".
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASKS = ROOT / "state" / "ASKS-int.md"
STATUSES = {"open", "fixed", "dropped"}
SHA = re.compile(r"\b[0-9a-f]{7,40}\b")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TICKED = re.compile(r"`([^`]+)`")


def rows(text):
    """The table rows, with the header and its separator skipped."""
    for number, line in enumerate(text.splitlines(), 1):
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells[0] in {"#", "---"} or set(cells[0]) == {"-"}:
            continue
        yield number, cells


def commit_exists(sha):
    if len(sha) < 7:
        return False
    run = subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"],
                         cwd=ROOT, capture_output=True, text=True)
    return run.returncode == 0


def file_exists(token):
    path = ROOT / token.split()[0]
    return path.is_file()


def problems(text):
    bad = []
    seen = 0
    for number, cells in rows(text):
        seen += 1
        where = f"ASKS-int.md line {number}"
        if len(cells) != 6:
            bad.append(f"{where}: expected 6 columns, found {len(cells)}")
            continue
        _num, date, ask, status, proof, note = cells
        if not DATE.match(date):
            bad.append(f"{where}: the date is {date!r}, not YYYY-MM-DD")
        if status not in STATUSES:
            bad.append(f"{where}: status {status!r} is not one of {sorted(STATUSES)}")
        if not ask or len(ask) < 8:
            bad.append(f"{where}: the ask is empty; put the operator's words in")
        if status == "fixed":
            shas = SHA.findall(proof)
            ticked = TICKED.findall(proof)
            evidence = any(commit_exists(sha) for sha in shas) or any(
                file_exists(token) for token in ticked)
            if not evidence:
                bad.append(f"{where}: fixed, but the proof names no real commit or file"
                           f" (commit {shas or 'none'}, file {ticked or 'none'})")
            if len(proof) < 12:
                bad.append(f"{where}: fixed, but the proof is not a command or a place")
        elif status == "open":
            if len(proof) < 10:
                bad.append(f"{where}: open, but no next step is named")
        elif status == "dropped" and "operator" not in note.lower():
            bad.append(f"{where}: dropped, but the note does not say the operator dropped it")
        if len(note) < 15:
            bad.append(f"{where}: the note must say what happened, or what blocked the first answer")
    if not seen:
        bad.append("no asks found; the register is empty or its table is broken")
    return bad


def main():
    text = ASKS.read_text()
    bad = problems(text)
    for line in bad:
        print(f"asks: {line}")
    if bad:
        print(f"asks: {len(bad)} problem(s); the register is not trustworthy")
        return 1
    print("asks: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
