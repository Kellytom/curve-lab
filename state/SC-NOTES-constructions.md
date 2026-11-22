# SC-NOTES-constructions — the name is the recipe, and the siblings are already here

Written 2026-11-21 after the operator's nudge: "add to the notes the way the
curve was made, maybe that will indicate how to make it simpler." It did —
the answer is that **the simpler curves already exist in the catalogue**.

## The rule, verified on the whole lace family

The lace names encode the recipe:

    lace-<p>of<q>[-<p2>of<q2>]-<stack>

= mirror root pairs at `p/q` and `(q−p)/q`, plus a root stack of `stack` at ½.
The degree follows from the name:

    speed degree = 2 × (mirror pairs) + stack
    curve degree = 2 × speed degree + 1

Verified on **all 31 lace curves** in the registry: 31 names follow the rule,
0 do not. Examples: `lace-1of10-3` → speed 5, curve 11 ✓; `lace-1of12-1of3-3`
→ speed 7, curve 15 ✓.

## The sibling map: the NURBS-ready curves are already here

The NURBS ceiling (curve ≤ 11) = speed degree ≤ 5 = **at most 2 mirror pairs
with a stack of 1, or 1 pair with a stack of 3**. Seven of the twelve
over-ceiling lace curves have their NURBS-ready sibling **already in the
catalogue** — same family, same root structure, smaller stack:

| over-ceiling (speed) | NURBS-ready sibling (speed) | sibling uid |
|---|---|---|
| `lace-1of10-4` (6) | `lace-1of10-2` (4) | c-0048 |
| `lace-1of12-1of3-3` (7) | `lace-1of12-1of3-1` (5) | c-0057 |
| `lace-1of8-1of3-3` (7) | `lace-1of8-1of3-0` (4) | c-0047 |
| `lace-1of5-2of5-3` (7) | `lace-1of5-2of5-1` (5) | c-0207 |
| `lace-3of10-5` (7) | `lace-3of10-3` (5) | c-0209 |
| `lace-1of8-1of5-3` (7) | `lace-1of8-1of5-1` (5) | c-0066 |
| `lace-1of8-1of4-3` (7) | `lace-1of8-1of4-1` (5) | c-0067 |

Five over-ceiling laces have no in-catalogue sibling yet — but the recipe
builds one exactly (`lace-1of10-2x1of3-1` → drop the stack: the same roots,
a smaller stack). No approximation anywhere: a sibling is a different curve,
built by the same rule, exact by construction.

## The other families, and where their degree comes from

- **loop (source B)** — `loop-5-8-12-mid-5`: the parameters are in the name;
  the generator enumerates the family, so the siblings are one generator call
  away.
- **the fit family** (involute, catenary, euler, logspiral — degree 15) — the
  degree came from the fit; re-fitting at ≤ 11 is the dial operation from the
  spec.
- **gumdrop** (found) — hand-tuned, no family; it stays exact in storage.

## The answer to the degree-11 choke point, restated smart

The catalogue already holds the NURBS-ready siblings of most over-ceiling
curves. The task is not reduction — it is **selection**: for each over-ceiling
curve, point at its in-catalogue sibling (or build one with the family
recipe), and let the operator pick which of the pair ships.
