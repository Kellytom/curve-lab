"""PH quintics: degree 5, integer controls after one scale, rational arc length.

    .venv/bin/python scripts/ph_quintic.py

The repo had PH cubics only. The degree lemma is n = deg h + 2·max(deg u, deg v)
+ 1, so a quintic is either u, v quadratic with h constant, or u, v linear with
h quadratic. Both are here. Because σ = h(u² + v²) is a polynomial, the arc
length is ∫σ, a rational number — that is what a PH curve buys.
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generators as G  # noqa: E402

# (title, h, u, v)
CASES = [
    ("PH quintic · u = 1+2t+t², v = 1−t+t²", (1,), (1, 2, 1), (1, -1, 1)),
    ("PH quintic · u = 1+t², v = 2t", (1,), (1, 0, 1), (0, 2)),
    ("PH quintic · h quadratic, u, v linear", (1, 1, 1), (2, 1), (1, -1)),
]
M = 8          # the milestone step used for the integer scale


def build_case(h, u, v, n=5):
    pc = G.PHCurve(n, u=u, v=v, h=h)
    scale = pc.scale(M)
    # σ = h (u² + v²); its integral over [0, 1] is the arc length
    uu = G.mul(list(u), list(u))
    vv = G.mul(list(v), list(v))
    width = max(len(uu), len(vv))
    sig = [a + b for a, b in zip(uu + [0] * (width - len(uu)),
                                vv + [0] * (width - len(vv)))]
    arc = sum((Fraction(c, k + 1) for k, c in enumerate(G.mul(list(h), sig))),
              Fraction(0))
    pts = [pc.bezier(i / 160) for i in range(161)]
    return {"pc": pc, "scale": scale, "arc": arc, "pts": pts}


def cases():
    out = []
    for title, h, u, v in CASES:
        d = build_case(h, u, v)
        out.append((title, d["pts"],
                    f"n = 5 · integer controls at scale {d['scale']:,} · "
                    f"arc length {d['arc']} rational",
                    "scripts/generators.py PHCurve"))
    return out


if __name__ == "__main__":
    for title, h, u, v in CASES:
        d = build_case(h, u, v)
        d["pc"].check(M, d["scale"])
        print(f"{title}: scale {d['scale']:,}, arc {d['arc']}")
