# A cloud, for veiling

The cathedral has no single artwork problem; it has one per piece. The proposal is a veil rather than a repair: tone the photographs into one palette of light tans and grays, and put a layered, semi-transparent cloud in front. The cloud is the constant; the works stay different behind it.

> The cloud is also a theological choice. At the Transfiguration, at the baptism, at the temple when Gabriel spoke, at Fatima, the cloud does not explain the action -- it shelters it. What is hidden stays God's to reveal.

| role | tone | use |
| --- | --- | --- |
| wall | #e6dbc9 | the constant ground |
| haze | #ded8cf | outer breath, alpha 0.01 |
| bank | #cfc9bf | the flat base, alpha 0.03 |
| billow | #ddd0bb | volume, alpha 0.04 |
| crown | #f2ead9 | lit tops, alpha 0.05 |
| shadow | #b7ad9d | under the mass, never black |


## 1. Tone first, then veil

![One photograph: value kept, colour dropped, then mapped onto the palette.](fig/cloud-tone.svg)

*One photograph: value kept, colour dropped, then mapped onto the palette.*

Tone is the first half of the unification and the cloud is the second. The photograph here is `reference/IMG_5972.JPG`, reduced to luminance and mapped onto the ramp above; the value structure stays, the colour argument goes. Two works of different periods then sit in the same room before the cloud is even drawn. The cloud hides the remaining seams -- the edges, the varnish, the reproduction -- rather than the subjects.

This is deliberately unheroic: no restoration, no repainting, no claim that the works match. They do not, and the veil says so honestly by being visible.


## 2. The veil

![Four layers of billows over a toned statue and a toned fresco: the works stay legible, the edges soften.](fig/cloud-veil.svg)

*Four layers of billows over a toned statue and a toned fresco: the works stay legible, the edges soften.*

The cloud is built from **exact ellipses**. A circle is a chain with one triangle angle per chord; scaling it by two rational radii and turning it by whole triangle angles gives an ellipse whose every point is still rational. So each billow can be placed on the integer lattice, repeated, mirrored and stored without a float deciding its edge. What is not exact is the compositing: tone and transparency are design numbers, not geometry.

```text
layers   4   haze 0.14, bank 0.34, billow 0.46, crown 0.6
puffs    35  ellipses, tilted by whole triangle angles
edge     fractal displacement + gaussian blur, optical only
veil     0.08, solved to keep 90% of the works' contrast
overlap  the sum does the softening
geometry exact; opacity and tone are choices
```

Two variants are worth keeping. A **cumulus** (above) has a flat base and a domed top. An **incense** cloud is taller, thinner and more transparent, with vertical drift; it is the better veil for a side chapel or a shrine, where the cloud should rise in front of the work rather than rest above it. Both are the same palette and the same ellipses -- only the layout and the opacities differ.


## 3. Circles, ellipses, parabolas, hyperbolas

![A circle and the same circle scaled: both exact, and the rays remain rational under the scale.](fig/cloud-conics.svg)

*A circle and the same circle scaled: both exact, and the rays remain rational under the scale.*

Not all four are the same curve, and it matters which is which. The chain is built from whole triangle angles, so its exact members are the circle (constant turn), the straight line (zero turn), the quarter-turn corner, and the clothoid-like family where curvature grows linearly. A circle is exact. An ellipse is exact **as an affine image of a circle** -- scale x by one rational and y by another, and every point stays rational -- but it is not a Euclidean circle and its curvature is not a clothoid. A parabola and a hyperbola have no such rational affine origin here, and no linear-curvature parameterisation; they can only be approximated, to the lattice's resolution, and the error should be measured rather than assumed.

The constructive part is real: because the ellipse is a scaled circle, a circle with rays from its diameter scales into an ellipse with rays, exactly. That is how the second drawing was made -- same points, same rational slopes, one rational scale. For a sunburst, a rose-window basis, or a billow with ribs, that is enough. For a true parabola or hyperbola, use the float path and report the gap.


## 4. The clothoid-like cloud, in four arcs

The simplest form is not a mass of puffs but four arcs: two big ones under the cloud, turning upward and meeting at (0,0); two half-size ones on top, turning downward and meeting near (0,200). Plotted with the stated centres, the form does not close -- the bottom circles are centred at (120,120) and (-120,120) with radius 169.7, the top at (60,180) and (-60,180) with radius 63.2, and the right-hand pair is nested by 21.6, so there is no side joint.

![The four arcs as stated, with centres and the two meeting points.](fig/cloud-form-stated.svg)

*The four arcs as stated, with centres and the two meeting points.*

Moving the bottom centres in to (100,100) fixes it more neatly than a side crossing would: the bottom radius becomes 141.4, which is also the distance to (0,200), so the bottom pair passes through both (0,0) and (0,200) -- and the top pair already passes through (0,200). That is the common point, and the cloud closes there. Two numbers remain: the big lobes reach x = 241 (about twice the intended width), and the tangent at (0,200) is G0, not G1, so the next tune is one centre and one tangent.

![Bottom centres at (100,100): all four arcs meet at (0,200).](fig/cloud-form-adjusted.svg)

*Bottom centres at (100,100): all four arcs meet at (0,200).*


## 5. What this is not

This framework does not replace the clothoid engine, and it is not a subset of its curves. Bertolazzi gives real clothoids -- exact Fresnel geometry, many parameterisations, tolerances. The chain here is an Euler polygon whose *headings* match a clothoid at the nodes; its position is up to a chord away, and its curvature is a staircase. What it adds is the other column: rational points, rational slopes, exact joins and mirrors, and a known lattice. The caps in `out/caps` came from the engine and transfer here by quantising each chord's turn, with a measured gap. The honest architecture is: engine for the transcendental curve, chain for the exact plan, and a converter between them.


## Reproduce

```text
cd pythagorean-spiral
../.venv/bin/python scripts/cloud.py
../.venv/bin/python -m unittest discover -s tests -t .
```
