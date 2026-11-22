// The per-construction partner of a stored path.
//
// docs/SIDE-CURVES.md §1 and §5: a side curve is the same construction with one
// parameter shifted, never a parallel offset. For the stored families the parameter is a
// scale about the construction centre (the origin): the double's wonk-half radius, the
// hybrid's middle weight, the mobile's arm radius. Scaling the stored path about the
// origin is that shift, and a scaled copy of a curve cannot cross itself.

export function partnersOf(path, d) {
  const s = Math.abs(Number(d)) || 0;
  const scaled = (factor) => path.map(([x, y]) => [x * factor, y * factor]);
  // right is the smaller construction (parameter − d), left the larger (+ d)
  return { right: scaled(1 - s), left: scaled(1 + s) };
}
