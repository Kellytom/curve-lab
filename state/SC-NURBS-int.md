# NURBS-READINESS-int — the curve inventory, the rails, and what NURBS costs

Computed 2026-11-21 from the registry and the metric store (`/tmp/nurbs-inventory.json`
holds the per-curve rows; the commands are printed below). The question: the
operator wants to move the catalogue — the curves **and their rails/offsets** —
to NURBS. This file says what we have, what NURBS does with it, and where the
exact conversions sit.

## 1 · The inventory, by degree

371 curves carry speed rows (the other 26 are polyline/path kinds). Degree
histogram of the position polynomials:

| degree | curves | the good ones in it |
|---|---|---|
| 3 | 2 | — |
| 5 | 4 | — |
| 7 | 34 | the original wave/lace seeds |
| 9 | 27 | `c-0261 loop-7-mid-2` (8 crossings) |
| **11** | **63** | `c-0059 lace-1of10-3-2` (11), `c-0262 loop-8-11-mid-1` (9), `c-0067` (8) |
| 13 | 27 | — |
| **15** | **80** | `c-0256 loop-3-5-11-mid-1` (15), the fit family (catenary, involute, euler, logspiral) |
| 17 | 1 | `c-0011 gumdrop` |
| 19 | 1 | `c-0257 loop-3-7-11-mid-3` (15 crossings) |
| **23** | **1** | **`c-0260 loop-5-8-12-mid-5` — 19 crossings, the best knot we have** |

200 of 371 sit at degree ≥ 9. 29 curves carry five or more crossing pairs; the
top three by crossings are exactly the top three by degree. The starred set is
small in this store (6 with rows, at degrees 9–11); the working "good" set is
better read as the 29 high-crossing curves plus the 111 starred names in the
registry (the rest are path/polyline kinds).

## 2 · The curves: already NURBS, exactly, for free

A polynomial curve **is** a rational Bézier curve with every weight equal to 1.
So every one of the 371 is exactly a NURBS of its own degree — no weights to
solve, no approximation, no error. The conversion is a basis change from the
power form to the Bernstein form, exact in `Fraction` arithmetic, curve by
curve. The rails' NURBS degrees are the numbers below; the curves' NURBS
degrees are the table above.

## 3 · The rails: the payoff nobody engineered on purpose

The rails are offsets of the spine. For an arbitrary curve the offset involves
a square root and is **not** representable — that is why the app's rails are
*approximations*: `fit_chain` refits the offset within `tol`, and the clearance
rule carries a `2·tol` honesty band for exactly that reason.

But our curves are **PH curves** (the speed rows make the speed `u² + v²` a
polynomial square), and a PH curve's offset is **exactly rational** — the
property the field values them for (Farouki's PH literature, already cited in
`state/RESEARCH-int.md`). Verified here by construction on the stored rows:

    X_num(t) = x(t)·w2(t) − d·y′(t)      Y_num(t) = y(t)·w2(t) + d·x′(t)
    W(t)     = w2(t) = u² + v²
    X = X_num/W,  Y = Y_num/W,  d = the offset distance

The perpendicularity to the tangent and the exact distance `d` both hold
*identically* in the polynomial algebra — there is nothing to verify
numerically. Measured facts:

| curve | degree n | speed degrees (u, v) | offset rational degree (2n−1) | denominator degree (2·max) |
|---|---|---|---|---|
| c-0001 amper | 7 | (3, 3) | 13 | 6 |
| c-0262 loop-8-11-mid-1 | 11 | (3, 3) | 21 | 6 |
| c-0260 loop-5-8-12-mid-5 | 23 | (0, 11) | 45 | 22 |
| c-0257 loop-3-7-11-mid-3 | 19 | (0, 9) | 37 | 18 |
| the 15-degree family | 15 | (0, 7) | 29 | 14 |

So **every rail in the catalogue is exactly a NURBS of degree 2n−1**: the
conversion replaces the approximated rails with exact ones and the `2·tol`
warning band disappears. That is the strongest argument for the move.

## 4 · The catch: big coefficients, and one honest warning

The exact offset's coefficients are enormous for high degrees (c-0260's
denominator polynomial carries coefficients near 10^16). Float evaluation of a
degree-45 rational at those magnitudes is meaningless — this is the same fault
`curve_lab/measure.py` was written to end, and `measure.ts` inherits the fix:
the NURBS evaluation must stay in BigInt/scaled arithmetic, or the weights must
be normalised so doubles survive. Ported naively, the NURBS move would
re-introduce the two-arithmetic-lines fault that this repository exists to
prevent.

One family needs a separate look: the (0, k) speed rows (`u` a constant, 63
curves at degree 11 and up). Their denominator `u² + v²` never vanishes (u is a
non-zero constant), so the rational offset has no poles — but its degree grows
as 2n−1 like everything else, and the stroke is a straight line when `u = 0`
exactly (none of the stored set has that; the nearest is `u = 1`).

## 5 · What "moving to NURBS" concretely means, in order

1. **Basis change per curve** — power → Bernstein, exact in `Fraction`, one
   curve at a time; the result is the same curve as a NURBS with weights 1.
   `Proves:` evaluating both forms at 41 samples, equal to 1e-12.
2. **Exact rational rails** — build the offset from the formulas above instead
   of `fit_chain`; degree 2n−1, denominator w2. `Proves:` the perpendicularity
   and distance identities hold exactly (they are algebra, not samples).
3. **Weights where they matter** — the only place a non-unit weight earns its
   keep is a rail whose alpha edge must soften; the curves never need one.
4. **The spans decision** — cubic spans can stay cubic NURBS spans (nothing
   forces merging); the exact rails arrive as single degree-(2n−1) NURBS and
   may be degree-reduced later if a tool complains.

## 6 · Commands, so the numbers re-derive

```sh
.venv/bin/python - <<'PY'        # the inventory: degrees, crossings, starred
import json, collections
rows = json.load(open('/tmp/nurbs-inventory.json'))   # or recompute from the registry
PY
# the offset identity, per curve: the exact construction plus the float echo
# (the scripts are inline in the session log; the algebra is the proof)
```

Status: analysis only; no code changed. The inventory JSON is
`/tmp/nurbs-inventory.json` (session temp) — regenerate from the registry when
the set moves.
