"""Watch a design file and rebuild the drawing when it is saved.

This is the two-window loop: Inkscape holds the SVG, an editor holds the design
JSON, and saving the JSON redraws the curve. Inkscape notices the file changed
and offers to reload.

Two rules make it safe to leave running.

The write is atomic. The new document is written beside the old one and renamed
over it, so Inkscape never opens a file that is half written, which is the one
failure that would look like a bug in the geometry.

A design that does not parse, or does not build, leaves the last good drawing
alone. Typing a number one digit at a time passes through states that are not
valid JSON, and a watcher that blanked the file on each of them would be useless.

The poll is a file timestamp, not a daemon and not a socket. Nothing here needs
dbus, and nothing runs when the watcher is not running.
"""

from __future__ import annotations

import os
import time

from . import presets, svg
from .model import Design


def seed(path: str, preset_name: str = "s-curve") -> Design:
    """Write a starting design so there is something to edit."""
    design = presets.get(preset_name)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    design.save(path)
    return design


def rebuild(design_path: str, out_path: str, render, encoding: str = "utf-8",
            **options) -> tuple[bool, str]:
    """Render the design file into the SVG, atomically. Never clobbers on failure."""
    try:
        with open(design_path, "r", encoding=encoding) as fh:
            design = Design.from_json(fh.read())
        text, info = render(design, **options)
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    tmp = f"{out_path}.tmp"
    svg.write(tmp, text)
    os.replace(tmp, out_path)
    fit = info["fit"]
    verdict = "ok" if info["ok"] else "OVER TOLERANCE"
    return True, (f"{fit['spans']:3d} cubics  {fit['error_max']:.4f} mm  "
                  f"{info['chain']['backend']}  {verdict}")


def run(design_path: str, out_path: str, render, interval: float = 0.4,
        seed_preset: str | None = None, **options) -> int:
    """Watch until interrupted. Returns the number of successful rebuilds."""
    if not os.path.exists(design_path):
        name = seed_preset or "s-curve"
        seed(design_path, name)
        print(f"seeded {design_path} from preset {name}", flush=True)

    stamp = _stamp(design_path)
    ok, message = rebuild(design_path, out_path, render, **options)
    print(f"built   {message}" if ok else f"waiting {message}", flush=True)
    rebuilds = 1 if ok else 0
    started = time.time()

    print(f"watching {design_path} -> {out_path}   (ctrl-c to stop)", flush=True)
    try:
        while True:
            time.sleep(interval)
            now = _stamp(design_path)
            if now == stamp:
                continue
            stamp = now
            ok, message = rebuild(design_path, out_path, render, **options)
            if ok:
                rebuilds += 1
                print(f"rebuilt {message}", flush=True)
            else:
                print(f"kept the last drawing: {message}", flush=True)
    except KeyboardInterrupt:
        secs = time.time() - started
        print(f"stopped after {rebuilds} rebuilds in {secs:.0f}s", flush=True)
        return rebuilds


def _stamp(path: str) -> tuple[int, int]:
    """Change stamp: modification time in nanoseconds, or zero when absent."""
    try:
        st = os.stat(path)
        return (st.st_mtime_ns, st.st_size)
    except OSError:
        return (0, 0)
