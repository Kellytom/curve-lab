// The dots on a piece or a double: orange for a solved cut on y = x, blue for an end of the
// drawn curve that is NOT on the line, brown where the two fall in the same place.
//
// The point of the colour is the check: a brown dot says "the curve reaches the axis here";
// an orange dot with a blue one beside it says "it does not".

const NEAR = 1e-3;

export function labelsFor(row) {
  const points = row.points || [];
  const cuts = row.cuts || [];
  const ends = points.length ? [points[0], points[points.length - 1]] : [];
  const near = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]) < NEAR;

  const labels = [];
  for (const cut of cuts) {
    const onCurve = ends.some((end) => near([cut.x, cut.y], end));
    labels.push({
      x: cut.x, y: cut.y,
      colour: onCurve ? "#5a3210" : "#c9761f",      // brown where the end sits on the cut
      text: onCurve ? `(${cut.x.toFixed(2)}, ${cut.y.toFixed(2)})`
        : `cut (${cut.x.toFixed(2)}, ${cut.y.toFixed(2)})`,
    });
  }
  for (const end of ends) {
    if (cuts.some((cut) => near([cut.x, cut.y], end))) continue;
    const offset = end[1] - end[0];
    labels.push({
      x: end[0], y: end[1], colour: "#2f6fa8",
      text: `end (${end[0].toFixed(2)}, ${end[1].toFixed(2)}) off ${offset.toFixed(2)}`,
    });
  }
  return labels;
}
