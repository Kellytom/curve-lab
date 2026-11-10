# G3 showcase — figure fixes and their proofs

Each row is a reported figure, the curve, the issue, the change, and the check
that proves it. Figure numbers are as reported; the **curve key** is stable, so
a renumbering does not lose the entry.

## The colour rule

- **Green** — an admitted cusp, or a passing G3 join.
- **Gold** — an advisory tight span, on the diagnostics page only.
- **Red** — a rejected cusp or a failing join.
- The **gallery carries no red tight rings**. A declared cusp is never a red
  ring. A red mark in the gallery is a rejected cusp or a failing join.

## Coordinates

Every figure uses **model coordinates, +y up**. The blue dashed lines are
`x = 0` and `y = 0` (where they fall inside the frame); the bottom-right gives
the x/y extent; every cusp label carries its `(x, y)`. The nephroid's two true
cusps are `(0, −4)` and `(0, 4)`; it has two, so both are green.

## Per-figure notes

Every figure on the showcase links to `g3-notes.html#note-<curve>`. The entry
carries the measurement, the fix note, the join table and a back-link to
`g3-showcase.html#fig-<n>`. A curve that appears both in the lead and in the
gallery shares one note. `tests/test_g3_notes_links.py` checks that every
figure link resolves, that the notes link back, and that the nephroid note
names its two true cusps.

## 2026-11-09

| Fig. | curve | issue | fix | proof |
|---|---|---|---|---|
| 89 | `S44 · Fig. 6 · LAC: p = 0, turn 270` | The LAC was carried by a quintic fit and the page carried a tight ring. It is a source cubic chain. | Carried as its own six four-point spans, S44 label, source tolerance 1e-5; measured 5.63e-8; cubic-native; no gallery ring. | `test_g3_catalogue` source-precision check; `test_g3_fixes` key + cubic-native; page Fig. 89. |
| 100 | `Stage II · Fig. 11 · Arc, Euler, line, Euler, arc · spine 3` | Advisory ring at 10.4% of chord speed read as a defect. | **Verified no defect:** G3 6.3e-14, deviation 0.30%; the ring is removed. If it still looks wrong, the point/coordinate is needed. | `test_g3_fixes` gallery red count 0; record in the page. |
| 104 | `Stage II · Fig. 13 · Log spiral, one turn each way · spine 3` | Advisory ring at 17.5%. | Gallery ring removed; gold on diagnostics. | `test_g3_fixes` gallery red count 0. |
| 106 | `Stage II · Fig. 14 · Involute, one turn each way · spine 3` | Advisory ring at 21.6%. | Gallery ring removed; gold on diagnostics. | same |
| 109 | `Stage II · Fig. 16 · Log spiral, two turns each way · spine 2` | Advisory ring at 10.9%. | Gallery ring removed; gold on diagnostics. | same |
| 118 | `Stage II · Fig. 19 · Log spiral, both ends · spine 3` | Advisory ring at 24.3%. | Gallery ring removed; gold on diagnostics. | same |
| 130 | `Stage II · Fig. 20 · Involute, both ends · spine 3` | Advisory ring at 22.0%. | Gallery ring removed; gold on diagnostics. | same |
| 141 | `Stage II · Fig. 5 · The S branch · spine 3` | Advisory ring at 12.6%. | Gallery ring removed; gold on diagnostics. | same |
| 143 | `Stage II · Fig. 5 · The S branch · spine 5` | Advisory ring at 12.6%. | Gallery ring removed; gold on diagnostics. | same |
| 148 | `Stage II · Fig. 6 · The S root · spine 4` | Advisory ring at 10.2%. | Gallery ring removed; gold on diagnostics. | same |
| 150 | `Stage II · Fig. 6 · The S root · spine 6` | Advisory ring at 10.0%. | Gallery ring removed; gold on diagnostics. | same |
| 161 | `misc · Maclaurin trisectrix · exact loop` | Advisory ring at 10.6%. | Gallery ring removed; gold on diagnostics. | same |
| 165 | `misc · Pell · x² − 2y² = 1 · +` | Advisory ring at 13.3%. | Gallery ring removed; gold on diagnostics. | same |
| 166 | `misc · Pell · x² − 2y² = 1 · −` | Advisory ring at 13.3%. | Gallery ring removed; gold on diagnostics. | same |
| 167 | `misc · Reuleaux triangle` | Advisory ring at 11.6%. | Gallery ring removed; gold on diagnostics. | same |
| 173 | `misc · catenary` | Advisory ring at 20.7%. | Gallery ring removed; gold on diagnostics. | same |
| 47 | `heart · Eisemann lower` | The 10% speed floor rejected the correct cusp-ending fit and chose a rounded alternative. | Cusp-aware fit (`allow_cusp`); the 0.0389 fit is restored; the cusp is declared; no ring. **Needs your eye:** the cusp is the junction with the upper half. | `test_g3_fixes`; error 0.0389 restored. |
| 48 | `heart · Hechinger lower` | Same floor regression. | Same fix; declared cusp. **Needs your eye:** half-heart junction. | `test_g3_fixes`. |
| 49 | `heart · Kuriscak lower` | The end cusp was rounded; the floor overruled the source. | Cusp-aware fit; one declared cusp at the end. **Needs your eye:** confirm the end tangent or draw the sibling. | `test_g3_fixes`. |
| 51 | `heart · Mangaldan` | Floor chose a worse fit (0.0914 vs 0.0226) with the cusp moved. | Cusp-aware fit; the 0.0226 fit is restored; cusp ×2. **Needs your eye:** the cusp locations. | `test_g3_fixes`; probe error 0.0226. |
| 54 | `heart · Valentine` | Floor chose a much worse fit (1.038 vs 0.331). | Cusp-aware fit; the 0.331 fit is restored; cusp ×2. **Needs your eye:** the cusp locations. | `test_g3_fixes`; probe error 0.331. |
| 59 | `heart · |x|^(2/3) lower` | The cusp at x=0 is an interior cusp and is currently smoothed. | **Needs fix:** split the branch at x=0 into two arcs; the two arcs then meet sharply. | `test_g3_fixes` needs-fix note. |
| 60 | `heart · |x|^(2/3) upper` | Same interior cusp. | Same split. | `test_g3_fixes` needs-fix note. |
| 30 | `bicorn` | Described as a node; the curve has two cusps. | `cusp ×2`; admitted cusp, green; no red ring. | `test_g3_fixes` "cusp ×2". |
| 35 | `deltoid` | Cusp count and red mark. | `cusp ×3`; admitted, green; no red ring. | `test_g3_fixes` "cusp ×3". |
| 14 | `nephroid` | The card showed only the first control branch, so the marker landed on a fake cusp. | Full control branches; the two true cusps `(0, −4)` and `(0, 4)` are green and coordinate-labelled. | `test_g3_fixes` nephroid labels. |
| 36 | `epicycloid k=3` | Cusp count and red mark. | `cusp ×4`; admitted, green; no red ring. | `test_g3_fixes` "cusp ×4". |
| 37 | `epicycloid k=5` | Cusp count and red mark. | `cusp ×6`; admitted, green; no red ring. | `test_g3_fixes` "cusp ×6". |
| 38 | `hypocycloid k=5` | Cusp count and red mark. | `cusp ×5`; admitted, green; no red ring. | `test_g3_fixes` "cusp ×5". |
| — | `semicubical`, `pear` | Rejected cusps kept beside the admitted family. | Red cusp marks and the measured rejection reason. | `test_g3_fixes`; cusp section. |

The contents block before Figure 1 links to **Every complete curve · 154**;
the count is generated from the catalogue, not typed.
