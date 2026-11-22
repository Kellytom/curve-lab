# The Inkscape extension glue: send a curve over, take it back.
#
#   curve-lab-send.inx  — the dialog: pick a curve, choose the actions
#   curve-lab-receive.inx — read the recipe back out of a selection
#
# This file runs INSIDE Inkscape (it imports inkex). Everything exact lives
# in ph_actions.py and ph_svg.py, which are pure stdlib and are tested by
# tests/test_ph_actions.py — this glue only wires the two to Inkscape's
# extension API and is checked by hand in Inkscape until an inkex harness
# exists.
#
# The round trip's contract (the operator's design, 2026-11-21):
#   - the SVG carries the recipe (uid, speed rows, placement) in metadata;
#   - the path data is a view drawn from the recipe, never the truth;
#   - the only edits on offer are the closed vocabulary's, so reading back
#     is arithmetic, not approximation;
#   - a drag that matches no legal action is refused with the miss in
#     curve units — never a percentage.

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from inkscape import ph_actions, ph_svg  # noqa: E402

try:
    import inkex
    from inkex import Element
except ImportError:  # the module is importable outside Inkscape for linting
    inkex = None
    Element = None

REGISTRY = ROOT / "workbench" / "curve-registry.json"


def rows_for(uid):
    """The stored speed rows, exact, from the registry."""
    registry = json.load(open(REGISTRY))
    return ph_actions.act_recipe_swap(registry, uid)


def send_svg(uid, out_path, placement=None):
    """Registry → SVG with the recipe in its metadata."""
    rows_x, rows_y, name = rows_for(uid)
    return ph_svg.write_svg(out_path, uid, name, rows_x, rows_y, placement)


def receive_svg(svg_path):
    """SVG → the recipe it carries. Returns (uid, name, rows, placement)."""
    return ph_svg.read_svg(svg_path)


def apply_action(rows_x, rows_y, placement, action, value):
    """One permitted action, applied exactly.

    action is one of: translate, rotate, scale, mirror, end-edit-u,
    end-edit-v, recipe <uid>. The degree gate runs before anything is
    drawn; a refusal raises with the degree stated."""
    if action == "translate":
        dx, dy = value
        return rows_x, rows_y, ph_actions.act_translate(placement, dx, dy)
    if action == "rotate":
        a, b = value
        return rows_x, rows_y, ph_actions.act_rotate_p_triple(placement, a, b)
    if action == "scale":
        return rows_x, rows_y, ph_actions.act_scale_square(placement, value)
    if action == "mirror":
        return rows_x, rows_y, ph_actions.act_mirror_x(placement)
    if action == "end-edit-u":
        return (*ph_actions.act_end_edit(rows_x, rows_y, value, 0), placement)
    if action == "end-edit-v":
        return (*ph_actions.act_end_edit(rows_x, rows_y, 0, value), placement)
    if action.startswith("recipe "):
        registry = json.load(open(REGISTRY))
        rx, ry, _ = ph_actions.act_recipe_swap(registry, action[len("recipe "):])
        return rx, ry, placement
    raise ValueError(f"no such action: {action}")


if inkex is not None:

    class CurveLabSend(inkex.EffectExtension):
        """The send dialog: pick a curve, emit the SVG with its recipe."""

        def add_arguments(self, pars):
            pars.add_argument("--uid", type=str, default="c-0002")
            pars.add_argument("--path", type=str, default="")

        def effect(self):
            uid = self.options.uid
            target = self.options.path or f"{uid}.svg"
            send_svg(uid, target)
            print(f"wrote {target} with the recipe for {uid}")

    class CurveLabReceive(inkex.EffectExtension):
        """Read the recipe back from an SVG file's metadata."""

        def add_arguments(self, pars):
            pars.add_argument("--path", type=str, required=True)

        def effect(self):
            uid, name, rows, placement = receive_svg(self.options.path)
            print(json.dumps({
                "uid": uid, "name": name,
                "speedX": [f"{v.numerator}/{v.denominator}" for v in rows[0]],
                "speedY": [f"{v.numerator}/{v.denominator}" for v in rows[1]],
                "placement": {k: f"{v.numerator}/{v.denominator}" if isinstance(v, __import__('fractions').Fraction) else v
                              for k, v in placement.items()},
            }, indent=1))

else:
    CurveLabSend = CurveLabReceive = None
