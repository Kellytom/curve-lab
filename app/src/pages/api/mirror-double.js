// POST /api/mirror-double  { parent }
//
// Cuts the curve where it crosses y = x and mirrors it — the wonk rule — using the diagonal
// basis, which is exact up to one scale:
//
//     u = x + y,   v = y − x        (length √2 times the original)
//
// In that basis the line y = x is v = 0, so the curve is cut and mirrored on a horizontal
// axis and turned back with x = (u − v)/2, y = (u + v)/2. Every join point lies on y = x, so
// the ends meet exactly. A curve that never crosses y = x falls back to the y-axis mirror and
// reports the two chords it needs.

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

const toDiagonal = ([x, y]) => [x + y, y - x];
const fromDiagonal = ([u, v]) => [(u - v) / 2, (u + v) / 2];

function mirrorDouble(points) {
  const diag = points.map(toDiagonal);
  const nodes = [];
  diag.forEach((point, index) => {
    nodes.push({ pos: index, point, cut: false });
    const next = diag[index + 1];
    if (next && (point[1] >= 0) !== (next[1] >= 0)) {
      const t = point[1] !== next[1] ? point[1] / (point[1] - next[1]) : 0;
      nodes.push({ pos: index + 0.5, cut: true, point: [point[0] + (next[0] - point[0]) * t, 0] });
    }
  });
  nodes.sort((a, b) => a.pos - b.pos);
  const cuts = nodes.map((node, index) => (node.cut ? index : -1)).filter((index) => index >= 0);

  if (cuts.length >= 2) {
    const arcs = [];
    for (let k = 0; k < cuts.length; k += 1) {
      const start = cuts[k];
      const end = cuts[(k + 1) % cuts.length];
      const arc = end > start
        ? nodes.slice(start, end + 1).map((node) => node.point)
        : [...nodes.slice(start).map((node) => node.point),
           ...nodes.slice(0, end + 1).map((node) => node.point)];
      if (arc.length > 2) arcs.push(arc);
    }
    const length = (arc) => arc.reduce((sum, p, i) =>
      (i ? sum + Math.hypot(p[0] - arc[i - 1][0], p[1] - arc[i - 1][1]) : 0), 0);
    arcs.sort((a, b) => length(b) - length(a));
    const half = arcs[0];
    const mirrored = [...half].reverse().map(([u, v]) => [u, -v]);
    const double = [...half, ...mirrored.slice(1)].map(fromDiagonal);
    const gap = Math.hypot(double[0][0] - double[double.length - 1][0],
      double[0][1] - double[double.length - 1][1]);
    return { points: double, closed: gap < 1e-6, endGap: gap, joins: [0, 0], maxJoin: 0,
      basis: "diagonal", scale: "√2" };
  }

  const first = points[0];
  const last = points[points.length - 1];
  const back = [...points].reverse().map(([x, y]) => [-x, y]);
  const double = [...points, back[0], ...back.slice(1), first];
  const chordB = Math.hypot(back[0][0] - last[0], back[0][1] - last[1]);
  const chordA = Math.hypot(first[0] - back[back.length - 1][0], first[1] - back[back.length - 1][1]);
  const gap = Math.hypot(double[0][0] - double[double.length - 1][0],
    double[0][1] - double[double.length - 1][1]);
  return { points: double, closed: gap < 1e-6, endGap: gap,
    joins: [Number(chordB.toFixed(6)), Number(chordA.toFixed(6))],
    maxJoin: Number(Math.max(chordA, chordB).toFixed(6)), basis: "y axis" };
}

export const POST = async ({ request }) => {
  try {
    const { parent } = await request.json();
    const candidate = geometry(parent);
    if (!candidate || !candidate.points) return json({ error: `no curve ${parent}` }, 404);
    const built = mirrorDouble(candidate.points.map(([x, y]) => [x, y]));
    if (!built) return json({ error: "could not mirror the curve" }, 422);

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
        kind: "double", parent, mirror: built.basis,
        p: candidate.p, q: candidate.q, use: candidate.use, block: candidate.block,
        ends: [built.points[0], built.points[built.points.length - 1]],
        closed: built.closed, endGap: Number(built.endGap.toFixed(6)),
        joins: built.joins, maxJoin: built.maxJoin,
        formula: candidate.formula || {},
        note: built.basis === "diagonal"
          ? `DW: ${parent} cut where it crosses y = x and mirrored, in the diagonal basis ` +
            `u = x + y, v = y - x (exact up to the scale √2); the ends meet on the line`
          : `DW: ${parent} mirrored across the y axis; the copies meet at joins of ` +
            `${built.joins.map((value) => value.toFixed(3)).join(" and ")} units`,
      },
      points: built.points, formula: candidate.formula || {},
      crossedAt: new Date().toISOString(),
    };
    await prisma.sandboxCurve.upsert({
      where: { name },
      create: { name, data: JSON.stringify(data) },
      update: { data: JSON.stringify(data) },
    });
    return json({ name, basis: built.basis, closed: built.closed, joins: built.joins });
  } catch (error) {
    return json({ error: String(error.message || error) }, 400);
  }
};
