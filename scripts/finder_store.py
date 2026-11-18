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

import hashlib
import json
import shutil
from datetime import datetime
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


def _signature(curve):
    pts = curve.get("path") or []
    if len(pts) < 8:
        return None
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    size = max(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    x0, y0 = min(xs), min(ys)
    rounded = [(round((x - x0) / size, 3), round((y - y0) / size, 3)) for x, y in pts]
    forward = json.dumps(rounded)
    backward = json.dumps(list(reversed(rounded)))
    return min(forward, backward)


def mark_duplicates(curves):
    """Flag a curve that draws the same shape as another, whatever its family."""
    seen = {}
    for curve in curves:
        curve.pop("dup", None)
        curve["flags"] = [f for f in (curve.get("flags") or []) if not str(f).startswith("dup of")]
    for curve in curves:
        sig = _signature(curve)
        if sig is None:
            continue
        if sig in seen:
            other = seen[sig]
            curve["dup"] = True
            curve.setdefault("flags", []).append(f"dup of {other['name']}")
        else:
            seen[sig] = curve
    return sum(1 for c in curves if c.get("dup"))


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
        if not curve.get("id"):
            digest = hashlib.sha1(json.dumps(curve.get("definition"), sort_keys=True).encode()).hexdigest()[:8]
            curve["id"] = f"{family}-{digest}"
    merged = kept + curves
    mark_duplicates(merged)
    if OUT.exists():
        shutil.copyfile(OUT, BACKUP)
        # Keep five timestamped generations, not one backup that the next bad
        # write would overwrite.
        backups = ROOT / "workbench" / "backups"
        backups.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.copyfile(OUT, backups / f"finder-{stamp}.json")
        for old in sorted(backups.glob("finder-*.json"))[:-5]:
            old.unlink()
    payload = {
        "format": FORMAT,
        "note": note or data.get("note", ""),
        "families": sorted({c.get("family", "other") for c in merged}),
        "curves": merged,
    }
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"families": payload["families"], "total": len(merged), "kept": len(kept)}
