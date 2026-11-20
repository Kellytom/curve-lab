"""The one loader for a data file: parse it, insist it declares a format.

Every JSON dataset under `workbench/` starts with a `format` line. Reading
through this function means an unstamped or unparseable file is an error with a
name, not a silently empty list — the fault class the register already holds
twice (row 19: a format change orphaned a reader; row 23: a failed read became
a write).
"""

from __future__ import annotations

import json
from pathlib import Path


# One row per dataset under workbench/. `state/DATA-int.md` is the same list for
# a reader; a test keeps the two in step. A new dataset is not real until it is
# here, because nothing will stamp or audit it otherwise.
FORMATS = {
    "family-census.json": "curve-lab.family-census/1",
    "flowers.json": "curve-lab.flowers/1",
    "found-curves.json": "curve-lab.curves/2",
    "frames.json": "curve-lab.frames/1",
    "curve-registry.json": "curve-lab.curve-registry/1",
    "curve-analysis.json": "curve-lab.curve-analysis/1",
    "curve-notes.json": "curve-lab.curve-notes/1",
    "curve-notes.backup.json": "curve-lab.curve-notes/1",
    "naming-todo.json": "curve-lab.naming-todo/1",
    "finder.json": "curve-lab.finder/1",
    "finder.backup.json": "curve-lab.finder/1",
    "finder-stars.json": "curve-lab.finder-stars/1",
    "finder-stars.backup.json": "curve-lab.finder-stars/1",
    "found-for-exp.json": "curve-lab.curves/2",
    "g3-catalogue-cache.json": "curve-lab.g3-catalogue-cache/1",
    "g3-catalogue.json": "curve-lab.g3-catalogue/1",
    "g3-diagnostics.json": "curve-lab.g3-diagnostics/1",
    "g3-handover.json": "curve-lab.g3-handover/1",
    "manifest.json": "curve-lab.manifest/1",
    "moved-curves.json": "curve-lab.moved/1",
    "mobile-curves.json": "curve-lab.mobile-curves/1",
    "coupler-curves.json": "curve-lab.coupler-curves/1",
    "bezier-knots.json": "curve-lab.bezier-knots/1",
    "hybrid-candidates.json": "curve-lab.hybrid-candidates/1",
    "hybrid-formulas.json": "curve-lab.hybrid-formulas/1",
    "hybrids.json": "curve-lab.hybrids/1",
    "wonkies.json": "curve-lab.wonkies/1",
    "doubles.json": "curve-lab.doubles/1",
    "hybrid-rejected.json": "curve-lab.hybrid-rejected/1",
    "mirror-doubles.json": "curve-lab.mirror-doubles/1",
    "pm-reform.json": "curve-lab.pm-reform/1",
    "root-candidates.json": "curve-lab.root-candidates/1",
    "wobble.json": "curve-lab.wobble/1",
    "near-zero.json": "curve-lab.near-zero/1",
    "operator-list.json": "curve-lab.operator-list/1",
    "ph-11th-fitted-curves.json": "curve-lab.ph-fitted/1",
    "ph-fitted-curves.json": "curve-lab.ph-fitted/1",
    "ph-quintic-presets.json": "curve-lab.ph-quintic-presets/1",
    "ph-quintic-yours.json": "curve-lab.ph-quintic-yours/1",
    "real-curves.json": "real-curves/1",
    "root-family.json": "curve-lab.root-family/1",
    "sandbox-curves.json": "curve-lab.sandbox-curves/1",
    "sandbox-parametric.json": "curve-lab.sandbox-parametric/1",
    "parametric-candidates.json": "curve-lab.parametric-candidates/1",
    "septic-curves.json": "curve-lab.septic-curves/1",
    "septic-samples.json": "curve-lab.septic-samples/1",
    "starred.json": "starred/1",
    "starred.backup.json": "starred/1",
    "character-candidates.json": "curve-lab.character-candidates/1",
    "character-curves.json": "curve-lab.character/1",
    "circle-split.json": "curve-lab.circle-split/1",
    "lattice-mobile-fine.json": "curve-lab.lattice.mobile.fine/1",
    "lattice-mobile-quiet.json": "curve-lab.lattice.mobile.quiet/1",
    "lattice-mobile.json": "curve-lab.lattice-mobile/1",
    "lattice-spirograph.json": "curve-lab.lattice-spirograph/1",
    "pm-deep.json": "curve-lab.pm-deep/1",
    "pm-product.json": "curve-lab.pm-product/1",
    "pm4-curves.json": "curve-lab.pm4/1",
    "prime-mover-sweep.json": "curve-lab.prime-mover-sweep/1",
    "circle-plots.json": "curve-lab.circle-plots/1",
}


# A file that is derived and gitignored: a fresh clone does not have it and
# must not fail the audit for that. Rebuild it with its own script.
# The two `.backup.json` files are the previous value kept by every save (the
# register row 23 fault); they exist only after a save on this machine.
OPTIONAL = {"g3-catalogue-cache.json", "finder-stars.json",
            "finder.backup.json", "finder-stars.backup.json",
            "curve-notes.backup.json", "starred.backup.json"}


class DataFileError(ValueError):
    """A data file that is missing, unparseable, or does not say what it is."""


def load(path: str | Path, expected: str | None = None):
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise DataFileError(f"{path}: cannot read ({error.strerror})") from error
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise DataFileError(f"{path}: not JSON ({error.msg} at line {error.lineno})") from error
    if not isinstance(data, dict):
        raise DataFileError(f"{path}: expected an object with a format field")
    fmt = data.get("format")
    if not fmt:
        raise DataFileError(f"{path}: no format field")
    if expected and fmt != expected:
        raise DataFileError(f"{path}: format {fmt}, expected {expected}")
    return data
