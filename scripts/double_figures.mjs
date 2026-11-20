// One figure per wonky, drawn by the app's figure builder.
//
//   node scripts/wonky_figures.mjs

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import { figureSvg } from "../app/src/lib/plot-figure.js";

const ROOT = path.resolve(import.meta.dirname, "..");
const data = JSON.parse(readFileSync(path.join(ROOT, "workbench", "doubles.json"), "utf8"));
const OUT = path.join(ROOT, "app", "public", "hybrid-figures");
mkdirSync(OUT, { recursive: true });

let n = 0;
for (const row of data.doubles) {
  const xs = row.points.map(([x]) => x);
  const ys = row.points.map(([, y]) => y);
  const svg = figureSvg({
    key: row.id,
    title: row.id,
    equation: row.formula.plain,
    legend: [{ label: `double wonky from ${row.parentName}`, colour: "#2f6fa8" }],
    paths: [{ name: row.id, colour: "#2f6fa8", points: row.points }],
    stations: [],
    labels: (row.cuts || []).map((cut) => ({
      x: cut.x, y: cut.y, text: `(${cut.x.toFixed(2)}, ${cut.y.toFixed(2)})`,
    })),
    bounds: [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)],
    samples: row.points.length,
  }, { width: 440 });
  const [, , w, h] = svg.match(/viewBox="([^"]+)"/)[1].split(/\s+/);
  const sized = svg
    .replace('width="100%"', `width="${w}" height="${h}"`)
    .replace(' style="height:auto"', "")
    .replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ');
  writeFileSync(path.join(OUT, row.figure), sized);
  n += 1;
}
console.log(`wrote ${n} wonky figures`);
