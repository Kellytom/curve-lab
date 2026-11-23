"""The rolling checklist made from /said/ — write it, then check it.

`/said/` lists the operator's own messages (`data/said.json`, personal and
gitignored). This script turns that list into `state/SAID-CHECKLIST-int.md`,
one row per message, newest first, and fails when the roll is not honest:

  - a message on /said/ has no row in the roll;
  - a row's words are not the message's words;
  - the state is not one of ask / open / done / chat / command / dropped;
  - a `done` row names no real commit or file;
  - an `open` row names no next step;
  - a `dropped` row does not say the operator dropped it.

`--write` appends the messages that are new, as `open`, and never deletes a row.
The state and the proof are the operator's checklist, so they are edited by
hand; a script cannot know that work was done.

    .venv/bin/python scripts/said_checklist.py --write   # add new messages
    .venv/bin/python scripts/said_checklist.py           # check the roll

The operator, 2026-11-23: "check http://127.0.0.1:4321/said/ on a regular basis
and make a rolling checklist from it in md and then prove that you did the work
and check it off."
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAID = ROOT / "data" / "said.json"
ROLL = ROOT / "state" / "SAID-CHECKLIST-int.md"
STATES = {"ask", "open", "done", "chat", "command", "dropped"}
SHA = re.compile(r"\b[0-9a-f]{7,40}\b")
TICKED = re.compile(r"`([^`]+)`")
HEAD = ("| key | at | what was said | state | proof | note |\n"
        "|---|---|---|---|---|---|\n")


def key_of(at, text):
    return hashlib.sha1(f"{at}\n{text}".encode()).hexdigest()[:10]


def cell(text, limit=220):
    one = " ".join(text.replace("|", "\\|").split())
    return one if len(one) <= limit else f"{one[:limit].rstrip()} …"


def rows(text):
    for number, line in enumerate(text.splitlines(), 1):
        if not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] in {"key", "---"} or set(cells[0]) == {"-"}:
            continue
        yield number, cells


def said_messages():
    data = json.loads(SAID.read_text())
    return data.get("messages", [])


def commit_exists(sha):
    run = subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"],
                         cwd=ROOT, capture_output=True, text=True)
    return run.returncode == 0


def file_exists(token):
    return (ROOT / token.split()[0]).is_file()


def same_words(shown, text):
    shorn = shown.replace("\\|", "|")
    norm = " ".join(text.split())
    if shorn.endswith("…"):
        return norm.startswith(shorn[:-1].rstrip())
    return shorn == norm


def write_roll():
    messages = said_messages()
    existing = ROLL.read_text() if ROLL.exists() else f"# SAID-CHECKLIST-int\n\n{HEAD}"
    known = {cells[0] for _n, cells in rows(existing) if len(cells) == 6}
    added = []
    for message in reversed(messages):  # newest first
        key = key_of(message["at"], message["text"])
        if key in known:
            continue
        added.append(f"| {key} | {message['at']} | {cell(message['text'])} "
                     f"| open | | |")
    if not added:
        print(f"said roll: no new messages ({len(messages)} on /said/)")
        return 0
    if not ROLL.exists():
        ROLL.parent.mkdir(parents=True, exist_ok=True)
        ROLL.write_text(
            "# SAID-CHECKLIST-int — the rolling checklist from /said/\n\n"
            "One row per message the operator sent, newest first. Written by\n"
            "`scripts/said_checklist.py --write`; the state and the proof are edited by hand\n"
            "and checked by `scripts/said_checklist.py`. Local only: the history in\n"
            "`data/said.json` is personal and gitignored.\n\n"
            "States: `ask` (a request, not started), `open` (started or blocked, next step in\n"
            "proof), `done` (a commit or file proves it), `chat` (nothing asked), `command`\n"
            "(a slash command or a paste), `dropped` (the operator dropped it).\n\n" + HEAD)
        existing = ROLL.read_text()
    head, _sep, body = existing.partition(HEAD)
    lines = body.splitlines()
    # new rows go under the table header, above the older ones
    new_body = "\n".join(added) + ("\n" + "\n".join(lines) if lines else "\n")
    ROLL.write_text(head + HEAD + new_body.rstrip() + "\n")
    print(f"said roll: added {len(added)} row(s); {len(messages)} on /said/")
    return 0


def check_roll():
    if not SAID.exists():
        print("said roll: no data/said.json; nothing to check")
        return 0
    if not ROLL.exists():
        print(f"said roll: {ROLL.relative_to(ROOT)} is missing; run --write")
        return 1
    messages = said_messages()
    by_key = {key_of(m["at"], m["text"]): m for m in messages}
    bad = []
    seen = set()
    for number, cells in rows(ROLL.read_text()):
        where = f"SAID-CHECKLIST-int.md line {number}"
        if len(cells) != 6:
            bad.append(f"{where}: expected 6 columns, found {len(cells)}")
            continue
        key, at, said, state, proof, note = cells
        seen.add(key)
        if state not in STATES:
            bad.append(f"{where}: state {state!r} is not one of {sorted(STATES)}")
        message = by_key.get(key)
        if message:
            if message["at"] != at:
                bad.append(f"{where}: the time is {at!r}, /said/ has {message['at']!r}")
            if not same_words(said, message["text"]):
                bad.append(f"{where}: the words are not the message's words")
        if state == "done":
            evidence = any(commit_exists(sha) for sha in SHA.findall(proof)) or any(
                file_exists(token) for token in TICKED.findall(proof))
            if not evidence:
                bad.append(f"{where}: done, but the proof names no real commit or file")
        elif state in {"ask", "open"} and len(proof) < 10:
            bad.append(f"{where}: {state}, but no next step is named")
        elif state == "dropped" and "operator" not in note.lower():
            bad.append(f"{where}: dropped, but the note does not say the operator dropped it")
    for key, message in by_key.items():
        if key not in seen:
            bad.append(f"/said/ {message['at']}: {cell(message['text'], 60)!r} has no row")
    for line in bad:
        print(f"said roll: {line}")
    if bad:
        print(f"said roll: {len(bad)} problem(s); the roll is not honest")
        return 1
    print(f"said roll: ok ({len(by_key)} messages on /said/, {len(seen)} rows)")
    return 0


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--write", action="store_true", help="append new messages as open rows")
    args = parser.parse_args()
    return write_roll() if args.write else check_roll()


if __name__ == "__main__":
    sys.exit(main())
