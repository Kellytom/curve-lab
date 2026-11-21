// Take named records out of the collection: the registry seed, the database rows, and the
// per-curve artefacts (plate, web copy, figure). The desk rows are left alone, so the
// working page that made them keeps its source.
//
//   node scripts/remove_curve_records.mjs --match '^wonk-\\d+$'          # report
//   node scripts/remove_curve_records.mjs --match '^wonk-\\d+$' --write  # remove
//
// The registry is copied to state/backups/ before a write. The figure index is filtered to
// match, because the gallery and its freshness test must name exactly the registry.

import { copyFileSync, existsSync, readFileSync, renameSync, unlinkSync, writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import { prisma } from "../app/src/lib/db.js";
import { exportTable } from "../app/src/lib/data-export.js";

const ROOT = path.resolve(import.meta.dirname, "..");
const REGISTRY = path.join(ROOT, "workbench", "curve-registry.json");
const BACKUP = path.join(ROOT, "state", "backups", "curve-registry.before-removal.json");
const INDEX = path.join(ROOT, "app", "public", "figures", "index.json");

const args = process.argv.slice(2);
const matchAt = args.indexOf("--match");
const pattern = matchAt >= 0 ? new RegExp(args[matchAt + 1]) : null;
const write = args.includes("--write");
if (!pattern) {
  console.error("give a --match pattern, for example '^wonk-\\\\d+$'");
  process.exit(2);
}

const registry = JSON.parse(readFileSync(REGISTRY, "utf8"));
const victims = registry.curves.filter((curve) => pattern.test(curve.name));
if (!victims.length) {
  console.log("nothing matches");
  process.exit(0);
}

const filesOf = (uid) => [
  path.join(ROOT, "book", "print", `${uid}.svg`),
  path.join(ROOT, "book", "print", `${uid}-3000-grey-300dpi.png`),
  path.join(ROOT, "app", "public", "plates-web", `${uid}-1600-grey.png`),
  path.join(ROOT, "app", "public", "figures", `${uid}.png`),
  path.join(ROOT, "workbench", "figures", `${uid}.png`),
];

console.log(`${victims.length} records match ${pattern}`);
console.log(victims.map((curve) => `${curve.uid}:${curve.name}`).join(" "));
const present = victims.flatMap((curve) => filesOf(curve.uid).filter((file) => existsSync(file)));
console.log(`${present.length} artefact files on disk`);

if (!write) {
  console.log("dry run; add --write to remove");
  process.exit(0);
}

mkdirSync(path.dirname(BACKUP), { recursive: true });
copyFileSync(REGISTRY, BACKUP);

const uids = victims.map((curve) => curve.uid);
const names = victims.map((curve) => curve.name);
registry.curves = registry.curves.filter((curve) => !uids.includes(curve.uid));
registry.sets = (registry.sets || []).filter((set) => !uids.includes(set.inner_uid));
writeFileSync(`${REGISTRY}.tmp`, `${JSON.stringify(registry, null, 2)}\n`);
renameSync(`${REGISTRY}.tmp`, REGISTRY);

await prisma.$transaction([
  prisma.curveMetric.deleteMany({ where: { uid: { in: uids } } }),
  prisma.curveSet.deleteMany({ where: { innerUid: { in: uids } } }),
  prisma.note.deleteMany({ where: { uid: { in: uids } } }),
  prisma.curve.deleteMany({ where: { uid: { in: uids } } }),
  prisma.star.deleteMany({ where: { name: { in: names } } }),
]);

for (const file of present) unlinkSync(file);

const index = JSON.parse(readFileSync(INDEX, "utf8"));
const before = (index.curves || []).length;
index.curves = (index.curves || []).filter((curve) => !uids.includes(curve.uid));
writeFileSync(INDEX, `${JSON.stringify(index, null, 2)}\n`);

await exportTable("curves");
console.log(`removed ${victims.length} records; registry ${registry.curves.length}, ` +
  `figures ${before} -> ${index.curves.length}, files ${present.length}; previous seed at ` +
  `${path.relative(ROOT, BACKUP)}`);
await prisma.$disconnect();
