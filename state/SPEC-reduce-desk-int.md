# SPEC-reduce-desk-int — the reduction desk, clean description

*The page is `/reduce/<uid>`. Written after the rebuild (2026-11-21/22); the
faults live beside it in `state/PROBLEMS-reduce-desk-int.md`.*

## What it is for

One curve at a time: the exact curve against its degree-11 truncation, with
a **proven** bound for the miss. The desk answers one question — *can this
curve's drawing reach the four-point-cubic ceiling, and by exactly how
much?* — and refuses to answer when its own checks fail.

## The words the page owns

- **position degree** — the exact curve's polynomial degree, `2·speed + 1`,
  stated for x and y separately (they can differ: c-0260 is 23 and 12).
- **curve ceiling** — 11, what four-point cubic spans carry.
- **rail degree** — `2·speed − 1`, stated separately from the curve gate: a
  curve can pass one and fail the other. Truncation cannot fix the rails.
- **proven miss bound** — the sum of the discarded Chebyshev coefficients'
  absolute values, per piece, computed in exact BigInt fractions
  (`app/src/lib/reduction/chebyshev.ts`). It is a guarantee: the worst miss
  on the piece is at most that sum.
- **measured miss** — the worst station distance at the 241 stations; must
  stay ≤ the bound, or the desk refuses.
- **desk status** — verified, or refused with the reason.
- The desk's **bar** is 0.05 % of the curve's size — a stated fraction, and
  the number to judge by is always the miss in units. The word "dial" is
  retired (operator, 2026-11-21): it gave no exact meaning.

## The layout

1. Verdict block first: YES — reducible / NO — over the bar / REFUSED.
2. The graph: the exact curve in black, the reduced form in green dashed,
   through the same 241 stations, JSXGraph. A wide band is stated as a band
   (aspect > 20), and the y axis is stretched to fill the frame with that
   said.
3. The numbers table: degrees, gates, pieces, bound (units and share),
   measured miss, bar, both bounding boxes, desk status.
4. What this means, in the operator's terms: the spans count, the rail
   gate's verdict, and whether the fix is truncation or a sibling.

## The rules, each with its check

- **Every printed number is plain** — integers and decimals, no exponent
  (`app/src/lib/plain-number.js`). Check: no `e` in the table's text.
- **No float touches the bound** — the bound is a Fraction basis change;
  float64 draws, it does not prove. Check: `app/tests/chebyshev.test.mjs`
  pins the bound to the Fraction reference for c-0260 at 1, 2 and 4 pieces.
- **The desk refuses a verdict when a self-check fails** — measured miss
  over the bound, or a reduced form collapsed to a line (bbox aspect).
  Check: the refusal paths are in the page code and the report shows the
  reason.
- **Ladder honesty** — pieces double 1 → 16; past 16 the verdict says "not
  at 16 pieces", which is a practical budget, not an eternal claim.
- **Render time** — the page is computed per request; it renders in under
  a second (0.2 s for c-0260). A page that takes minutes is a regression.

## What is NOT on the page

- The exact Fraction record of a variant — that belongs to the reduction
  pipeline's rows, and the page says so in its footer.
- Any claim that a reduced drawing is a PH curve — the truncation is a
  drawing within a stated miss; the catalogue entry still needs the
  speed-space reduction or a sibling, and the page says which gate fails.

## The index (`/reduce/`)

- Rows: every curve whose position degree (read from the speed rows) is
  above 11 — the desk's population, not the stored `degree` field.
- Columns: uid, name, position degree, **speed → 5 miss (units)**, curve
  size (units), crossings, desk link. The miss column comes from
  `workbench/speed-fit-census.json` (cache; the page works without it —
  a missing census prints "—", it never breaks the page).
- Numbers are plain (`plain-number.js`); no exponent anywhere.
- The summary sentence states how many curves can live at the ceiling by the
  re-fit alone (miss under one per cent of the curve's size — an
  informational cut, the decision is by units per curve).
- Sort: smallest miss first — the reducible curves are the reading order.
