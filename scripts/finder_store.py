"""One finder file, many families — merged, never overwritten wholesale.

    from finder_store import save_family
    save_family("septic", curves)      # replaces only the septic family

Why: `workbench/finder.json` is written by several generators (septic, solved
crossings, weighted balance, bounded curves). Each one used to write the whole
file, so whichever ran last deleted the others' curves — and with them the cards
the operator had starred. The file is now keyed by family, the other families are
preserved, and the previous version is copied to `finder.backup.json` first.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "finder.json"
BACKUP = ROOT / "workbench" / "finder.backup.json"
FORMAT = "curve-lab.finder/1"


def _read():
    if not OUT.exists():
        return {"format": FORMAT, "curves": []}
    try:
        data = json.loads(OUT.read_text(encoding="utf-8"))
        if isinstance(data.get("curves"), list):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    # A damaged file is repaired from the backup, never treated as empty.
    if BACKUP.exists():
        return json.loads(BACKUP.read_text(encoding="utf-8"))
    return {"format": FORMAT, "curves": []}


def save_family(family: str, curves: list[dict], note: str = "") -> dict:
    # The same recipe twice is the same curve: drop the repeat, keep the first.
    seen, unique = set(), []
    for curve in curves:
        key = json.dumps(curve.get("definition"), sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        unique.append(curve)
    curves = unique
    data = _read()
    kept = [c for c in data["curves"] if c.get("family") != family]
    for curve in curves:
        curve["family"] = family
    merged = kept + curves
    if OUT.exists():
        shutil.copyfile(OUT, BACKUP)
    payload = {
        "format": FORMAT,
        "note": note or data.get("note", ""),
        "families": sorted({c.get("family", "other") for c in merged}),
        "curves": merged,
    }
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"families": payload["families"], "total": len(merged), "kept": len(kept)}
