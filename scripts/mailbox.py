#!/usr/bin/env python3
"""The DeepSeek1 ↔ DeepSeek2 mailbox: read it cheaply, check its shape.

    .venv/bin/python scripts/mailbox.py --read        # the newest job and reply
    .venv/bin/python scripts/mailbox.py --read 3      # the last three entries
    .venv/bin/python scripts/mailbox.py --check       # shape, proof, size
    .venv/bin/python scripts/mailbox.py --check --quiet

Why this exists: two agents reading a full transcript spend their context on
history. The logs stay complete and append-only, but a session reads only the
newest entries, and `--check` catches the two faults that actually hurt:
an entry with no shape, and a "done" with no command that proves it.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAILBOX = {
    "deep-to-side.md": "DeepSeek1 → DeepSeek2",
    "side-to-deep.md": "DeepSeek2 → DeepSeek1",
}
FILES = {name: ROOT / "archive" / "notes" / name for name in MAILBOX}
HEADER = re.compile(r"^## (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) — (.+)$")
FIELD = re.compile(r"^(Job|Files|Done|Proved by|Blocked|Next):\s*(.*)$")
MAX_LINES = 400


def entries(path: Path):
    """Every entry: (line number, timestamp text, subject, lines)."""
    found = []
    current = None
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = HEADER.match(line)
        if match:
            current = [number, match.group(1), match.group(2), []]
            found.append(current)
            continue
        if current is not None:
            current[3].append(line)
    return found


def quiet_read(path: Path, count: int) -> str:
    found = entries(path)
    if not found:
        return f"{path.name}: no entries yet"
    chosen = found[-count:]
    out = []
    for _, stamp, subject, body in chosen:
        text = "\n".join(body).strip()
        out.append(f"## {stamp} — {subject}\n{text}")
    return f"### {MAILBOX[path.name]}\n" + "\n\n".join(out)


def check(path: Path) -> list[str]:
    problems = []
    text = path.read_text(encoding="utf-8").splitlines()
    if len(text) > MAX_LINES:
        problems.append(
            f"{path.name}: {len(text)} lines, over the {MAX_LINES}-line limit — "
            "move the oldest entries to archive/notes/mailbox-history.md"
        )
    found = entries(path)
    found_any = set(range(1, len(text) + 1))
    for number, stamp, subject, body in found:
        try:
            datetime.strptime(stamp, "%Y-%m-%d %H:%M")
        except ValueError:
            problems.append(f"{path.name}:{number}: bad timestamp {stamp!r}")
        if len(subject.strip()) < 4:
            problems.append(f"{path.name}:{number}: subject is too short")
        fields = {}
        for offset, line in enumerate(body):
            match = FIELD.match(line.strip())
            if match:
                fields[match.group(1)] = match.group(2).strip()
                if not match.group(2).strip():
                    problems.append(f"{path.name}:{number + 1 + offset}: empty {match.group(1)}:")
        done = fields.get("Done")
        if done and done.lower() not in {"nothing", "none"} and not fields.get("Proved by"):
            problems.append(
                f"{path.name}:{number}: claims Done without `Proved by:` — a result "
                "needs the command that proves it"
            )
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read", nargs="?", type=int, const=1, metavar="N",
                        help="print the last N entries of each file (default 1)")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    if args.read:
        for path in FILES.values():
            print(quiet_read(path, args.read))
            print()
        return 0

    if args.check:
        problems = []
        for path in FILES.values():
            if not path.exists():
                problems.append(f"{path.name}: missing")
                continue
            problems.extend(check(path))
        if problems:
            for problem in problems:
                print(f"FAIL {problem}")
            return 1
        if not args.quiet:
            print("ok — both mailboxes parse, every Done has its proof")
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
