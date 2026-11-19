// GET  /api/sandbox-curves — every curve saved from the sandbox.
// POST /api/sandbox-curves — save one; the record is stored as written.

import { z } from "zod";
import { prisma } from "../../lib/db.js";

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
    await prisma.$transaction(curves.map((curve) => prisma.sandboxCurve.upsert({
      where: { name: curve.name },
      create: { name: curve.name, data: JSON.stringify(curve) },
      update: { data: JSON.stringify(curve) },
    })));
    return json({ saved: curves.length });
  } catch (error) {
    return json({ error: String(error.message || error) }, 400);
  }
};
