"""Exact midpoint-rule Pythagorean chain for the T-PH curve (u=1, v=t).

Everything is Fractions. Nothing here imports curve_lab: this is the
discrete-method holding pen and must stay separable from ph_hermite.

Curve:  x'(t) = 1 - t^2,  y'(t) = 2t,  sigma(t) = 1 + t^2
        x(t)  = t - t^3/3,  y(t) = t^2,  s(t) = t + t^3/3

Run:  .venv/bin/python tph_tri_chain/chain.py
"""

from fractions import Fraction as F
from math import lcm, sqrt

# ---------------------------------------------------------------- the curve


def integral(t):
    """Exact curve point and exact arc length at parameter t."""
    return (t - t**3 / 3, t**2, t + t**3 / 3)


def speed(t):
    return (1 - t**2, 2 * t, 1 + t**2)


def chain(t0, t1, n_steps):
    """Midpoint-rule chain of straight steps over [t0, t1].

    Each step is a right triangle whose legs are (dx, dy) and whose
    hypotenuse is the travelled chord ds, with dx^2 + dy^2 = ds^2 exactly.
    """
    dt = (t1 - t0) / n_steps
    x = y = s = F(0)
    rows = []
    for i in range(n_steps):
        tm = t0 + (i + F(1, 2)) * dt
        ux, uy, us = speed(tm)
        dx, dy, ds = ux * dt, uy * dt, us * dt
        assert dx * dx + dy * dy == ds * ds, (i, tm)  # Pythagorean, exactly
        x += dx
        y += dy
        s += ds
        rows.append(dict(i=i, t=tm, dx=dx, dy=dy, ds=ds, x=x, y=y, s=s))
    return rows, dt


def grid(rows):
    """Smallest integer grid on which every leg AND hypotenuse is an integer."""
    g = 1
    for r in rows:
        for v in (r["dx"], r["dy"], r["ds"]):
            g = lcm(g, v.denominator)
    return g


def integers(rows, g):
    return [(r["dx"] * g, r["dy"] * g, r["ds"] * g) for r in rows]


def primitive(tri):
    a, b, c = tri
    k = 1
    for v in (a, b, c):
        if v:
            k = max(k, abs(v))
    while k > 1:
        if all(v % k == 0 for v in (a, b, c)):
            return a // k, b // k, c // k
        k -= 1
    return a, b, c


def show(rows, g, cols=("i", "t", "dx", "dy", "ds", "x", "y")):
    """Print a table; integer legs are shown at grid scale."""
    print("  ".join(f"{c:>12}" for c in cols))
    for r in rows:
        out = []
        for c in cols:
            v = r[c]
            if c in ("dx", "dy", "ds"):
                out.append(f"{int(v * g):>12}")
            elif c == "i":
                out.append(f"{v:>12d}")
            else:
                out.append(f"{float(v):>12.5f}")
        print("  ".join(out))


def main():
    print("=" * 78)
    print("1. AUDIT OF THE FOUR-STEP EXAMPLE over t in [0,2], N=4")
    print("=" * 78)
    rows, _ = chain(F(0), F(2), 4)
    g = grid(rows)
    print(f"minimal exact integer grid: {g}")
    show(rows, g, ("i", "t", "dx", "dy", "ds", "x", "y"))
    print(f"next vertex (x,y) = ({float(rows[-1]['x']):.5f}, {float(rows[-1]['y']):.5f})")
    print(f"chain length {rows[-1]['s']} = {float(rows[-1]['s']):.6f}")
    print(f"exact length  s(2) = {integral(F(2))[2]} = {float(integral(F(2))[2]):.6f}")

    print()
    print("=" * 78)
    print("2. GRID SCALING: the exact integer grid is NOT 3125")
    print("=" * 78)
    print(f"{'t_max':>8} {'N':>6} {'dt':>8} {'minimal grid':>16} {'vs 3125':>10}")
    for tmax, N in [(F(2), 5), (F(2), 25), (F(2), 125), (F(2), 625),
                    (F(5, 2), 5), (F(5, 2), 25), (F(5, 2), 125),
                    (F(12, 5), 120), (F(1), 25)]:
        r, _ = chain(F(0), tmax, N)
        gg = grid(r)
        rel = gg / F(3125) if gg >= 3125 else F(-1)
        print(f"{str(tmax):>8} {N:>6} {str(tmax/N):>8} {gg:>16} {float(rel):>10.2f}x")

    print()
    print("=" * 78)
    print("3. COORDINATE TABLE, t in [0,2], N=25 (n=5), exact integers on 15625")
    print("=" * 78)
    rows, _ = chain(F(0), F(2), 25)
    g = grid(rows)
    print(f"grid {g}; columns dx,dy,ds are counts of 1/{g}")
    show(rows, g, ("i", "t", "dx", "dy", "ds", "x", "y"))
    print(f"end ({float(rows[-1]['x']):.6f}, {float(rows[-1]['y']):.6f})  s={float(rows[-1]['s']):.6f}")
    print("first five triples, primitive:", [primitive(t) for t in integers(rows, g)[:5]])

    print()
    print("=" * 78)
    print("4. FISH GLYPH, half-chain t in [0, 12/5], N=120 (dt = 1/50)")
    print("=" * 78)
    half, _ = chain(F(0), F(12, 5), 120)
    g = grid(half)
    print(f"grid {g} = {F(g, 3125)} x 3125")
    show(half[:6], g, ("i", "t", "dx", "dy", "ds", "x", "y"))
    print("   ... 114 more steps ...")
    show(half[-3:], g, ("i", "t", "dx", "dy", "ds", "x", "y"))
    xt, yt, st = half[-1]["x"], half[-1]["y"], half[-1]["s"]
    print(f"tail tip ({float(xt):.6f}, {float(yt):.6f}); half length {float(st):.6f}")
    print(f"full glyph: length {float(2*st):.6f}, exact curve length {integral(F(12,5))[2]*2}")
    print(f"full-glyph error {float(2*st - 2*integral(F(12,5))[2]):+.3e}")

    print()
    print("=" * 78)
    print("5. STOPPING POINTS: geometry vs exact grid")
    print("=" * 78)
    inner = 4 * sqrt(3)  # exact inner-loop length, t = -sqrt3 .. +sqrt3
    print(f"inner loop closes at (0,3) at t = +-sqrt(3); arc length 4*sqrt(3) = {inner:.6f}")
    print(f"{'t_max':>8} {'tail tip (x,y)':>26} {'full len':>12} {'ratio':>7} {'grid':>10} {'N':>5}")
    for label, tmax, N in [("5/2", F(5, 2), 125), ("12/5", F(12, 5), 120)]:
        r, _ = chain(F(0), tmax, N)
        gg = grid(r)
        tip = integral(tmax)
        full = r[-1]["s"] * 2
        print(f"{label:>8} ({float(tip[0]):>9.4f}, {float(tip[1]):>7.4f})"
              f" {float(full):>12.6f} {float(full)/inner:>7.3f} {gg:>10} {N:>5}")
    tip6 = integral(F(12, 5))  # stand-in: sqrt6 is irrational, no rational chain ends there
    print(f"{'sqrt6':>8} ({-sqrt(6):>9.4f}, {6.0:>7.4f})  irrational t: no exact rational chain;"
          f" nearest grid stop 12/5 gives y={float(integral(F(12,5))[1]):.4f}, gap {6.0-5.76:.2f}")

    print()
    print("=" * 78)
    print("6. GRID LADDER: what a dense chain actually costs")
    print("=" * 78)

    def ladder(tmax, n_list):
        exact = integral(tmax)
        print(f"t_max = {tmax}")
        print(f"{'N':>5} {'dt':>8} {'minimal grid':>13} {'on 3125?':>9} {'on 500000?':>11}"
              f" {'len err':>10}")
        for N in n_list:
            r, _ = chain(F(0), tmax, N)
            gg = grid(r)
            print(f"{N:>5} {str(tmax / N):>8} {gg:>13}"
                  f" {'yes' if 3125 % gg == 0 else 'no':>9}"
                  f" {'yes' if 500000 % gg == 0 else 'no':>11}"
                  f" {float(r[-1]['s'] - exact[2]):>10.2e}")
        print()

    ladder(F(12, 5), (6, 12, 24, 30, 60, 120, 240))
    ladder(F(5, 2), (5, 10, 25, 50, 125, 250))

    print()
    print("=" * 78)
    print("7. MEMO CORRECTIONS")
    print("=" * 78)
    r4, _ = chain(F(0), F(2), 4)
    rest = r4[-1]["s"] * 2  # symmetric-ish check is not used here
    checks = [
        ("4-step end y exactly 4", r4[-1]["y"] == 4),
        ("4-step end x = -0.625", r4[-1]["x"] == F(-5, 8)),
        ("4-step length 37/8", r4[-1]["s"] == F(37, 8)),
        ("step1 triple is (15,8,17)/32 at grid 32", integers(r4, 32)[0] == (15, 8, 17)),
        ("[0,2] N=25 grid is 15625 not 3125", grid(chain(F(0), F(2), 25)[0]) == 15625),
        ("[0,2] N=25 step0 = (1248,100,1252) not 200", integers(chain(F(0), F(2), 25)[0], 15625)[0] == (1248, 100, 1252)),
        ("[0,1] N=25 grid is 62500 not 3125", grid(chain(F(0), F(1), 25)[0]) == 62500),
        ("[0,1] N=25 step0 = (2499,100,2501)", integers(chain(F(0), F(1), 25)[0], 62500)[0] == (2499, 100, 2501)),
        ("[0,2.4] N=120 grid is 500000", grid(half) == 500000),
        ("3125 works only at N=5 over [0,2]", grid(chain(F(0), F(2), 5)[0]) == 125),
    ]
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")


if __name__ == "__main__":
    main()
