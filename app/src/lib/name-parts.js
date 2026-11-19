// @ts-check
// A curve's name is three parts: the construction (prefix), the middle, and the
// variant (postfix). The middle may be empty: a curve that is the only one of
// its construction is named by the construction alone ("amper", "swan"), and a
// variant can stand on its own ("knot-6"). An empty middle used to compose to
// an empty string, so the desk refused to save ten of the 212 chosen curves.

/**
 * @typedef {Object} NameParts
 * @property {string} prefix
 * @property {string} core
 * @property {string} postfix
 */

/**
 * @typedef {{ value?: string, at?: number } | string} Draft
 */

/**
 * @param {string} text
 * @returns {string}
 */
export function slugName(text) {
  return String(text || "").toLowerCase()
    .replace(/(\d+)\s*\/\s*(\d+)/g, "$1of$2")
    .replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

/**
 * @param {Partial<NameParts>} [parts]
 * @returns {string}
 */
export function composeName({ prefix, core, postfix } = {}) {
  const clean = (part) => String(part || "").trim().replace(/^-+|-+$/g, "");
  return [clean(prefix), clean(core), clean(postfix)].filter(Boolean).join("-");
}

/**
 * @param {string} name
 * @param {string} [familyId]
 * @returns {NameParts}
 */
export function splitName(name, familyId) {  const match = String(name || "").match(/-(\d+)$/);
  const postfix = match ? match[1] : "";
  const slug = slugName(name);
  const prefix = familyId && familyId !== "curve" ? familyId : slug.split("-")[0];
  const core = slug
    .replace(new RegExp(`^${prefix}-?`), "")
    .replace(new RegExp(`-?${postfix}$`), "");
  return { prefix, core, postfix };
}

// A draft in the browser versus the saved name in the record.
//
// The fault this prevents: a saved name looked "gone" because an old draft in
// the same browser still sat in the box. A draft only counts when it is newer
// than the save; an empty draft never counts. `savedAt` and `draft.at` are
// milliseconds; a draft in the old string format has no time, so it is stale.
/**
 * @param {Draft | null | undefined} entry
 * @param {number} [savedAt]
 * @returns {{ value: string | undefined, stale: boolean }}
 */
export function draftState(entry, savedAt = 0) {
  if (entry === undefined || entry === null) return { value: undefined, stale: true };
  const value = typeof entry === "string" ? entry : entry.value;
  const at = typeof entry === "string" ? 0 : Number(entry.at) || 0;
  if (typeof value !== "string" || value === "") return { value: undefined, stale: true };
  return { value, stale: Number(savedAt) > at };
}
