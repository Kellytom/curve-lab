// Read the versions the app actually runs, and write them into
// app/src/content/docs/docs/stack.md between two markers.
//
//   node scripts/stack_doc.mjs          # write the table
//   node scripts/stack_doc.mjs --check  # fail if the doc is stale
//
// The versions come from the resolved node_modules, not from app/package.json:
// the range in package.json is a wish, the installed package is what runs.

import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const APP = path.join(ROOT, "app");
const DOC = path.join(APP, "src", "content", "docs", "docs", "stack.md");
const START = "<!-- stack:start -->";
const END = "<!-- stack:end -->";

function version(name) {
  const file = path.join(APP, "node_modules", name, "package.json");
  return JSON.parse(readFileSync(file, "utf8")).version;
}

const rows = [
  ["Node", process.version.replace(/^v/, "")],
  ["Astro", version("astro")],
  ["Astro Node adapter", version("@astrojs/node")],
  ["Starlight", version("@astrojs/starlight")],
  ["Prisma", version("prisma")],
  ["Prisma client", version("@prisma/client")],
  ["Zod", version("zod")],
];

const table = [
  "| what | version |",
  "|---|---|",
  ...rows.map(([what, value]) => `| ${what} | ${value} |`),
].join("\n");

const doc = readFileSync(DOC, "utf8");
const start = doc.indexOf(START);
const end = doc.indexOf(END);
if (start < 0 || end < 0) {
  console.error(`stack: markers not found in ${path.relative(ROOT, DOC)}`);
  process.exit(1);
}

const current = doc.slice(start + START.length, end).trim();
const next = `${doc.slice(0, start + START.length)}\n${table}\n${doc.slice(end)}`;

if (process.argv.includes("--check")) {
  if (current !== table) {
    console.error("stack.md is stale: run node scripts/stack_doc.mjs");
    process.exit(1);
  }
  console.log("stack.md matches the installed versions");
} else {
  writeFileSync(DOC, next);
  console.log(`wrote ${path.relative(ROOT, DOC)}`);
}
