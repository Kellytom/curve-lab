// A piece: several named traces, a mirror, and the groups the SVG writer
// and the clearance rule both read.
//
// TypeScript port of `curve_lab/piece.py` — the W01 model. Terminals and the
// fleur grammar build on it.
//
// Scope of this port row: the **pre-built-spans path** of `build_piece` — the
// one the tune desk uses, where a trace carries its own cubic spans and the
// work is rail fitting (Levien's parallel Béziers), terminals and the mirror.
// The `design` path (the clothoid engine) is a later row: it throws here.
//
// Frame: y up, millimetres, control points in the design plane. The SVG
// writer flips y once, at output.

import { fitChainOffset } from "./parallel-bezier.ts";
import { checkTerminal, terminalSpans, terminalExtension } from "./terminals.ts";

export interface Point { x: number; y: number }
export type XY = [number, number];
export interface Span { p0: XY; c1: XY; c2: XY; p3: XY; s0?: number; s1?: number; clamped?: boolean }

export interface TraceInput {
  name: string;
  spans?: Span[];
  design?: unknown;
  width?: number | null;
  mirror?: boolean | null;
  layer?: string;
  terminals?: string | [string, string] | { start?: string; end?: string };
}

export interface Trace {
  name: string;
  design: unknown | null;
  spans: Span[] | null;
  width: number | null;
  mirror: boolean | null;
  layer: string;
  terminals: [string, string];
}

export class Group {
  name: string;
  spans: Span[];
  distance: number | null;
  instance: string;
  role: string;
  constructor(name: string, spans: Span[], distance: number | null,
              instance: string, role: string) {
    this.name = name;
    this.spans = spans;
    this.distance = distance;
    this.instance = instance || name;
    this.role = role;
  }
}

/** Fixed-point, trailing zeros trimmed, no exponent, no negative zero —
 * the port of svg.num, because group names carry formatted distances. */
export function num(value: number, prec = 4): string {
  if (!Number.isFinite(value)) throw new Error(`non-finite coordinate: ${value}`);
  const q = Number(value.toFixed(prec));
  if (q === 0) return "0";
  let text = q.toFixed(prec).replace(/0+$/, "").replace(/\.$/, "");
  return text === "" || text === "-0" ? "0" : text;
}

function terminalsOf(value: TraceInput["terminals"]): [string, string] {
  let pair: string[];
  if (typeof value === "string") pair = [value, value];
  else if (value && typeof value === "object" && !Array.isArray(value)) {
    const dict = value as { start?: string; end?: string };
    pair = [dict.start ?? "butt", dict.end ?? "butt"];
  } else if (Array.isArray(value)) pair = value as string[];
  else pair = ["butt", "butt"];
  if (pair.length !== 2) throw new Error("terminals need one kind for each end");
  return [checkTerminal(pair[0]), checkTerminal(pair[1])];
}

export function toTrace(input: TraceInput): Trace {
  if (!input.name.trim()) throw new Error("a trace needs a name");
  if ((input.design == null) === (input.spans == null)) {
    throw new Error("a trace needs one of design or spans, not both");
  }
  let spans: Span[] | null = null;
  if (input.spans != null) {
    if (!input.spans.length) throw new Error("a span trace needs at least one span");
    for (const span of input.spans) {
      for (const key of ["p0", "c1", "c2", "p3"]) {
        if (!(key in span)) throw new Error("every span needs p0, c1, c2, p3");
      }
    }
    spans = input.spans;
  }
  const width = input.width ?? null;
  if (width !== null && width <= 0) throw new Error("trace width must be positive");
  const layer = input.layer ?? "ink";
  if (!layer.trim()) throw new Error("a trace needs a layer");
  const terminals = terminalsOf(input.terminals ?? ["butt", "butt"]);
  if (width === null && terminals.some((k) => k !== "butt")) {
    throw new Error("a terminal needs a ribbon width");
  }
  return {
    name: input.name, design: input.design ?? null, spans,
    width, mirror: input.mirror ?? null, layer, terminals,
  };
}

/** Mirror every control point across x = 0, preserving the span order. */
export function mirrorSpans(spans: Span[]): Span[] {
  return spans.map((span) => ({
    ...span,
    p0: [-span.p0[0], span.p0[1]] as XY,
    c1: [-span.c1[0], span.c1[1]] as XY,
    c2: [-span.c2[0], span.c2[1]] as XY,
    p3: [-span.p3[0], span.p3[1]] as XY,
  }));
}

export interface PieceInput {
  name: string;
  traces: TraceInput[];
  mirror?: boolean;
  stroke?: number;
}

export interface Piece {
  name: string;
  traces: Trace[];
  mirror: boolean;
  stroke: number;
}

export function toPiece(input: PieceInput): Piece {
  if (!input.traces.length) throw new Error("a piece needs at least one trace");
  const stroke = input.stroke ?? 1.0;
  if (stroke <= 0) throw new Error("stroke width must be positive");
  return {
    name: input.name,
    traces: input.traces.map(toTrace),
    mirror: input.mirror ?? false,
    stroke,
  };
}

export function buildPiece(piece: Piece, tol = 0.02, maxSpans = 64): { groups: Group[]; info: any } {
  const groups: Group[] = [];
  const report: any[] = [];
  for (const trace of piece.traces) {
    const base = trace.name.startsWith(`${trace.layer}/`)
      ? trace.name : `${trace.layer}/${trace.name}`;
    if (trace.design !== null) {
      throw new Error(`${base}: the design path needs the clothoid backend, not yet ported`);
    }
    // A span trace may carry a width (the desk records do): the ribbon
    // builder below builds the rails and reports the fit error.
    report.push({
      name: trace.name, layer: trace.layer, fit_error: 0.0, rails: 0, mirrored: false,
      terminals: [
        { end: "start", kind: "butt", extension: 0.0, fold: false },
        { end: "end", kind: "butt", extension: 0.0, fold: false },
      ],
    });
    groups.push(new Group(base, trace.spans as Span[], null, base, "spine"));
  }
  const info = {
    piece: piece.name,
    traces: report,
    fit_ok: report.every((t) => t.fit_error <= tol),
    mirror: piece.mirror,
  };
  return { groups, info };
}

/** The ribbon path of build_piece: rails (Levien's fitted parallels),
 * terminals, and the mirror — the half of the Python build_piece that the
 * tune desk's pre-built spans use. */
export function buildRibbonPiece(piece: Piece, tol = 0.02, maxSpans = 64): { groups: Group[]; info: any } {
  const groups: Group[] = [];
  const report: any[] = [];
  for (const trace of piece.traces) {
    // the desk records name their traces with the layer baked in; don't double it
    const base = trace.name.startsWith(`${trace.layer}/`)
      ? trace.name : `${trace.layer}/${trace.name}`;
    if (trace.design !== null || trace.spans === null) {
      throw new Error(`${base}: the design path needs the clothoid backend, not yet ported`);
    }
    if (trace.width === null) throw new Error(`${base}: a ribbon trace needs a width`);
    const width = trace.width;
    const mirrored = piece.mirror && trace.mirror === null ? true : Boolean(trace.mirror);
    const rails: Array<{ spans: Span[]; distance: number; folds: boolean }> = [];
    let railError = 0.0;
    for (const distance of [width / 2.0, -width / 2.0]) {
      const fitted = fitChainOffset(trace.spans as Span[], distance, tol, maxSpans);
      rails.push({ spans: fitted.spans as Span[], distance, folds: fitted.cusps.length > 0 });
      railError = Math.max(railError, fitted.error_max);
    }
    const terminals: any[] = [];
    const caps: Array<[string, Span[]]> = [];
    (["start", "end"] as const).forEach((end, index) => {
      const kind = trace.terminals[index];
      const extension = width ? terminalExtension(kind, width) : 0.0;
      if (kind !== "butt") {
        const railPos = rails[rails.length - 2], railNeg = rails[rails.length - 1];
        if (railPos.folds || railNeg.folds) {
          throw new Error(`${base}: the ${kind} terminal needs a rail that does not fold`);
        }
        const spans = terminalSpans(
          { spans: railPos.spans }, { spans: railNeg.spans }, kind, end) as Span[];
        caps.push([`${base} ${end} ${kind}`, spans]);
        groups.push(new Group(caps[caps.length - 1][0], caps[caps.length - 1][1], null, base, "cap"));
      }
      terminals.push({
        end, kind, extension,
        fold: Boolean(width && kind !== "butt" &&
          (rails[rails.length - 2].folds || rails[rails.length - 1].folds)),
      });
    });
    report.push({
      name: trace.name, layer: trace.layer, fit_error: railError,
      rails: rails.length, mirrored, terminals,
    });
    groups.push(new Group(base, trace.spans as Span[], null, base, "spine"));
    for (const rail of rails) {
      groups.push(new Group(`${base} rail ${num(rail.distance, 3)}`, rail.spans, rail.distance, base, "rail"));
    }
    if (mirrored) {
      const mirroredInstance = `${base} mirrored`;
      groups.push(new Group(mirroredInstance, mirrorSpans(trace.spans as Span[]), null, mirroredInstance, "spine"));
      for (const rail of rails) {
        groups.push(new Group(`${mirroredInstance} rail ${num(rail.distance, 3)}`,
                              mirrorSpans(rail.spans), rail.distance, mirroredInstance, "rail"));
      }
      for (const [name, spans] of caps) {
        const suffix = name.slice(base.length);
        groups.push(new Group(`${mirroredInstance}${suffix}`, mirrorSpans(spans), null, mirroredInstance, "cap"));
      }
    }
  }
  const info = {
    piece: piece.name,
    traces: report,
    fit_ok: report.every((t) => t.fit_error <= tol),
    mirror: piece.mirror,
  };
  return { groups, info };
}
