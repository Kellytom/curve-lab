# PORT-int — browser JS, Node where it earns it, Python where it is debugged

The operator's position, 2026-11-17: **the page layer should be JS**, but do not
get dependent on Node for its own sake, and **do not rewrite code that is already
debugged**. This file turns that into a rule with a boundary, so the same
argument is not had again.

## The rule

1. **The browser is the product, so live maths is JS.** A number a control, a
   slider or a readout computes at load comes from a JS module the page loads.
2. **Node is a verification tool, not a build dependency.** It runs the browser
   modules' tests (`node --test`) and the Playwright page checks. No page
   generator moves to Node just to be Node.
3. **Python stays where it is debugged** — the engine (`curve_lab/`), the stored
   records, the audits, and the page generators that write static cards.
4. **Move a calculation only when the page must compute it live.** A static card
   may keep the Python-computed record; it does not need a second implementation
   in the browser.
5. **One number, one source.** A live number comes from the JS module; a stored
   number comes from the record. Never a third.
6. **No floats on an exact path.** `floatSampler` is for drawing only. Any
   lattice, grid or crossing answer is `Rational`/`BigInt`, and the 1e16 case
   that broke doubles is a mandatory test when such a function moves.

## What moved on 2026-11-17

| file | lines | what it is |
|---|---|---|
| `workbench/exact.js` | 100 | `Rational` on `BigInt`: normalise, add/sub/mul/div, compare, integer check |
| `workbench/poly_exact.js` | 80 | coefficient lists low-to-high: add, multiply, integrate, derivative, evaluate |
| `workbench/ph_offset.js` | 129 | the PH curve, the exact offset, lattice scale, first interior hit, hits at a scale |
| `tests/js/ph_offset.test.js` | 85 | pinned to the Python numbers: polynomials, normal equations, grid 3360, rail grids, the symmetric candidate |

The gate is `scripts/test.py`: after the Python modules it runs `node --test
tests/js` and prints the pass/fail count (8 pass, ~0.3 s). `scripts/test.py`
remains the one command; no second gate.

Sizes: every module above is under 200 lines, has one job, and loads either as a
plain script (`globalThis.Exact`) or through `require`. That is the house shape
for JS modules: no bundler, no import graph to debug.

## The conversion track's rows (the sidechat's, 2026-11-21/22)

| row | landed | parity | notes |
|---|---|---|---|
| `measure.py` | `app/src/lib/measure.ts` | 212 curves, 0 mismatches | the one exact core |
| `clearance.py` | `app/src/lib/clearance.ts` | 15 checks, 0 mismatches | flatten, distance, gap/crossings |
| `piece.py` | `app/src/lib/piece.ts` | 4 pieces, 0 mismatches | the pre-built-spans path |
| `model.py` | `app/src/lib/model.ts` | JSON shape round-trips | one widening: null `kappa0` through `fromPieces` |
| `svg.py` | `app/src/lib/svg.ts` | 9 laws pinned | TEXT layer only; `document()` stays in Python until the site emits documents |
| `contact.py` | `app/src/lib/contact.ts` | the licensing laws | declared merges, pair- and order-blind |
| `fillet.py` | `app/src/lib/fillet.ts` | the ruler numbers | `corner_fillet` + `arc_segment`; `fillet_span` is the next row |
| `junction.py` | `app/src/lib/junction.ts` | the report numbers | geometry + report; spans need the clothoid engine row |

## What is deliberately not moving

- **`curve_lab/measure.py`** (293 lines). It is the debugged exact core, and the
  pages display its stored numbers. It moves only if a live control needs grid,
  bend, arc, inflection or closest; then that one function moves, with a parity
  test over every stored record.
- **The 123 page generators.** They are the 49k, and they work. A generator is
  replaced only when its page's maths moves live, and then the `.py` is deleted
  in the same commit.
- **`web/server.py`** (329 lines, Cloud Run image). A deploy decision, not a
  curve decision. It can be the last Python process in the repo.

## Next fruit, in order

1. **`workbench/rail_chart.js`** — the labelled-figure helper for the rail lab.
   The Python `rail_chart.py` is its twin until the page moves live.
2. **The rail lab controls** — the page reads `ph_offset.js` at load for the
   offset, the lattice grid and the station; the generator writes only the
   shell and the prose. This is the page that proves the shape.
3. **Crossings in JS** — small and pure, needed if a lab control reports a live
   crossing count. Parity against `scripts/ph_crossings.py` on the stored
   records.
4. **Grid and bend in JS** — only with the 1e16 guard and the full-record parity
   test. Do not start until a page needs them live.
5. **`measure.py` last**, and the generators on touch.
6. **The server never**, unless the deploy changes for another reason.

## The measure of progress

Run at every handoff:

```sh
sh scripts/code_count.sh
```

August 2026 baseline (2026-11-17): Python 67,062 lines (engine 8,027 · scripts
48,916 · tests 9,790 · web 329), our JS 11,951 (workbench 5,527 · scripts 6,424).
The target is not zero Python. It is: **no new page maths in Python, and the
Python count flat or falling at each handoff.** A handoff that raises the Python
count must say why in one line.

## Risks, named

- **BigInt is slower than Fraction is on CPython for this arithmetic.** The
  q ≤ 40 search is 35 ms in Node; a q ≤ 200 search was not timed and must be
  measured before a page depends on it.
- **Float creep.** JS makes `number` the easy path; the exact path must stay
  explicit. The tests reject a float passed to `Rational.from`.
- **Two implementations during a move.** A moved function is two implementations
  until the Python twin is deleted; that window is one commit, not one release.
- **The 1e16 case.** `loop-13-15-17-mid-1`: a coefficient of 1.03e8 squares past
  2^53. Any JS grid answer that does not carry it is wrong by 143×.

## What is not decided

Whether the rail lab replaces `integer-ph-rail.html` or sits beside it, and
whether the Python chart survives. Those follow from the lab's first version,
not from this plan.
