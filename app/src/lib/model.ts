// The design model in TypeScript: a chain of clothoid segments, anchored.
//
// The port of `curve_lab/model.py` (the conversion track, state/SCToDo-int.md).
// Same semantics, same refusals, same JSON shape — a design written by the
// Python side loads here and vice versa. Lengths are in design units;
// curvature is 1/design-unit; a segment is a clothoid: kappa(s) = kappa0 +
// kd·s over its length. `kappa0: null` continues from the previous segment's
// end curvature, which is what makes a chain G2 at that join.
//
// Naming: camelCase in code; the JSON keys stay snake-free as the Python
// writes them (`kd`, `length`, `kappa0`, `corner`), because the file is the
// contract.

export type Anchor = { x: number; y: number; angle: number };

export type SegmentDict = {
  kd: number;
  length: number;
  kappa0: number | null;
  corner?: number;
};

export type DesignDict = {
  name: string;
  anchor: Anchor;
  segments: SegmentDict[];
  offsets: number[];
  stroke: number;
  g1?: boolean;
};

const finite = (value: number): boolean => Number.isFinite(value);

export class Segment {
  readonly kd: number;
  readonly length: number;
  readonly kappa0: number | null;
  readonly corner: number;

  constructor(kd: number, length: number, kappa0: number | null = null, corner = 0) {
    if (!(length > 0)) {
      throw new Error(`segment length must be positive, got ${length}`);
    }
    if (kappa0 !== null && !finite(kappa0)) {
      throw new Error("segment kappa0 must be a finite number or null");
    }
    if (!finite(corner)) {
      throw new Error("segment corner must be a finite angle");
    }
    this.kd = kd;
    this.length = length;
    this.kappa0 = kappa0;
    this.corner = corner;
  }

  /** The curvature at the segment's end, given the curvature it starts at. */
  kappaEnd(startCurvature: number): number {
    return startCurvature + this.kd * this.length;
  }

  toDict(): SegmentDict {
    const out: SegmentDict = {
      kd: this.kd,
      length: this.length,
      kappa0: this.kappa0,
    };
    if (this.corner) out.corner = this.corner;
    return out;
  }

  static fromDict(data: SegmentDict): Segment {
    return new Segment(
      Number(data.kd),
      Number(data.length),
      data.kappa0 === null || data.kappa0 === undefined ? null : Number(data.kappa0),
      Number(data.corner ?? 0),
    );
  }
}

export class Design {
  readonly segments: Segment[];
  readonly anchor: Anchor;
  readonly offsets: number[];
  readonly stroke: number;
  readonly name: string;
  /** A G1 spline is G1 by construction: curvature jumps at the joins are the
   * fit, not a mistake, so the report must not fail the run. */
  readonly g1: boolean;

  constructor(options: {
    segments: Segment[];
    anchor?: Partial<Anchor>;
    offsets?: number[];
    stroke?: number;
    name?: string;
    g1?: boolean;
  }) {
    const { segments } = options;
    if (!segments.length) {
      throw new Error("a design needs at least one segment");
    }
    const anchor: Anchor = { x: 0, y: 0, angle: 0, ...(options.anchor ?? {}) };
    const stroke = options.stroke ?? 1;
    if (!(stroke > 0)) {
      throw new Error("stroke width must be positive");
    }
    this.segments = segments;
    this.anchor = anchor;
    this.offsets = [...(options.offsets ?? [])];
    this.stroke = stroke;
    this.name = options.name ?? "untitled";
    this.g1 = options.g1 ?? false;
  }

  /** A design from backend pieces: start point, direction, curvature, rate,
   * length. */
  static fromPieces(
    pieces: Array<Record<string, number | undefined>>,
    options: { anchor?: Partial<Anchor>; name?: string; stroke?: number; g1?: boolean } = {},
  ): Design {
    if (!pieces.length) {
      throw new Error("a design needs at least one piece");
    }
    const anchor: Partial<Anchor> = options.anchor ?? {
      x: Number(pieces[0].x0),
      y: Number(pieces[0].y0),
      angle: Number(pieces[0].theta0),
    };
    const segments = pieces.map((piece) =>
      new Segment(
        Number(piece.kd),
        Number(piece.length),
        // a null kappa0 means "continue from the previous segment" — the
        // model's own law; the Python's from_pieces assumed a number here,
        // from_dict carries the null, and the design file can hold either
        piece.kappa0 === null
          ? null
          : Number(piece.kappa0 ?? piece.k0),
        Number(piece.corner ?? 0),
      ),
    );
    return new Design({
      segments,
      anchor,
      stroke: Number(options.stroke ?? 1),
      name: options.name ?? "untitled",
      g1: options.g1 ?? false,
    });
  }

  toDict(): DesignDict {
    const out: DesignDict = {
      name: this.name,
      anchor: { ...this.anchor },
      segments: this.segments.map((segment) => segment.toDict()),
      offsets: [...this.offsets],
      stroke: this.stroke,
    };
    if (this.g1) out.g1 = true;
    return out;
  }

  static fromDict(data: Partial<DesignDict>): Design {
    const segments = (data.segments ?? []).map((segment) => Segment.fromDict(segment));
    return new Design({
      segments,
      anchor: { ...(data.anchor ?? {}) },
      offsets: (data.offsets ?? []).map(Number),
      stroke: Number(data.stroke ?? 1),
      name: String(data.name ?? "untitled"),
      g1: Boolean(data.g1 ?? false),
    });
  }

  toJson(): string {
    return JSON.stringify(this.toDict(), null, 2);
  }

  static fromJson(text: string): Design {
    return Design.fromDict(JSON.parse(text));
  }
}
