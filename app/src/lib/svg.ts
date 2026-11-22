// The SVG text layer in TypeScript — the port of curve_lab/svg.py's core.
//
// Scope, stated plainly: this is the TEXT layer, not the layout builder.
// `document()` (title, legend, sheet sizing, y-flip placement) stays in
// curve_lab/svg.py for now — the site draws in the browser and does not yet
// emit design documents; porting the layout before it is needed would be
// speculative code. What is ported is what the round-trip work and any future
// exporter touch: the number formatter, the path writer and its reader, the
// cubic evaluation, the grid step and lines, the bounding box, the slug, the
// escaper and the design-metadata recovery.
//
// The Python is the reference; the laws are in app/tests/svg.test.mjs.

export type Point = [number, number];

/** A cubic span: four points, y-up in design units (the writer flips only
 * inside document(), which is not ported here). */
export type Span = { p0: Point; c1: Point; c2: Point; p3: Point };

/** A cubic Bézier span at parameter t, in design units. */
export function spanEval(span: Span, t: number): Point {
  const mt = 1 - t;
  return [
    mt ** 3 * span.p0[0] + 3 * mt * mt * t * span.c1[0] + 3 * mt * t * t * span.c2[0] + t ** 3 * span.p3[0],
    mt ** 3 * span.p0[1] + 3 * mt * mt * t * span.c1[1] + 3 * mt * t * t * span.c2[1] + t ** 3 * span.p3[1],
  ];
}

/** A round grid step (1, 2, 2.5, 5 × 10^k) giving about `target` lines. */
export function gridStep(span: number, target = 10): number {
  if (!(span > 0)) return 1;
  const raw = span / target;
  const p = 10 ** Math.floor(Math.log10(raw));
  for (const k of [1, 2, 2.5, 5, 10]) {
    if (raw <= k * p) return k * p;
  }
  return 10 * p;
}

/** Vertical and horizontal rules at every multiple of `step`, placed through
 * the caller's y-flip. */
export function gridLines(
  place: (x: number, y: number) => Point,
  x0: number, x1: number, y0: number, y1: number, step: number,
  colour = "#ece4cf", width = 0.25,
): string[] {
  const out: string[] = [];
  for (let gx = Math.floor(x0 / step) * step; gx <= x1 + 1e-9; gx += step) {
    const [ax, ay] = place(gx, y0);
    const [bx, by] = place(gx, y1);
    out.push(`<line x1="${ax.toFixed(3)}" y1="${ay.toFixed(3)}" x2="${bx.toFixed(3)}" ` +
             `y2="${by.toFixed(3)}" stroke="${colour}" stroke-width="${width}"/>`);
  }
  for (let gy = Math.floor(y0 / step) * step; gy <= y1 + 1e-9; gy += step) {
    const [ax, ay] = place(x0, gy);
    const [bx, by] = place(x1, gy);
    out.push(`<line x1="${ax.toFixed(3)}" y1="${ay.toFixed(3)}" x2="${bx.toFixed(3)}" ` +
             `y2="${by.toFixed(3)}" stroke="${colour}" stroke-width="${width}"/>`);
  }
  return out;
}

/** Fixed-point, trailing zeros trimmed, no exponent, no negative zero. */
export function svgNum(value: number, prec = 4): string {
  if (!Number.isFinite(value)) {
    throw new Error(`non-finite coordinate: ${value}`);
  }
  const q = Number(value.toFixed(prec));
  if (q === 0) return "0";
  const text = q.toFixed(prec).replace(/0+$/, "").replace(/\.$/, "");
  return text === "" || text === "-0" ? "0" : text;
}

/** Absolute `M` then `C` for every span, as one path string. */
export function pathD(spans: Span[], prec = 4, close = false): string {
  if (!spans.length) {
    throw new Error("no spans to write");
  }
  const parts = [`M ${svgNum(spans[0].p0[0], prec)},${svgNum(spans[0].p0[1], prec)}`];
  for (const span of spans) {
    parts.push(
      "C " +
        `${svgNum(span.c1[0], prec)} ${svgNum(span.c1[1], prec)}, ` +
        `${svgNum(span.c2[0], prec)} ${svgNum(span.c2[1], prec)}, ` +
        `${svgNum(span.p3[0], prec)} ${svgNum(span.p3[1], prec)}`,
    );
  }
  if (close) parts.push("Z");
  return parts.join(" ");
}

/** A small reader for our own path data, for the round-trip tests. Not a
 * general SVG parser: `M`, `C`, `L`, `Z` with absolute coordinates, which is
 * what this writer emits. */
export function parseD(d: string): Array<{ command: string; values: number[] }> {
  const tokens = d.replace(/,/g, " ").split(/\s+/).filter(Boolean);
  const out: Array<{ command: string; values: number[] }> = [];
  let i = 0;
  const counts: Record<string, number> = { M: 2, L: 2, C: 6 };
  while (i < tokens.length) {
    const command = tokens[i];
    if (command in counts) {
      const n = counts[command];
      const values = tokens.slice(i + 1, i + 1 + n).map(Number);
      out.push({ command, values });
      i += 1 + n;
    } else if (command === "Z") {
      out.push({ command: "Z", values: [] });
      i += 1;
    } else {
      throw new Error(`unsupported path token: ${command}`);
    }
  }
  return out;
}

/** The bounding box of the spans' control points — the writer's own rule:
 * control points count, so the box is the algebra's, not the ink's. */
export function bbox(spans: Span[]): [number, number, number, number] {
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const span of spans) {
    for (const [px, py] of [span.p0, span.c1, span.c2, span.p3]) {
      x0 = Math.min(x0, px); x1 = Math.max(x1, px);
      y0 = Math.min(y0, py); y1 = Math.max(y1, py);
    }
  }
  return [x0, y0, x1, y1];
}

/** A filename-safe slug: alphanumerics stay, everything else becomes a dash. */
export function slug(name: string): string {
  return [...name]
    .map((ch) => (/[a-zA-Z0-9]/.test(ch) ? ch : "-"))
    .join("")
    .replace(/^-+|-+$/g, "");
}

/** The XML text escape the Python writer uses. */
export function escapeXml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/** Recover the design JSON from a file svg.py wrote (`<desc id=...>`). */
export function metadataDesign(svgText: string): Record<string, unknown> {
  const marker = '<desc id="curve-lab-design">';
  const start = svgText.indexOf(marker);
  const end = start < 0 ? -1 : svgText.indexOf("</desc>", start);
  if (start < 0 || end < 0) {
    throw new Error("no design metadata in this file");
  }
  const raw = svgText
    .slice(start + marker.length, end)
    .replace(/&quot;/g, '"')
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&");
  return JSON.parse(raw);
}
