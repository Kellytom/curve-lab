// Load the analysis into SQLite through Prisma: Python computes, this writes.
//
//   node app/scripts/load-analysis.mjs
//   node app/scripts/load-analysis.mjs --check   # report, do not write
//
// The file is workbench/curve-analysis.json (format curve-lab.curve-analysis/1),
// written by scripts/analyse_curves.py. One row per curve in CurveMetric; a
// curve that is no longer in the registry has its metric removed.

import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { PrismaClient } from "@prisma/client";

const APP_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const ROOT = path.resolve(APP_ROOT, "..");
const FILE = path.join(ROOT, "workbench", "curve-analysis.json");
const CHECK = process.argv.includes("--check");

const data = JSON.parse(readFileSync(FILE, "utf8"));
if (data.format !== "curve-lab.curve-analysis/1") {
  console.error(`wrong format: ${data.format}`);
  process.exit(1);
}
const rows = data.curves || [];
const numbers = (value) => (typeof value === "number" && Number.isFinite(value) ? value : 0);
// The grid is an exact integer and can pass 2^53, so it travels as a string.
const big = (value) => {
  try { return BigInt(String(value ?? 0)); } catch { return 0n; }
};

const prisma = new PrismaClient();
try {
  const curves = await prisma.curve.findMany({ select: { uid: true } });
  const known = new Set(curves.map((curve) => curve.uid));
  const present = rows.filter((row) => known.has(row.uid));
  const stale = [...known].filter((uid) => !rows.some((row) => row.uid === uid));

  const exact = present.filter((row) => row.method === "exact").length;
  const crossed = present.filter((row) => (row.crossings || 0) > 0).length;
  console.log(`${present.length} rows · ${exact} exact · ${crossed} with crossings · ${stale.length} registry curves without a metric`);

  if (CHECK) process.exit(0);

  await prisma.$transaction([
    ...present.map((row) => prisma.curveMetric.upsert({
      where: { uid: row.uid },
      create: {
        uid: row.uid,
        family: row.family || null,
        kind: row.kind || "rows",
        method: row.method || "sampled",
        degree: row.degree || 0,
        step: numbers(row.step),
        grid: big(row.grid),
        bend: numbers(row.bend),
        arc: numbers(row.arc),
        chord: numbers(row.chord),
        inflections: row.inflections || 0,
        inflectionMax: row.inflectionMax || 0,
        closest: numbers(row.closest),
        crossings: row.crossings || 0,
        meetingPoints: row.meetingPoints || 0,
        bboxW: numbers(row.bboxW),
        bboxH: numbers(row.bboxH),
        area: numbers(row.area),
        maxCurvature: numbers(row.maxCurvature),
        curvatureMedian: numbers(row.curvatureMedian),
        mirrorY: numbers(row.mirrorY),
        halfTurn: numbers(row.halfTurn),
        mirrorYX: numbers(row.mirrorYX),
      },
      update: {
        family: row.family || null,
        kind: row.kind || "rows",
        method: row.method || "sampled",
        degree: row.degree || 0,
        step: numbers(row.step),
        grid: big(row.grid),
        bend: numbers(row.bend),
        arc: numbers(row.arc),
        chord: numbers(row.chord),
        inflections: row.inflections || 0,
        inflectionMax: row.inflectionMax || 0,
        closest: numbers(row.closest),
        crossings: row.crossings || 0,
        meetingPoints: row.meetingPoints || 0,
        bboxW: numbers(row.bboxW),
        bboxH: numbers(row.bboxH),
        area: numbers(row.area),
        maxCurvature: numbers(row.maxCurvature),
        curvatureMedian: numbers(row.curvatureMedian),
        mirrorY: numbers(row.mirrorY),
        halfTurn: numbers(row.halfTurn),
        mirrorYX: numbers(row.mirrorYX),
      },
    })),
    ...(stale.length ? [prisma.curveMetric.deleteMany({ where: { uid: { in: stale } } })] : []),
  ]);
  console.log(`wrote ${present.length} metrics; removed ${stale.length}`);
} finally {
  await prisma.$disconnect();
}
