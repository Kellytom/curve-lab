# UNRESOLVED — curves held for a link

Items found in research that cannot be built yet. Each names what is missing,
where it would land, and a place for the link. The operator supplies links; a
later session reads this file first and does not re-search from scratch.

| item | what is missing | where it would land | link |
|---|---|---|---|
| σ-curve (sigma) | the definition — named as an LAC extension in Miura & Gobithaasan, *Log-Aesthetic Curves and Similarity Geometry*, IJAT 18(5) 591–602 (2024); the article page is open but the definition is in the PDF | the Gen-Arch / LA page, beside α = 3 and Nielsen | |
| τ-curve (tau) | same paper, same problem — the abstract names it, the formula is in the PDF | the Gen-Arch / LA page | |
| quartic Catmull–Rom | no standard planar curve of that name was found; Catmull–Rom is cubic. A source that defines the quartic variant is needed before anything is drawn | probably not a family; if real, alongside the presets | |
| propeller curve | no standard planar curve found; looks like a shape name, not a family | only if a definition appears | |
| σ/τ discrete analogues | whether the discrete LAC scheme extends to them; the paper's recurrence is in arXiv 1808.03104 for LAC only | the discrete LAC section | |

**How to use it.** Add the link, say in one line which row it belongs to, and
leave the rest. Do not draw the curve from memory: the project's rule is that a
curve enters from a table, never from recall.

**Not here** (already resolved): biarcs, kappa curve, qAC, discrete LAC,
Beta-splines, Lissajous, yin-yang boundary — these have definitions and belong
to the showcase or the joins documentation.


## Found in the session record — audit 2026-11-07

These were named in `HANDOFF-int.md`, `TASKS-int.md`, `BACKBURNER-int.md` or
`goals.md` but never drawn. They are listed separately because they are local
gaps, not literature gaps: each has a source in the repo, not a missing citation.

| item | where it was named | state | what would resolve it |
|---|---|---|---|
| Stage III serif outlines (4) | `goals.md` §Source intake | **not wired** — the plate spine is a straight `data-line`, so the cubic-spine reader returns 0 | a straight-spine reader, or the four outlines taken from the terminal intake; lands beside the W02 terminals |
| Combined curves, "excluding the ones not certain" | `state/TASKS-int.md` | unchecked | name which combined panels are uncertain, then the companion pass applies to those that remain |
| Euler spiral → cubic Bézier fit (endpoint parabolas) | `BACKBURNER-int.md` **B02** | candidate, not implemented | a fitted seam option: left/right parabolas, controls at their intersection with the tangent rays; O(n⁵) |
| Spiro / G2 interpolating spirals | `app/src/content/docs/docs/junction.md` prior art | not built | evaluate as the global G2 alternative to per-join solving; one page, one measured comparison |
| "Full cubic catalogue" | `LTMemory-int.md` open list | **ambiguous** — 316 curves / 632 sign variants already exist | decide whether "full" means the 632 variant set or the 992 representative set, then say which is drawn |
| Canonical fleur | `HANDOFF-int.md` deferred | a **form**, not a curve; blocked on silhouette approval | `fleur_canonical()` from the measured reference; keep study 01 as history |

**Not curves — do not add here:** the ribbon fill (`ribbon.outline`), turned
terminals, the six remaining W05 storeys, the primal gate, the veil (a 3D cloud
study), double tangency and the Gerono arc choice. They are tracked in
`TODO.md` and `HANDOFF-int.md`; putting them in this register would blur what a
"missing curve" means.
