// A declared place where two strokes may touch, cross or merge.
//
// The port of curve_lab/contact.py (the conversion track). Contacts are
// DECLARED by the caller, never inferred: a terminal is a contact because the
// drawing says so, not because the geometry happens to meet. Inside its
// footprint a contact is a merge — the clearance rule does not apply there.

export type Point = [number, number];

export class Contact {
  readonly point: Point;
  readonly radius: number;
  readonly a: string | null;
  readonly b: string | null;
  /** Inside the footprint the strokes are joined: the clearance rule does
   * not apply. Outside it, it very much does. */
  readonly waivesClearance: boolean;

  constructor(
    point: Point,
    radius = 1,
    a: string | null = null,
    b: string | null = null,
    waivesClearance = true,
  ) {
    if (!(radius > 0)) {
      throw new Error("contact radius must be positive");
    }
    this.point = [Number(point[0]), Number(point[1])];
    this.radius = Number(radius);
    this.a = a;
    this.b = b;
    this.waivesClearance = Boolean(waivesClearance);
  }

  /** Whether this contact licenses the pair (a, b) to meet at `point`. */
  allows(point: Point, a: string, b: string): boolean {
    if (this.a !== null && this.b !== null) {
      const wanted = new Set([this.a, this.b]);
      if (!(wanted.has(a) && wanted.has(b) && wanted.size === new Set([a, b]).size)) {
        return false;
      }
    } else if (this.a !== null && this.a !== a && this.a !== b) {
      return false;
    } else if (this.b !== null && this.b !== a && this.b !== b) {
      return false;
    }
    const dx = point[0] - this.point[0];
    const dy = point[1] - this.point[1];
    return Math.hypot(dx, dy) <= this.radius;
  }

  toString(): string {
    return `Contact(${this.point}, r=${this.radius})`;
  }
}
