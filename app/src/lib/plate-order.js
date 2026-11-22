// The order of the plates page.
//
// The operator, 2026-11-21: "once we add the ten stars, we will be able to rearrange all the
// curves and their variations." The star order groups a curve with its variants (so a variant
// stays beside its parent) and orders the families by their best rating. The uid order is the
// plain fallback and is still one click away.

export const baseUidOf = (curve) => String(curve?.params?.variantOf || curve?.uid || "");

export const starsOf = (curve) => Number(curve?.stars ?? curve?.importance ?? 0);

export function orderPlates(curves, by = "stars") {
  const list = [...curves];
  if (by === "uid") return list.sort((a, b) => a.uid.localeCompare(b.uid));

  const groups = new Map();
  for (const curve of list) {
    const base = baseUidOf(curve);
    if (!groups.has(base)) groups.set(base, []);
    groups.get(base).push(curve);
  }
  const rank = (rows) => rows.reduce((top, curve) => Math.max(top, starsOf(curve)), 0);
  const within = (rows) => rows.sort((a, b) => {
    const ka = `${a.uid === baseUidOf(a) ? "0" : "1"}${a.uid}`;
    const kb = `${b.uid === baseUidOf(b) ? "0" : "1"}${b.uid}`;
    return ka.localeCompare(kb);
  });

  return [...groups.entries()]
    .sort(([baseA, rowsA], [baseB, rowsB]) => rank(rowsB) - rank(rowsA) || baseA.localeCompare(baseB))
    .flatMap(([, rows]) => within(rows));
}
