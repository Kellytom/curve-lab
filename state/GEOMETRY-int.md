# GEOMETRY — the book, and the parts of it this project uses

Read this before drawing a figure. It exists because figures were being drawn by eye
and corrected afterwards; geometry is the part that settles a figure before it is
drawn.

## The source

- **Euclid, *Elements*.** The edition to read online is David E. Joyce's, at Clark
  University: <http://aleph0.clarku.edu/~djoyce/elements/Euclid.html>. It is the
  Heath translation with commentary, out of copyright, and every proposition has its
  own page.
- **A single PDF**, if a whole book is wanted: Richard Fitzpatrick's edition,
  <https://farside.ph.utexas.edu/Books/Euclid/Elements.pdf> — free to read and to
  cite.
- For the parts Euclid does not have — reflections, rotations, groups — the standard
  public-domain reference is **Hilbert, *Foundations of Geometry* (1902)**, and for
  the group language, Armstrong, *Groups and Symmetry* (library).

## What is used here, and where

| proposition | what it says | where it is used |
|---|---|---|
| **I.4** (SAS) | two triangles with two sides and the included angle equal are congruent | the chain of triangles is a chain of congruent copies |
| **I.47** | in a right triangle the square on the hypotenuse equals the sum of the squares on the legs | `7² + 24² = 25²`; every p-triple figure |
| **I.18 / I.19** | the greater side lies opposite the greater angle | why the leg order matters when a triangle is written down |
| **III.2** | a straight line through the centre meets the circle at its extreme points | the radius used as a measuring stick |
| **III.20** | the angle at the centre is twice the angle at the circumference | turning the triangle's angle into the apex's angle |
| **III.36** (tangent–secant) | the square on the tangent equals the product of the secant's parts | the size of a step between two circles |
| reflections | a reflection in a line fixes the line and preserves every distance | the mirror line through `O` keeps apices on radius 25, feet on radius 24 |
| **two reflections = one rotation** | reflecting in two lines that meet at `O` composes to a rotation about `O` by **twice** the angle between them | the step of the walk is the square of the triangle's turn: `527 + 336i = (24 + 7i)²` |
| orbit | the set of points reached by repeatedly applying one symmetry | the walk itself: `apex, R·apex, R²·apex, …` |

## The definitions the figures must obey

- **Circle**: the set of points at one distance — the **radius** — from a **centre**.
  A figure of a circle must contain the centre and the whole circumference, or it is
  a figure of an arc and must say so.
- **Congruent**: same lengths, same angles. A rotation, a reflection and a
  translation are the only moves that keep congruence; drawing "the same triangle
  again" by eye is not one of them.
- **Reflection in a line through the centre** preserves distance to the centre. This
  is the single fact that keeps a walk on its circle; it is not an observation about
  the drawing.
- **Rotation about `O`** preserves every distance from `O`. In this project a rotation
  is written as multiplication by a Gaussian rational of length 1:
  `(24 + 7i)/25`, `(527 + 336i)/625`. If its length is not exactly 1, it is not a
  rotation and the walk leaves the circle.
- **Orbit**: the points `x, g·x, g²·x, …` for one symmetry `g`. The walk is an orbit;
  the figure is the orbit drawn; the table is its coordinates. Store the generator
  and the seed, derive the rest.

## How to use this file

1. Before drawing, write down which object the figure is: a circle, a congruence, a
   rotation, an orbit. If none fits, the figure is not yet understood.
2. Check the figure against the propositions above — not against how it looks. The
   two failures this project has had (`state/PROBLEMS-prime-mover-int.md` §11 and
   §12) were both a circle drawn outside its own frame, which I.2 and the definition
   of a circle refuse on sight.
3. Put the theorem in the spec, beside the figure it governs, so the check can
   assert it: radius preserved, angles equal, spacing equal, and so on.
