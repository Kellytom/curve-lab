#!/usr/bin/env python3
"""Keep the rejected candidates in a plain JSON file, forever.

    .venv/bin/python scripts/record_rejected.py            # report
    .venv/bin/python scripts/record_rejected.py --write    # merge new rejections

The database is where the desk writes a decision; this file is the memory of what has
been tried and rejected, so a later search does not propose it again. It is **JSON only**,
on purpose: readable without SQLite, and it travels with the repository.

Nothing is ever removed. If a rejected curve is later saved, its entry stays and gains
`reinstated: true` and the date — the history is the point.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ROOT / "workbench" / "sandbox-curves.json"
CANDIDATES = ROOT / "workbench" / "hybrids.json"
OUT = ROOT / "workbench" / "hybrid-rejected.json"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--unstarred", action="store_true",
                        help="also record every candidate with no stars, as tried and set aside")
    args = parser.parse_args(argv)

    decisions = json.loads(DECISIONS.read_text()).get("curves", []) if DECISIONS.exists() else []
    candidates = {row["id"]: row for row in json.loads(CANDIDATES.read_text())["candidates"]}
    existing = json.loads(OUT.read_text()) if OUT.exists() else {"rejected": []}
    by_id = {row["id"]: row for row in existing.get("rejected", [])}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    added = 0
    for row in decisions:
        key = row.get("name")
        if row.get("decision") != "rejected" or key not in candidates:
            continue
        if key in by_id:
            continue
        candidate = candidates[key]
        by_id[key] = {
            "id": key,
            "p": candidate["p"],
            "q": candidate["q"],
            "use": candidate["use"],
            "block": candidate["block"],
            "crossings": candidate["crossings"],
            "formula": candidate["formula"]["plain"],
            "middle": candidate["formula"]["middle"],
            "rejectedAt": row.get("crossedAt") or now,
            "reason": "rejected",
            "reinstated": False,
        }
        added += 1

    if args.unstarred:
        importance = {row.get("name"): int(row.get("importance") or 0) for row in decisions}
        for key, candidate in candidates.items():
            if key in by_id or importance.get(key, 0) > 0:
                continue
            by_id[key] = {
                "id": key,
                "p": candidate["p"],
                "q": candidate["q"],
                "use": candidate["use"],
                "block": candidate["block"],
                "crossings": candidate["crossings"],
                "formula": candidate["formula"]["plain"],
                "middle": candidate["formula"]["middle"],
                "rejectedAt": now,
                "reason": "unstarred",
                "reinstated": False,
            }
            added += 1

    # a rejected curve that is later saved is kept, and marked
    saved = {row.get("name") for row in decisions
             if row.get("decision") == "saved" or int(row.get("importance") or 0) > 0}
    for key in saved:
        if key in by_id:
            by_id[key]["reinstated"] = True

    print(f"{added} new rejections; {len(by_id)} on record")
    if not args.write:
        print("report only; --write merges them")
        return 0

    OUT.write_text(json.dumps({
        "format": "curve-lab.hybrid-rejected/1",
        "about": "Candidates already tried and rejected. Keep them: a later search must not "
                 "propose them again. JSON only; nothing is deleted. `reinstated` marks a "
                 "curve that was saved after being rejected.",
        "count": len(by_id),
        "rejected": sorted(by_id.values(), key=lambda row: row["id"]),
    }, indent=1) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
