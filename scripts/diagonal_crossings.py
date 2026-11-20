#!/usr/bin/env python3
"""Where a hybrid crosses the line y = x — solved, not scanned.

    .venv/bin/python scripts/diagonal_crossings.py 3 4

The curve is x = C(t)^p, y = S(t)^q with

    C(t) = (1 − t²)/(1 + t²),   S(t) = 2t/(1 + t²).

The line y = x therefore gives

    (1 − t²)^p (1 + t²)^q  =  (2t)^q (1 + t²)^p

a polynomial in t with integer coefficients (degree 2p + 2q at most). Its real roots are the
crossings. They are isolated with a **Sturm sequence** and refined by bisection, so nothing
is found by walking the drawn polygon.

The radial scale cancels: for the radius use the point is (x·P, y·P), and y·P = x·P is the
same equation wherever P ≠ 0.
"""

from __future__ import annotations

import sys
from fractions import Fraction


def poly_mul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def poly_add(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n)]


def poly_scale(a, k):
    return [k * x for x in a]


def poly_sub(a, b):
    return poly_add(a, poly_scale(b, -1))


def poly_derivative(a):
    return [i * a[i] for i in range(1, len(a))] or [0]


def poly_divmod(a, b):
    a = list(a)
    b = [x for x in b]
    while b and b[-1] == 0:
        b.pop()
    if not b:
        raise ZeroDivisionError("divide by zero polynomial")
    q = [0] * max(1, len(a) - len(b) + 1)
    while len(a) >= len(b) and any(a):
        while a and a[-1] == 0:
            a.pop()
        if len(a) < len(b):
            break
        factor = Fraction(a[-1], b[-1])
        shift = len(a) - len(b)
        q[shift] = factor
        for i, x in enumerate(b):
            a[i + shift] -= factor * x
        while a and a[-1] == 0:
            a.pop()
    return q, a or [0]


def poly_eval(a, x):
    total = Fraction(0)
    for coefficient in reversed(a):
        total = total * x + coefficient
    return total


def sturm_chain(a):
    """p, p', −rem(p, p'), … — the sequence whose sign changes count the real roots."""
    chain = [a, poly_derivative(a)]
    while True:
        _, remainder = poly_divmod(chain[-2], chain[-1])
        if not remainder or (len(remainder) == 1 and remainder[0] == 0):
            break
        chain.append(poly_scale(remainder, -1))
    return chain


def sign_changes(chain, x):
    signs = []
    for poly in chain:
        value = poly_eval(poly, x)
        signs.append(1 if value > 0 else (-1 if value < 0 else 0))
    signs = [s for s in signs if s != 0]
    return sum(1 for a, b in zip(signs, signs[1:]) if a != b)


def real_roots(a, bound=None):
    """all distinct real roots, isolated by Sturm and refined by bisection."""
    a = list(a)
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    if len(a) < 2:
        return []
    chain = sturm_chain(a)
    lead = Fraction(a[-1])
    bound = bound or 1 + max(abs(Fraction(c) / lead) for c in a[:-1] or [0])
    lo, hi = -bound, bound
    total = sign_changes(chain, lo) - sign_changes(chain, hi)
    roots = []

    def isolate(left, right, count):
        if count == 0:
            return
        if count == 1:
            roots.append(refine(chain, left, right))
            return
        mid = (left + right) / 2
        left_count = sign_changes(chain, left) - sign_changes(chain, mid)
        isolate(left, mid, left_count)
        isolate(mid, right, count - left_count)

    isolate(lo, hi, total)
    return sorted(roots)


def refine(chain, left, right, steps=80):
    """bisection on the polynomial: one root between left and right."""
    poly = chain[0]
    fl = poly_eval(poly, left)
    for _ in range(steps):
        mid = (left + right) / 2
        fm = poly_eval(poly, mid)
        if fl * fm <= 0:
            right = mid
        else:
            left, fl = mid, fm
    return (left + right) / 2


def equation(p, q):
    """(1 − t²)^p (1 + t²)^q − (2t)^q (1 + t²)^p, the polynomial whose roots are the cuts."""
    one_minus = [1, 0, -1]        # 1 − t²
    one_plus = [1, 0, 1]          # 1 + t²
    two_t = [0, 2]                # 2t

    def power(base, n):
        out = [1]
        for _ in range(n):
            out = poly_mul(out, base)
        return out

    return poly_sub(poly_mul(power(one_minus, p), power(one_plus, q)),
                    poly_mul(power(two_t, q), power(one_plus, p)))


def equation_in_sin2(p, q):
    """(1 − s)^p − s^q, with s = sin²θ. Degree max(p, q), not 2p + 2q."""
    left = [1, -1]                       # 1 − s
    right = [0, 1]                       # s

    def power(base, n):
        out = [1]
        for _ in range(n):
            out = poly_mul(out, base)
        return out

    return poly_sub(power(left, p), power(right, q))


def crossings_via_sin2(p, q):
    """the same crossings, from the trig identity cos^p θ = sin^q θ.

    s = sin²θ solves a polynomial of degree max(p, q); each s in (0, 1) gives four angles,
    and only those where cos^p and sin^q have the same sign are crossings. The t values follow
    from t = tan(θ/2) = sin θ / (1 + cos θ), which is exact in s.
    """
    roots = [r for r in real_roots(equation_in_sin2(p, q)) if 0 < r < 1]
    out = []
    for root in roots:
        s = float(root)
        sin_t = s ** 0.5
        cos_t = (1 - s) ** 0.5
        for theta_cos, theta_sin in ((cos_t, sin_t), (-cos_t, sin_t),
                                     (-cos_t, -sin_t), (cos_t, -sin_t)):
            if _same_sign(theta_cos ** p, theta_sin ** q):
                out.append(theta_sin / (1 + theta_cos))
    return sorted(out)


def _same_sign(a, b):
    return (a > 0 and b > 0) or (a < 0 and b < 0) or (a == 0 and b >= 0) or (b == 0 and a >= 0)


def crossings(p, q):
    """the t values where the curve crosses y = x, in order."""
    return [float(root) for root in real_roots(equation(p, q))]


def main(argv=None) -> int:
    args = (argv if argv is not None else sys.argv)[1:]
    p = int(args[0]) if args else 3
    q = int(args[1]) if len(args) > 1 else 4
    roots = crossings(p, q)
    via = crossings_via_sin2(p, q)
    print(f"p = {p}, q = {q}: {len(roots)} crossings of y = x "
          f"(sin²θ reduction: {len(via)})")
    for root in roots:
        print(f"   t = {root:+.9f}")
    if p == q:
        print("check: p = q gives 1 − t² = 2t, so t = −1 ± √2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
