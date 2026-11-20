// What a saved row must carry so the curve can be rebuilt without the page: the kind, the
// parent, the cut points, the ends, the formulas and a note in words.

export function constructionOf(row) {
  const kind = row.kind || (row.parent ? "piece" : "hybrid");
  const points = row.points || [];
  const ends = points.length ? [points[0], points[points.length - 1]] : [];
  const cuts = (row.cuts || []).map((cut) => ({ t: cut.t, x: cut.x, y: cut.y }));
  const formula = row.formula || {};
  let note = formula.use || formula.plain || "";
  if (kind === "double") {
    note = `DW: the mirrored half of ${row.parentName || "a wonk"} (${row.half || "piece"}), ` +
      `mirrored across the line y = x. ${formula.plain || ""}`.trim();
  }
  return { kind, parent: row.parent || null, parentName: row.parentName || null,
           half: row.half || null, cuts, ends, formula, note };
}
