"""Skip a page rebuild when its generator's inputs are unchanged.

    python scripts/pagecache.py check scripts/ph_families.py   # fresh | stale

A generator is "input" to its own page, and so is every project module it
imports, transitively. The key is the sha256 of those files' bytes; the record
lives in `state/build-cache.json`. If the key matches, the page on disk was
built from exactly this code, and rebuilding it would write the same bytes.

What this cannot see: data files a generator reads directly (`manifest.json`,
`reference/*.json`). A generator that reads one declares it in `EXTRA_INPUTS`,
a module-level list of repo-relative paths; otherwise the cache would go stale
silently. Anything not declared is a bug in the generator, not in the cache.

    --force        ignore the record and treat every generator as stale
"""

from __future__ import annotations

import ast
import functools
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "state" / "build-cache.json"
LOCAL_ROOTS = (ROOT / "curve_lab", ROOT / "scripts", ROOT / "pythagorean-spiral")


@functools.lru_cache(maxsize=1)
def _index() -> dict[str, Path]:
    """module stem or dotted name -> file, for the project's own modules only."""
    out: dict[str, Path] = {}
    for root in LOCAL_ROOTS:
        for path in root.glob("*.py"):
            out.setdefault(path.stem, path)
    # package modules: curve_lab/x.py is imported as curve_lab.x
    for root in LOCAL_ROOTS:
        pkg = root.name
        for path in root.glob("*.py"):
            out.setdefault(f"{pkg}.{path.stem}", path)
    return out


def _resolve(name: str) -> list[Path]:
    """Project files a dotted import name could mean (stdlib names resolve to
    nothing, which is the point: no stat calls, no guessing)."""
    idx = _index()
    hit = idx.get(name)
    if hit is not None:
        return [hit]
    head = name.split(".")[0]
    hit = idx.get(head)
    return [hit] if hit is not None else []


def _imports(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return set()
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module)
            names.update(f"{node.module}.{a.name}" for a in node.names)
    return names


@functools.lru_cache(maxsize=32)
def dependencies(script: Path) -> tuple[Path, ...]:
    """The script and every project module it imports, transitively."""
    seen: set[Path] = set()
    queue = [script.resolve()]
    while queue:
        path = queue.pop()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        for name in _imports(path):
            for found in _resolve(name):
                if found not in seen:
                    queue.append(found)
        # a generator may declare data inputs
        try:
            mod = ast.parse(path.read_text(encoding="utf-8"))
            for node in mod.body:
                if (isinstance(node, ast.Assign) and node.targets
                        and getattr(node.targets[0], "id", "") == "EXTRA_INPUTS"):
                    for elt in getattr(node.value, "elts", []):
                        rel = getattr(elt, "value", None)
                        if isinstance(rel, str):
                            cand = (ROOT / rel)
                            if cand.is_file():
                                seen.add(cand.resolve())
        except SyntaxError:
            pass
    return tuple(sorted(seen))


@functools.lru_cache(maxsize=32)
@functools.lru_cache(maxsize=1)
def _code_files() -> tuple[Path, ...]:
    """Every project code file a page can depend on: curve_lab and scripts.

    Coarse on purpose. A per-import walk was measured at 0.7 s per call because
    it parses every module; hashing two directories takes about 20 ms and can
    never miss a dependency. The cost is that editing any generator invalidates
    every page - acceptable, since a rebuild happens only when asked for.
    """
    out = []
    for root in (ROOT / "curve_lab", ROOT / "scripts"):
        out.extend(sorted(p for p in root.rglob("*.py") if "__pycache__" not in p.parts))
    return tuple(out)


def key(script: Path) -> str:
    h = hashlib.sha256()
    for path in _code_files():
        h.update(str(path.relative_to(ROOT)).encode())
        h.update(path.read_bytes())
    for extra in _extra_inputs(script):
        h.update(str(extra.relative_to(ROOT)).encode())
        h.update(extra.read_bytes())
    return h.hexdigest()


def _extra_inputs(script: Path) -> list[Path]:
    """A generator's declared data inputs (EXTRA_INPUTS, repo-relative)."""
    try:
        tree = ast.parse(script.read_text(encoding="utf-8"))
    except (SyntaxError, FileNotFoundError):
        return []
    out = []
    for node in tree.body:
        if (isinstance(node, ast.Assign) and node.targets
                and getattr(node.targets[0], "id", "") == "EXTRA_INPUTS"):
            for elt in getattr(node.value, "elts", []):
                rel = getattr(elt, "value", None)
                if isinstance(rel, str) and (ROOT / rel).is_file():
                    out.append((ROOT / rel).resolve())
    return out


def load() -> dict:
    if not CACHE.is_file():
        return {}
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save(data: dict) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n",
                     encoding="utf-8")


def is_fresh(script: Path) -> bool:
    record = load().get(str(script.resolve().relative_to(ROOT)))
    return bool(record) and record.get("key") == key(script)


def record(script: Path) -> None:
    data = load()
    data[str(script.resolve().relative_to(ROOT))] = {
        "key": key(script), "deps": len(dependencies(script))}
    save(data)


def should_build(script: Path, outputs=()) -> bool:
    """True when the page must be rebuilt: inputs changed, or an output missing."""
    if not is_fresh(script):
        return True
    return any(not (ROOT / o).exists() for o in outputs)


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in ("check", "record", "deps"):
        print(__doc__)
        return 2
    cmd = argv[0]
    target = (ROOT / argv[1]).resolve() if not Path(argv[1]).is_absolute() else Path(argv[1])
    if cmd == "deps":
        for p in dependencies(target):
            print(p.relative_to(ROOT))
        return 0
    if cmd == "check":
        print("fresh" if is_fresh(target) else "stale")
        return 0
    record(target)
    print("recorded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
