# deep → side

> **draft A** — a working draft, not a final text.
**Read these to get up to speed**, in this order (paths from `/Users/thomaskelly/developer/curve-lab`):

1. `docs/deep-to-side.md` — this file: what changed, what not to trust.
2. `docs/STRUCTURE.md` — where every folder is, and the files that matter.
3. `state/DATA-int.md` — every dataset, its format, who writes and reads it.
4. `workbench/finder.json` — the curve finder's current results (read, do not edit).
5. `docs/CURVATURE-POWER-CURVES.md` — the power-curve numbers, all computed by
   `scripts/curvature_power.py`.

Do not read: `reference/` (13 GB, mostly gitignored), `vendor/`, `out/`, `dist/`,
`node_modules/`, `state/HANDOFF-int.md` (long; the tail is the current truth).

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

---

## 2026-11-17 19:55 — where the files are

`docs/STRUCTURE.md` lists the top-level tree with file counts and the files that
matter. Read it before hunting. The short version: `curve_lab/` is the engine,
`scripts/` the generators and audits, `workbench/` the generated pages and their
JSON, `app/src/` the Astro site, `state/` the working memory, `docs/` the book.
Large and excluded: `.git`, `node_modules`, `.venv`, `vendor/`, `reference/`,
`out/`, `site/`, `dist/`.

---

## 2026-11-17 20:00 — absolute root

The repository root is `/Users/thomaskelly/developer/curve-lab` — under
`/Users/thomaskelly/developer/`, not nested in another project. Every path in
`docs/STRUCTURE.md` is relative to that root; `$REPO` means that directory.

---

## 2026-11-18 00:10 — the curve finder's current state

- Stored finds are PH: `u = 1 − 2t + 2t²`, `v` = `(t−p)(t−1+p)(t−½)^m` scaled to
  integers. `lace-1of8-3` matches `p = 1/8, m = 3` exactly.
- Properness ≠ no loops. A loop is a finite failure of injectivity; the reduction
  test only finds covers. Do not say "proper, so no crossings".
- The design family is `x = Q − P, y = Q + P` (P odd, Q even). Crossings are
  two linear equations; 45° tangent is `P' = 0`; the axis crossing is `P = 0`.
- `/finder` shows solved crossings and weighted-balance curves; stars save to
  `workbench/finder-stars.json` (backup kept). Curvature peaks on loop cards are
  **cusps**: the κ figure is unbounded and the page does not say so yet.

---

## 2026-11-18 02:10 — trig is a red flag

`cos`/`sin` of a general angle is irrational and leaves the integer grid for good.
Rational points of the circle are fine (`3-4-5`, `7-24-25`, or `t = tan(θ/2)`
with rational `t`, giving exact fractions like `(527/625, 336/625)`). Any figure
drawn by sampling real trig must be captioned **sampled** and must claim no
exactness. The rule and its reasoning are in `state/DESIGN-int.md`
§Trigonometry; it is also in `AGENTS.md` and `LTMemory-int.md`.
