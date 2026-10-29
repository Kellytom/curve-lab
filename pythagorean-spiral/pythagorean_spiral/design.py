"""Named chains, each ending exactly on an axis.

All three use the same convention as `Spiral`: the first chord lies on the
starting heading, so the turn applied at node k is `k*alpha` for the spiral and
the coefficient bookkeeping is offset by one from the "first chord already
turned" convention used in the notes this was checked against.

Every builder asserts the turn coefficient is exactly zero.  That is not
decoration: `closure.py` proves no other exact axis landing exists.
"""

from __future__ import annotations

import math

from .closure import closure_pairs, g2_pairs, inverse_triangular, triangular
from .spiral import Spiral, triangular
from .triples import Triple, for_angle


def spiral(triangle: Triple, steps: int, length=1) -> Spiral:
    """A plain Euler spiral: turns 0, 1, 2, ..., steps-1."""
    path = Spiral(triangle, length)
    path.extend(range(0, steps))
    return path


def lobe(triangle: Triple, steps: int, length=1) -> Spiral:
    """Out with growing curvature, back with it reversed.  Sharp apsis.

    Turns 0..n-1, then -(n-1)..0.  The heading peaks at `T(n-1)*alpha`, the
    curvature flips sign there, and the sum is zero, so the exit is exactly
    parallel to the entry.
    """
    path = Spiral(triangle, length)
    path.extend(range(0, steps))
    path.extend(range(-(steps - 1), 1))
    _assert_closed(path)
    return path


def hook(triangle: Triple, multiplier: int, n_out: int | None = None,
         length=1) -> Spiral:
    """Spiral in on 1, 2, 3..., unwind on -m, -2m, ...  Sharp apsis.

    The unwind is `multiplier` times faster than the wind, which is what makes
    a teardrop rather than a symmetric lobe.  Only pairs where the turn sums
    cancel exist; `n_out` defaults to the first one found.
    """
    pairs = closure_pairs(multiplier)
    if not pairs:
        raise ValueError(f"no exact closure for multiplier {multiplier}")
    if n_out is None:
        n_in, n_out = pairs[0]
    else:
        match = [p for p in pairs if p[1] == n_out]
        if not match:
            raise ValueError(
                f"multiplier {multiplier} does not close with {n_out} out-steps; "
                f"try {[p[1] for p in pairs]}")
        n_in, n_out = match[0]
    path = Spiral(triangle, length)
    path.extend(range(0, n_in + 1))          # n_in + 1 chords, sum T(n_in)
    path.extend(-multiplier * k for k in range(1, n_out + 1))
    _assert_closed(path)
    return path


def g2_lobe(triangle: Triple, steps: int, length=1) -> Spiral:
    """The same lobe with the curvature continuous at the apsis.

    Turns 0..n-1, then n-1, n-2, ..., 0, -1, ..., -j, where j(j+1) = 2n(n-1).
    The exit opens at exactly the entry's final curvature, so the join is G2.
    Solutions are sparse: n = 3, 15, 85, ...
    """
    m = steps - 1
    j = inverse_triangular(2 * triangular(m))
    if j is None:
        raise ValueError(
            f"no G2 closure for {steps} steps; try "
            f"{[m + 1 for m, _ in g2_pairs(60)]}")
    path = Spiral(triangle, length)
    path.extend(range(0, steps))
    path.extend(range(m, -1, -1))
    path.extend(-k for k in range(1, j + 1))
    _assert_closed(path)
    return path


def _assert_closed(path: Spiral) -> None:
    if path.coeff != 0:
        raise AssertionError(f"chain does not close: coefficient {path.coeff}")
    if not path.heading.is_axis_aligned():
        raise AssertionError(f"chain does not end on an axis: {path.heading}")


def curl(peak: float = 200.0, chord: float = 6.0, length=1) -> Spiral:
    """A volute whose smoothness you ask for in degrees.

    `peak` is the heading at the apsis; `chord` is the widest turn any single
    chord may take, which fixes the triangle -- the thinner the triangle, the
    smoother the drawn curve, at the cost of a longer hypotenuse.  The step
    count follows from the two: T(n-1)*alpha = peak.

    Two numbers instead of three, and neither is a hairiness knob you have to
    tune by eye: the chord budget *is* the resolution.
    """
    if not 0 < chord < 45:
        raise ValueError(f"chord budget must be in (0, 45) degrees, got {chord}")
    if not 0 < peak < 720:
        raise ValueError(f"peak must be in (0, 720) degrees, got {peak}")

    rough = max(3, math.ceil(2 * peak / chord) + 1)
    triangle = for_angle(chord / (rough - 1))
    alpha = triangle.degrees
    steps = max(2, int(round((-1 + math.sqrt(1 + 8 * peak / alpha)) / 2)) + 1)
    # exactness is carried by integers over a power of the hypotenuse, so the
    # cost is set by c^T(steps-1). Guard it rather than hang for ten minutes.
    digits = triangular(steps - 1) * math.log10(triangle.c)
    if digits > 25_000:
        raise ValueError(
            f"chord {chord} deg needs about {digits:.0f}-digit integers at "
            f"c={triangle.c}; the exact chain stops being practical here, "
            f"use a chord budget of 4 deg or more")
    return lobe(triangle, steps, length)
