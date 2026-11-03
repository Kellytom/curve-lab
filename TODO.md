# Focused todo

## Heart forms

- [x] `scripts/heart_forms.py` has the expanded formula list; `workbench/heart-forms.html`
  renders **15** forms and `tests/test_heart_forms.py` guards one card per form.
  Done in `41f3d8c`.
- [x] Link the five-figure clothoid-heart page `workbench/hearts.html` to the
  expanded `heart-forms.html`, so the five figures are not read as the whole
  formulaic set.
- [x] If the formula list grows past fifteen, add the form to `FORMS`, rerun
  `scripts/heart_forms.py`; the test already fails until the page catches up.

## Clothoid cut

- [x] Full ± table-contact figure **Fig. 5** at **38.5° CW**; the old half-only
  claim is corrected. Done in `73b56a6`.
- [x] Regression test `tests/test_clothoid_cut.py`: the page has Fig. 5,
  `38.5° CW`, and the table-contact text; the measured gap is below 0.001.
- [x] Note the measured gap: **0.00002** at the page's 40,000-chord sampling.
  The request's **0.0003** is not reproduced; if 0.0003 is wanted, it is a
  different sampling/angle, not a wording change.

## Offset catalogue — complete

- [x] `stem-library-offset.html`: OffS1–OffS12; formulaic curves, then conics,
  then the LAC chain rails, then a two-stalk card.
- [x] **Levien's parallel Bézier** is the fitted cubic-Bézier option
  (`curve_lab/parallel_bezier.py`); its error is compared with the exact PH
  rail and the LAC chain rail, and cusp/clamp counts are reported.
- [x] Parallel conics: **OffS7 parallel parabola**, OffS8 ellipse, OffS9
  hyperbola.
- [x] Every pair is separated by 2 × offset; the card gutter is the breathing
  room. OffS12 shows two stalks with their envelopes separated.

Focused todo complete. The next layer is the plant-form endings (flower,
seagrass/leaf, or cone terminal at R = 2 × offset), then growth marks and
branches; `next-fhandoff-int.md` carries that action. The long arc stays in
`goals.md`.
