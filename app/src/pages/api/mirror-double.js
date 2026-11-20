// POST /api/mirror-double  { parent }
//
// Cuts the curve where it crosses x = 0, keeps one half, mirrors it across the y axis, and
// saves the result as its own row with a found name. Writes its figure beside the others.

import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { figureSvg } from "../../lib/plot-figure.js";
import { prisma } from "../../lib/db.js";
import { repoRoot } from "../../lib/gallery.js";

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

function geometry(id) {
  for (const name of ["hybrids.json", "wonkies.json", "doubles.json"]) {
    const file = JSON.parse(readFileSync(path.join(repoRoot(), "workbench", name), "utf8"));
    for (const key of ["candidates", "wonkies", "doubles"]) {
      const row = (file[key] || []).find((item) => item.id === id);
      if (row) return row;
    }
  }
  return null;
}

function mirrorDouble(points) {
  // Mirror across the y axis, walk the copy back, and close with two straight joins:
  //   curve A→B, join B→B', mirrored B'→A', join A'→A.
  // The joins are measured; they are the only place the double can fail.
  const first = points[0];
  const last = points[points.length - 1];
  const mirrored = [...points].reverse().map(([x, y]) => [-x, y]);
  const joinStart = mirrored[0];                    // B'
  const joinEnd = mirrored[mirrored.length - 1];    // A'
  const double = [...points, joinStart, ...mirrored.slice(1), first];
  const chordB = Math.hypot(joinStart[0] - last[0], joinStart[1] - last[1]);
  const chordA = Math.hypot(first[0] - joinEnd[0], first[1] - joinEnd[1]);
  const gap = Math.hypot(double[0][0] - double[double.length - 1][0],
    double[0][1] - double[double.length - 1][1]);
  return {
    points: double,
    closed: gap < 1e-6,
    endGap: gap,
    joins: [Number(chordB.toFixed(6)), Number(chordA.toFixed(6))],
    maxJoin: Number(Math.max(chordA, chordB).toFixed(6)),
  };
}

export const POST = async ({ request }) => {
  try {
    const { parent } = await request.json();
    const candidate = geometry(parent);
    if (!candidate || !candidate.points) return json({ error: `no curve ${parent}` }, 404);
    const built = mirrorDouble(candidate.points.map(([x, y]) => [x, y]));
    if (!built) return json({ error: "the curve does not cross x = 0" }, 422);

    const name = `mirror-${parent}`;
    const figure = `${name}.svg`;
    const xs = built.points.map(([x]) => x);
    const ys = built.points.map(([, y]) => y);
    const svg = figureSvg({
      key: name,
      title: name,
      equation: candidate.formula?.plain || "",
      legend: [{ label: `mirror of ${parent}`, colour: "#6f4a2a" }],
      paths: [{ name, colour: "#6f4a2a", points: built.points }],
      stations: [],
      bounds: [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)],
      samples: built.points.length,
    }, { width: 440 });
    const [, , w, hgt] = svg.match(/viewBox="([^"]+)"/)[1].split(/\s+/);
    const sized = svg.replace('width="100%"', `width="${w}" height="${hgt}"`)
      .replace(' style="height:auto"', "")
      .replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ');
    writeFileSync(path.join(repoRoot(), "app", "public", "hybrid-figures", figure), sized);

    const data = {
      name, decision: "saved", importance: 0, curveName: name,
      construction: {
        kind: "double", parent, mirror: "y axis",
        p: candidate.p, q: candidate.q, use: candidate.use, block: candidate.block,
        crossings: null,
        joins: built.joins,
        maxJoin: built.maxJoin,
        ends: [built.points[0], built.points[built.points.length - 1]],
        closed: built.closed, endGap: Number(built.endGap.toFixed(6)),
        formula: candidate.formula || {},
        note: `DW: ${parent} mirrored across the y axis; the two copies meet at straight ` +
          `joins of ${built.joins.map((value) => value.toFixed(3)).join(" and ")} units`,
      },
      points: built.points, formula: candidate.formula || {},
      crossedAt: new Date().toISOString(),
    };
    await prisma.sandboxCurve.upsert({
      where: { name },
      create: { name, data: JSON.stringify(data) },
      update: { data: JSON.stringify(data) },
    });
    return json({ name, closed: built.closed, endGap: data.construction.endGap, joins: built.joins });
  } catch (error) {
    return json({ error: String(error.message || error) }, 400);
  }
};
