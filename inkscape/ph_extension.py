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
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# The extension can run from two homes: the repo (inkscape/ph_extension.py,
# HERE.parent is the repo) or Inkscape's user extensions folder (the repo is
# pointed at by CURVE_LAB_ROOT). Both paths land on the same modules — the
# recipe machinery is the repo's, never a copy.
ROOT = Path(os.environ.get("CURVE_LAB_ROOT", HERE.parent)).resolve()
if not (ROOT / "curve_lab").is_dir():
    ROOT = Path.home() / "developer" / "curve-lab"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from inkscape import ph_actions, ph_svg  # noqa: E402

try:
    import inkex
except ImportError:  # the module is importable outside Inkscape for linting
    inkex = None

REGISTRY = ROOT / "workbench" / "curve-registry.json"


def rows_for(uid):
    """The stored speed rows, exact, from the registry."""
    registry = json.load(open(REGISTRY))
    return ph_actions.act_recipe_swap(registry, uid)


def ph_extension_root():
    """The repo root the glue resolved (for sibling modules)."""
    return ROOT


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
            pars.add_argument("--mode", type=str, default="send")
            pars.add_argument("--uid", type=str, default="c-0002")
            pars.add_argument("--path", type=str, default="")
            pars.add_argument("--ceiling", type=int, default=11)

        def effect(self):
            uid = self.options.uid
            target = self.options.path or f"{uid}.svg"
            rows_x, rows_y, name = rows_for(uid)
            ok, degree = ph_actions.degree_gate(rows_x, rows_y, self.options.ceiling)
            if not ok:
                raise SystemExit(f"{uid} is position degree {degree}, over the "
                                 f"ceiling of {self.options.ceiling}")
            send_svg(uid, target)
            print(f"wrote {target} with the recipe for {uid} "
                  f"(position degree {degree}, ceiling {self.options.ceiling})")

    class CurveLabReceive(inkex.EffectExtension):
        """Read the recipe back, snap any dragged nodes to the closed
        vocabulary, and rewrite the file with the acted recipe."""

        def add_arguments(self, pars):
            pars.add_argument("--mode", type=str, default="receive")
            pars.add_argument("--path", type=str, required=True)
            pars.add_argument("--variant", type=str, default="")
            pars.add_argument("--post", type=str, default="")
            pars.add_argument("--ceiling", type=int, default=11)

        def effect(self):
            from inkscape import ph_handles
            svg = self.options.path
            uid, name, (rows_x, rows_y), placement = receive_svg(svg)
            report = ph_handles.apply_snap(
                svg, rows_x, rows_y, placement, ph_svg.stations,
                ceiling=self.options.ceiling)
            out = {
                "uid": uid, "name": name,
                "action": report["action"],
                "miss": str(report["miss"]) if report["miss"] is not None else None,
                "rewritten": report["rewritten"],
                "note": report.get("note", ""),
                "placement": {k: f"{v.numerator}/{v.denominator}"
                              for k, v in placement.items()},
            }
            if self.options.variant:
                # the acted recipe as a registry-variant PROPOSAL (the save
                # endpoint owns the registry; this only prints the payload)
                from inkscape import ph_variant
                acted = ph_svg.read_svg(svg)
                record, note = ph_variant.variant_record(acted, json.load(
                    open(ph_extension_root() / "workbench" / "curve-registry.json")))
                out["variant"] = record
                out["variant_note"] = note
                if record and self.options.post:
                    out["posted"] = ph_variant.post_candidate(record, self.options.post)
            print(json.dumps(out, indent=1))

else:
    CurveLabSend = CurveLabReceive = None

if __name__ == "__main__" and inkex is not None:
    # one script, two extensions: the .inx files carry <param name="mode">
    mode = "send"
    argv = sys.argv
    if "--mode=receive" in argv or ("--path" in argv and "--uid" not in argv):
        mode = "receive"
    elif "--mode=send" in argv:
        mode = "send"
    (CurveLabSend if mode == "send" else CurveLabReceive)().run()
