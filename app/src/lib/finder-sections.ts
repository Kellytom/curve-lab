// The finder's sections: one card per curve, in a fixed order.
//
// The order is starred, symmetric, best, then the remaining families. The
// groups must not overlap: a mirrored curve that is also featured used to be
// built into both "Symmetric" and "Best so far", so the page showed the same
// curve twice. Each group here excludes everything the earlier ones took.

export type Curve = {
  id?: string;
  flags?: string[];
  featured?: boolean;
  family?: string;
  [key: string]: any;
};

export type Section = {
  key: string;
  title: string;
  lead: string;
  curves: Curve[];
};

const isMirrored = (curve: Curve): boolean => (curve.flags || []).some((flag) => String(flag).startsWith("mirror "));

export function finderSections(curves: Curve[], isStarred: (curve: Curve) => boolean = () => false): Section[] {
  const starred = curves.filter((curve) => isStarred(curve));
  const symmetric = curves
    .filter((curve) => isMirrored(curve) && !isStarred(curve))
    .sort((a, b) => {
      if (a.id === "symmetric-rotated345") return -1;
      if (b.id === "symmetric-rotated345") return 1;
      const rank = (curve: Curve) =>
        (curve.flags || []).some((flag) => String(flag).startsWith("mirror y=x")) ? 0 : 1;
      return rank(a) - rank(b);
    });
  const featured = curves.filter((curve) => curve.featured && !isStarred(curve) && !isMirrored(curve));
  const rest = curves.filter(
    (curve) => !isStarred(curve) && !curve.featured && !isMirrored(curve),
  );
  const familyNames = [...new Set(rest.map((curve) => curve.family || "other"))].sort();

  const sections: Section[] = [
    { key: "starred", title: "Starred", lead: "Your choices, at the top.", curves: starred },
  ];
  if (symmetric.length) {
    sections.push({
      key: "symmetric",
      title: "Symmetric",
      lead: "Mirror curves, measured. The top one is new: a 3-4-5 rotation of a vertically mirrored curve, exact gap 0.0000 about slope −3/4.",
      curves: symmetric,
    });
  }
  if (featured.length) {
    sections.push({
      key: "best",
      title: "Best so far",
      lead: "The strongest of the new methods: solved crossings, arcs, ends-first, bounded curves.",
      curves: featured,
    });
  }
  for (const family of familyNames) {
    sections.push({
      key: family,
      title: family,
      lead: "",
      curves: rest.filter((curve) => (curve.family || "other") === family),
    });
  }
  return sections;
}
