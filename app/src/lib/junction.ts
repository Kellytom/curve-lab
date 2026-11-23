// A junction: where a branch meets a trunk.
//
// The port of curve_lab/junction.py's GEOMETRY: the corner the two centre
// lines make, the circular fillet, the two ribbon widths, the declared merge,
// and the report a review reads (the join grade, the arc length, the trim).
//
// Scope: the piece is returned as a PieceInput with the two Designs attached.
// Turning those designs into cubic spans is the clothoid engine's job, which
// is a later port row (piece.ts's design path throws for now) — so this module
// stops where the ruler stops, and says so.
//
// The geometry is deliberately conservative: a straight branch, a circular
// fillet, then the trunk. That is G1 — curvature steps to 1/r at the touch
// point — and the report says so instead of pretending otherwise.

import { Design, Segment } from "./model.ts";
import { Contact } from "./contact.ts";
import { arcSegment, cornerFillet, FilletError } from "./fillet.ts";
import type { PieceInput } from "./piece.ts";

export type Point = [number, number];

export class Junction {
  readonly corner: Point;
  readonly branchEnd: Point;
  readonly trunkEnd: Point;
  readonly radius: number;
  readonly branchWidth: number;
  readonly trunkWidth: number;
  readonly branchName: string;
  readonly trunkName: string;
  readonly trunkLength: number;
  readonly branchTerminal: string;

  constructor(options: {
    corner: Point;
    branchEnd: Point;
    trunkEnd: Point;
    radius?: number;
    branchWidth?: number;
    trunkWidth?: number;
    branchName?: string;
    trunkName?: string;
    trunkLength?: number;
    branchTerminal?: string;
  }) {
    const {
      corner, branchEnd, trunkEnd,
      radius = 6, branchWidth = 6, trunkWidth = 12,
      branchName = "ink/branch", trunkName = "ink/trunk",
      trunkLength = 80, branchTerminal = "cone",
    } = options;
    if (!(radius > 0)) {
      throw new Error("junction radius must be positive");
    }
    if (!(branchWidth > 0) || !(trunkWidth > 0)) {
      throw new Error("ribbon widths must be positive");
    }
    const same = (p: Point, q: Point) => p[0] === q[0] && p[1] === q[1];
    if (same(branchEnd, corner) || same(trunkEnd, corner)) {
      throw new Error("a junction needs two edges away from the corner");
    }
    this.corner = corner;
    this.branchEnd = branchEnd;
    this.trunkEnd = trunkEnd;
    this.radius = radius;
    this.branchWidth = branchWidth;
    this.trunkWidth = trunkWidth;
    this.branchName = branchName;
    this.trunkName = trunkName;
    this.trunkLength = trunkLength;
    this.branchTerminal = branchTerminal;
  }

  /** The fillet's two touch points, centre and arc — computed once. */
  private fillet() {
    return cornerFillet(this.branchEnd, this.corner, this.trunkEnd, this.radius);
  }

  /** The merge point: where the fillet meets the trunk edge. */
  get mergePoint(): Point {
    return this.fillet().end;
  }

  /** The merge, as a declared contact wide enough to cover the branch. */
  contact(): Contact {
    return new Contact(this.mergePoint, this.radius + this.branchWidth,
                       this.branchName, this.trunkName);
  }

  /** `{ pieceInput, contact, report }` for this junction. */
  build(): { pieceInput: PieceInput; contact: Contact; report: Record<string, unknown> } {
    const fillet = this.fillet();
    const branchLength =
      Math.hypot(this.branchEnd[0] - this.corner[0], this.branchEnd[1] - this.corner[1]) -
      fillet.trim[0];
    if (branchLength <= 0) {
      throw new FilletError("the fillet consumes the whole branch");
    }

    const anchorAngle = Math.atan2(this.corner[1] - this.branchEnd[1],
                                   this.corner[0] - this.branchEnd[0]);
    const arc = arcSegment(fillet);
    const branch = new Design({
      name: "branch",
      anchor: { x: this.branchEnd[0], y: this.branchEnd[1], angle: anchorAngle },
      segments: [
        new Segment(0, branchLength, 0),
        new Segment(arc.segment.kd, arc.segment.length, arc.segment.kappa0),
      ],
    });

    const trunkAngle = Math.atan2(this.trunkEnd[1] - this.corner[1],
                                  this.trunkEnd[0] - this.corner[0]);
    const back = this.trunkLength / 2;
    const trunk = new Design({
      name: "trunk",
      anchor: {
        x: this.corner[0] - Math.cos(trunkAngle) * back,
        y: this.corner[1] - Math.sin(trunkAngle) * back,
        angle: trunkAngle,
      },
      segments: [new Segment(0, this.trunkLength, 0)],
    });

    const pieceInput: PieceInput = {
      name: "junction",
      stroke: 0.6,
      traces: [
        { name: "branch", design: branch.toDict(), width: this.branchWidth,
          terminals: [this.branchTerminal, "butt"] },
        { name: "trunk", design: trunk.toDict(), width: this.trunkWidth,
          terminals: ["butt", "butt"] },
      ],
    };

    const report = {
      angle: fillet.angle,
      tangent: fillet.tangent,
      arc_length: fillet.length,
      trim: [fillet.trim[0], fillet.trim[1]],
      merge: [fillet.end[0], fillet.end[1]],
      branch_length: branchLength,
      join: "G1",
      curvature_step: 1 / this.radius,
    };
    return { pieceInput, contact: this.contact(), report };
  }
}
