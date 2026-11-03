# Focused todo

## Heart forms

- [x] `scripts/heart_forms.py` has the expanded formula list; `workbench/heart-forms.html`
  renders **15** forms and `tests/test_heart_forms.py` guards one card per form.
  Done in `41f3d8c`.
- [x] Link the five-figure clothoid-heart page `workbench/hearts.html` to the
  expanded `heart-forms.html`, so the five figures are not read as the whole
  formulaic set.
- [ ] If the formula list grows past fifteen, add the form to `FORMS`, rerun
  `scripts/heart_forms.py`, and let the test fail until the page catches up.

## Clothoid cut

- [x] Full ± table-contact figure **Fig. 5** at **38.5° CW**; the old half-only
  claim is corrected. Done in `73b56a6`.
- [x] Regression test `tests/test_clothoid_cut.py`: the page has Fig. 5,
  `38.5° CW`, and the table-contact text; the measured gap is below 0.001.
- [ ] Note the measured gap: **0.00002** at the page's 40,000-chord sampling.
  The request's **0.0003** is not reproduced; if 0.0003 is wanted, it is a
  different sampling/angle, not a wording change.

The next real work remains the offset catalogue and the plant-form arc in
`goals.md`.
