---
title: "Concepts"
---

> **draft A** — a working draft, not a final text.

The words this project uses, each with one meaning. If a term is missing, the
[Glossary](/docs/glossary/) has the longer list.

## Euler curve

An **Euler curve** is the curve whose curvature rises in proportion to arc
length. Roads and railways use it as the transition into a bend, and a
draughtsman's French curve is a short piece of one. The older name is
**clothoid**, or **Euler spiral**; this project says Euler curve in prose and
keeps `clothoid` in code, file names and the name of the vendored library
(Bertolazzi and Frego's *Clothoids*).

Two facts follow from the definition, and they are why the project uses it:

- the tangent turns smoothly, with no jump in curvature at a join;
- the shape is fixed by very few numbers, so it is easy to state and compare.

## Exact curve

An **exact curve** here is a curve written as polynomials in a parameter `t`,
with whole-number or rational coefficients. Nothing is sampled. Given `t`, the
point is a fraction, and the measurement is arithmetic rather than a fit.

## Speed, and the square

Write the curve as a complex polynomial `w(t) = p(t) + i q(t)`, and let the curve
be

```
z(t) = ∫ w(t)² dt
```

Then the velocity is `w²`, and its length is `|w|² = p² + q²`, a polynomial. A
polynomial length means the arc length is a polynomial integral, which is why it
can be computed exactly. A curve with this property is called a **Pythagorean
hodograph** curve, or **PH** curve.

## Grid

The **grid** is the pitch the curve's points can land on, written as a fraction
`1/n`. To find it, integrate the speed rows term by term, collect the
denominators of the position terms, and take their least common multiple. Grid
1/2730 means: multiply the position by 2730 and every coefficient is a whole
number.

A cheap grid is a curve that is easy to store and compare. A grid of
1/86,625,000,000,000 is not, which is why the page refuses certain tweak sizes.

## Bend

**Bend** is arc length divided by the straight distance between the two ends:
how much longer the curve is than the line it spans. A straight line has bend 1.
Bend 1.418 means the curve is 41.8% longer than its chord.

It is a single number for the whole curve, not a curvature at a point.

## Arc and chord

The **arc** is the length along the curve, exact as a fraction. The **chord** is
the straight distance between the two ends. Bend is arc over chord.

## Flat spot

A **flat spot** is a place where the stroke runs horizontal: a root of `q(t)`.
A flat spot counted twice or three times is a repeated root, and a repeated root
holds the stroke flat for a stretch. The number of flat spots, and where they
are, is one of the few things that fixes the shape.

## Crossing pair

A **crossing pair** is two parameters `t₁ < t₂` where the stroke passes through
the same point. The number is scale-free, and it is what the galleries sort by.

Three passes through one point are **three pairs at one place**. If a reader
needs places, say *meeting points*; never call both "crossings".

## Loop

The **loop** is the part of `t` that holds the knot, written as a range such as
`t 0.0249 to 0.9741`. It is a viewing window, not a different curve.

## Step

The **step** is the power step of the rows. At step 1 the powers are whole
numbers. At step ½ they are halves, and the curve is a polynomial in `√t`.
Fractional steps are an experiment: they give new shapes but no exact integer
grid and no mirror symmetry.

## Symmetry

Measured on the spine at 400 stations, not guessed:

- **half turn**: `C(1/2+s) + C(1/2−s) = 2C(1/2)`;
- **mirror**: the same about the vertical line through the midpoint;
- **none**: neither, within 0.5% of the bounding-box diagonal.

The operator's category is stricter than the axis test, so both are printed.

## Rails

A **rail** is a side curve at a stated distance from the spine. The book plates
use **character rails**: the offset is bowed by a strength and a profile, so the
rail reads as a drawn edge rather than a mechanical parallel. A rail folds where
`|d · κ| ≥ 1`; the fold is measured and printed.

## Plate, section, junction, contact

- A **plate** is one book image: a spine plus its rails, clipped to the curve.
- A **section** is one station across a full line.
- A **junction** is a branch plus a trunk plus a declared merge.
- A **contact** is a declared legal touch, so a deliberate join is not reported
  as a collision.

## Positive y

In the model, positive y points up. SVG's y points down, so the writer flips once
at output and nowhere else. A figure never inherits y-down silently.

## How a claim is checked

A number is a fraction or a count, produced by one function and reproduced by one
command. The commands are in [Verification](/docs/verify/). A drawing can show a
result; it cannot prove one.
