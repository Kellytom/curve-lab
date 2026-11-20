# Maximum curvature of power-law curves

> **draft A** — a working draft, not a final text.
A quick reference for where the bending is tightest on curves of the form
\(y = x^n\), and on the related septic hyperbola and superellipse.

**Every number below is computed by `scripts/curvature_power.py`** — the location *and* the curvature there. Run it to
reproduce the table, the septic points and the scan; `--check` fails if the two
numbers this page once got wrong (the \(n = 4\) row, the superellipse maximum)
drift back.

## The simple parabola

For \(y = x^2\) the curvature is

\[
\kappa(x) = \frac{2}{\left(1 + 4x^2\right)^{3/2}}.
\]

The denominator is smallest at \(x = 0\), so the maximum curvature is at the
vertex:

\[
(0, 0), \qquad \kappa_{\max} = 2.
\]

Scaling the coefficient only changes the amount of curvature, not the location.
For \(y = a x^2\) the maximum is still at the vertex, with \(\kappa_{\max} = 2|a|\).

## Higher power curves \(y = x^n\)

For \(n \ge 3\) the curvature at the origin is zero, because the first
\(n - 1\) derivatives vanish there. The maximum curvature moves away from the
origin.

The curvature of \(y = x^n\) is

\[
\kappa(x) = \frac{|n(n-1) x^{n-2}|}{\left(1 + n^2 x^{2n-2}\right)^{3/2}}.
\]

Setting \(\kappa'(x) = 0\) gives the location of maximum curvature:

\[
x_{\max} = \left(\frac{n - 2}{n^2(2n - 1)}\right)^{\frac{1}{2n - 2}},
\qquad
y_{\max} = x_{\max}^{\,n}.
\]

### Numerical values

| \(n\) | \(x_{\max}\) | \(y_{\max}\) | \(\kappa_{\max}\) | Point |
|------:|------------:|------------:|-------------:|------|
| 2 | 0.000 | 0.000 | 2.000 | $(0.000, 0.000)$ |
| 3 | 0.386 | 0.058 | 1.762 | $(0.386, 0.058)$ |
| 4 | 0.511 | 0.068 | 2.151 | $(0.511, 0.068)$ |
| 5 | 0.583 | 0.067 | 2.573 | $(0.583, 0.067)$ |
| 6 | 0.631 | 0.063 | 2.998 | $(0.631, 0.063)$ |
| 7 | 0.668 | 0.059 | 3.421 | $(0.668, 0.059)$ |
| 10 | 0.738 | 0.048 | 4.672 | $(0.738, 0.048)$ |
| 20 | 0.837 | 0.028 | 8.729 | $(0.837, 0.028)$ |
| 100 | 0.952 | 0.007 | 40.061 | $(0.952, 0.007)$ |

The \(y\)-coordinate stays small because \(x^n\) is still tiny at the
maximum-curvature \(x\). The point is close to the \(x\)-axis.

### Large-\(n\) behaviour

As \(n \to \infty\), the point slides toward \((1, 0)\). A useful approximation
for large \(n\) is

\[
x_{\max} \approx 1 - \frac{\ln n}{n}.
\]

Measured: at \(n = 20\) it gives 0.850 against the exact 0.837 (1.6% high);
at \(n = 100\), 0.954 against 0.951 (0.3% high). So it is a guide from about
\(n = 100\), and poor below \(n = 20\). Use the exact formula for anything
you will draw.

## Why \(n = 2\) is special

For \(y = x^2\) the second derivative is constant and nonzero at the origin.
For every \(n > 2\) the second derivative at the origin is zero, so the curve is
flat there and the maximum curvature is pushed outward. That makes the jump
from \(n = 2\) to \(n = 3\) look abrupt, but from \(n = 3\) onward the slide is
smooth and monotone.

## Septic hyperbola

For

\[
x^7 - y^7 = r^7,
\]

the maximum curvature also occurs away from the axis crossing. The curve scales
with \(r\), so if \((x_0, y_0)\) is the maximum-curvature point for \(r = 1\),
then for general \(r\) it is

\[
(r x_0, \; r y_0).
\]

For \(r = 1\) the maximum-curvature point is approximately

\[
(1.05, \; 0.88).
\]

So for \(r = 5\) the point is approximately

\[
(5.25, \; 4.38).
\]

This point lies between the axis crossing \((r, 0)\) and the asymptote
\(y = x\). It has no simple closed form; it is found by numerically maximizing
curvature along the branch.

## Septic superellipse

For

\[
|x|^7 + |y|^7 = r^7,
\]

the maximum curvature is at the **diagonal** points, not the axis crossings:

\[
\left(\pm \frac{r}{2^{1/7}}, \; \pm \frac{r}{2^{1/7}}\right).
\]

Scanned: the maximum sits at 45.0° with \(\kappa = 4.684\) for \(r = 1\),
at \((0.906, 0.906)\). The axis crossings \((\pm r, 0)\) and
\((0, \pm r)\) are the **flattest** points — curvature there is zero, which is
why the shape reads as a square with rounded sides. The earlier version of this
page had the two the wrong way round.
