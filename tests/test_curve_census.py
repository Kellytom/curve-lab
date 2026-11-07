"""Every curve table is accounted for: named, or declared outside NAMED.

`generators.NAMED` is the table of named *algebraic* curves with a rational
parametrisation. It is not every curve the project draws: the cycloid, the
catenary and the tractrix are transcendental; the conics other than the circle
live in the conics family; the hearts are their own table. Before this test,
nothing said so, and an audit had to be done by hand.

The rule: a curve is either in NAMED, or listed in OUTSIDE with the table it
lives in and the reason it is not named. A new curve that is added to any table
without a declaration fails here.
"""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import euler_sections as ES  # noqa: E402
import generators as G  # noqa: E402
import heart_forms as H  # noqa: E402
import stem_library as SL  # noqa: E402

# a section of the spine or the stem catalogue, not a curve in its own right
SECTION = re.compile(
    r"(LAC|Fig\.|\+|SM\d|3125|series|fractions|grid|p =|p$|r=|Euler \d|"
    r"½|cubic|quartic|quintic|sextic|ending|stalk|tip arc)", re.I)

# the same curve under two names: the section table's label -> the NAMED key
ALIAS = {
    "semicubical / neile": "semicubical",
}

# name -> (home, kind, why it is not in NAMED)
OUTSIDE = {
    # transcendental: no polynomial equation to test against
    "cycloid": ("euler_sections · stem S69 · ½ cycloid", "transcendental",
                "no rational parametrisation; fitted rails"),
    "catenary": ("stem S66 · ½ catenary", "transcendental",
                 "cosh does not close rationally; four PH cubics carry it"),
    "tractrix": ("euler_sections · stem S52", "transcendental",
                 "cusp at the top; fitted, kept as a curl ending"),
    "involute": ("stem S68", "transcendental",
                 "exact within its own family, but not algebraic"),
    "volute": ("stem S67 · Corinthian and violin scrolls", "composite",
               "a spiral of arcs, not one algebraic curve"),
    "rosette": ("showcase Fig. 10b", "composite",
                "six petals placed on a ring, not one equation"),
    "logarithmic spiral": ("showcase Fig. 12b · leaf C300", "transcendental",
                           "self-similar, not algebraic"),
    "clothoid": ("Euler 45° / 90° · euler_sections", "transcendental",
                 "Fresnel integral; the spines are its discretisation"),
    # conics: rational, but drawn in their own family
    "parabola": ("showcase_catalogue.conic_panels", "rational algebraic",
                 "drawn in the conics family, not the named table"),
    "ellipse": ("showcase_catalogue.conic_panels", "rational algebraic",
                "drawn in the conics family, not the named table"),
    "hyperbola": ("showcase_catalogue.conic_panels · Fig. 11d",
                  "rational algebraic", "two branches; conics family"),
    # hearts: their own table, one of each form
    "Beutel sextic": ("heart_forms.FORMS", "algebraic sextic",
                      "a heart family member, not the named heart"),
    "Fourier Valentine": ("heart_forms.FORMS", "sampled", "Fourier series"),
    "Polar heart": ("heart_forms.FORMS", "sampled", "polar form"),
    "Kuriscak heart": ("heart_forms.FORMS", "sampled", "cartesian form"),
    "Wu/Nick heart": ("heart_forms.FORMS", "sampled", "cartesian form"),
    "Mangaldan heart": ("heart_forms.FORMS", "sampled", "cartesian form"),
    "Dascanio heart": ("heart_forms.FORMS", "sampled", "polar form"),
    "|x| heart": ("heart_forms.FORMS", "sampled", "absolute value of x"),
    "Half-ellipses": ("heart_forms.FORMS", "composite", "assembled arcs"),
    "Square-root heart": ("heart_forms.FORMS", "sampled", "square root"),
    "Eisemann heart": ("heart_forms.FORMS", "sampled", "parametric"),
    "sio heart": ("heart_forms.FORMS", "sampled", "parametric"),
    "Holzapfel heart": ("heart_forms.FORMS", "sampled", "parametric"),
    "Hechinger heart": ("heart_forms.FORMS", "sampled", "parametric"),
}


def norm(name):
    return str(name).lower().replace("×", "x").strip()


def named_keys():
    return {s["key"] for s in G.NAMED}


def outside_keys():
    return {norm(k) for k in OUTSIDE}


def accounted(name):
    key = norm(name)
    return (key in hosted_keys() or key in outside_keys()
            or ALIAS.get(key) in hosted_keys())


def hosted_keys():
    return named_keys() | {norm(f["key"]) for f in H.FORMS}


class TestCurveCensus(unittest.TestCase):
    def test_every_euler_section_is_accounted_for(self):
        for section in ES.SECTIONS:
            name = section[0] if isinstance(section, tuple) else section
            with self.subTest(curve=name):
                self.assertTrue(accounted(name), f"{name} is in no table or declaration")

    def test_every_heart_form_is_accounted_for(self):
        for form in H.FORMS:
            with self.subTest(curve=form["key"]):
                self.assertTrue(accounted(form["key"]), form["key"])

    def test_every_stem_card_is_a_section_or_a_declared_curve(self):
        SL.build()
        for card in SL.CARDS:
            name = card["name"]
            if name in named_keys() or SECTION.search(name):
                continue
            with self.subTest(curve=name):
                self.assertTrue(accounted(name), f"stem card {name!r} is unclassified")

    def test_declarations_do_not_duplicate_the_named_table(self):
        for name in OUTSIDE:
            self.assertNotIn(norm(name), named_keys(), f"{name} is both named and outside")

    def test_every_declaration_states_a_home_and_a_kind(self):
        for name, row in OUTSIDE.items():
            self.assertEqual(len(row), 3, name)
            self.assertTrue(all(part.strip() for part in row), name)


if __name__ == "__main__":
    unittest.main()
