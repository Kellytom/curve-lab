// One figure for Fig. 9: axes, whole-number grid, a cubic Bézier chain per path, a
// legend inside the frame, and a title inside it too.
//
// Spec: state/SPEC-prime-mover-int.md, "The circle taken out (Fig. 9)".
//
// The stations are exact (evaluated in Fraction on the Python side); the line between
// them is a Catmull-Rom chain drawn as cubic Béziers, so the drawing is approximate and
// the caption says so. A polyline through the same points is a fault, not a shortcut.

const PAD = 34;

function niceStep(span) {
  for (const step of [0.5, 1, 2, 5, 10, 20, 50]) {
    if (span / step <= 10) return step;
  }
  return 100;
}

/** Catmull-Rom through the points, written as cubic Béziers. */
export function bezierChain(points, project) {
  if (points.length < 2) return "";
  const at = points.map(([x, y]) => project(x, y));
  let d = `M${at[0][0].toFixed(2)},${at[0][1].toFixed(2)}`;
  for (let i = 0; i < at.length - 1; i += 1) {
    const p0 = at[Math.max(0, i - 1)];
    const p1 = at[i];
    const p2 = at[i + 1];
    const p3 = at[Math.min(at.length - 1, i + 2)];
    const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
    const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
    d += ` C${c1[0].toFixed(2)},${c1[1].toFixed(2)} `
      + `${c2[0].toFixed(2)},${c2[1].toFixed(2)} `
      + `${p2[0].toFixed(2)},${p2[1].toFixed(2)}`;
  }
  return d;
}

export function figureSvg(panel, { width: boxWidth = 460 } = {}) {
  const [xmin, xmax, ymin, ymax] = panel.bounds;
  const margin = 0.06;
  const dataWidth = (xmax - xmin) * (1 + 2 * margin) || 1;
  const dataHeight = (ymax - ymin) * (1 + 2 * margin) || 1;

  // the canvas takes the data's own aspect, within limits that keep the title and the
  // legend readable: never flatter than 1:0.45, never taller than 1:1.4.
  const ratio = Math.max(0.45, Math.min(1.4, dataHeight / dataWidth));
  const size = boxWidth;
  const height = Math.round(size * ratio);

  // three bands: the title, the plot, the legend. Nothing overlaps because nothing
  // is allowed into another band.
  const titleBand = 28;
  const legendBand = 16 + panel.legend.length * 20;
  const plot = { left: PAD, right: size - PAD, top: titleBand, bottom: height - legendBand };

  const k = Math.min((plot.right - plot.left) / dataWidth, (plot.bottom - plot.top) / dataHeight);
  const cx = (xmin + xmax) / 2;
  const cy = (ymin + ymax) / 2;
  const project = (x, y) => [
    (plot.left + plot.right) / 2 + (x - cx) * k,
    (plot.top + plot.bottom) / 2 - (y - cy) * k,
  ];

  const clipId = `clip-${panel.key.replace(/[^a-z0-9-]/gi, "")}`;
  const parts = [];
  parts.push(`<rect x="0" y="0" width="${size}" height="${height}" fill="#fffef9"/>`);
  parts.push(`<clipPath id="${clipId}"><rect x="${plot.left}" y="${plot.top}" `
    + `width="${plot.right - plot.left}" height="${plot.bottom - plot.top}"/></clipPath>`);
  const drawn = [];

  // grid, clipped to the plot band
  const step = niceStep(Math.max(dataWidth, dataHeight));
  for (let value = Math.ceil(xmin / step) * step; value <= xmax; value += step) {
    const [px] = project(value, 0);
    const axis = Math.abs(value) < 1e-9;
    drawn.push(`<line x1="${px.toFixed(1)}" x2="${px.toFixed(1)}" y1="${plot.top}" y2="${plot.bottom}" `
      + `stroke="${axis ? "#b9a98a" : "#f0e8d8"}" stroke-width="${axis ? 1.2 : 1}"/>`);
    if (!axis) {
      drawn.push(`<text x="${px.toFixed(1)}" y="${(plot.bottom + 14).toFixed(1)}" `
        + `font-family="ui-monospace, Menlo, monospace" font-size="11" fill="#9c8a6a" `
        + `text-anchor="middle">${+value.toFixed(2)}</text>`);
    }
  }
  for (let value = Math.ceil(ymin / step) * step; value <= ymax; value += step) {
    const [, py] = project(0, value);
    const axis = Math.abs(value) < 1e-9;
    drawn.push(`<line x1="${plot.left}" x2="${plot.right}" y1="${py.toFixed(1)}" y2="${py.toFixed(1)}" `
      + `stroke="${axis ? "#b9a98a" : "#f0e8d8"}" stroke-width="${axis ? 1.2 : 1}"/>`);
    if (!axis) {
      drawn.push(`<text x="${(plot.left - 6).toFixed(1)}" y="${(py + 4).toFixed(1)}" `
        + `font-family="ui-monospace, Menlo, monospace" font-size="11" fill="#9c8a6a" `
        + `text-anchor="end">${+value.toFixed(2)}</text>`);
    }
  }

  // the curves: a cubic Bézier chain each
  for (const path of panel.paths) {
    const d = bezierChain(path.points, project);
    drawn.push(`<path d="${d}" fill="none" stroke="${path.colour}" stroke-width="1.8" `
      + `stroke-linecap="round" data-path="${path.name}"/>`);
  }

  // the exact stations of the walk
  for (const [x, y] of panel.stations || []) {
    const [px, py] = project(x, y);
    drawn.push(`<circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="3.2" fill="#c9761f" `
      + `stroke="#fffef9" stroke-width="1"/>`);
  }
  // named points, inside the frame: a wonky's cut points, for example
  for (const label of panel.labels || []) {
    const [px, py] = project(label.x, label.y);
    // keep the label inside the frame: flip the offset at the right edge and the top
    const dx = px > plot.right - 72 ? -72 : (label.dx ?? 6);
    const dy = py < plot.top + 16 ? 14 : (label.dy ?? -6);
    const tone = label.colour || "#c9761f";        // orange: the cut on y = x
    drawn.push(`<circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="3.6" fill="${tone}" `
      + `stroke="#fffef9" stroke-width="0.8"/>`
      + `<text x="${(px + dx).toFixed(1)}" y="${(py + dy).toFixed(1)}" `
      + `font-family="ui-monospace, Menlo, monospace" font-size="11" fill="${tone}">${label.text}</text>`);
  }
  parts.push(`<g clip-path="url(#${clipId})">${drawn.join("")}</g>`);

  // axis names, inside the plot band
  const [ax] = project(xmax, 0);
  parts.push(`<text x="${Math.min(plot.right - 8, ax).toFixed(1)}" y="${(plot.bottom - 6).toFixed(1)}" `
    + `font-family="Georgia, serif" font-size="14" font-style="italic" fill="#3b2d1c">x</text>`);
  const [, by] = project(0, ymax);
  parts.push(`<text x="${(plot.left + 4).toFixed(1)}" y="${Math.max(plot.top + 14, by - 4).toFixed(1)}" `
    + `font-family="Georgia, serif" font-size="14" font-style="italic" fill="#3b2d1c">y</text>`);

  // the title, in its own band
  parts.push(`<text x="${PAD - 12}" y="19" font-family="Georgia, serif" font-size="14" `
    + `fill="#3b2d1c">${escapeText(panel.title)}</text>`);

  // the legend, in its own band, at 15 px
  let legendY = height - legendBand + 20;
  for (const entry of panel.legend) {
    parts.push(`<line x1="${PAD}" x2="${PAD + 22}" y1="${legendY - 5}" y2="${legendY - 5}" `
      + `stroke="${entry.colour}" stroke-width="3"/>`);
    parts.push(`<text x="${PAD + 30}" y="${legendY}" font-family="Georgia, serif" `
      + `font-size="15" fill="#3b2d1c">${escapeText(entry.label)}</text>`);
    legendY += 20;
  }

  return `<svg viewBox="0 0 ${size} ${height}" width="100%" style="height:auto" role="img" `
    + `aria-label="${escapeText(panel.title)}" data-panel="${panel.key}">`
    + `${parts.join("")}</svg>`;
}

function escapeText(text) {
  return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
