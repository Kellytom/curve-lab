```text
Read state/HANDOFF-int.md. Read docs/PH-INTEGER.md and workbench/ph-families.html; read docs/HANDOVER.md only for durable detail.
Make a complete examination of PH and PHH/PPH curves, **2D only** (the operator's only self-imposed limitation). First reconcile the operator's note of 116 standalone PH occurrences: the current tree gives 32 docs-only `\bPH\b` and 18 in the three named files, so record the pattern and snapshot that give 116, or mark the note stale, before editing. The generated docs/PH-INTEGER.md and .html come from scripts/ph_doc.py and must not be hand-edited; docs/INTEGER-CUBIC.md and docs/FLOWERS-int.md are hand-edited. Then centralise the definitions: PH = polynomial Pythagorean-hodograph curve; PHH = PH Hermite (the PH quintic interpolant through two points with prescribed tangents); PPH = piecewise PH (PH spans joined with continuity, the C² PH spline). Enumerate every rung of the degree ladder (n=3,4,5,6,7,rational,n=8+) with several examples and all four quadrants — for n=3 show the full nodal Tschirnhausen alpha (self-crossing, endings on the right), with the C-shaped arc only as one segment of it — add the integer lattice hits with their scale, and build the interactive explainer: sliders for the PH-valid generators, the grid m with a live hit count and scale, the quadrants, and the offset (exact PH versus fitted non-PH).
Proves: the 2D PH/PHH/PPH page covers the definitions, the occurrence audit, several examples per rung/all quadrants, the integer hits and scales, and the not-built list; the sliders work; tests and recheck are green.
```

Source: state/HANDOFF-int.md · 2026-11-11 · 31fa200
Context: the PH gallery is the static 9-card base at workbench/ph-families.html; the next session extends it.

---

**Plain English.** A PH curve is a curve whose **speed is a polynomial**. That one
condition makes three things exact: the arc length integrates as a polynomial,
the tangent direction has a rational formula, and the offset curve is rational
instead of a refit. The degree lemma says which degree you get: with `h=1` and
`u,v` linear the curve is cubic; `h` linear gives a quartic; `u,v` quadratic
gives a quintic; and so on. The plain family is the Tschirnhausen cubic, the
quartic, the quintics, the sextic, the septic and the rational circle. The
integer lattice hits are the points at chosen rational parameters that land on
integer coordinates after one common scale: a larger grid (larger `m`) gives
more hits but a larger scale, and the curve itself does not change.

**PHH/PPH (2D only).** The operator's only self-imposed limitation is to stay in
the plane. So **PHH = PH Hermite**: a PH curve through two points with
prescribed tangents, i.e. the PH quintic Hermite interpolant; `hodograph.py` is
the cubic analogue. **PPH = piecewise PH**: PH spans joined with continuity, the
C² PH spline the PH-INTEGER notes already point at. The spatial/helix reading is
out. Do not assume either is the same family as plain PH; the next session must
pin the exact Hermite data and the continuity at the joins.

**The trap.** The `pyth_cubic` integer family is exact but **not PH**: its
name is the control triple, not the hodograph. The cubic PH family is the
Tschirnhausen, the alpha. The C-shaped PH span is one arc of that nodal cubic.

**Sliders.** They help only if they expose the constraints. The useful set is:
the generators (degree, `h`, `u`, `v`), the grid `m` with the live hit count and
scale, the four quadrants/mirror, and the offset `d` showing the exact PH offset
next to a fitted non-PH offset. A "break PH" toggle makes the difference
visible. The PH Hermite and piecewise modes need their own controls (the
endpoint tangents, the join continuity), not the same row.
