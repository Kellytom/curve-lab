"""Quintic theory: the parts that make claims checkable instead of plausible.

Plain stdlib, no inkex, so it is tested by `.venv/bin/python` without Inkscape.

What lives here, and why:

1. `chain_error_bound` — a **certified** bound on how far the cubic chain is
   from the quintic. No sampling: the difference of two Beziers is a Bezier, and
   a Bezier stays inside the convex hull of its control points, so the largest
   difference coefficient bounds the error. The sampled number elsewhere is a
   measurement; this one is a proof.

2. `split_bezier`, `elevate` — exact de Casteljau subdivision and exact degree
   elevation, both in `Fraction`. The bound above is built from them.

3. `smooth_seams` — neighbouring quintics each end on the drawn stroke's
   tangent; at a span cut that leaves two different tangents and a corner. This
   turns the two neighbouring control points onto one shared direction and
   reports the angle and curvature gap before and after.

4. `is_pythagorean` — whether the quintic's hodograph is a Pythagorean pair, so
   the curve has an exact offset. Decided with polynomial arithmetic in
   `Fraction`: x'^2 + y'^2 must be a perfect square, which is exactly
   deg(gcd(p, p')) == deg(p) / 2. A general quintic is NOT PH, and that matters
   because this project's rails assume exact offsets.

5. `offset_chain` — the offset of a curve that is not PH, drawn as a cubic chain
   through sampled normals. It is an approximation and says so; it is not the
   exact offset the PH machinery gives.

6. `arclength_knots`, `curvature_cuts`, `fit_least_squares_reparametrised` —
   the three "best practice" knobs: where the chain's stations go, where a
   stroke is cut into spans, and the parameter-correction passes of Piegl &
   Tiller 9.4.2.
"""

from fractions import Fraction
from math import comb

from . import quintic_math as qm

DEGREE = 5


# ---------------------------------------------------------------------------
# exact Bezier subdivision and degree elevation (Fractions throughout)
# ---------------------------------------------------------------------------


def _as_fractions(points, rationalise=False):
    return qm._as_fractions(points, rationalise=rationalise)


split_bezier = qm.split_bezier


def elevate(points):
    return qm.elevate(points)


def cubic_to_quintic(segment):
    return qm.cubic_to_quintic(segment)


chain_error_bound = qm.chain_error_bound


# ---------------------------------------------------------------------------
# the certified bound
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# seams
# ---------------------------------------------------------------------------


def _unit(v):
    n = (v[0] * v[0] + v[1] * v[1]) ** 0.5
    if n == 0.0:
        return (0.0, 0.0)
    return (v[0] / n, v[1] / n)


def seam_angle(control_a, control_b):
    """The angle in degrees between the two spans' tangents at the shared point."""
    d1 = _unit(qm.sub(control_a[-1], control_a[-2]))
    d2 = _unit(qm.sub(control_b[1], control_b[0]))
    dot = max(-1.0, min(1.0, d1[0] * d2[0] + d1[1] * d2[1]))
    import math
    return math.degrees(math.acos(dot))


def _curvature_at_start(control):
    d = qm.derivative(control, 0.0)
    dd = qm.second_derivative(control, 0.0)
    speed = (d[0] * d[0] + d[1] * d[1]) ** 0.5
    if speed == 0.0:
        return 0.0
    cross = d[0] * dd[1] - d[1] * dd[0]
    return abs(cross) / speed ** 3


def _curvature_at_end(control):
    d = qm.derivative(control, 1.0)
    dd = qm.second_derivative(control, 1.0)
    speed = (d[0] * d[0] + d[1] * d[1]) ** 0.5
    if speed == 0.0:
        return 0.0
    cross = d[0] * dd[1] - d[1] * dd[0]
    return abs(cross) / speed ** 3


def seam_curvature_gap(control_a, control_b):
    """The step in curvature (1/px) across the seam. Zero is G2."""
    return abs(_curvature_at_end(control_a) - _curvature_at_start(control_b))


def smooth_seams(controls):
    """Make neighbouring quintics meet C1, and report what that cost.

    Each span's end tangent is moved onto the bisector of the two tangents, with
    its own length kept. Only the two control points next to the seam move, so
    every drawn point the curve passes through is untouched — the curve still
    goes through all of them, and the seam stops being a corner.

    Returns (new_controls, before, after) where before/after are lists of
    (angle_degrees, curvature_gap) per seam.
    """
    out = [list(c) for c in controls]
    before, after = [], []
    for a, b in zip(out, out[1:]):
        before.append((seam_angle(a, b), seam_curvature_gap(a, b)))
    for index in range(len(out) - 1):
        a = out[index]
        b = out[index + 1]
        seam = a[-1]
        d1 = _unit(qm.sub(a[-1], a[-2]))
        d2 = _unit(qm.sub(b[1], b[0]))
        direction = _unit((d1[0] + d2[0], d1[1] + d2[1]))
        if direction == (0.0, 0.0):  # the tangents are exactly opposed
            direction = d1
        length_a = qm.sub(a[-1], a[-2])
        length_b = qm.sub(b[1], b[0])
        la = (length_a[0] ** 2 + length_a[1] ** 2) ** 0.5
        lb = (length_b[0] ** 2 + length_b[1] ** 2) ** 0.5
        a[-2] = qm.sub(seam, qm.scale(direction, la))
        b[1] = qm.add(seam, qm.scale(direction, lb))
    for a, b in zip(out, out[1:]):
        after.append((seam_angle(a, b), seam_curvature_gap(a, b)))
    return out, before, after


# ---------------------------------------------------------------------------
# Pythagorean hodograph: does this curve have an exact offset?
# ---------------------------------------------------------------------------


def _poly_mul(a, b):
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def _poly_derivative(p):
    return [p[i] * i for i in range(1, len(p))]


def _poly_trim(p):
    out = list(p)
    while out and out[-1] == 0:
        out.pop()
    return out


def _poly_divmod(a, b):
    a = _poly_trim(a)
    b = _poly_trim(b)
    if not b:
        raise ZeroDivisionError("polynomial division by zero")
    q = [Fraction(0)] * max(0, len(a) - len(b) + 1)
    while len(a) >= len(b) and _poly_trim(a):
        shift = len(a) - len(b)
        factor = a[-1] / b[-1]
        q[shift] = factor
        for i in range(len(b)):
            a[i + shift] -= factor * b[i]
        a = _poly_trim(a)
    return q, a


def _poly_gcd(a, b):
    a = _poly_trim(a)
    b = _poly_trim(b)
    while b:
        _, r = _poly_divmod(a, b)
        a, b = b, r
    if a:
        lead = a[-1]
        a = [c / lead for c in a]
    return a


def _bernstein_to_power(points):
    """Power-basis coefficients, lowest first, from a Bezier's control points."""
    n = len(points) - 1
    out = [[Fraction(0), Fraction(0)] for _ in range(n + 1)]
    # expand each C(n,i) P_i t^i (1-t)^(n-i)
    for i, p in enumerate(points):
        weight = Fraction(comb(n, i))
        for j in range(n - i + 1):
            coefficient = weight * Fraction(comb(n - i, j)) * ((-1) ** j)
            out[i + j][0] += coefficient * p[0]
            out[i + j][1] += coefficient * p[1]
    return out


def is_pythagorean(control):
    """True when the quintic's hodograph is a Pythagorean pair (exact offsets).

    The hodograph has degree 4. It is PH exactly when x'(t)^2 + y'(t)^2 is a
    perfect square, i.e. when gcd(p, p') has degree 4 of p's 8 — the square root
    is then the speed polynomial and the offset is rational.
    """
    points = _as_fractions(control, rationalise=True)
    hodograph = []
    for i in range(len(points) - 1):
        delta = qm.sub(points[i + 1], points[i])
        hodograph.append((delta[0] * DEGREE, delta[1] * DEGREE))
    power = _bernstein_to_power(hodograph)
    x = [c[0] for c in power]
    y = [c[1] for c in power]
    xx = _poly_mul(x, x)
    yy = _poly_mul(y, y)
    width = max(len(xx), len(yy))
    xx += [Fraction(0)] * (width - len(xx))
    yy += [Fraction(0)] * (width - len(yy))
    p = _poly_trim([a + b for a, b in zip(xx, yy)])
    if len(p) <= 1:
        return True  # a point: speed is identically zero
    common = _poly_gcd(p, _poly_derivative(p))
    return len(common) - 1 == (len(p) - 1) // 2


def speed_report(control, samples=200):
    """(min speed, max speed, cusps) over the span, in px per unit t.

    A cusp is a place where the speed vanishes, and no cubic chain can carry one
    exactly; this is the number that says whether the curve has one.
    """
    worst = 0.0
    fastest = 0.0
    cusps = 0
    previous = None
    for k in range(samples + 1):
        d = qm.derivative(control, k / samples)
        s = (d[0] * d[0] + d[1] * d[1]) ** 0.5
        if k == 0 or s < worst:
            worst = s
        if s > fastest:
            fastest = s
        if previous is not None and previous > 1e-9 and s < 1e-9:
            cusps += 1
        previous = s
    return worst, fastest, cusps


# ---------------------------------------------------------------------------
# the offset of a curve that is not PH
# ---------------------------------------------------------------------------


def offset_points(control, distance, samples=200):
    """Points on the offset at the given distance, offset along the normal.

    Sign convention: positive distance moves the curve to its left as t grows
    (the SVG convention with y down means that is visually the right side; the
    extension states the sign rather than guessing).
    """
    points = []
    for k in range(samples + 1):
        t = k / samples
        p = qm.evaluate(control, t)
        d = qm.derivative(control, t)
        speed = (d[0] * d[0] + d[1] * d[1]) ** 0.5
        if speed == 0.0:
            points.append(p)
            continue
        normal = (-d[1] / speed, d[0] / speed)
        points.append((p[0] + normal[0] * distance, p[1] + normal[1] * distance))
    return points


def spline_through(points, segments, start_tangent=None, end_tangent=None):
    """A clamped C2 cubic chain through arbitrary points, with given end tangents.

    The same solve as `quintic_math.cubic_chain`, but the stations are the given
    points instead of samples of a quintic — this is what the offset needs.
    """
    count = len(points) - 1
    if count < 1:
        raise ValueError("need at least two points")
    ts = [i / count for i in range(count + 1)]
    h = [ts[i + 1] - ts[i] for i in range(count)]
    if start_tangent is None:
        start_tangent = qm.scale(qm.sub(points[1], points[0]), count)
    if end_tangent is None:
        end_tangent = qm.scale(qm.sub(points[-1], points[-2]), count)
    tangents = qm._knot_tangents(points, h, start_tangent, end_tangent)
    chain = []
    for i in range(count):
        b0 = points[i]
        b3 = points[i + 1]
        b1 = qm.add(b0, qm.scale(tangents[i], h[i] / 3.0))
        b2 = qm.sub(b3, qm.scale(tangents[i + 1], h[i] / 3.0))
        chain.append((b0, b1, b2, b3))
    return chain


def offset_chain(control, distance, segments=8, samples=200):
    """The offset as a cubic chain — an approximation, never called exact.

    A curve that is not PH has no rational offset, so this samples the exact
    normals and fits a C2 chain through them. The miss is measured against the
    sampled offset points, not against a formula that does not exist.
    """
    pts = offset_points(control, distance, samples)
    stations = [pts[round(i * samples / segments)] for i in range(segments + 1)]
    chain = spline_through(stations, segments)
    flat = _flatten(chain)
    worst = 0.0
    for p in pts:
        worst = max(worst, _distance_to_polyline(p, flat))
    return chain, worst


def _distance_to_polyline(p, poly):
    """Distance from a point to a polyline: to its segments, not to its vertices.

    Measuring to vertices put a 0.25 px floor under the offset's own error, the
    same fault the chain measurement had before it measured to the cubic.
    """
    best = float("inf")
    for a, b in zip(poly, poly[1:]):
        vx = b[0] - a[0]
        vy = b[1] - a[1]
        wx = p[0] - a[0]
        wy = p[1] - a[1]
        vv = vx * vx + vy * vy
        if vv <= 1e-18:
            t = 0.0
        else:
            t = (wx * vx + wy * vy) / vv
            t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
        dx = p[0] - (a[0] + vx * t)
        dy = p[1] - (a[1] + vy * t)
        d = dx * dx + dy * dy
        if d < best:
            best = d
    return best ** 0.5


def _flatten(chain, steps=24):
    out = [chain[0][0]]
    for seg in chain:
        for s in range(1, steps + 1):
            out.append(qm.evaluate_cubic(seg, s / steps))
    return out


# ---------------------------------------------------------------------------
# where the stations go, and where a stroke is cut
# ---------------------------------------------------------------------------


def arclength_knots(control, segments, samples=400):
    """Knot parameters at equal arc length along the quintic, not equal t.

    A quintic with uneven speed wants its stations where the curve travels, not
    where t advances. Returns `segments + 1` parameter values, first 0, last 1.
    """
    if segments < 1:
        raise ValueError("need at least one segment")
    lengths = []
    total = 0.0
    previous = qm.evaluate(control, 0.0)
    for k in range(1, samples + 1):
        current = qm.evaluate(control, k / samples)
        total += ((current[0] - previous[0]) ** 2 + (current[1] - previous[1]) ** 2) ** 0.5
        lengths.append(total)
        previous = current
    if total <= 0.0:
        return [i / segments for i in range(segments + 1)]
    knots = [0.0]
    target_index = 0
    for i in range(1, segments):
        target = total * i / segments
        while target_index < len(lengths) - 1 and lengths[target_index] < target:
            target_index += 1
        # linear interpolation between the two samples around the target
        before = lengths[target_index - 1] if target_index > 0 else 0.0
        after = lengths[target_index]
        span = after - before
        frac = 0.0 if span <= 0.0 else (target - before) / span
        knots.append((target_index - 1 + frac) / samples)
    knots.append(1.0)
    return knots


def curvature_at_samples(segments, points, steps=48):
    """Curvature of the drawn chain, read off at each of `points`.

    A fine vertex table is built from the chain (curvature from the first and
    second differences), then every sample takes the curvature of the nearest
    vertex. That is enough to choose where to cut a stroke, which is all it is
    for; it is not a curvature measurement for the record.
    """
    verts = []
    curvature = []
    for seg in segments:
        for k in range(steps):
            u = k / steps
            p = qm.evaluate_cubic(seg, u)
            ahead = qm.evaluate_cubic(seg, min(1.0, u + 1e-4))
            behind = qm.evaluate_cubic(seg, max(0.0, u - 1e-4))
            v = (ahead[0] - behind[0], ahead[1] - behind[1])
            a = (ahead[0] - 2 * p[0] + behind[0], ahead[1] - 2 * p[1] + behind[1])
            speed = (v[0] * v[0] + v[1] * v[1]) ** 0.5
            curvature.append(abs(v[0] * a[1] - v[1] * a[0]) / speed ** 3
                             if speed > 0.0 else 0.0)
            verts.append(p)
    out = []
    for point in points:
        best = 0
        best_distance = float("inf")
        for i, vertex in enumerate(verts):
            d = (vertex[0] - point[0]) ** 2 + (vertex[1] - point[1]) ** 2
            if d < best_distance:
                best_distance = d
                best = i
        out.append(curvature[best])
    return out


def curvature_cuts(points, curvatures, spans, window=6):
    """Cut a dense, arc-length-even sample list at curvature peaks.

    Starts from the even cuts and slides each one to the highest curvature
    within `window` samples, keeping order and a minimum chunk length. Cutting
    where the curve bends hardest is where a cubic chain needs the freedom.
    """
    if spans < 2:
        return [0, len(points) - 1]
    total = len(points) - 1
    minimum = max(qm.COUNT + 1, total // (spans * 3))
    cuts = [round(total * i / spans) for i in range(spans + 1)]
    for i in range(1, spans):
        low = max(cuts[i - 1] + minimum, cuts[i] - window)
        high = min(cuts[i + 1] - minimum, cuts[i] + window)
        if low >= high:
            continue
        best = cuts[i]
        best_value = curvatures[cuts[i]]
        for k in range(low, high + 1):
            if curvatures[k] > best_value:
                best_value = curvatures[k]
                best = k
        cuts[i] = best
    return cuts


# ---------------------------------------------------------------------------
# the least-squares fit with parameter correction (Piegl & Tiller 9.4.2)
# ---------------------------------------------------------------------------


def fit_least_squares_reparametrised(points, passes=3):
    """Kept as the theory-side name; the correction now lives in the fit itself."""
    return qm.fit_least_squares(points, passes=passes)


# ---------------------------------------------------------------------------
# degeneracy: a quintic that is really a cubic needs one cubic, not two
# ---------------------------------------------------------------------------


low_degree = qm.low_degree


# ---------------------------------------------------------------------------
# the frame and the joins the shared contract asks for
# (workbench/quintic.schema.json, curve-lab.quintic/1)
# ---------------------------------------------------------------------------


def signed_curvature(control, t):
    """Signed curvature at t, 1/unit. Positive turns left along increasing t."""
    d = qm.derivative(control, t)
    dd = qm.second_derivative(control, t)
    speed = (d[0] * d[0] + d[1] * d[1]) ** 0.5
    if speed == 0.0:
        return 0.0
    return (d[0] * dd[1] - d[1] * dd[0]) / speed ** 3


def _curvature_rate(control, t, direction):
    """d(kappa)/ds at an end, by a one-sided difference in arc length.

    `direction` is +1 at the start (step forward) and -1 at the end.
    """
    step = 1e-4 * direction
    t2 = t + step
    if t2 < 0.0 or t2 > 1.0:
        return 0.0
    p1 = qm.evaluate(control, t)
    p2 = qm.evaluate(control, t2)
    ds = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    if ds == 0.0:
        return 0.0
    return (signed_curvature(control, t2) - signed_curvature(control, t)) / ds


def end_frame(control, which):
    """The contract's `frame.start` / `frame.end` for a span.

    `tangent` is the un-normalised forward derivative — P1 - P0 at the start and
    P5 - P4 at the end, exactly as the contract states, so a join needs no sign
    flip. `p` is the on-curve point.
    """
    if which == "start":
        return {
            "p": [control[0][0], control[0][1]],
            "tangent": [control[1][0] - control[0][0], control[1][1] - control[0][1]],
            "kappa": signed_curvature(control, 0.0),
            "rate": _curvature_rate(control, 0.0, 1),
        }
    return {
        "p": [control[-1][0], control[-1][1]],
        "tangent": [control[-1][0] - control[-2][0], control[-1][1] - control[-2][1]],
        "kappa": signed_curvature(control, 1.0),
        "rate": _curvature_rate(control, 1.0, -1),
    }


def join_residual(control_a, control_b):
    """What a join actually measures, for the contract's `residual`.

    Position gap, tangent angle in degrees, curvature step, and curvature-rate
    step. A G1 claim without these numbers is a label, not a joint.
    """
    end = end_frame(control_a, "end")
    start = end_frame(control_b, "start")
    gap = ((end["p"][0] - start["p"][0]) ** 2 + (end["p"][1] - start["p"][1]) ** 2) ** 0.5
    return {
        "position": gap,
        "tangentDegrees": seam_angle(control_a, control_b),
        "kappa": abs(end["kappa"] - start["kappa"]),
        "rate": abs(end["rate"] - start["rate"]),
    }


def count_self_crossings(chain, steps=16):
    """How many times the drawn chain crosses itself.

    Counted on a fine flattening of the chain, so it is a measurement of the
    drawing, not a theorem about the quintic. Adjacent segments are skipped.
    """
    polyline = []
    for seg in chain:
        for s in range(steps):
            polyline.append(qm.evaluate_cubic(seg, s / steps))
    polyline.append(chain[-1][3])
    crossings = 0
    count = len(polyline) - 1
    for i in range(count):
        a0, a1 = polyline[i], polyline[i + 1]
        for j in range(i + 2, count):
            b0, b1 = polyline[j], polyline[j + 1]
            if _segments_cross(a0, a1, b0, b1):
                crossings += 1
    return crossings


def _orientation(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _segments_cross(a, b, c, d):
    o1 = _orientation(a, b, c)
    o2 = _orientation(a, b, d)
    o3 = _orientation(c, d, a)
    o4 = _orientation(c, d, b)
    return (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0)


# ---------------------------------------------------------------------------
# the written contract: workbench/quintic.schema.json, curve-lab.quintic/1
# ---------------------------------------------------------------------------


def span_record(control, uid):
    """One span in the contract's shape. `control` must already be y up."""
    points = [[round(p[0], 9), round(p[1], 9)] for p in control]
    return {
        "uid": uid,
        "kind": "quintic",
        "points": points,
        "weights": None,
        "frame": {"start": end_frame(points, "start"), "end": end_frame(points, "end")},
    }


def contract_document(curves, created_by="curve-lab/quintic-guide", units="px"):
    """A file in the shared format, ready for either side to read.

    `curves` is a list of dicts already in the schema's shape; this only adds the
    envelope (format, degree, count, axes with its extent). It checks nothing —
    `scripts/quintic_contract.py` is the check.
    """
    xs, ys = [], []
    for curve in curves:
        for span in curve["spans"]:
            for x, y in span["points"]:
                xs.append(x)
                ys.append(y)
    extent = [min(xs), max(xs), min(ys), max(ys)] if xs else [0, 0, 0, 0]
    return {
        "format": "curve-lab.quintic/1",
        "degree": DEGREE,
        "createdBy": created_by,
        "axes": {"x": "right", "y": "up", "units": units, "extent": extent},
        "count": len(curves),
        "curves": curves,
    }
