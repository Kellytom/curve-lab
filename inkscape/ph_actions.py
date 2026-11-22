# The closed vocabulary of Inkscape edits, exactly.
#
# The operator's design (2026-11-21): restrict the user to actions whose
# effect on the speed rows is exact algebra, so sending a curve to Inkscape
# and back is arithmetic, not approximation. There is no re-fit: the recipe
# (the speed rows) is the truth, the SVG is a view, and every permitted
# action maps to a formula below that keeps the curve Pythagorean-hodograph
# and keeps its degree.
#
# A placement is (offset_x, offset_y, a, b, q, m) in exact Fractions:
# the drawn curve is  R · ∫((u+iv) placed)² + offset, where the placed speed
# is (a + ib)(u + iv), then conjugated when m = −1. The rotation's φ is the
# HALF angle with rational cosine and sine (a p-triple: a² + b² = 1) — the
# half angle is what makes rotation exact, because doubling the angle stays
# rational: cos 2φ = a² − b², sin 2φ = 2ab. The mirror is a conjugation,
# which is why it is a flag and not a rotation: (u + iv) → its conjugate
# negates y' and keeps x'. Scale is a rational q (speed ×q, position ×q² —
# the square comes free in the derivative); a scale that is not a rational
# square root of the wanted factor would need √q in the speed.
#
# Refusals carry a miss in curve units, never a percentage.

from fractions import Fraction

Frac = Fraction


# ── placements ──────────────────────────────────────────────────────────────

def identity_placement():
    return {"dx": Frac(0), "dy": Frac(0), "a": Frac(1), "b": Frac(0),
            "q": Frac(1), "m": 1}


def place_rows(rows_x, rows_y, placement):
    """The drawn curve's speed rows after the placement's own transforms:
    the half-angle rotation (a + ib), then conjugation when mirrored, then
    the scale q. The offset does not touch the rows."""
    a, b, q, m = placement["a"], placement["b"], placement["q"], placement["m"]
    out_x, out_y = [], []
    for u, v in zip(rows_x, rows_y):
        ru, rv = (a * u - b * v) * q, (b * u + a * v) * q
        out_x.append(ru if m == 1 else ru)
        out_y.append(rv if m == 1 else -rv)
    return out_x, out_y


def position_of(rows_x, rows_y, placement):
    """The exact position polynomial with the placement applied.

    The integral is coefficient-wise (curve_lab/measure.py's law): the
    antiderivative of Σ c_k t^k is Σ c_k t^(k+1)/(k+1) — never a running
    sum (register 91's fault). The scale's square comes free in the
    derivative (the speed is already ×q, so the squared rows are ×q²)."""
    ux, vy = place_rows(rows_x, rows_y, placement)
    xs = [(u * u - v * v) for u, v in zip(ux, vy)]
    ys = [2 * (u * v) for u, v in zip(ux, vy)]

    def integral(row):
        return [Frac(0)] + [c / (j + 1) for j, c in enumerate(row)]

    px, py = integral(xs), integral(ys)
    # The rotation and the mirror are already in the placed rows: squaring
    # the placed speed applies the double angle (and the conjugation) to the
    # derivative, and integrating coefficient-wise keeps it. The offset is a
    # TRANSLATION — it enters the constant term alone; adding it to every
    # coefficient would slide the curve differently at each t (register 55).
    px[0] = px[0] + placement["dx"]
    py[0] = py[0] + placement["dy"]
    return px, py


# ── the actions ─────────────────────────────────────────────────────────────

def act_translate(placement, dx, dy):
    """Move the curve by (dx, dy). Exact; the degree is untouched."""
    return {**placement, "dx": placement["dx"] + Frac(dx), "dy": placement["dy"] + Frac(dy)}


def act_rotate_p_triple(placement, a, b):
    """Rotate by the double of the half angle with rational cosine a and
    sine b — given directly as the reduced (a, b) with a² + b² = 1. The
    placement stores the HALF angle (the speed's factor (a + ib)); composing
    two half angles is complex multiplication, and the position's rotation
    (the double angle) is derived from it in position_of."""
    a, b = Frac(a), Frac(b)
    if a * a + b * b != 1:
        raise ValueError(f"the half angle must be a unit p-triple, got (a, b) = ({a}, {b})")
    oa, ob = placement["a"], placement["b"]
    return {**placement,
            "a": oa * a - ob * b,
            "b": oa * b + ob * a}


def act_scale_square(placement, q):
    """Scale the curve by q² — the speed picks up q, the position q².
    Exact; the degree is untouched."""
    q = Frac(q)
    if q == 0:
        raise ValueError("a zero scale erases the curve")
    return {**placement, "q": placement["q"] * q}


def act_mirror_x(placement):
    """(x, y) → (x, −y): a conjugation, so it is a flag, not a rotation.
    Exact."""
    return {**placement, "m": -placement["m"], "dy": -placement["dy"]}


def act_end_edit(rows_x, rows_y, du_top, dv_top):
    """Replace the top coefficients of u and v — the end tangent and end
    speed handles. Exact; the degree is untouched (zeros stay zeros)."""
    if not du_top and not dv_top:
        return rows_x, rows_y
    out_x, out_y = list(rows_x), list(rows_y)
    degree = max(len(out_x), len(out_y)) - 1
    if du_top:
        while len(out_x) < degree + 1:
            out_x.append(Frac(0))
        out_x[degree] = out_x[degree] + Frac(du_top)
    if dv_top:
        while len(out_y) < degree + 1:
            out_y.append(Frac(0))
        out_y[degree] = out_y[degree] + Frac(dv_top)
    return out_x, out_y


def act_recipe_swap(registry, uid):
    """Take another curve's rows from the registry — the parameter edit.
    Exact, because the registry is the record. Returns (rows, name)."""
    from curve_lab.measure import to_fraction
    for record in registry["curves"]:
        if record["uid"] == uid:
            return ([to_fraction(v) for v in record["speedX"]],
                    [to_fraction(v) for v in record["speedY"]], record["name"])
    raise KeyError(f"no curve {uid} in the registry")


def degree_of(rows_x, rows_y):
    """The position degree: 2 × speed degree + 1, read off the rows."""
    def trimmed(row):
        row = list(row)
        while row and row[-1] == 0:
            row.pop()
        return len(row) - 1
    return 2 * max(trimmed(rows_x), trimmed(rows_y)) + 1


def degree_gate(rows_x, rows_y, ceiling):
    """The editor's refusal: the degree read from the rows before drawing."""
    degree = degree_of(rows_x, rows_y)
    if degree > ceiling:
        return False, degree
    return True, degree


# ── snapping ────────────────────────────────────────────────────────────────

def legal_handle_positions(rows_x, rows_y, placement, registry=None, ceiling=11):
    """Where each permitted action would put the END handle (the curve's
    point at t = 1), exactly. This is the closed set the snapper chooses
    from: end-edit steps on the grid's coarse unit, recipe swaps to every
    curve inside the ceiling, and the rigid motions at their unit steps."""
    # the base curve's handle
    px, py = position_of(rows_x, rows_y, placement)
    base = (px[-1], py[-1])
    spots = [{"action": "stay", "point": base, "miss": Frac(0)}]

    # end-edit steps: ±1 in the top coefficient of u and of v, at the grid
    # unit of the curve's own size
    unit = _grid_unit(rows_x, rows_y)
    for sign in (1, -1):
        ex, ey = act_end_edit(rows_x, rows_y, sign * unit, 0)
        ok, _ = degree_gate(ex, ey, ceiling)
        if ok:
            sx, sy = position_of(ex, ey, placement)
            spots.append({"action": f"end-edit u{'+' if sign > 0 else '-'}{unit}",
                          "point": (sx[-1], sy[-1]),
                          "miss": Frac(0)})
        ex, ey = act_end_edit(rows_x, rows_y, 0, sign * unit)
        ok, _ = degree_gate(ex, ey, ceiling)
        if ok:
            sx, sy = position_of(ex, ey, placement)
            spots.append({"action": f"end-edit v{'+' if sign > 0 else '-'}{unit}",
                          "point": (sx[-1], sy[-1]),
                          "miss": Frac(0)})

    # recipe swaps: every registry curve inside the ceiling
    if registry:
        from curve_lab.measure import to_fraction
        for record in registry["curves"]:
            if not record.get("speedX"):
                continue
            rx = [to_fraction(v) for v in record["speedX"]]
            ry = [to_fraction(v) for v in record["speedY"]]
            ok, degree = degree_gate(rx, ry, ceiling)
            if ok:
                sx, sy = position_of(rx, ry, placement)
                spots.append({"action": f"recipe {record['uid']}",
                              "point": (sx[-1], sy[-1]),
                              "miss": Frac(0)})

    # rigid motions at one unit step
    for dx, dy, name in ((unit, 0, "translate +x"), (-unit, 0, "translate −x"),
                         (0, unit, "translate +y"), (0, -unit, "translate −y")):
        moved = act_translate(placement, dx, dy)
        sx, sy = position_of(rows_x, rows_y, moved)
        spots.append({"action": name, "point": (sx[-1], sy[-1]), "miss": Frac(0)})
    return spots


def _grid_unit(rows_x, rows_y):
    """The curve's own coarse unit: one over the largest position
    coefficient's denominator, so the handle steps land on the grid."""
    from math import gcd

    def lcm(a, b):
        return a * b // gcd(a, b)

    denom = 1
    for row in (rows_x, rows_y):
        for c in row:
            if c:
                denom = lcm(denom, c.denominator)
    return Frac(1, denom)


def snap(target, spots, tolerance):
    """Choose the legal spot nearest `target`. Returns (action, miss) or
    (None, miss) when nothing is within the tolerance — a refusal that
    states the miss in units, never a percentage."""
    best, best_miss = None, None
    for spot in spots:
        px, py = spot["point"]
        miss = abs(Frac(px) - Frac(target[0])) + abs(Frac(py) - Frac(target[1]))
        if best_miss is None or miss < best_miss:
            best, best_miss = spot["action"], miss
    if best_miss is not None and best_miss <= Frac(tolerance):
        return best, best_miss
    return None, best_miss
