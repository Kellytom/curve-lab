"""The maths behind Quintic from Guide: plain Python, no inkex, no file I/O.

The operator's workflow (2026-11-26):

  1. draw an outer guide curve in Inkscape;
  2. take six points off it (its six nodes, or six arc-length samples);
  3. dial one fullness scalar alpha over the four interior points;
  4. the quintic B(t) = sum C(5,i) (1-t)^(5-i) t^i P_i is drawn, and drawn
     again as a cubic Bezier chain because SVG renders only cubics;
  5. the six control points are exported exactly to Blender and GeoGebra, so
     the degree-5 curve survives even though the screen shows cubics.

Everything here works in SVG document coordinates: x to the right, **y down**.
Only the Blender and GeoGebra exports flip y, and they say so in the text they
write (both of those tools are y up).

Units: the numbers are pixels of the SVG user space. Every error figure printed
by this module is in those same units.
"""

import bisect
from fractions import Fraction
from math import comb

DEGREE = 5
COUNT = DEGREE + 1

# ---------------------------------------------------------------------------
# small vector helpers (2-tuples of float)
# ---------------------------------------------------------------------------


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def scale(a, k):
    return (a[0] * k, a[1] * k)


def lerp(a, b, s):
    return (a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s)


def lerp_points(a, b, s):
    return (a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s)


# ---------------------------------------------------------------------------
# the quintic itself
# ---------------------------------------------------------------------------


def bernstein_weight(i, n, t):
    """The i-th Bernstein weight of degree n at t (float)."""
    return comb(n, i) * (1.0 - t) ** (n - i) * t ** i


def evaluate(control, t):
    """B(t) for a list of six control points."""
    if len(control) != COUNT:
        raise ValueError("a quintic needs exactly 6 control points, got %d" % len(control))
    x = 0.0
    y = 0.0
    for i, p in enumerate(control):
        w = bernstein_weight(i, DEGREE, t)
        x += w * p[0]
        y += w * p[1]
    return (x, y)


def derivative(control, t):
    """dB/dt at t. The end tangents are the ones the cubic chain must keep."""
    if len(control) != COUNT:
        raise ValueError("a quintic needs exactly 6 control points, got %d" % len(control))
    dx = 0.0
    dy = 0.0
    for i in range(DEGREE):
        w = DEGREE * bernstein_weight(i, DEGREE - 1, t)
        dx += w * (control[i + 1][0] - control[i][0])
        dy += w * (control[i + 1][1] - control[i][1])
    return (dx, dy)


def second_derivative(control, t):
    """d2B/dt2 at t; used by the tests, not by the drawing."""
    dx = 0.0
    dy = 0.0
    for i in range(DEGREE - 1):
        w = DEGREE * (DEGREE - 1) * bernstein_weight(i, DEGREE - 2, t)
        dx += w * (control[i + 2][0] - 2 * control[i + 1][0] + control[i][0])
        dy += w * (control[i + 2][1] - 2 * control[i + 1][1] + control[i][1])
    return (dx, dy)


# ---------------------------------------------------------------------------
# six points in, six control points out
# ---------------------------------------------------------------------------


def blend_fullness(control, alpha):
    """P_i = (1-a) L_i + a G_i, with L_i the straight chord at i/5.

    a = 1 keeps the guide's own points (the cage); a = 0 collapses the four
    interior points onto the chord, which is exactly a straight line. The two
    end points never move.
    """
    if alpha < 0.0:
        alpha = 0.0
    if alpha > 1.0:
        alpha = 1.0
    p0 = control[0]
    p5 = control[DEGREE]
    out = [p0]
    for i in range(1, DEGREE):
        chord = lerp(p0, p5, i / DEGREE)
        guide = control[i]
        out.append(lerp(chord, guide, alpha))
    out.append(p5)
    return out


def overshoot(control, points):
    """How far the control points stick out of the box holding `points`, in px.

    A curve that passes through six points can still balloon far outside them:
    interpolation does not stay inside the drawn stroke. This is the number
    that tells the operator the curve is about to leave its own cage.
    """
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    worst = 0.0
    for x, y in control:
        worst = max(worst, x0 - x, x - x1, y0 - y, y - y1, 0.0)
    return worst


def clamp_inside(control, points):
    """Pull every control point into the box of `points`.

    The Bezier convex-hull property then guarantees the whole curve is inside
    that box, so the clamped curve cannot overshoot the drawn stroke at all.
    This is the quintic's version of Blender's "Auto Clamped" handle type,
    which exists for the same reason: auto handles that are not clamped
    overshoot at the extremes.
    """
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    return [(min(max(p[0], x0), x1), min(max(p[1], y0), y1)) for p in control]


def _solve_linear(matrix, rhs):
    """Gaussian elimination with partial pivoting. Small systems only."""
    n = len(rhs)
    m = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-15:
            raise ValueError("singular system")
        m[col], m[pivot] = m[pivot], m[col]
        pv = m[col][col]
        m[col] = [v / pv for v in m[col]]
        for r in range(n):
            if r == col:
                continue
            f = m[r][col]
            if f:
                m[r] = [a - f * b for a, b in zip(m[r], m[col])]
    return [m[i][n] for i in range(n)]


def fit_least_squares(points, passes=3):
    """The six control points with the smallest squared miss to `points`.

    Textbook single-span Bezier least squares (Piegl & Tiller, ch. 9): each
    sample's parameter is its arc-length fraction — the samples are already
    evenly spaced by arc length — the two end points are pinned to the drawn
    ends, and the four interior points solve the 4x4 normal equations.

    Unlike interpolation, these control points are NOT on the drawn stroke.
    That is the trade: the curve misses the stroke by less in total, but it no
    longer passes through six named points.
    """
    m = len(points)
    if m < COUNT:
        raise ValueError("least squares needs at least 6 samples, got %d" % m)
    ts = [i / (m - 1) for i in range(m)]
    basis = [[bernstein_weight(i, DEGREE, t) for i in range(1, DEGREE)] for t in ts]
    p0 = points[0]
    p5 = points[-1]
    normal = [[sum(basis[k][i] * basis[k][j] for k in range(m))
               for j in range(DEGREE - 1)] for i in range(DEGREE - 1)]
    control = [p0]
    for axis in (0, 1):
        rhs = []
        for i in range(DEGREE - 1):
            total = 0.0
            for k in range(m):
                t = ts[k]
                known = (bernstein_weight(0, DEGREE, t) * p0[axis]
                         + bernstein_weight(DEGREE, DEGREE, t) * p5[axis])
                total += basis[k][i] * (points[k][axis] - known)
            rhs.append(total)
        solved = _solve_linear(normal, rhs)
        for i in range(DEGREE - 1):
            if len(control) <= i + 1:
                control.append([0.0, 0.0])
            control[i + 1][axis] = solved[i]
    control = [p0] + [(control[i][0], control[i][1]) for i in range(1, DEGREE)] + [p5]
    if passes:
        control = _correct_parameters(control, points, passes)
    return control


def _correct_parameters(control, points, passes):
    """Piegl & Tiller 9.4.2: move each sample onto its nearest point, refit.

    One Newton step per sample per pass, the ends pinned, then the same linear
    fit at the new parameters. This is what halves the miss on a stroke that one
    span cannot follow; it is not a search over the shape, and it never runs the
    fit against a sampled objective (the mistake in PROBLEMS §5).
    """
    m = len(points)
    ts = [i / (m - 1) for i in range(m)]
    for _ in range(passes):
        for k in range(1, m - 1):
            c = evaluate(control, ts[k])
            d = derivative(control, ts[k])
            dd = second_derivative(control, ts[k])
            delta = sub(points[k], c)
            denominator = d[0] * d[0] + d[1] * d[1] + delta[0] * dd[0] + delta[1] * dd[1]
            if abs(denominator) < 1e-12:
                continue
            step = (delta[0] * d[0] + delta[1] * d[1]) / denominator
            ts[k] = min(ts[k + 1] - 1e-9, max(ts[k - 1] + 1e-9, ts[k] + step))
        control = _fit_at(control, points, ts)
    return control


def _fit_at(current, points, ts):
    """The linear fit at given sample parameters."""
    m = len(points)
    basis = [[bernstein_weight(i, DEGREE, t) for i in range(1, DEGREE)] for t in ts]
    p0 = points[0]
    p5 = points[-1]
    normal = [[sum(basis[k][i] * basis[k][j] for k in range(m))
               for j in range(DEGREE - 1)] for i in range(DEGREE - 1)]
    control = [p0]
    for axis in (0, 1):
        rhs = []
        for i in range(DEGREE - 1):
            total = 0.0
            for k in range(m):
                t = ts[k]
                known = (bernstein_weight(0, DEGREE, t) * p0[axis]
                         + bernstein_weight(DEGREE, DEGREE, t) * p5[axis])
                total += basis[k][i] * (points[k][axis] - known)
            rhs.append(total)
        solved = _solve_linear(normal, rhs)
        for i in range(DEGREE - 1):
            if len(control) <= i + 1:
                control.append([0.0, 0.0])
            control[i + 1][axis] = solved[i]
    return [p0] + [(control[i][0], control[i][1]) for i in range(1, DEGREE)] + [p5]


def low_degree(control, tolerance=1e-9):
    """The true degree of the curve, from its forward differences.

    A degree-5 Bezier whose 5th difference is zero is a quartic; with the 4th
    zero too it is a cubic, and one cubic reproduces it exactly. 68 of the 200
    curves on DeepSeek1's sheet are in this case, so the chain must not spend
    two cubics on them.
    """
    diffs = [list(control)]
    for _ in range(DEGREE):
        previous = diffs[-1]
        diffs.append([sub(previous[i + 1], previous[i]) for i in range(len(previous) - 1)])
    scale = max(1.0, max((p[0] ** 2 + p[1] ** 2) ** 0.5 for p in control))

    def is_zero(d):
        return (abs(d[0]) + abs(d[1])) <= tolerance * scale

    for degree in range(0, DEGREE):
        if all(is_zero(d) for d in diffs[degree + 1]):
            return degree
    return DEGREE


def distance_to_quintic(p, control, coarse=64, refine=24):
    """Distance from a point to the quintic, in px.

    Coarse grid for the global basin, then golden section inside it. The grid is
    deliberately fine: an early study optimised against a 24-point grid and the
    optimiser found the grid's errors before it found the curve. It is a
    measurement here, never a target.
    """
    def sq(u):
        q = evaluate(control, u)
        return (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2

    best_value = sq(0.0)
    best_u = 0.0
    for k in range(1, coarse + 1):
        u = k / coarse
        value = sq(u)
        if value < best_value:
            best_value = value
            best_u = u
    lo = max(0.0, best_u - 1.0 / coarse)
    hi = min(1.0, best_u + 1.0 / coarse)
    phi = 0.6180339887498949
    for _ in range(refine):
        a = hi - (hi - lo) * phi
        b = lo + (hi - lo) * phi
        if sq(a) < sq(b):
            hi = b
        else:
            lo = a
    u = 0.5 * (lo + hi)
    q = evaluate(control, u)
    return ((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2) ** 0.5


def fit_report(control, points):
    """(max, rms) distance from the drawn points to the quintic, in px.

    This is the number the operator's middle layer lives or dies by: how far
    the six-point curve sits from the stroke that was actually drawn.
    """
    worst = 0.0
    total = 0.0
    for p in points:
        d = distance_to_quintic(p, control)
        if d > worst:
            worst = d
        total += d * d
    return worst, (total / len(points)) ** 0.5 if points else 0.0


def split_samples(points, spans):
    """Cut a dense, arc-length-even sample list into `spans` sharing chunks.

    The boundary point belongs to both neighbours, so consecutive spans meet
    exactly and no gap is introduced at the cut.
    """
    if spans < 1:
        raise ValueError("a split needs at least one span")
    if spans == 1:
        return [list(points)]
    count = (len(points) - 1) // spans
    if count < COUNT - 1:
        raise ValueError("a dense sample list needs at least %d points per span"
                         % (COUNT * spans))
    chunks = []
    for s in range(spans):
        start = s * count
        end = (s + 1) * count if s < spans - 1 else len(points) - 1
        chunks.append(list(points[start:end + 1]))
    return chunks


def six_points_even(points):
    """Six points evenly spaced through a dense, arc-length-even sample list.

    One implementation for both the extension and the report, so the number the
    docs quote and the number the dialog produces cannot drift apart.
    """
    step = (len(points) - 1) // DEGREE
    if step < 1:
        raise ValueError("need at least %d samples for six even points" % COUNT)
    return [points[i * step] for i in range(DEGREE)] + [points[-1]]


def nodes_from_segments(segments):
    """The on-curve nodes of a cubic chain: first start, then every end point."""
    if not segments:
        raise ValueError("the guide path has no segments")
    nodes = [segments[0][0]]
    for seg in segments:
        nodes.append(seg[3])
    return nodes


def _bernstein_matrix():
    """6x6 matrix of Bernstein weights at t = k/5, as exact Fractions."""
    rows = []
    for k in range(COUNT):
        t = Fraction(k, DEGREE)
        row = []
        for i in range(COUNT):
            w = Fraction(comb(DEGREE, i))
            w *= (1 - t) ** (DEGREE - i)
            w *= t ** i
            row.append(w)
        rows.append(row)
    return rows


def solve_through_samples(samples):
    """The six control points of the quintic that passes through `samples`.

    The samples are taken at t = 0, 1/5, ..., 1, so the system is exactly
    solvable in rationals: B(t_k) = Q_k for k = 0..5. Gaussian elimination on
    Fractions, then a float copy out. This is interpolation, not a cage.
    """
    if len(samples) != COUNT:
        raise ValueError("interpolation needs exactly 6 samples, got %d" % len(samples))
    matrix = _bernstein_matrix()
    # one right-hand side per coordinate, solved together
    m = [row[:] + [Fraction(samples[k][0]), Fraction(samples[k][1])]
         for k, row in enumerate(matrix)]
    n = COUNT
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if m[pivot][col] == 0:
            raise ValueError("the six samples are degenerate; no quintic passes through them")
        m[col], m[pivot] = m[pivot], m[col]
        pv = m[col][col]
        m[col] = [v / pv for v in m[col]]
        for r in range(n):
            if r == col:
                continue
            f = m[r][col]
            if f == 0:
                continue
            m[r] = [a - f * b for a, b in zip(m[r], m[col])]
    control = [(float(m[i][n]), float(m[i][n + 1])) for i in range(n)]
    return control


def interpolation_residual(control, samples):
    """Largest distance between B(t_k) and the sample at t_k, in pixels."""
    worst = 0.0
    for k, s in enumerate(samples):
        b = evaluate(control, k / DEGREE)
        worst = max(worst, abs(b[0] - s[0]), abs(b[1] - s[1]))
    return worst


# ---------------------------------------------------------------------------
# the guide path, sampled by arc length
# ---------------------------------------------------------------------------


def evaluate_cubic(seg, t):
    (p0, c1, c2, p3) = seg
    mt = 1.0 - t
    a = mt * mt * mt
    b = 3.0 * mt * mt * t
    c = 3.0 * mt * t * t
    d = t * t * t
    return (a * p0[0] + b * c1[0] + c * c2[0] + d * p3[0],
            a * p0[1] + b * c1[1] + c * c2[1] + d * p3[1])


def _cubic_length(seg, steps=32):
    total = 0.0
    prev = seg[0]
    for s in range(1, steps + 1):
        cur = evaluate_cubic(seg, s / steps)
        total += ((cur[0] - prev[0]) ** 2 + (cur[1] - prev[1]) ** 2) ** 0.5
        prev = cur
    return total


def samples_along(segments, fractions, steps=32):
    """Points at the given arc-length fractions (0 = start, 1 = end).

    Each cubic is flattened into `steps` chords to build a length table, so the
    sampling error is below the chord sag, not visible at drawing scale.
    """
    lengths = [_cubic_length(seg, steps) for seg in segments]
    total = sum(lengths)
    if total <= 0.0:
        raise ValueError("the guide path has zero length")
    points = []
    for f in fractions:
        target = max(0.0, min(1.0, f)) * total
        walked = 0.0
        for seg, seg_len in zip(segments, lengths):
            if target <= walked + seg_len or seg is segments[-1]:
                u = 0.0 if seg_len == 0 else (target - walked) / seg_len
                u = max(0.0, min(1.0, u))
                points.append(evaluate_cubic(seg, u))
                break
            walked += seg_len
    return points


# ---------------------------------------------------------------------------
# the cubic chain: C2 spline through the quintic's own stations
# ---------------------------------------------------------------------------


def _solve_tridiagonal(lower, diag, upper, rhs):
    """Thomas algorithm. The spline matrix is diagonally dominant, so this is stable."""
    n = len(diag)
    c = upper[:]
    d = rhs[:]
    b = diag[:]
    for i in range(1, n):
        w = lower[i] / b[i - 1]
        b[i] -= w * c[i - 1]
        d[i] -= w * d[i - 1]
    x = [0.0] * n
    x[-1] = d[-1] / b[-1]
    for i in range(n - 2, -1, -1):
        x[i] = (d[i] - c[i] * x[i + 1]) / b[i]
    return x


def _knot_tangents(points, h, d0, dm):
    """Tangent vectors at the knots of a clamped C2 cubic spline.

    With control points b1 = q[j] + (h/3) d[j] and b2 = q[j+1] - (h/3) d[j+1],
    the cubic's second derivative at its ends is

        B''(0) = 6(q[j+1] - q[j]) - 4 h d[j] - 2 h d[j+1]
        B''(1) = -6(q[j+1] - q[j]) + 2 h d[j] + 4 h d[j+1]

    so equal second derivatives across the joint at knot j give

        h[j-1] d[j-1] + 2(h[j-1] + h[j]) d[j] + h[j] d[j+1]
            = 3 (Δ[j-1] + Δ[j]),      Δ[j] = q[j+1] - q[j].

    The two end tangents are the quintic's own, so the chain leaves and arrives
    on exactly the same tangent as the curve it replaces. The first version of
    this solve carried a 1/h factor from a Hermite parameterisation mixed with
    a Bezier one; it left a 467 px second-derivative gap at the joints and is
    the fault registered in `state/PROBLEMS-quintic-guide-int.md`.
    """
    m = len(h)
    n = m + 1  # every knot, including the two clamped ends
    lower = [0.0] * n
    diag = [0.0] * n
    upper = [0.0] * n
    rhs_x = [0.0] * n
    rhs_y = [0.0] * n
    diag[0] = 1.0
    rhs_x[0] = d0[0]
    rhs_y[0] = d0[1]
    diag[-1] = 1.0
    rhs_x[-1] = dm[0]
    rhs_y[-1] = dm[1]
    for j in range(1, m):
        prev = sub(points[j], points[j - 1])
        nxt = sub(points[j + 1], points[j])
        lower[j] = h[j - 1]
        diag[j] = 2.0 * (h[j - 1] + h[j])
        upper[j] = h[j]
        rhs_x[j] = 3.0 * (prev[0] + nxt[0])
        rhs_y[j] = 3.0 * (prev[1] + nxt[1])
    tang_x = _solve_tridiagonal(lower, diag, upper, rhs_x)
    tang_y = _solve_tridiagonal(lower, diag, upper, rhs_y)
    return [(tang_x[k], tang_y[k]) for k in range(n)]


def cubic_chain(control, segments, knots=None):
    """A C2 cubic Bezier chain through (segments + 1) stations of the quintic.

    The stations are exact, the two end tangents are exact, and the chain is
    C2 at every interior joint. Between the stations it is an approximation,
    and its size is measured rather than assumed.

    `knots` overrides the station parameters (equal arc length, say, instead of
    equal t); the segment count is then taken from the knot list.
    """
    if knots is not None:
        ts = list(knots)
        segments = len(ts) - 1
    if segments < 1:
        raise ValueError("a chain needs at least one cubic segment")
    if knots is None:
        ts = [i / segments for i in range(segments + 1)]
    points = [evaluate(control, t) for t in ts]
    h = [ts[i + 1] - ts[i] for i in range(segments)]
    tangents = _knot_tangents(points, h, derivative(control, 0.0), derivative(control, 1.0))
    chain = []
    for i in range(segments):
        b0 = points[i]
        b3 = points[i + 1]
        b1 = add(b0, scale(tangents[i], h[i] / 3.0))
        b2 = sub(b3, scale(tangents[i + 1], h[i] / 3.0))
        chain.append((b0, b1, b2, b3))
    return chain


def _distance_to_cubic(p, seg, coarse=16, refine=24):
    """Distance from p to the cubic, not to its polyline.

    The first version flattened each cubic into chords and measured to those,
    which put a 0.02 px floor under every error figure — a floor bigger than
    the 0.001 px the whole exercise is about. Coarse scan for the basin, then
    golden-section inside it.
    """
    def sq(u):
        q = evaluate_cubic(seg, u)
        return (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2

    best_u = 0.0
    best = sq(0.0)
    for k in range(1, coarse + 1):
        u = k / coarse
        v = sq(u)
        if v < best:
            best = v
            best_u = u
    lo = max(0.0, best_u - 1.0 / coarse)
    hi = min(1.0, best_u + 1.0 / coarse)
    phi = 0.6180339887498949
    for _ in range(refine):
        a = hi - (hi - lo) * phi
        b = lo + (hi - lo) * phi
        if sq(a) < sq(b):
            hi = b
        else:
            lo = a
    u = 0.5 * (lo + hi)
    q = evaluate_cubic(seg, u)
    return ((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2) ** 0.5


def _as_fractions(points, rationalise=False):
    """Points as Fractions.

    `rationalise=True` snaps a float to the nearest simple fraction first
    (0.3333333333333333 becomes 1/3). The PH decision is about exact algebra, so
    a float that is only *nearly* a third turns a perfect square into a mess of
    noise; snapping recovers the number the operator actually typed.
    """
    def one(v):
        if isinstance(v, Fraction):
            return v
        f = Fraction(v)
        return f.limit_denominator(10 ** 9) if rationalise else f

    return [(one(p[0]), one(p[1])) for p in points]


def split_bezier(points, t):
    """de Casteljau split at t. Returns (left, right), both the same degree."""
    t = Fraction(t) if not isinstance(t, Fraction) else t
    def flerp(a, b):
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

    rows = [list(points)]
    while len(rows[-1]) > 1:
        rows.append([flerp(a, b) for a, b in zip(rows[-1], rows[-1][1:])])
    left = [row[0] for row in rows]
    right = [row[-1] for row in reversed(rows)]
    return left, right


def elevate(points):
    """Raise a Bezier by one degree, exactly. c_i = (i/(n+1)) b_(i-1) + (1-i/(n+1)) b_i."""
    n = len(points) - 1
    out = [points[0]]
    for i in range(1, n + 1):
        a = Fraction(i, n + 1)
        out.append((a * points[i - 1][0] + (1 - a) * points[i][0],
                    a * points[i - 1][1] + (1 - a) * points[i][1]))
    out.append(points[-1])
    return out


def cubic_to_quintic(segment):
    """A cubic Bezier raised twice, so it can be compared with a quintic."""
    p0, c1, c2, p3 = _as_fractions(segment)
    return elevate(elevate([p0, c1, c2, p3]))


def _sub_poly(a, b):
    return (a[0] - b[0], a[1] - b[1])


def _norm(p):
    return (p[0] * p[0] + p[1] * p[1]) ** 0.5


def chain_error_bound(control, chain):
    """A proved upper bound on |quintic(t) - chain(t)|, in px, per segment.

    The quintic is split at each station by de Casteljau, the cubic is raised to
    degree 5, and the six differences are the control points of the difference
    curve. A Bezier lies inside the convex hull of its control points, so the
    largest difference coefficient is an upper bound — no sampling, and no way
    for the bound to sit below the truth.

    Returns (worst_bound, per_segment_bounds).
    """
    stations = len(chain)
    bounds = []
    if stations < 1:
        raise ValueError("the chain is empty")
    # the quintic's sub-curves, split at every station, in exact rationals
    pieces = []
    remaining = _as_fractions(control)
    # split off each station from the left in turn
    for index in range(stations):
        left, remaining = split_bezier(remaining, Fraction(1, stations - index))
        pieces.append(left)
    worst = 0.0
    for piece, seg in zip(pieces, chain):
        raised = cubic_to_quintic(seg)
        differences = [_sub_poly(a, b) for a, b in zip(piece, raised)]
        bound = max(_norm(d) for d in differences)
        bounds.append(bound)
        if bound > worst:
            worst = bound
    return worst, bounds



def measure_max_error(control, chain, samples=None, knots=None):
    """Largest distance from the quintic to the cubic chain, in pixels.

    Each quintic sample is measured against the chain segment it belongs to, so
    the cost does not grow with the segment count. That is a slight
    over-estimate — a neighbour can be closer — and an over-estimate is the safe
    direction for a stated error.

    `knots` must be passed when the stations are not at equal t: with
    arc-length knots, `int(t * n)` picks the wrong segment and reports a miss
    that belongs to a different stretch of the curve.
    """
    n = len(chain)
    if samples is None:
        samples = max(120, 24 * n)
    if knots is None:
        knots = [i / n for i in range(n + 1)]
    worst = 0.0
    for k in range(samples + 1):
        t = k / samples
        i = bisect.bisect_right(knots, t) - 1
        i = 0 if i < 0 else (n - 1 if i > n - 1 else i)
        d = _distance_to_cubic(evaluate(control, t), chain[i])
        if d > worst:
            worst = d
    return worst


def fit_to_tolerance(control, tolerance, start=None, max_segments=32, knots=None):
    """Smallest chain (from `start`) whose measured error is within tolerance.

    Returns (chain, measured_error, segment_count). If even `max_segments`
    is not enough, the last chain is returned with its true error, so the
    caller can print the miss instead of claiming a fit it does not have.
    """
    if start is None:
        start = 1 if low_degree(control) <= 3 else 2
    segments = max(1, start)
    chain = cubic_chain(control, segments)
    err = measure_max_error(control, chain)
    # accept only when the PROVED bound is inside the tolerance: the measured
    # number runs about 1.6-2.1x below the bound, so fitting to the measurement
    # alone quietly overshoots the promise
    bound, _ = chain_error_bound(control, chain)
    while bound > tolerance and segments < max_segments:
        segments = min(max_segments, segments * 2)
        chain = cubic_chain(control, segments)
        err = measure_max_error(control, chain)
        bound, _ = chain_error_bound(control, chain)
    return chain, err, segments


# ---------------------------------------------------------------------------
# writing: the SVG path, and the two exact bridges
# ---------------------------------------------------------------------------


def num(v, precision=6):
    """A plain decimal, never an exponent, and never a bare -0."""
    s = ("%.*f" % (precision, v)).rstrip("0").rstrip(".")
    if s in ("-0", ""):
        return "0"
    return s


def chain_to_d(chain, precision=6):
    """The chain as SVG path data: one M, then one C per segment."""
    if not chain:
        raise ValueError("empty chain")
    head = "M %s,%s" % (num(chain[0][0][0], precision), num(chain[0][0][1], precision))
    parts = [head]
    for (_, c1, c2, p3) in chain:
        parts.append("C %s,%s %s,%s %s,%s" % (
            num(c1[0], precision), num(c1[1], precision),
            num(c2[0], precision), num(c2[1], precision),
            num(p3[0], precision), num(p3[1], precision)))
    return " ".join(parts)


def to_y_up(control):
    """SVG is y down; the shared record, Blender and GeoGebra are y up.

    This is the ONE flip. The document keeps the path it drew; everything that
    leaves Inkscape goes through here, so a y never gets flipped twice.
    """
    return [(p[0], -p[1]) for p in control]


def _flip(control):
    """Deprecated name kept for the old callers: now just `to_y_up`."""
    return to_y_up(control)


def sidecar(control, alpha, pointmode, segments, error, guide_id=""):
    """The record: the six control points as the truth, the chain as the view."""
    return {
        "kind": "quintic-bezier",
        "degree": DEGREE,
        "endpoint": True,
        "guide_id": guide_id,
        "pointmode": pointmode,
        "fullness_alpha": round(alpha, 6),
        "control_svg_y_down": [[round(p[0], 9), round(p[1], 9)] for p in control],
        "cubic_segments": segments,
        "cubic_error_px": round(error, 9),
        "note": ("control_svg_y_down is the exact quintic in SVG coordinates "
                 "(y down). The cubic chain is only the drawing."),
    }


def sidecar_many(spans, mode, alpha, guide_id="", note=None, options=None):
    """The shared record, format `curve-lab.quintic/1`.

    This is the contract with the curve-lab side (state/QUINTIC-CONTRACT-int.md):
    **y up**, six control points per curve, numbers not strings, and the two
    measured misses. The SVG document keeps its own y-down path; this is the
    only flip.
    """
    curves = []
    for index, span in enumerate(spans):
        row = {
            "index": index,
            "control": [[round(p[0], 9), round(p[1], 9)]
                        for p in to_y_up(span["control"])],
            "exact_degree": span.get("exact_degree", DEGREE),
            "weighted": False,
            "ph": bool(span.get("ph", False)),
            "cusps": int(span.get("cusps", 0)),
            "quintic_to_chain": {
                "max_px": round(span["chain_miss"], 9),
                "proved_bound_px": round(span.get("bound", 0.0), 9),
                "cubic_segments": span["segments"],
            },
        }
        if "fit_max" in span:
            row["drawn_to_quintic"] = {
                "max_px": round(span["fit_max"], 9),
                "rms_px": round(span["fit_rms"], 9),
            }
        curves.append(row)
    record = {
        "format": "curve-lab.quintic/1",
        "degree": DEGREE,
        "order": DEGREE + 1,
        "axes": {"x": "right", "y": "up", "units": "px"},
        "source": "extension",
        "guide": {
            "id": guide_id,
            "pointmode": mode,
            "fullness": round(alpha, 6),
            "spans": len(spans),
            "options": options or {},
        },
        "curves": curves,
        "note": note or ("y is up. Each control list is the exact quintic; the "
                         "cubic chain in the document is only the drawing. "
                         "Spans join C0 unless seams were smoothed."),
    }
    return record


def blender_script_many(controls, name="Quintic", flip_y=True):
    """A paste-into-Blender script: one exact degree-5 NURBS spline per span.

    Cardano's trap, learned the hard way: Blender clamps order_u to the point
    count silently, so 6 points + order_u = 6 + use_endpoint_u is the only
    combination that is one exact quintic span. Several spans become several
    splines in one object; they meet C0, which is what the drawing does.
    """
    flip_note = ("# y flipped: Blender is y up, the SVG document is y down.\n"
                 if flip_y else "# y not flipped.\n")
    blocks = []
    for index, control in enumerate(controls):
        pts = _flip(control) if flip_y else list(control)
        rows = ",\n        ".join("(%.9f, %.9f, 0.0)" % (p[0], p[1]) for p in pts)
        blocks.append(
            "P = [\n        %s,\n    ]\n"
            "sp = cu.splines.new('NURBS')\n"
            "sp.points.add(len(P) - 1)\n"
            "for vert, co in zip(sp.points, P):\n"
            "    vert.co = (co[0], co[1], co[2], 1.0)\n"
            "sp.order_u = 6\n"
            "sp.use_endpoint_u = True\n"
            "sp.resolution_u = 24\n" % rows)
    body = "\n".join(blocks)
    return (
        "import bpy\n"
        "# Exact quintic Bezier: 6 control points, order_u = 6, clamped ends.\n"
        + flip_note +
        "name = %r\n" % name +
        "cu = bpy.data.curves.new(name, 'CURVE')\n"
        "cu.dimensions = '2D'\n"
        + body +
        "ob = bpy.data.objects.new(name, cu)\n"
        "bpy.context.collection.objects.link(ob)\n"
        "bpy.context.view_layer.objects.active = ob\n"
        "print('quintic: spans=%d control=%s order_u=%d' % "
        "(len(cu.splines), [len(sp.points) for sp in cu.splines], 6))\n"
    )


def blender_script(control, name="Quintic", flip_y=True):
    """One span: the single-span form of blender_script_many."""
    return blender_script_many([control], name=name, flip_y=flip_y)


def geogebra_commands_many(controls, flip_y=True):
    """Input-bar commands: the points, then the exact Bernstein curve per span."""
    lines = []
    multiple = len(controls) > 1
    for index, control in enumerate(controls):
        pts = _flip(control) if flip_y else list(control)
        prefix = "S%d_" % (index + 1) if multiple else ""
        for i, p in enumerate(pts):
            lines.append("%sP%d = (%.9f, %.9f)" % (prefix, i, p[0], p[1]))
        curve_name = "C%d(t)" % (index + 1) if multiple else "Q(t)"
        lines.append(
            "%s = (1-t)^5*%sP0 + 5*(1-t)^4*t*%sP1 + 10*(1-t)^3*t^2*%sP2"
            " + 10*(1-t)^2*t^3*%sP3 + 5*(1-t)*t^4*%sP4 + t^5*%sP5"
            % (curve_name, prefix, prefix, prefix, prefix, prefix, prefix))
    if flip_y:
        lines.append("# y flipped: GeoGebra is y up, the SVG document is y down.")
    return "\n".join(lines) + "\n"


def geogebra_commands(control, flip_y=True):
    """One span: the single-span form of geogebra_commands_many."""
    return geogebra_commands_many([control], flip_y=flip_y)


def ggb_from_commands(control):
    """GeoGebra's own .ggb is a zip; the command list is the portable form."""
    return geogebra_commands(control)


def inflection_parameters(control, samples=400, tolerance=1e-9):
    """Parameters where the curvature changes sign, found by sign changes.

    The cross product B' x B'' is a polynomial in t; a sign change is an
    inflection. A curve that is straight (the cross product identically zero) has
    none, and a zero *run* is not a crossing — an early version reported 400
    "inflections" on a straight line, which is how the guard below got written.
    """
    def cross(t):
        d = derivative(control, t)
        dd = second_derivative(control, t)
        return d[0] * dd[1] - d[1] * dd[0]

    values = [cross(k / samples) for k in range(samples + 1)]
    speeds = []
    for k in range(0, samples + 1, max(1, samples // 40)):
        d = derivative(control, k / samples)
        speeds.append((d[0] * d[0] + d[1] * d[1]) ** 0.5)
    scale = max(speeds) ** 3 if speeds else 1.0
    if scale <= 0.0 or max(abs(v) for v in values) <= 1e-9 * scale:
        return []

    # sign changes are read between the nearest NON-ZERO samples, so a root that
    # lands exactly on a sample (the symmetric S) is found, and a zero run
    # (a straight line) yields no crossings at all
    nonzero = [(k / samples, values[k]) for k in range(samples + 1) if values[k] != 0.0]
    found = []
    for (t0, v0), (t1, v1) in zip(nonzero, nonzero[1:]):
        if (v0 < 0.0) == (v1 < 0.0):
            continue
        low, high = t0, t1
        for _ in range(60):
            middle = 0.5 * (low + high)
            if (cross(low) < 0.0) == (cross(middle) < 0.0):
                low = middle
            else:
                high = middle
        root = 0.5 * (low + high)
        if tolerance < root < 1.0 - tolerance:
            found.append(root)
    unique = []
    for value in found:
        if not unique or abs(value - unique[-1]) > 1e-4:
            unique.append(value)
    return unique
