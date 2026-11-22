// What the collection has, and what it plainly does not.
//
//   PATH="$HOME/node24/bin:$PATH" node scripts/curve_gaps.mjs
//
// Reads the registry and the exported metrics, prints the census, the crossings × inflections
// cells that have no curve, the symmetry classes and the named classical curves that are not
// present. Writes state/GAPS-int.md. It proposes, it does not create.
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

const ROOT = path.resolve(import.meta.dirname, "..");
const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));
const rows = JSON.parse(readFileSync(path.join(ROOT, "data", "curves.json"), "utf8")).rows;
const byUid = new Map(rows.map((row) => [row.uid, row]));

const curves = registry.curves.map((record) => {
  const row = byUid.get(record.uid) || {};
  const metric = row.metric || {};
  const note = row.note || {};
  return {
    uid: record.uid,
    name: record.name,
    aliases: record.aliases || [],
    family: record.family || record.family_id || "(none)",
    kind: record.path ? "path" : "rows",
    stars: Number(row.stars || 0),
    grid: metric.grid ?? null,
    bend: metric.bend ?? null,
    crossings: metric.crossings ?? null,
    inflections: metric.inflections ?? null,
    mirror: metric.mirrorY ?? null,
    half: metric.halfTurn ?? null,
    step: metric.step ?? record.step ?? null,
  };
});

// ---- the named classical curves the generators already know ------------------------------
const generatorSource = readFileSync(path.join(ROOT, "scripts", "generators.py"), "utf8");
const named = [...generatorSource.matchAll(/dict\(key="([^"]+)"/g)].map((m) => m[1]);
// the equation and the one-line description of each named curve, for the extra-curves page
const polyText = (list) => {
  if (!list) return "";
  const sup = (n) => String(n).replace(/[0-9]/g, (d) => "⁰¹²³⁴⁵⁶⁷⁸⁹"[d]);
  const terms = [];
  list.forEach((c, i) => {
    if (!c) return;
    const magnitude = Math.abs(c) === 1 && i > 0 ? "" : String(Math.abs(c));
    const power = i === 0 ? "" : i === 1 ? "t" : `t${sup(i)}`;
    terms.push(`${c < 0 ? "−" : "+"}${magnitude}${power}`);
  });
  if (!terms.length) return "0";
  const first = terms[0].replace(/^\+/, "");
  return terms.slice(1).reduce((text, term) => `${text} ${term}`, first);
};

const namedDetails = new Map();
for (const block of generatorSource.split("dict(key=").slice(1)) {
  const key = (block.match(/^"([^"]+)"/) || [])[1];
  if (!key) continue;
  const eq = (block.match(/eq="([^"]*)"/) || [])[1] || "";
  const h = (block.match(/h=\(([^)]*)\)/) || [])[1];
  const u = (block.match(/u=\(([^)]*)\)/) || [])[1];
  const v = (block.match(/v=\(([^)]*)\)/) || [])[1];
  const asList = (text) => (text ? text.split(",").map((n) => Number(n.trim())) : null);
  const speedEq = h && u && v
    ? `h = ${polyText(asList(h))} · u = ${polyText(asList(u))} · v = ${polyText(asList(v))}`
    : "";
  namedDetails.set(key, {
    key,
    eq: eq || speedEq,
    tail: (block.match(/tail="([^"]*)"/) || [])[1] || (block.match(/note="([^"]*)"/) || [])[1] || "",
    deg: Number((block.match(/deg=(\d+)/) || [])[1] || (block.match(/n=(\d+)/) || [])[1] || 0),
  });
}
const present = new Set(curves.flatMap((c) => [c.name.toLowerCase(), ...c.aliases.map((a) => a.toLowerCase())]));
const missingNamed = named.filter((key) => ![...present].some((name) => name.includes(key.toLowerCase())));

// ---- crossings × inflections --------------------------------------------------------------
const crossingsMax = Math.max(...curves.map((c) => c.crossings ?? 0), 0);
const inflectionsMax = Math.max(...curves.map((c) => c.inflections ?? 0), 0);
const cells = new Map();
for (const c of curves) {
  if (c.crossings === null || c.inflections === null) continue;
  const key = `${c.crossings}:${c.inflections}`;
  cells.set(key, (cells.get(key) || 0) + 1);
}
const emptyCells = [];
for (let x = 0; x <= crossingsMax; x += 1) {
  for (let y = 0; y <= inflectionsMax; y += 1) {
    if (!cells.has(`${x}:${y}`)) emptyCells.push([x, y]);
  }
}

// ---- families -----------------------------------------------------------------------------
const byFamily = new Map();
for (const c of curves) {
  if (!byFamily.has(c.family)) byFamily.set(c.family, []);
  byFamily.get(c.family).push(c);
}
const families = [...byFamily.entries()]
  .map(([family, list]) => ({
    family,
    count: list.length,
    rated: list.filter((c) => c.stars >= 2).length,
    rows: list.filter((c) => c.kind === "rows").length,
    paths: list.filter((c) => c.kind === "path").length,
    grids: [...new Set(list.map((c) => c.grid).filter((g) => g !== null))].sort((a, b) => a - b),
  }))
  .sort((a, b) => b.count - a.count);

// ---- symmetry -----------------------------------------------------------------------------
const symmetry = (list) => {
  const tolerance = 0.005;
  let mirror = 0, half = 0, neither = 0;
  for (const c of list) {
    if (c.mirror === null && c.half === null) continue;
    if (c.mirror !== null && c.mirror <= tolerance) mirror += 1;
    else if (c.half !== null && c.half <= tolerance) half += 1;
    else neither += 1;
  }
  return { mirror, half, neither };
};

// ---- write the report ---------------------------------------------------------------------
const lines = [];
lines.push("# GAPS-int — what the 371 curves cover, and what they plainly miss", "");
lines.push("Generated by `scripts/curve_gaps.mjs` from the registry and the exported metrics.");
lines.push("It proposes; nothing here is created until the operator says so.", "");
lines.push(`## The set`, "");
lines.push(`- **${curves.length} curves**, ${curves.filter((c) => c.kind === "rows").length} as speed rows and ` +
  `${curves.filter((c) => c.kind === "path").length} as stored paths.`);
lines.push(`- **${curves.filter((c) => c.stars >= 2).length}** are rated 2/10 or more; ` +
  `${curves.filter((c) => c.crossings !== null).length} have a recorded exact measurement.`);
lines.push("");
lines.push("## Families", "");
lines.push("| family | curves | rated 2+ | speed rows | paths | grids |");
lines.push("|---|---|---|---|---|---|");
for (const f of families) {
  lines.push(`| ${f.family} | ${f.count} | ${f.rated} | ${f.rows} | ${f.paths} | ${f.grids.join(", ") || "—"} |`);
}
lines.push("");
lines.push("## The crossings × inflections grid", "");
lines.push(`Measured curves run to **${crossingsMax} crossing pairs** and **${inflectionsMax} inflections**. ` +
  `**${emptyCells.length} of the ${(crossingsMax + 1) * (inflectionsMax + 1)} cells are empty.**`, "");
lines.push("| crossing pairs | inflections | curves |");
lines.push("|---|---|---|");
for (let x = 0; x <= crossingsMax; x += 1) {
  const rowCells = [];
  for (let y = 0; y <= inflectionsMax; y += 1) rowCells.push(`${y}:${cells.get(`${x}:${y}`) || 0}`);
  lines.push(`| ${x} | ${rowCells.join(" · ")} |`);
}
lines.push("");
lines.push("Empty cells with a plain reading:");
for (const [x, y] of emptyCells.slice(0, 20)) {
  lines.push(`- **${x} crossing pairs, ${y} inflection(s)** — no curve.`);
}
lines.push("");
lines.push("## Symmetry", "");
lines.push("| family | mirror | half turn | neither |");
lines.push("|---|---|---|---|");
for (const [family, list] of [...byFamily.entries()].sort((a, b) => b[1].length - a[1].length)) {
  const s = symmetry(list);
  if (s.mirror + s.half + s.neither === 0) continue;
  lines.push(`| ${family} | ${s.mirror} | ${s.half} | ${s.neither} |`);
}
lines.push("");
lines.push("## Named classical curves not present", "");
lines.push(`The generators already know ${named.length} named curves; ` +
  `**${missingNamed.length} have no record in the collection**:`, "");
for (const key of missingNamed) lines.push(`- ${key}`);
lines.push("");
lines.push("## Obvious candidates to create", "");
lines.push("In the order they would fill the biggest holes:");
lines.push("");
lines.push("1. **The named classical curves above** — each has an equation already written in " +
  "`scripts/generators.py`, so a record is data entry plus a figure, not new mathematics.");
lines.push(`2. **The empty crossing/inflection cells** — ${emptyCells.length} cells, starting with the ` +
  "ones adjacent to a full cell (one more crossing, one more inflection), which are the cheapest " +
  "new shapes to find.");
lines.push("3. **Families with no 2+ rated curve** — " +
  [...byFamily.entries()].filter(([, list]) => list.every((c) => c.stars < 2)).map(([f]) => f).join(", "));
lines.push("");
const report = `${lines.join("\n")}\n`;
writeFileSync(path.join(ROOT, "state", "GAPS-int.md"), report);

// the page's data: the missing named curves with their equations, and the empty cells
const pageData = {
  format: "curve-lab.extra-curves/1",
  note: "The named classical curves the generators know but the collection does not, and the " +
    "crossing x inflection cells with no curve. Generated by scripts/curve_gaps.mjs.",
  count: { curves: curves.length, emptyCells: emptyCells.length, missingNamed: missingNamed.length },
  missingNamed: missingNamed.map((key) => namedDetails.get(key) || { key, eq: "", tail: "", deg: 0 }),
  emptyCells: emptyCells.map(([crossings, inflections]) => ({ crossings, inflections })),
  familiesWithoutRating: [...byFamily.entries()]
    .filter(([, list]) => list.every((c) => c.stars < 2))
    .map(([family, list]) => ({ family, curves: list.length })),
};
writeFileSync(path.join(ROOT, "app", "src", "data", "extra-curves.json"), `${JSON.stringify(pageData, null, 1)}\n`);
console.log(JSON.stringify({
  curves: curves.length,
  families: families.length,
  crossingsMax, inflectionsMax,
  emptyCells: emptyCells.length,
  missingNamed: missingNamed.length,
  wrote: "state/GAPS-int.md",
}, null, 1));
