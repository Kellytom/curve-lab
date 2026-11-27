"""Quintic from Guide: the Inkscape glue.

Runs INSIDE Inkscape (imports inkex). All the maths is in `quintic_math.py`,
which is plain stdlib and is tested by `tests/test_quintic_math.py`; this file
only reads the selection, asks for the six points, and writes the answer back.

Three layers (the operator's model, 2026-11-26):

  1. the drawn curve — the freehand stroke, read from the selection;
  2. the six-point curve — six points taken off that stroke, and the quintic
     through them; it comes close to the drawn curve but is not it;
  3. the quintic display — the same curve drawn as a C2 chain of cubics,
     because SVG renders nothing else.

The miss at each join is measured and printed: drawn → quintic (how good the
reduction is) and quintic → cubic chain (how good the display is).
"""

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("CURVE_LAB_ROOT", HERE.parent)).resolve()
if not (ROOT / "curve_lab").is_dir():
    ROOT = Path.home() / "developer" / "curve-lab"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from inkscape import quintic_math as qm  # noqa: E402
from inkscape import quintic_theory as qt  # noqa: E402

try:
    import inkex
except ImportError:  # importable outside Inkscape for linting
    inkex = None

MARK = "data-quintic-guide"
MARK_POINTS = "data-quintic-points"
SAMPLES_PER_SPAN = 60     # dense arc-length samples per span; 61 points, 5x12
POINT_RADIUS = 2.5


def _cubic_segments(path_element):
    """Every span of the path as one cubic, in document coordinates.

    Inkex gives the path as a 'superpath': nodes of [in, point, out]. A cubic
    from node A to node B is (A.point, A.out, B.in, B.point). Arc, line and
    quad commands are already converted to cubics by to_superpath().
    """
    element = path_element
    if not isinstance(element, inkex.elements.PathElement):
        element = element.to_path_element()
    path = element.path.to_absolute().transform(element.composed_transform())
    segments = []
    for subpath in path.to_superpath():
        for a, b in zip(subpath, subpath[1:]):
            segments.append((
                (a[1][0], a[1][1]),
                (a[2][0], a[2][1]),
                (b[0][0], b[0][1]),
                (b[1][0], b[1][1]),
            ))
    return segments


def _guide_in_selection(selection):
    for element in list(selection.values()):
        if isinstance(element, inkex.elements.PathElement):
            return element
        if hasattr(element, "to_path_element"):
            return element
    return None


def _six_points(chunk, mode):
    """Six points from one stretch of the drawn curve.

    'even'          six points ON the stretch, evenly spaced by arc length,
                    with the quintic solved to pass through all six. This is
                    the operator's middle layer: six points on the curve.
    'lsq'           the six control points with the smallest total miss;
                    they are not on the stretch, and the miss is smaller.
    'cage-samples'  the same six even points, used as a cage instead.
    """
    if mode == "lsq":
        return qm.fit_least_squares(chunk), "least squares"
    six = qm.six_points_even(chunk)
    if mode == "cage-samples":
        return six, "cage from six samples"
    return qm.solve_through_samples(six), "six points on the curve"


def _copy_to_clipboard(text):
    """Best effort; macOS first because that is this machine."""
    try:
        if sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
            return "pbcopy"
        for cmd in (["xclip", "-selection", "clipboard"], ["wl-copy"]):
            try:
                subprocess.run(cmd, input=text.encode("utf-8"), check=True)
                return " ".join(cmd)
            except (OSError, subprocess.CalledProcessError):
                continue
    except (OSError, subprocess.CalledProcessError):
        return ""
    return ""


class QuinticFromGuide(inkex.EffectExtension if inkex else object):
    """Read six points, draw the quintic as cubics, keep the six as the truth."""

    def add_arguments(self, pars):
        pars.add_argument("--pointmode", type=str, default="even")
        pars.add_argument("--spans", type=int, default=1)
        pars.add_argument("--splitmode", type=str, default="curvature")
        pars.add_argument("--smoothseams", type=inkex.Boolean, default=False)
        pars.add_argument("--fullness", type=float, default=1.0)
        pars.add_argument("--segments", type=int, default=0)
        pars.add_argument("--tolerance", type=float, default=0.01)
        pars.add_argument("--clampovershoot", type=inkex.Boolean, default=False)
        pars.add_argument("--showpoints", type=inkex.Boolean, default=True)
        pars.add_argument("--strokecolour", type=str, default="#000000")
        pars.add_argument("--keepguide", type=inkex.Boolean, default=True)
        pars.add_argument("--exportdir", type=str, default="")
        pars.add_argument("--clipboard", type=inkex.Boolean, default=False)
        pars.add_argument("--writeoffset", type=inkex.Boolean, default=False)
        pars.add_argument("--offsetdistance", type=float, default=10.0)

    # -- the run ---------------------------------------------------------

    def effect(self):
        guide = _guide_in_selection(self.svg.selection)
        if guide is None:
            inkex.errormsg("Quintic from Guide: select the outer guide path first.")
            return
        guide_id = guide.get("id") or ""
        mode = (self.options.pointmode or "").strip()
        spans = max(1, int(self.options.spans))
        splitmode = (self.options.splitmode or "curvature").strip()
        if mode not in ("even", "lsq", "cage-nodes", "cage-samples"):
            # a mode the dialog never offers is a caller's mistake, never a
            # silent fall back to the default: this is how a shell quoting slip
            # once made five different runs print the same answer
            inkex.errormsg("Quintic from Guide: unknown point mode %r "
                           "(even, lsq, cage-nodes, cage-samples)" % mode)
            return
        if splitmode not in ("even", "curvature"):
            inkex.errormsg("Quintic from Guide: unknown split mode %r "
                           "(even, curvature)" % splitmode)
            return
        if mode == "cage-nodes" and spans > 1:
            inkex.errormsg("Quintic from Guide: a control cage from the guide's "
                           "own nodes is one span; set spans to 1.")
            return

        try:
            segments = _cubic_segments(guide)
        except Exception as exc:  # a shape that will not convert
            inkex.errormsg("Quintic from Guide: cannot read that path: %s" % exc)
            return
        if not segments:
            inkex.errormsg("Quintic from Guide: the guide path has no segments.")
            return
        # a stroke whose last point is its first is a loop; the record says so
        first_point = segments[0][0]
        last_point = segments[-1][3]
        is_closed = (len(segments) > 2 and
                     abs(first_point[0] - last_point[0]) < 1e-6 and
                     abs(first_point[1] - last_point[1]) < 1e-6)

        if mode == "cage-nodes":
            nodes = qm.nodes_from_segments(segments)
            if len(nodes) != qm.COUNT:
                inkex.errormsg(
                    "Quintic from Guide: the guide path has %d nodes; that mode "
                    "needs exactly 6. Use the six-points mode instead." % len(nodes))
                return
            chunks = [nodes]
            how = "cage from the guide's 6 nodes"
        else:
            count = SAMPLES_PER_SPAN * spans
            dense = qm.samples_along(segments, [i / count for i in range(count + 1)])
            try:
                if splitmode == "curvature" and spans > 1:
                    curvature = qt.curvature_at_samples(segments, dense)
                    cuts = qt.curvature_cuts(dense, curvature, spans)
                    chunks = [dense[cuts[i]:cuts[i + 1] + 1] for i in range(spans)]
                else:
                    chunks = qm.split_samples(dense, spans)
            except ValueError as exc:
                inkex.errormsg("Quintic from Guide: %s" % exc)
                return
            how = None

        alpha = max(0.0, min(1.0, self.options.fullness))

        # phase one: the six control points of every span
        plans = []
        for chunk in chunks:
            if how is None:
                control, point_how = _six_points(chunk, mode)
            else:
                control, point_how = list(chunk), how
            control = qm.blend_fullness(control, alpha)
            plans.append({"chunk": chunk, "control": control, "point_how": point_how})

        # phase two: the seams, then the drawings
        seam_before = seam_after = 0.0
        if self.options.smoothseams and len(plans) > 1:
            controls, before, after = qt.smooth_seams([p["control"] for p in plans],
                                                      closed=is_closed)
            for plan, control in zip(plans, controls):
                plan["control"] = control
            seam_before = max(a for a, _ in before) if before else 0.0
            seam_after = max(a for a, _ in after) if after else 0.0

        results = []
        for plan in plans:
            control = plan["control"]
            chunk = plan["chunk"]
            runaway = qm.overshoot(control, chunk)
            clamped = False
            if runaway > 0.0 and self.options.clampovershoot:
                control = qm.clamp_inside(control, chunk)
                clamped = True

            if self.options.segments <= 0:
                chain, chain_miss, used = qm.fit_to_tolerance(
                    control, self.options.tolerance)
            else:
                used = int(self.options.segments)
                chain = qm.cubic_chain(control, used)
                chain_miss = qm.measure_max_error(control, chain)
            if chain_miss > self.options.tolerance:
                inkex.errormsg(
                    "Quintic from Guide: %d cubics miss the quintic by %.4f px "
                    "(tolerance %.4f). Raise the segments count to fit tighter."
                    % (used, chain_miss, self.options.tolerance))

            bound, _ = qt.chain_error_bound(control, chain)
            if bound > self.options.tolerance:
                inkex.errormsg(
                    "Quintic from Guide: the PROVED bound is %.4f px, above the "
                    "tolerance %.4f; the measured %.4f px is optimistic."
                    % (bound, self.options.tolerance, chain_miss))

            fitted_max, fitted_rms = qm.fit_report(control, chunk)
            speed_min, _, cusps = qt.speed_report(control)
            results.append({
                "control": control,
                "chain": chain,
                "segments": used,
                "chain_miss": chain_miss,
                "bound": bound,
                "fit_max": fitted_max,
                "fit_rms": fitted_rms,
                "clamped": clamped,
                "overshoot": runaway,
                "cusps": cusps,
                "certified": bound <= self.options.tolerance,
                "point_how": plan["point_how"],
                "exact_degree": qm.low_degree(control),
                "ph": qt.is_pythagorean(control),
            })

        self._remove_previous(guide_id)
        self._draw(guide, guide_id, results)
        self._exports(guide_id, alpha, mode, results, is_closed)

        if not self.options.keepguide:
            guide.delete()

        worst_fit = max(r["fit_max"] for r in results)
        worst_chain = max(r["chain_miss"] for r in results)
        worst_bound = max(r["bound"] for r in results)
        worst_box = max(r["overshoot"] for r in results)
        worst_degree = max(r["exact_degree"] for r in results)
        cusps = sum(r["cusps"] for r in results)
        if worst_box <= 0.0:
            box = "inside the six points"
        elif all(r["clamped"] for r in results):
            box = "clamped (was %.1f px out)" % worst_box
        else:
            box = "out of the six points by up to %.1f px" % worst_box
        seams = ""
        if seam_before:
            seams = " seams %.1f deg -> %.1f deg;" % (seam_before, seam_after)
        inkex.errormsg(
            "Quintic from Guide: %d span%s, %s, alpha %.2f, %d cubic%s; "
            "drawn->quintic max %.3f rms %.3f px; quintic->chain %.4f px "
            "(proved bound %.4f px);%s PH %s, %d cusp%s, true degree %d; %s."
            % (len(results), "" if len(results) == 1 else "s",
               results[0]["point_how"], alpha,
               sum(r["segments"] for r in results),
               "" if sum(r["segments"] for r in results) == 1 else "s",
               worst_fit, max(r["fit_rms"] for r in results), worst_chain,
               worst_bound, seams,
               "no" if not all(qt.is_pythagorean(r["control"]) for r in results)
               else "yes", cusps, "" if cusps == 1 else "s", worst_degree, box))

    # -- the pieces ------------------------------------------------------

    def _remove_previous(self, guide_id):
        if not guide_id:
            return
        for selector in ("//*[@%s='%s']" % (MARK, guide_id),
                         "//*[@%s='%s']" % (MARK_POINTS, guide_id)):
            for element in list(self.svg.xpath(selector)):
                element.delete()

    def _draw(self, guide, guide_id, results):
        leaf = inkex.elements.PathElement()
        leaf.set("d", " ".join(qm.chain_to_d(r["chain"]) for r in results))
        leaf.set(MARK, guide_id)
        stroke = self.options.strokecolour or "#000000"
        width = guide.style.get("stroke-width", "1") or "1"
        leaf.style = {
            "fill": "none",
            "stroke": stroke,
            "stroke-width": width,
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
        }
        layer = guide.getparent()
        layer.append(leaf)
        index = list(layer).index(guide)
        layer.remove(leaf)
        layer.insert(index, leaf)

        if self.options.showpoints:
            group = inkex.elements.Group()
            group.set(MARK_POINTS, guide_id)
            for r in results:
                for x, y in r["control"]:
                    dot = inkex.elements.Circle()
                    dot.set("cx", qm.num(x))
                    dot.set("cy", qm.num(y))
                    dot.set("r", qm.num(POINT_RADIUS))
                    dot.style = {"fill": "none", "stroke": stroke,
                                 "stroke-width": "0.75", "opacity": "0.8"}
                    group.append(dot)
            layer.append(group)
            index = list(layer).index(guide)
            layer.remove(group)
            layer.insert(max(0, index - 1), group)
        return leaf

    def _exports(self, guide_id, alpha, mode, results, is_closed=False):
        report = []
        folder = (self.options.exportdir or "").strip()
        stem = guide_id or "quintic"
        if folder:
            out = Path(folder).expanduser()
            try:
                out.mkdir(parents=True, exist_ok=True)
                # the contract file: curve-lab.quintic/1, schema-checked
                spans = [qm.to_y_up(r["control"]) for r in results]
                closed = bool(is_closed)
                winding = None
                if closed:
                    loop = []
                    for r, control in zip(results, spans):
                        loop.extend(qm.cubic_chain(control, max(1, r["segments"])))
                    winding = qt.winding_of(loop)
                curve = {
                    "uid": (guide_id or "quintic") + ":curve",
                    "group": "ornament",
                    "family": "freehand",
                    "name": (guide_id or "quintic") + " from a drawn guide",
                    "note": ("six points taken off a drawn stroke; the drawn "
                             "chain is an approximation, the points are the object"),
                    "closed": closed,
                    "winding": winding,
                    "fitError": round(max(r["fit_max"] for r in results), 9),
                    "selfCrossings": int(qt.count_self_crossings(
                        qm.cubic_chain(spans[0], 12)) if len(spans) == 1 else 0),
                    "spans": [qt.span_record(control, "%s:%d" % (guide_id or "q", i))
                              for i, control in enumerate(spans)],
                    "joins": [],
                }
                seams = len(spans) - 1 + (1 if closed and len(spans) > 1 else 0)
                for i in range(seams):
                    pair = (i, (i + 1) % len(spans))
                    residual = qt.join_residual(spans[pair[0]], spans[pair[1]])
                    # 0.01 deg is a hundredth of a degree: exact for a drawing
                    # and loose enough for float noise in the solve
                    if residual["tangentDegrees"] < 0.01:
                        curve["joins"].append({
                            "uid": "%s:join%d" % (guide_id or "q", i),
                            "a": {"span": curve["spans"][pair[0]]["uid"], "end": "end"},
                            "b": {"span": curve["spans"][pair[1]]["uid"], "end": "start"},
                            "continuity": "G1",
                            "residual": {
                                "position": round(residual["position"], 9),
                                "tangentDegrees": round(residual["tangentDegrees"], 9),
                                "kappa": round(residual["kappa"], 9),
                                "rate": round(residual["rate"], 12),
                            },
                        })
                document = qt.contract_document([curve])
                (out / ("%s-quintic.json" % stem)).write_text(
                    json.dumps(document, indent=2) + "\n", encoding="utf-8")
                # my own numbers, deliberately NOT in the contract file
                numbers = {
                    "note": "not the contract: measured numbers for the extension only",
                    "guide_id": guide_id,
                    "pointmode": mode,
                    "fullness": round(alpha, 6),
                    "options": {"splitmode": self.options.splitmode,
                                "smooth_seams": bool(self.options.smoothseams),
                                "clamp": bool(self.options.clampovershoot),
                                "tolerance_px": self.options.tolerance},
                    "spans": [{
                        "index": i,
                        "drawn_to_quintic_max_px": round(r["fit_max"], 9),
                        "drawn_to_quintic_rms_px": round(r["fit_rms"], 9),
                        "quintic_to_chain_max_px": round(r["chain_miss"], 9),
                        "quintic_to_chain_proved_bound_px": round(r["bound"], 9),
                        "cubic_segments": r["segments"],
                        "ph": bool(r["ph"]),
                        "cusps": int(r["cusps"]),
                        "true_degree": int(r["exact_degree"]),
                        "overshoot_px": round(r["overshoot"], 9),
                        "clamped": bool(r["clamped"]),
                    } for i, r in enumerate(results)],
                }
                (out / ("%s-report.json" % stem)).write_text(
                    json.dumps(numbers, indent=2) + "\n", encoding="utf-8")
                (out / ("%s-blender.py" % stem)).write_text(
                    "# Paste into Blender's Text Editor and press Run Script.\n"
                    + qm.blender_script_many(spans, name=stem, flip_y=False),
                    encoding="utf-8")
                (out / ("%s-geogebra.txt" % stem)).write_text(
                    "# Paste into GeoGebra's Input Bar, one line at a time.\n"
                    + qm.geogebra_commands_many(spans, flip_y=False),
                    encoding="utf-8")
                report.append("wrote %s-quintic.json (contract), %s-report.json, "
                              "%s-blender.py, %s-geogebra.txt" % (stem, stem, stem, stem))
            except OSError as exc:
                inkex.errormsg("Quintic from Guide: export folder failed: %s" % exc)
        if self.options.writeoffset:
            distance = float(self.options.offsetdistance)
            spans = []
            for r in results:
                chain, miss = qt.offset_chain(r["control"], distance, segments=8)
                spans.append({
                    "distance_px": round(distance, 9),
                    "exact": bool(qt.is_pythagorean(r["control"])),
                    "note": ("the curve is PH, so this offset is exact"
                             if qt.is_pythagorean(r["control"]) else
                             "the curve is not PH, so this offset is an "
                             "approximation measured against sampled normals"),
                    "miss_px": round(miss, 9),
                    "cubic_chain": [[[round(v, 9) for v in point] for point in seg]
                                    for seg in chain],
                })
            try:
                out = Path(folder or ".").expanduser()
                out.mkdir(parents=True, exist_ok=True)
                (out / ("%s-offset.json" % stem)).write_text(
                    json.dumps({"guide_id": guide_id, "spans": spans}, indent=2) + "\n",
                    encoding="utf-8")
                report.append("wrote %s-offset.json (approx %.4f px)"
                              % (stem, max(s["miss_px"] for s in spans)))
            except OSError as exc:
                inkex.errormsg("Quintic from Guide: offset export failed: %s" % exc)
        if self.options.clipboard:
            payload = (json.dumps([{ "control_svg_y_down":
                                     [[round(p[0], 9), round(p[1], 9)]
                                      for p in r["control"]]}
                                    for r in results], indent=2))
            used_tool = _copy_to_clipboard(payload)
            report.append("clipboard via %s" % used_tool if used_tool
                          else "clipboard unavailable (no pbcopy/xclip/wl-copy)")
        for line in report:
            inkex.errormsg("Quintic from Guide: " + line)


if __name__ == "__main__":
    QuinticFromGuide().run()
