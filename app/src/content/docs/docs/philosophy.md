---
title: "Design philosophy"
---

> **draft A** — a working draft, not a final text.
The question this answers: when we say "a fleur", what is the object, in what
order is it built, and what are its parts called?

## The logic of beauty

Beauty is not an optional accessory.

Take a simple black square on a white background, say a piece of paper. Stare at
the square for a little, then look at the white part of the paper. You see a
floating square. If you just look at the square continuously, you notice the
edges seem to have the same effect as when you looked at the white part of the
paper: a halo effect. This is because of the way our eye is constructed; the
receptors get tired, and so a shadow shape is formed.

When we add a beautiful frame to the square, we are softening the effect of
tiredness in our eyes. The halo effect is swallowed up by the ornate part of the
frame. Frames are often gold coloured not to show richness, but because the halo
often has a golden or reddish-brown luminance.

The same with a diploma on the wall, with an engraved outside edge — it makes it
easier to look at.

The line weight has to vary, and different colours help as well. This keeps the
halo effect to a minimum.

When we look at a window, we get the same effect in reverse: the light from the
window creates a halo or shadow effect when we look away. Stained glass windows
soften that effect, when they are done right.

Another thing beauty does is orient us. Usually they help us retain balance by
literally showing us which way is up. Often beautiful designs are symmetric
side to side but they are different on top than they are on the bottom.

The consequences for this project: **the frame is not decoration around the
curve, it is the part that lets the eye rest.** A uniform hairline is the case
the eye tires of first, which is why the plates want two weights and a mid tone,
and why a border that collides with its centre reads as a fault however correct
the geometry.

## The glyph is a graph, not a walk

There is no single curve to walk from 1 to 2 to 3. A glyph is:

    glyph   = parts + joints + symmetry + measurement
    part    = a full line (stroke body) with two terminals
    joint   = a declared contact between two parts
    symmetry= mirror, applied to the whole glyph
    measure = clearance, crossings, folds

Order of drawing is **layer order**, not connectivity. Order of building is
**part by part**, each part walked once along its spine. A fleur is not "trace
the outline"; it is "a lance, two petals, a band, a foot, two tails, mirrored,
with declared joints between them".

## The full line

The three lines together — centre and both rails — are a **full line**.

- **spine** — the centre line, the curve the engine computes.
- **rail** — either edge. `rail +` is on the left of travel, `rail −` on the
  right, with left = `(-t.y, t.x)` for tangent `t` (y up).
- **full line** — spine + both rails + the width law that relates them. This is
  the unit of design, measurement and naming ("the petal's full line").
- **stroke** is reserved for what SVG means: the drawn mark. Using it for the
  body would collide with `stroke-width` and `stroke-linecap` in every file.

**Direction is part of a full line.** A stroke is walked from its *start*
terminal to its *end* terminal, and the rails are named by that direction.
Mirroring reverses handedness: the mirror's left rail is the original's right.
A terminal is therefore never just "the end"; it is the start or the end.

## Sections, not independent walks

At one station `s` along the spine, the three lines are one cross-section:

    section(s) = (left, spine, right, tangent, curvature, width)

This is the "design box" idea, and it is how the model should *think*: width,
terminal width laws, clearance and folds are all properties of a section or a
pair of sections. The rails are **derived at the same stations**, never walked
separately and never independently re-timed.

Rendering is allowed to disagree in representation, not in meaning: each rail is
fitted to cubics for SVG, so the output is three paths that no longer share a
parameter. That is fine — the authoring model is section-locked, the output is
path-locked. Measurements take the fitted paths and carry their error bound.

## Infinity, linearity, curve

Every design carries three aspects. They may live in different parts, but all
three must be present:

- **linearity** — a section with zero curvature: a straight run, a line, a
  chord. It is the rest in the phrase.
- **curve** — a section whose curvature *changes*: an Euler span, a LAC, a
  petal. An arc is bent, but a circle has constant curvature, so it is one
  limit case, not the whole of the aspect.
- **infinity** — a tendency the stroke approaches and does not reach: a spiral
  whose curvature tends to a circle's, a heading that tends to a limit, a line
  whose direction is a point at infinity. Infinity is a tendency, not a
  vanishing point and not a decorative taper.

A design with only two is incomplete: a circle alone is all curve, a cross
alone is all line, a plain spiral is curve plus infinity with no rest. The rule
is about the whole design, not every part: a straight stem can supply
linearity, a petal the curve, and a spiral tail the infinity.

Examples:

| object | linearity | curve | infinity |
|---|---|---|---|
| Euler curve / Euler | κ → 0 at one end | κ grows | the heading limit |
| LAC | the low-curvature start | the power-law bend | the limiting circle |
| 3-4-5 exact chain | straight chords | triangular-number headings | the open spiral's limit |
| integer cubic | straight end tangents | the S bend | **absent** — pair it with a spiral or a ray |
| fleur | band and lance | petals | **absent** — needs a spiral tail or ray |
| volute proof | the straight chords | the growing headings | the open spiral's limit heading |
| cruciform proof | the arms | the fillets | **absent** — needs a ray or a spiral tail |
| ending-fit sheet | the stalk | the sections | n/a — a measurement, not a design |
| modulated-width sheet | the spine | the width law | n/a — a measurement, not a design |

The last two rows are recorded gaps, not rejections: the cubic and the fleur
are legal parts, and a design that contains one must supply the missing aspect
elsewhere. Name the three aspects on the page or in the notes. A missing aspect is a gap
to fill, not a silent pass. The rule applies to **designs**; a measurement or
catalogue page states the aspects of the objects it measures, but is not
itself a design.

## Grounded

Every design must be grounded: it has a horizontal datum — a ground line,
baseline, plinth, band or foot — and a vertical element (stem, lance, axis,
trunk) whose relation to that datum is stated. The relation may be visible
(drawn) or invisible (declared in the construction), but it may not be absent.

- **visible:** the fleur's band and foot; the cruciform's horizontal arms; a
  plant stalk's ground line.
- **invisible:** the volute's start tangent as the ground and its 90° heading
  as the vertical; the integer cubic's horizontal chord and its vertical arm
  tangents.

A design that floats — a curve with no ground and no vertical — is incomplete.
Name both on the page or in the notes: "ground: …; vertical: …".

| design | ground | vertical |
|---|---|---|
| fleur | band + foot | lance |
| cruciform | horizontal arms | trunk |
| volute | start tangent (declared) | 90° heading (declared) |
| integer cubic | chord P0–P3 | arm tangents |
| plant stalk | baseline / grid | stalk |
| modulated width | endpoint horizontals | spine |

## Lattice: points and stations

Two different things are called "a lattice hit". Keep them apart:

- a **lattice point** — both coordinates are integers. This is the strong
  claim, and it is what cuts, joins, branches and exact nodes need.
- a **lattice station** — one coordinate is an integer: the stalk crosses a
  horizontal grid line. This is what a growth mark needs, because the mark sits
  at a place on the stalk, not at a point that must be integer in both axes.

Measured on the plant-form stalk (the proof's unit-scale curve, y from 0 to 8):
**seven** horizontal crossings at y = 1…7, and **none** of them has an integer
x; the only full lattice point on the whole stalk is its start (0, 0). On the
3-4-5 lobe, 2 of 11 nodes are integer at scale 1, and all 11 are integer at
×9,765,625. A rule that demanded full points for marks would put one mark on
the proof stalk and none on most real stems.

So: marks at **stations**, exact operations at **points**. Never call a
station a lattice point in a page or a note.

## Terminals

- A **terminal** is any treatment of a full line's end.
- A **cap** is the subset that closes the cross-section without turning past the
  cap limit (120° for now, tunable).
- A **taper** closes by narrowing: `taper`, `cone`, `bulb` (the width-law bulb).
- A **turned terminal** goes past the limit: hairpin, wrapped bulb. Not caps.

Terminals belong to ends, not to traces: `(start, end)` is part of the model.

## Joints

A **joint** is where two full lines meet: leaf into branch, branch into trunk.
It is declared, never inferred from proximity. Declaring it does two things:

1. it permits the crossing or merge inside its footprint;
2. it waives clearance *inside* that footprint, and only there.

The **gore** is the part of the gap just outside the footprint; it is measured
normally, which is what keeps a junction from hiding crowding. The **counter**
is the white shape the gap makes — the bulb beside a terminal is a counter.

## Mirror

The mirror is a symmetry of the glyph, not a second drawing. It duplicates
every part whose rule says it is mirrored, and swaps the handedness of terminals
and rails. The centre seam is a joint like any other: if the two halves touch,
that contact is declared.

## What this rules out

- **No global walk.** No 1,2,3 around the outline; no imposed starting point.
- **No implicit joins.** Two strokes that happen to touch are a violation until
  declared.
- **No rail-first design.** A rail is always a section of a full line, never an
  independent curve that the spine is inferred from.
- **No style in geometry.** Width is geometry (a law), not a stroke attribute.

## Where the code stands

| Idea | In code |
|---|---|
| glyph = parts + joints + mirror | `Piece` (traces, contacts, mirror) |
| full line | `Trace` + width; rails built as `Group`s |
| section | `section.py`: `Section`, sampled by arc length |
| terminal (cap / taper / turned) | `terminals.py`; turned not built |
| joint | `Contact`, `Junction` |
| measurement | `clearance.py` |
| grammar | `grammar.py` (study 01) |

The read model is `Section`; the grouping object is `Bundle`. It is what a terminal width law, a
junction gore and a clearance sample all want to read, and today each of them
reconstructs it from the fitted paths.
