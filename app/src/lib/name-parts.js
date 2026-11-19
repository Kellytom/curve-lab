// A curve's name is three parts: the construction (prefix), the middle, and the
// variant (postfix). The middle may be empty: a curve that is the only one of
// its construction is named by the construction alone ("amper", "swan"), and a
// variant can stand on its own ("knot-6"). An empty middle used to compose to
// an empty string, so the desk refused to save ten of the 212 chosen curves.

export function slugName(text) {
  return String(text || "").toLowerCase()
    .replace(/(\d+)\s*\/\s*(\d+)/g, "$1of$2")
    .replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

export function composeName({ prefix, core, postfix } = {}) {
  const clean = (part) => String(part || "").trim().replace(/^-+|-+$/g, "");
  return [clean(prefix), clean(core), clean(postfix)].filter(Boolean).join("-");
}

export function splitName(name, familyId) {
  const match = String(name || "").match(/-(\d+)$/);
  const postfix = match ? match[1] : "";
  const slug = slugName(name);
  const prefix = familyId && familyId !== "curve" ? familyId : slug.split("-")[0];
  const core = slug
    .replace(new RegExp(`^${prefix}-?`), "")
    .replace(new RegExp(`-?${postfix}$`), "");
  return { prefix, core, postfix };
}
