// One star per curve, whatever it was called when it was starred.
//
// A star may carry the finder's stable id, a name, or both. The page writes
// ids, the export file writes names, and a rename leaves an old name behind,
// so the same curve can appear twice in a browser's list. The key is the id
// when there is one; a name resolves to its id through the page's own table.

export function starKey(star, nameToId = {}) {
  if (!star) return "";
  if (star.id) return star.id;
  if (star.name && nameToId[star.name]) return nameToId[star.name];
  return star.name ? `name:${star.name}` : "";
}

export function dedupeStars(list, nameToId = {}) {
  const byKey = new Map();
  for (const star of Array.isArray(list) ? list : []) {
    const key = starKey(star, nameToId);
    if (!key) continue;
    const previous = byKey.get(key);
    // Keep the copy that carries the id: it is the one the page can match.
    byKey.set(key, previous && (previous.id || !star.id) ? previous : star);
  }
  return [...byKey.values()];
}

// The number of stars this page can actually show: one per curve on it.
export function countStars(list, nameToId = {}, knownIds = new Set()) {
  const keys = new Set();
  for (const star of Array.isArray(list) ? list : []) {
    const key = starKey(star, nameToId);
    if (!key) continue;
    if (key.startsWith("name:")) {
      if (!nameToId[key.slice(5)]) keys.add(key);
    } else if (knownIds.has(key)) {
      keys.add(key);
    }
  }
  return keys.size;
}
