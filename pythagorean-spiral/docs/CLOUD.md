# A cloud, for veiling

The cathedral has no single artwork problem; it has one per piece. The proposal is a veil rather than a repair: tone the photographs into one palette of light tans and grays, and put a layered, semi-transparent cloud in front. The cloud is the constant; the works stay different behind it.

> The cloud is also a theological choice. At the Transfiguration, at the baptism, at the temple when Gabriel spoke, at Fatima, the cloud does not explain the action -- it shelters it. What is hidden stays God's to reveal.

| role | tone | use |
| --- | --- | --- |
| wall | #e6dbc9 | the constant ground |
| haze | #ded8cf | outer breath, alpha 0.07 |
| bank | #cfc9bf | the flat base, alpha 0.07 |
| billow | #ddd0bb | volume, alpha 0.22 |
| crown | #f2ead9 | lit tops, alpha 0.31 |
| shadow | #b7ad9d | under the mass, never black |


## 1. Tone first, then veil

![One photograph: value kept, colour dropped, then mapped onto the palette.](fig/cloud-tone.svg)

*One photograph: value kept, colour dropped, then mapped onto the palette.*

Tone is the first half of the unification and the cloud is the second. The photograph here is `reference/IMG_5972.JPG`, reduced to luminance and mapped onto the ramp above; the value structure stays, the colour argument goes. Two works of different periods then sit in the same room before the cloud is even drawn. The cloud hides the remaining seams -- the edges, the varnish, the reproduction -- rather than the subjects.

This is deliberately unheroic: no restoration, no repainting, no claim that the works match. They do not, and the veil says so honestly by being visible.


## 2. The veil

Two versions, same composition, different geometry. **v1** is the original cloud of exact ellipses -- the one that was right in principle and only too opaque -- now with the veil factor on every layer instead of the base alone. **v2** replaces each ellipse with a turn-chain ribbon. Both are measured by the same function and judged by the same strips.

![v1: the original ellipse cloud, one veil factor on every layer.](fig/veil-v1.svg)

*v1: the original ellipse cloud, one veil factor on every layer.*

![v2: the same composition in turn-chain ribbons, one veil factor on every layer.](fig/veil-v2.svg)

*v2: the same composition in turn-chain ribbons, one veil factor on every layer.*

The cloud is built from **exact turn chains**, not circles. A billow is a lobe whose turns run k**p and then reverse, so the exit is parallel to the entry; a taper through `ribbon.outline` turns it into a closed rational polygon with pointed ends. The power dial is the layer: p = 1 is the clothoid, p = 2 and 3 hold the turn back to the apsis and curl the tail. So each billow can be placed, repeated and stored without a float deciding its edge. What is not exact is the compositing: tone and transparency are design numbers, not geometry.

```text
layers   4   haze 0.1, bank 0.09, billow 0.3, crown 0.42
billows  90  turn-chain ribbons: turns k**p, tapered
edge     fractal displacement + gaussian blur, optical only
veil     v1 0.104 (peak 80%), v2 0.736 (peak 80%)
overlap  the sum does the softening
geometry exact; opacity and tone are choices
```

Two variants are worth keeping. A **cumulus** (above) has a flat base and a domed top. An **incense** cloud is taller, thinner and more transparent, with vertical drift; it is the better veil for a side chapel or a shrine, where the cloud should rise in front of the work rather than rest above it. Both are the same palette and the same ellipses -- only the layout and the opacities differ.


## 2b. Against four test patterns

A veil is judged by what it leaves legible. Four standard patterns -- a Siemens star, an eleven-step grey wedge, colour bars and a chequer with a crosshair -- sit under the same billows as the works: two on top, where the cloud is densest and meets the top of the image, two below, where it drifts. Each is sampled on a grid and the composited alpha is reported as mean, 95th percentile and worst. Both versions are solved to the same peak, 80 per cent -- the number chosen on the slider below -- so the comparison is about where the density lands, not how strong it is. The gate reads the row mean, because the mean is how much of the image is covered: top mean under 0.25 (a hot corner is allowed up to 0.50), bottom mean under 0.12 (up to 0.30).

![v1 under the four patterns: two on top, two below.](fig/veil-test-v1.svg)

*v1 under the four patterns: two on top, two below.*

![v2 under the four patterns: two on top, two below.](fig/veil-test-v2.svg)

*v2 under the four patterns: two on top, two below.*

| version | pattern | row | mean | p95 | worst |
| --- | --- | --- | --- | --- | --- |
| v1 | Siemens star | top left | 0.428 | 0.553 | 0.587 |
| v1 | grey step wedge | top right | 0.424 | 0.589 | 0.609 |
| v1 | colour bars | bottom left | 0.104 | 0.222 | 0.232 |
| v1 | chequer + cross | bottom right | 0.112 | 0.214 | 0.269 |
| v2 | Siemens star | top left | 0.131 | 0.301 | 0.417 |
| v2 | grey step wedge | top right | 0.085 | 0.240 | 0.475 |
| v2 | colour bars | bottom left | 0.089 | 0.205 | 0.264 |
| v2 | chequer + cross | bottom right | 0.045 | 0.186 | 0.264 |

The numbers come from `pythagorean_spiral.veil`, the same function the drawing fills, so a strip cannot pass on paper while the picture covers it. `scripts/veil_test.py` writes the standalone page and `tests/test_veil.py` holds the gate.


## 2c. Set the transparency by eye

The model should not be the authority on a design number. This strip is one uniform layer of one cloud colour over the same four patterns; drag the slider until the top row is as legible as you want it and the bottom as light as you want it. The percentage is the target the veil should then be solved to.

<div class="veillab">
<style>
.veillab { margin: 22px 0 8px; }
.veillab .wrap { position: relative; border: 1px solid #d8ccae; }
.veillab .strips { display: grid; grid-template-columns: 1fr 1fr; gap: 6px;
  padding: 6px; background: #e6dbc9; }
.veillab figure { margin: 0; }
.veillab svg { display: block; width: 100%; height: 120px; border: 1px solid #cbbfa2; }
.veillab figcaption { font: 10px ui-monospace, Menlo, monospace; color: #7b6c4e;
  padding-top: 3px; }
.veillab .veil { position: absolute; inset: 0; background: #ddd0bb;
  opacity: 0.80; pointer-events: none; }
.veillab .controls { display: flex; gap: 14px; align-items: baseline;
  margin-top: 12px; font: 12px ui-monospace, Menlo, monospace; color: #7b6c4e; }
.veillab input[type=range] { flex: 1; max-width: 420px; accent-color: #8c6a21; }
.veillab output { font-size: 15px; color: #2e2413; }
.veillab .note { font-size: 12px; color: #7b6c4e; margin-top: 6px; }
</style>
<div class="wrap">
  <div class="strips"><figure><svg viewBox="0 0 100 100" preserveAspectRatio="none" role="img" aria-label="Siemens star · top left"><polygon points="50,50 96.00,50.00 95.61,56.00" fill="#14120e"/><polygon points="50,50 94.43,61.91 92.50,67.60" fill="#f7f4ec"/><polygon points="50,50 89.84,73.00 86.49,78.00" fill="#14120e"/><polygon points="50,50 82.53,82.53 78.00,86.49" fill="#f7f4ec"/><polygon points="50,50 73.00,89.84 67.60,92.50" fill="#14120e"/><polygon points="50,50 61.91,94.43 56.00,95.61" fill="#f7f4ec"/><polygon points="50,50 50.00,96.00 44.00,95.61" fill="#14120e"/><polygon points="50,50 38.09,94.43 32.40,92.50" fill="#f7f4ec"/><polygon points="50,50 27.00,89.84 22.00,86.49" fill="#14120e"/><polygon points="50,50 17.47,82.53 13.51,78.00" fill="#f7f4ec"/><polygon points="50,50 10.16,73.00 7.50,67.60" fill="#14120e"/><polygon points="50,50 5.57,61.91 4.39,56.00" fill="#f7f4ec"/><polygon points="50,50 4.00,50.00 4.39,44.00" fill="#14120e"/><polygon points="50,50 5.57,38.09 7.50,32.40" fill="#f7f4ec"/><polygon points="50,50 10.16,27.00 13.51,22.00" fill="#14120e"/><polygon points="50,50 17.47,17.47 22.00,13.51" fill="#f7f4ec"/><polygon points="50,50 27.00,10.16 32.40,7.50" fill="#14120e"/><polygon points="50,50 38.09,5.57 44.00,4.39" fill="#f7f4ec"/><polygon points="50,50 50.00,4.00 56.00,4.39" fill="#14120e"/><polygon points="50,50 61.91,5.57 67.60,7.50" fill="#f7f4ec"/><polygon points="50,50 73.00,10.16 78.00,13.51" fill="#14120e"/><polygon points="50,50 82.53,17.47 86.49,22.00" fill="#f7f4ec"/><polygon points="50,50 89.84,27.00 92.50,32.40" fill="#14120e"/><polygon points="50,50 94.43,38.09 95.61,44.00" fill="#f7f4ec"/></svg><figcaption>Siemens star · top left</figcaption></figure><figure><svg viewBox="0 0 100 100" preserveAspectRatio="none" role="img" aria-label="grey wedge · top right"><rect x="0.00" y="0" width="9.29" height="100" fill="#000000"/><rect x="9.09" y="0" width="9.29" height="100" fill="#1a1a1a"/><rect x="18.18" y="0" width="9.29" height="100" fill="#333333"/><rect x="27.27" y="0" width="9.29" height="100" fill="#4c4c4c"/><rect x="36.36" y="0" width="9.29" height="100" fill="#666666"/><rect x="45.45" y="0" width="9.29" height="100" fill="#808080"/><rect x="54.55" y="0" width="9.29" height="100" fill="#999999"/><rect x="63.64" y="0" width="9.29" height="100" fill="#b2b2b2"/><rect x="72.73" y="0" width="9.29" height="100" fill="#cccccc"/><rect x="81.82" y="0" width="9.29" height="100" fill="#e6e6e6"/><rect x="90.91" y="0" width="9.29" height="100" fill="#ffffff"/></svg><figcaption>grey wedge · top right</figcaption></figure><figure><svg viewBox="0 0 100 100" preserveAspectRatio="none" role="img" aria-label="colour bars · bottom left"><rect x="0.00" y="0" width="12.70" height="100" fill="#c81e1e"/><rect x="12.50" y="0" width="12.70" height="100" fill="#e0a000"/><rect x="25.00" y="0" width="12.70" height="100" fill="#e8e000"/><rect x="37.50" y="0" width="12.70" height="100" fill="#1f9b3a"/><rect x="50.00" y="0" width="12.70" height="100" fill="#1f6fd0"/><rect x="62.50" y="0" width="12.70" height="100" fill="#7a3fbf"/><rect x="75.00" y="0" width="12.70" height="100" fill="#f7f4ec"/><rect x="87.50" y="0" width="12.70" height="100" fill="#101010"/></svg><figcaption>colour bars · bottom left</figcaption></figure><figure><svg viewBox="0 0 100 100" preserveAspectRatio="none" role="img" aria-label="chequer · bottom right"><rect x="0" y="0.00" width="10" height="16.87" fill="#14120e"/><rect x="10" y="0.00" width="10" height="16.87" fill="#f7f4ec"/><rect x="20" y="0.00" width="10" height="16.87" fill="#14120e"/><rect x="30" y="0.00" width="10" height="16.87" fill="#f7f4ec"/><rect x="40" y="0.00" width="10" height="16.87" fill="#14120e"/><rect x="50" y="0.00" width="10" height="16.87" fill="#f7f4ec"/><rect x="60" y="0.00" width="10" height="16.87" fill="#14120e"/><rect x="70" y="0.00" width="10" height="16.87" fill="#f7f4ec"/><rect x="80" y="0.00" width="10" height="16.87" fill="#14120e"/><rect x="90" y="0.00" width="10" height="16.87" fill="#f7f4ec"/><rect x="0" y="16.67" width="10" height="16.87" fill="#f7f4ec"/><rect x="10" y="16.67" width="10" height="16.87" fill="#14120e"/><rect x="20" y="16.67" width="10" height="16.87" fill="#f7f4ec"/><rect x="30" y="16.67" width="10" height="16.87" fill="#14120e"/><rect x="40" y="16.67" width="10" height="16.87" fill="#f7f4ec"/><rect x="50" y="16.67" width="10" height="16.87" fill="#14120e"/><rect x="60" y="16.67" width="10" height="16.87" fill="#f7f4ec"/><rect x="70" y="16.67" width="10" height="16.87" fill="#14120e"/><rect x="80" y="16.67" width="10" height="16.87" fill="#f7f4ec"/><rect x="90" y="16.67" width="10" height="16.87" fill="#14120e"/><rect x="0" y="33.33" width="10" height="16.87" fill="#14120e"/><rect x="10" y="33.33" width="10" height="16.87" fill="#f7f4ec"/><rect x="20" y="33.33" width="10" height="16.87" fill="#14120e"/><rect x="30" y="33.33" width="10" height="16.87" fill="#f7f4ec"/><rect x="40" y="33.33" width="10" height="16.87" fill="#14120e"/><rect x="50" y="33.33" width="10" height="16.87" fill="#f7f4ec"/><rect x="60" y="33.33" width="10" height="16.87" fill="#14120e"/><rect x="70" y="33.33" width="10" height="16.87" fill="#f7f4ec"/><rect x="80" y="33.33" width="10" height="16.87" fill="#14120e"/><rect x="90" y="33.33" width="10" height="16.87" fill="#f7f4ec"/><rect x="0" y="50.00" width="10" height="16.87" fill="#f7f4ec"/><rect x="10" y="50.00" width="10" height="16.87" fill="#14120e"/><rect x="20" y="50.00" width="10" height="16.87" fill="#f7f4ec"/><rect x="30" y="50.00" width="10" height="16.87" fill="#14120e"/><rect x="40" y="50.00" width="10" height="16.87" fill="#f7f4ec"/><rect x="50" y="50.00" width="10" height="16.87" fill="#14120e"/><rect x="60" y="50.00" width="10" height="16.87" fill="#f7f4ec"/><rect x="70" y="50.00" width="10" height="16.87" fill="#14120e"/><rect x="80" y="50.00" width="10" height="16.87" fill="#f7f4ec"/><rect x="90" y="50.00" width="10" height="16.87" fill="#14120e"/><rect x="0" y="66.67" width="10" height="16.87" fill="#14120e"/><rect x="10" y="66.67" width="10" height="16.87" fill="#f7f4ec"/><rect x="20" y="66.67" width="10" height="16.87" fill="#14120e"/><rect x="30" y="66.67" width="10" height="16.87" fill="#f7f4ec"/><rect x="40" y="66.67" width="10" height="16.87" fill="#14120e"/><rect x="50" y="66.67" width="10" height="16.87" fill="#f7f4ec"/><rect x="60" y="66.67" width="10" height="16.87" fill="#14120e"/><rect x="70" y="66.67" width="10" height="16.87" fill="#f7f4ec"/><rect x="80" y="66.67" width="10" height="16.87" fill="#14120e"/><rect x="90" y="66.67" width="10" height="16.87" fill="#f7f4ec"/><rect x="0" y="83.33" width="10" height="16.87" fill="#f7f4ec"/><rect x="10" y="83.33" width="10" height="16.87" fill="#14120e"/><rect x="20" y="83.33" width="10" height="16.87" fill="#f7f4ec"/><rect x="30" y="83.33" width="10" height="16.87" fill="#14120e"/><rect x="40" y="83.33" width="10" height="16.87" fill="#f7f4ec"/><rect x="50" y="83.33" width="10" height="16.87" fill="#14120e"/><rect x="60" y="83.33" width="10" height="16.87" fill="#f7f4ec"/><rect x="70" y="83.33" width="10" height="16.87" fill="#14120e"/><rect x="80" y="83.33" width="10" height="16.87" fill="#f7f4ec"/><rect x="90" y="83.33" width="10" height="16.87" fill="#14120e"/><line x1="0" y1="50" x2="100" y2="50" stroke="#c81e1e" stroke-width="1"/><line x1="50" y1="0" x2="50" y2="100" stroke="#c81e1e" stroke-width="1"/></svg><figcaption>chequer · bottom right</figcaption></figure></div>
  <div class="veil" id="veil-layer"></div>
</div>
<div class="controls">
  <label for="veil-alpha">veil</label>
  <input id="veil-alpha" type="range" min="0" max="100" step="1" value="80">
  <output id="veil-read" for="veil-alpha">80%</output>
</div>
<div class="note">One layer, one cloud colour (<code>#ddd0bb</code>). Top row is
where the cloud meets the top of the work; bottom row is the drift. The number
you settle on is the target the model should be solved to.</div>
<script>
(function () {
  var q = new URLSearchParams(location.search).get('veil');
  var slider = document.getElementById('veil-alpha');
  var layer = document.getElementById('veil-layer');
  var read = document.getElementById('veil-read');
  if (q !== null && !isNaN(parseFloat(q))) {
    var pct = Math.max(0, Math.min(100, parseFloat(q) * 100));
    slider.value = Math.round(pct);
  }
  function apply() {
    var v = slider.value / 100;
    layer.style.opacity = v;
    read.textContent = Math.round(v * 100) + '%';
  }
  slider.addEventListener('input', apply);
  apply();
})();
</script>
</div>

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
