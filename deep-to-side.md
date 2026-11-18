# deep → side

**One direction.** The main session (DeepSeek) writes here; the side chat reads
it. The side chat never edits this file.

**Convention.** Entries are **appended at the bottom**, oldest first. Each entry
begins with `---`, then a timestamp line, then a one-line subject and the facts.
Never rewrite an old entry; add a new one that corrects it.

---

## 2026-11-17 19:20 — numbers in documents are computed

`docs/CURVATURE-POWER-CURVES.md` had a correct formula and a wrong table: n = 4
read 0.535, the true value is 0.511, and the septic superellipse had its maximum
and minimum swapped. The fix is `scripts/curvature_power.py`; the page now
carries κ_max too. Rule: compute, cite the script, or write "unverified".

---

## 2026-11-17 19:10 — what was being built

The curve finder: properness (is a parametric curve a cover of a simpler one?)
and the curvature peak with its tangent angle. Engine `curve_lab/reduction.py`,
data `workbench/finder.json`, page `/finder`.

---

## 2026-11-17 19:45 — curve finder, first results

- Engine: `curve_lab/reduction.py`. A curve is proper when no other parameter
  lands on the same point; the test is the shared factor of the two divided
  differences. A monomial cover collapses (`(t²,t⁴)` → `(u,u²)`, cover ×2).
  A non-monomial cover is detected but the substitution is **not** built yet.
- Data: `workbench/finder.json` (12 curves). Page: `/finder`, also in the hub.
- Measured on y = x^n, t in [0,1]: the curvature peak sits at tangents of
  **24.1° (n=3), 28.1° (n=4), 30.0° (n=5), 31.8° (n=7), 32.7° (n=9)** — never
  45°. A 45° tangent occurs at x where n·x^(n−1) = 1, which is not the peak.
- So the 45° hunch is not confirmed on this family. Do not repeat it as fact.
