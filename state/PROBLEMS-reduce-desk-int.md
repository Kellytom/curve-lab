# PROBLEMS-reduce-desk-int — every fault the desk has had

*The clean description is `state/SPEC-reduce-desk-int.md`. Each fault here
is the operator's words where they exist, what was actually wrong, the fix,
and the guard. Nothing leaves this file when a change makes it awkward.*

## 1 · The integral was a running sum (register row 54)

The desk printed "proven miss bound: 0.00 %, actual miss: 108 %, always ≤
the bound" — three claims that cannot all be true. Two faults, one root
area: the integral of the squared speed rows was a running sum
(`out[i+1] = out[i] + c/(i+1)`) instead of the antiderivative, and the
squared rows were built only over the speed rows' length instead of the
full convolution. Every degree, bound and verdict the desk ever printed
was computed on a wrong polynomial: c-0260's true position degree is 23,
not 25; its true single-piece truncation miss ~3 %, not 29 %.

**Guard.** `app/tests/chebyshev.test.mjs` — the bound pinned to the
Fraction reference for c-0260 at 1, 2 and 4 pieces; measured ≤ proven; a
collapsed reduced form refused.

## 2 · The "proven" bound was float64 (register row 54's second half)

Before the rebuild the bound summed float DCT coefficients, so on
ill-conditioned polynomials the tail was noise: at 4 pieces the claimed
bound (0.033 %) sat below the desk's own noise floor. A bound computed in
float is not proven.

**Guard.** `app/src/lib/reduction/chebyshev.ts` computes the bound as an
exact Fraction basis change (substitute → triangular solve against the
T_k power forms); no float touches it.

## 3 · "Genuinely over-degree" — a wrong verdict from wrong numbers

The desk's verdict for c-0260 was NO at 64 pieces with a 29 % bound. With
the correct integral the honest verdict flipped: 4 pieces, proven miss
0.1316 units = 0.0058 % of size. The earlier sessions' R1 conclusions
built on the desk's numbers were suspect too (the census reading speed
degrees was unaffected).

**Guard.** The same pinned test; and the verdict text states the miss in
units, so a wrong number is visible, not hidden behind a word.

## 4 · "Within the dial" — not a real expression (operator, 2026-11-21)

"i am nervous…", then: "dont say 'within the dial' since it is not a real
expression and gives no exact meaning." The dial was an eye-forgiveness
percentage; it let a verdict wear a number's authority without a number.

**Fix.** Retired everywhere on the page. The verdict states the miss in
units and as a share; the desk's bar (0.05 % of size) is labelled a bar,
and the acceptance is per curve by the unit count.

## 5 · Exponents on the page (operator: "i like numbers like 5, 25, 3125")

Every measure was `toExponential(2)`: 3125 printed as 3.13e+3, a large
bound as 1.23e+16.

**Fix.** `app/src/lib/plain-number.js` (DeepSeek1's, handed over) formats
every table cell. **Guard.** `app/tests/plain-number.test.mjs`.

## 6 · The mixed gates (DeepSeek1's review, item 5)

The page mixed "position degree" with "curve and rail inside 11": a
degree-7 curve has a degree-13 rail, so one number cannot carry both
gates.

**Fix.** The verdict and the table state the curve gate and the rail gate
separately; c-0260's row says the rails stay at degree 21 and truncation
cannot fix them.

## 7 · A flat green line that meant "broken" (DeepSeek1's review, items 2 and 7)

The page said "where the two coincide you cannot see the green" while the
green was a flat line — a visible contradiction left to the eye.

**Fix.** The desk checks the reduced form's bounding box against the
exact one; a collapsed reduced form is a REFUSED verdict with the reason
in words, the same way a NaN would be.

## 8 · The graph's template variables rendered literally

An earlier draft broke the Astro fence, and `{W}`, `{H}` printed as text
with flat-line paths. Rewritten in one pass (patch-a-line → rewrite-a-
structure), and the page is checked by fetching it and grepping the
rendered HTML, not by reading the source.

**Guard.** `/reduce/c-0260` renders in ~0.2 s with the verdict text
present; the page suite runs in the app's checks.
