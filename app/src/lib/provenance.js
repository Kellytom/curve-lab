// Why a curve is on the plates page.
//
// The operator's rule, 2026-11-21: "put the curves with stars? just dont put the ones with
// 1 star." A curve is kept when it is rated 2 or more, or when it is a new curve made from
// a kept one (a variant joins its parent). The sentence below each plate is the proof:
// the rating, the construction, and the note that was saved with it.

export const MIN_STARS = 2;

export const starsOf = (curve) => {
  if (curve && Object.prototype.hasOwnProperty.call(curve, "stars")) return Number(curve.stars) || 0;
  return Number(curve?.importance || 0);
};
export const starsLabel = (value) => (Number(value) > 0 ? `${Number(value)}/10` : "none");

const oneLine = (text) => String(text || "").replace(/\s+/g, " ").trim().replace(/\.$/, "");

export function parentOf(curve, byUid) {
  const uid = curve?.params?.variantOf;
  return uid && byUid ? byUid.get(uid) || null : null;
}

// kept: rated at least MIN_STARS, or a variant of a kept curve
export function isKept(curve, byUid) {
  if (starsOf(curve) >= MIN_STARS) return true;
  const parent = parentOf(curve, byUid);
  return Boolean(parent && starsOf(parent) >= MIN_STARS);
}

export function provenanceFor(curve, byUid) {
  const stars = starsOf(curve);
  const parent = parentOf(curve, byUid);
  const parts = [];
  if (parent) {
    parts.push(`Variant of ${parent.uid} (${parent.name}, ${starsOf(parent)}/10)`);
  } else {
    parts.push(`Chosen at ${stars}/10`);
  }

  let note = oneLine(curve.note);
  if (parent) note = note.replace(/^variant of [^·]+·\s*/i, "");
  if (note) {
    parts.push(note);
  } else {
    if (curve.formula?.plain) parts.push(oneLine(curve.formula.plain));
    const family = String(curve.family || "");
    if (family && family.toLowerCase() !== String(curve.name || "").toLowerCase()) {
      parts.push(`${family} family`);
    }
    const source = String(curve.source || "");
    if (source === "found") parts.push("found in the finder");
    else if (source) parts.push(`saved as ${source}`);
    else if (curve.lists?.length) parts.push(`from the ${curve.lists.join("/")} set`);
  }
  if (parent && stars) parts.push(`this one rated ${stars}/10`);
  return `${parts.join(" · ")}.`;
}
