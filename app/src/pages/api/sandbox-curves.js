// GET  /api/sandbox-curves — every curve saved from the sandbox.
// POST /api/sandbox-curves — save one; the record is stored as written.

import { z } from "zod";
import { prisma } from "../../lib/db.js";
import { exportTable } from "../../lib/data-export.js";

const Curve = z.object({ name: z.string().min(1).max(120) }).passthrough();
const Payload = z.object({ curves: z.array(Curve).min(1) });

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

export const GET = async () => {
  try {
    const rows = await prisma.sandboxCurve.findMany({ orderBy: { name: "asc" } });
    return json({ curves: rows.map((row) => JSON.parse(row.data)) });
  } catch (error) {
    return json({ error: String(error.message || error) }, 500);
  }
};

export const POST = async ({ request }) => {
  try {
    const { curves } = Payload.parse(await request.json());

    // One name, one curve. A row's own name is its key; a *chosen* name (`curveName`)
    // must be unique across the table, or two candidates would promote under one name.
    const rows = await prisma.sandboxCurve.findMany();
    const taken = new Map();
    for (const row of rows) {
      let data = {};
      try { data = JSON.parse(row.data); } catch { data = {}; }
      const chosen = String(data.curveName || "").trim().toLowerCase();
      if (chosen) taken.set(chosen, row.name);
    }
    for (const curve of curves) {
      const chosen = String(curve.curveName || "").trim().toLowerCase();
      if (!chosen) continue;
      const owner = taken.get(chosen);
      if (owner && owner !== curve.name) {
        return json({ error: `name "${curve.curveName}" is already used by ${owner}` }, 409);
      }
    }
    await prisma.$transaction(curves.map((curve) => prisma.sandboxCurve.upsert({
      where: { name: curve.name },
      create: { name: curve.name, data: JSON.stringify(curve) },
      update: { data: JSON.stringify(curve) },
    })));
    // The visible record: a save writes data/sandbox-curves.json too. If the
    // write fails the save still stands, but the response says so.
    let warning;
    try {
      await exportTable("sandbox-curves");
    } catch (error) {
      warning = `saved, but the JSON copy is stale: ${String(error.message || error)}`;
    }
    return json({ saved: curves.length, ...(warning ? { warning } : {}) });
  } catch (error) {
    return json({ error: String(error.message || error) }, 400);
  }
};
