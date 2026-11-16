"""The knot experiments that did not work, parked on their own page.

    .venv/bin/python scripts/ph_nth_exp_notes.py
    open workbench/ph-nth-exp-notes.html

These three controls lived on the experimental sandbox and were taken off it: each
one tries to shorten the legs of a curve by working on the parameter `t`, and on
this family of curves that cannot work. The measurements are on the page so the
attempt is not repeated without them.

The page is generated: edit this file, never the HTML.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "ph-nth-exp-notes.html"

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Knot experiments that did not work</title>
<style>
:root{--paper:#fbf7ec;--ink:#2e2413;--muted:#7b6c4e;--rule:#d8ccae}
*{box-sizing:border-box}
body{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}
main{max-width:1000px;margin:0 auto;padding:34px 22px 70px}
.eyebrow{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
h1{font-size:28px;line-height:1.15;margin:0 0 8px}
h2{font-size:19px;margin:0 0 8px}
.panel{background:var(--paper);border:1px solid var(--rule);padding:18px 20px;margin:0 0 22px}
p{margin:0 0 12px}
code{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}
.small{font-size:13px;color:var(--muted)}
table{border-collapse:collapse;width:100%;font:13px/1.4 ui-monospace,Menlo,monospace}
th,td{border-bottom:1px solid var(--rule);padding:5px 8px;text-align:left;vertical-align:top}
th{font-weight:600;color:var(--muted)}
button{font:12px/1.2 ui-monospace,Menlo,monospace;padding:5px 9px;background:#efe7d3;color:var(--muted);
  border:1px solid var(--rule);border-radius:3px;cursor:not-allowed;opacity:.6}
</style></head><body><main>
<p class="eyebrow">curve-lab &middot; parked</p>
<h1>Knot experiments that did not work</h1>
<p class="small">Three controls were built on
<a href="ph-nth-sandbox-exp.html">the experimental sandbox</a> to shorten the legs of a curve.
They were taken off it because they cannot work on this family, and the reason is a
measurement, not an opinion. The buttons below are shown, disabled, so the shape of the
attempt is not lost.</p>

<section class="panel">
<h2>Why they cannot work</h2>
<p>The legs are not a separable stretch of the parameter. A curve's <strong>self-crossings</strong>
— the knot — run from about <code>t = 0.02</code> to <code>t = 0.98</code>. Any window that removes
a leg from `t` therefore also removes crossings, which changes the knot rather than tidying it.</p>
<p>The rebuild has a second limit: it is exact only over a span whose length is the square of a
fraction, and the largest such span below the whole curve is <code>(15/16)&sup2; = 0.879</code> —
shorter than the 0.96 the knot occupies. So the only exact span that holds the knot is the whole
curve, and the rebuild says so instead of cutting.</p>
<p>A third limit is the exponent step: at step 1/2 a row is a polynomial in <code>&radic;t</code>,
so substituting <code>t = a + span&middot;u</code> does not give a polynomial at all. The rebuild is
undefined there and now asks for step 1.</p>
</section>

<section class="panel">
<h2>The three controls, as they were</h2>
<p><button type="button" disabled>show only the knot</button>
<button type="button" disabled>rebuild without the legs</button>
<button type="button" disabled>cut and rebuild</button></p>
<table>
<tr><th>control</th><th>what it did</th><th>measured result</th></tr>
<tr><td><code>show only the knot</code></td><td>set the `t` window to the outermost self-crossings</td>
<td>cut t 1/48 &hellip; 47/48 — two per cent off each end, i.e. nothing, because the crossings span the curve</td></tr>
<tr><td><code>rebuild without the legs</code></td><td>rebuild the crossing span as a new exact curve</td>
<td>&ldquo;the span needed is the whole curve, so nothing was cut&rdquo;</td></tr>
<tr><td><code>cut and rebuild</code></td><td>cut a fraction of arc length off each end, then rebuild</td>
<td>the same: the needed span has no exact square length below the whole curve</td></tr>
</table>
<p class="small">The exact rebuild itself is sound and was checked against a Python reference to the
integer: the browser produced <code>[8017920, &minus;50761728, 40310784]</code> for the same span. It is
the ilegibility of these curves for a short span, not the arithmetic, that parked them.</p>
</section>

<section class="panel">
<h2>What replaces them</h2>
<p><strong>Shorter legs come from the numbers, not from a cut.</strong> Measured on one curve, moving
the two outer flat spots inward takes the legs from 88% of the figure to 42% and then 12%, and the
knot from 12% to 57% to 87%.</p>
<p><strong>At the Bezier step the question dissolves.</strong> A leg is nearly straight, so one
cubic span covers it to any sane tolerance, while the knot needs several. Spending spans where the
curvature is gives short legs and a faithful knot without cutting the curve at all — which is the
plan recorded in <code>TODO.md</code>.</p>
</section>

<section class="panel">
<h2>Failed: the census families on the sandbox</h2>
<p>The census (<code>workbench/family-census.json</code>) measured 7,068 symmetric
flat-spot curves and found better knots than the sections above carry: nine crossings at
grid 1/42, six at grid 1/36. Twelve of them were wired into a section on the sandbox,
"Best of the census: every copy count". <strong>The section is withdrawn.</strong></p>
<p>The reason is arithmetic, not the census. A curve with three outer pairs and five
copies at 1/2 has eleven flat spots, so its row runs to <code>t^11</code> and the
coefficients reach 10<sup>13</sup> to 10<sup>23</sup>. The page draws in double precision:
the knot is 10<sup>-13</sup> of the row's size, so the whole picture collapses to a single
point. Measured on the page: frame span 2&times;10<sup>-6</sup>, all 701 path points at the
same coordinate.</p>
<p>Two things are true at once: the census numbers are exact (whole-number arithmetic, no
sampling), and the page cannot show those particular curves. The six cheaper knots in the
census &mdash; <code>1/8 + 1/11</code> at 9 crossings, grid 1/42 &mdash; draw correctly and
are the ones worth promoting; the eleven-spot families need either a scaled row or an
exact renderer before they belong on a page.</p>
</section>

<section class="panel">
<h2>The point count is not part of the formula</h2>
<p>The view panel shows a line like <code>visible part: 12,001 points over t 0.021 to 0.979
(4&times;)</code>. That number is about the <strong>drawing</strong>, not about the curve. It says how
many sample points the polyline was built from at the current magnification; the curve itself is the
row of numbers above the figure, and nothing in the row is changed by pressing
<strong>recalculate at this zoom</strong>.</p>
<p>Why it exists: a picture is a polyline of straight segments, and at 10&times; or 12&times; the
corners of a 700-point polyline are visible. The button multiplies the detail by four and samples only
the window on screen, so a zoomed view looks like a line. Press it again for four times more. Panning
and zooming do not resample, so dragging stays cheap.</p>
<p>Why it must not be used later: the cubic spans for the lead are fitted to the <em>numbers</em>, from
the speed row and the tolerance the G3 gate asks for. A point count from the screen is a rendering
choice, has no tolerance attached, and changes whenever the operator zooms. Treat it as a label on the
glass, not a measurement of the curve. The measurements that do travel are
<code>bend</code> (arc over chord), <code>grid</code> (the pitch the row needs), the crossing count and
the loop window &mdash; and those are what a saved record carries.</p>
</section>

<p><a href="ph-nth-sandbox-exp.html">&larr; back to the experimental sandbox</a></p>
</main></body></html>
"""


def build() -> None:
    OUT.write_text(PAGE)
    print(OUT.relative_to(ROOT), len(PAGE), "bytes")


if __name__ == "__main__":
    build()
