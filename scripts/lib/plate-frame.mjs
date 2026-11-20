// The plate's frame: turn a point as the desk turns it, and map it into pixels with +y up.
//
// Kept apart from the exporter so a test can pin the two things that are easy to get wrong:
//   * the turn follows the screen (CSS rotate is clockwise), not the maths convention;
//   * the pixel map puts a larger y nearer the top of the image.

export function turn(points, degrees) {
  if (!degrees) return points;
  const a = (-degrees * Math.PI) / 180;       // screen clockwise
  const c = Math.cos(a), s = Math.sin(a);
  return points.map(([x, y]) => [x * c - y * s, x * s + y * c]);
}

/** width, height in pixels and the projection, from the data box and the long side */
export function frame(x0, x1, y0, y1, longSide) {
  const w = x1 - x0 || 1, h = y1 - y0 || 1;
  const long = Math.max(w, h);
  const margin = 0.012 * long;
  const boxW = w + 2 * margin, boxH = h + 2 * margin;
  const scale = longSide / Math.max(boxW, boxH);
  const pxW = Math.round(boxW * scale);
  const pxH = Math.round(boxH * scale);
  const ox = (pxW - w * scale) / 2 - x0 * scale;
  const oy = (pxH + h * scale) / 2 + y0 * scale;
  return { pxW, pxH, project: ([x, y]) => [ox + x * scale, oy - y * scale] };
}
