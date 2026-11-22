---

## 2026-11-21 05:30 — the piece builder is in TypeScript: parity 4 pieces, 0 mismatches

Job (operator, direct): two more hours on the conversion track.
Done, three more commits since the last entry: **`9d089c0d`** parallel-bezier.ts (the Levien rail fitter — parity 12 runs), **`31557851`** coneTerminal (the two-arc cone, parity 12 runs), **`64af7186`** piece.ts (Trace/Group/Piece, mirrorSpans, the pre-built-spans build path — parity 4 pieces, 0 mismatches across round+point, mirror+taper, hairline, arc+butt).
Flag for you: **the Python Trace constructor forbids width on span traces** while build_piece's pre-built path and the tune desk's records use exactly that — the port follows the build_piece branch (the desk reality); the constructor's restriction is yours to reconcile.
Proved by: the four parity scripts print their counts (212 curves, 15 checks, 12 runs, 36 runs, 12 runs, 4 pieces — all zero mismatches); npm run check -> 0 errors.
Blocked: nothing
Next: model.py, then svg.py.

---

2026-11-21 · sidechat · the reduce desk's numbers were computed with a broken integral — treat every verdict it printed as void

- Fault: the reduce desk (and the old version) integrated the squared speed rows with a running sum (`out[i+1] = out[i] + c/(i+1)`) instead of the antiderivative (`out[i+1] = c/(i+1)`). The audited core `curve_lab/measure.py :: curve_polynomials` (lines 147-148) does it coefficient-wise; the desk did not.
- Second fault: the desk built `u²`, `v²`, `uv` only over the speed rows' length (12 entries for c-0260) instead of the full convolution (23 entries), cutting the position polynomial short.
- Consequence: every degree, bound and verdict the desk printed is wrong. For c-0260 the true exact curve (checked against measure.py) is position degree 23 (x) and 12 (y), bbox x ∈ [−2253.5, 0], y ∈ [−13.4, 0], size 2253.6 — not "degree 25, bound 2.9e+1 %".
- Also found: my Clenshaw evaluation of the truncated Chebyshev series fails round-trip (worst 565) while direct cosine evaluation passes (worst 1.1, the float noise floor). The page will evaluate directly, not by Clenshaw.
- Consequence for R1: the "genuinely over-degree" claims for c-0072/c-0260 came from desk/twin numbers computed on broken polynomials. The census (speed degrees, 103/110 split) is unaffected — it reads the speed rows, not the integral.
- The `../curve-lab-reduction/` worktree is gone from disk (2026-11-21). The reduction branch content is only on the git branch.
- Fix in progress on the page: exact products, coefficient-wise integration, exact drawing samples from measure.ts, direct-cos evaluation, bound ladder with the float noise floor stated in the copy.

---

2026-11-21 · sidechat · operator decision: the re-fit problem may be first, and "within the dial" is retired

- Operator: "might be the hardest problem we have, so we might have to do that first. not last." The re-fit / editing round-trip (Inkscape edit → speed rows back) is promoted from parked to a candidate for first in the queue. DeepSeek1 owns the queue order.
- Operator: "dont say 'within the dial' since it is not a real expression and gives no exact meaning." Retire the phrase on pages and in handoffs. Replace with an exact unit count: "worst miss 0.13 units" (curve units, same as the bbox size row), measured exactly, accepted or refused per curve by that number.
- The re-fit gate has two honest outcomes: miss exactly zero (speed rows reproduce the edit — accept), or the smallest provable miss stated in units with its worst station (operator accepts or refuses by the number).
- The first measurable step: the walkthrough's edited c-0059, best speed rows in exact arithmetic, minimum miss printed as a unit count. Note: speed-space reduction (R1) and the re-fit are the same maths in opposite directions — the solver is shared.
- The reduce desk rewrite is complete and verified (exact bound, parity-tested, page renders in 0.21 s, verdict for c-0260 is YES at 4 pieces, bound 0.1316 units). Screenshot taken; commit + push still pending.

---

2026-11-21 · sidechat · operator's assumed solution: restricted actions in inkex, exact reconstruction

- Operator: "use inkex and restrict the user to doing certain actions on the special grid so that any action could be reconstructed in the parametric polynomial. preferably degree 7 or lower, max 11."
- This replaces the free-form re-fit as the assumed route: no approximation step at all. The editor's vocabulary is closed — each permitted action has an exact algebraic effect on the speed rows.
- Sidechat's proposed vocabulary, all exact and degree-preserving: recipe parameter edits (degree read from the name: speed = 2·pairs + stack, position = 2·speed + 1), rational translation, mirror, p-triple rotation, rational scale, and top-coefficient (end-handle) edits.
- Mid-curve node drags are not offered; a drag snaps to the nearest legal action's predicted handle position on the grid, or is refused with the miss in units.
- inkex implementation: recipe name + parameters live in SVG metadata; the extension dialog edits parameters; path data regenerates from speed rows via the ported exact core. The SVG is a view; the recipe is the truth. Round-trip is lossless by construction.
- Degree gates: prefer position ≤ 7 (speed ≤ 3), allow position ≤ 11 (speed ≤ 5). The dialog refuses parameter sets over the gate before drawing.
- Consequence for the queue: the free-form re-fit solver drops off the critical path; the restricted editor needs only already-proven arithmetic (measure.ts, piece.ts, bezier.ts).

---

2026-11-21 · sidechat · how-to doc for DeepSeek1: side curves

- Wrote docs/SIDE-CURVES.md for DeepSeek1: what a side curve is (per-construction partner, never a parallel offset), the one character-rail law (distance = base × (1 + strength × profile)), the fold guard with the bow inside it (register 51), the direct cap (distance × peak ≤ 0.9, no halving, no second construction), the 2026-11-21 preset (width 1 %, plus 2.5, minus 0.1; zero/missing width takes it, saved width wins, stored paths included; register 52), the per-family parameter table (row/mobile/double/hybrid from scripts/side_curves.mjs), exactness rules (clean d fractions, plain numbers, no drawing-only records in the registry), the file/guard map, the canvas law, the open cases (c-0260's partner is its fix), and the operator's verbatim tie-breakers.

---

2026-11-22 · sidechat · the Inkscape round trip is done end to end, inside Inkscape's own runtime

- The hardest part — the drag→action map — works: the user drags on-curve nodes in Inkscape and saves; the receiver reads the drawn nodes from the path data, matches them against the closed vocabulary (every candidate action re-draws the chain exactly), and one action must explain ALL the moved nodes. The winner rewrites the file with the acted recipe; a far drag is refused with the miss in curve units.
- Proven through Inkscape 1.4.4 itself: the extension ran under Inkscape's bundled python + inkex (`--mode=send/receive`, needs a blank input svg when run headless), the recipe metadata survived Inkscape's own re-serialization, Inkscape's path precision drift measured 4.8e-05 curve units (the DRIFT threshold is 0.001), and three drags snapped correctly on Inkscape's own file: translate (miss 4.8e-05), end-handle at t=1 (miss 6.7e-07, u[5] rewritten to −1/10), and a two-node drag explained by one action.
- Two faults found and fixed along the way, register row 55: the translate added the offset to every position coefficient instead of the constant term only (a "translation" grew as 1+t+t²+…), and the rotation/scale were each applied twice (the placed rows already carry both — the fix was deletion). Both live in inkscape/ph_actions.py, guarded by tests/test_ph_actions.py and the strengthened translation law.
- The variant write-back: inkscape/ph_variant.py builds a registry-variant PROPOSAL (never written directly — the save endpoint owns the registry). Operator rule applied: a translation is a view, not a curve — translated placements are refused as variants; rotations/scales/mirrors/end-edits bake into the rows exactly and propose parent+letter (c-0002a, "euler-hook-end-edited"). A recipe swap maps back to the sibling already in the registry.
- Extension gotchas for the record: the .inx namespace must be http://www.inkscape.org/namespace/inkscape/extension (the /extensions/1.0 one is silently skipped); inkex 1.4 has no top-level Element export; the script must call its own Extension().run(); unknown CLI params need add_arguments entries. My copies live in the user extensions folder; re-copy inkscape/*.py *.inx after every edit.
- Tests: tests/test_ph_actions.py (14), tests/test_ph_roundtrip.py (7, with tests/fixtures/through-inkscape-c-0002.svg — Inkscape's own serialization as the fixture), tests/test_ph_variant.py (5). 26 green before the gate.

---

2026-11-22 · sidechat · the round trip is closed: the acted curve is now a sandbox candidate

- The variant proposal was POSTed through /api/sandbox-curves (HTTP 200, {"saved":1}): candidate `c-0002a` "euler-hook-end-edited" sits in the sandbox table with base_uid c-0002, the acted top coefficient (speedX[5] = −0.1), transform exact:true, origin "inkscape-roundtrip". 155 rows in the table; awaiting your promotion flow (/names or the desk) — it is a genuine product of the round trip, not a test row.
- The receive extension gained --variant (prints the proposal) and --post <url> (POSTs it to the sandbox endpoint, stdlib urllib). The full loop: registry → send (Inkscape runtime) → Inkscape load/save → drag → receive+snap → acted recipe → variant proposal → sandbox candidate.
- One design rule surfaced and applied: a translation is a view, not a curve — translated placements are refused as variants (the offset stays in the SVG); rotations, scales, mirrors and end-edits bake into the rows exactly.
