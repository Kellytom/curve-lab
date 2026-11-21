// POST /api/curve-stars — store a curve's star rating (0 = none, 1..10).
//
// The rating is the note's `importance`, the value every page reads through
// loadRegistry. It is one transaction and then the JSON copy; a bad uid or rating
// is refused before a row is written.

import { z } from "zod";
import { prisma } from "../../lib/db.js";
import { exportTable } from "../../lib/data-export.js";

const Payload = z.object({
  uid: z.string().regex(/^[a-z0-9-]+$/).max(40),
  stars: z.number().int().min(0).max(10),
});

const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json" },
});

export const POST = async ({ request }) => {
  try {
    const { uid, stars } = Payload.parse(await request.json());
    const note = await prisma.note.findUnique({ where: { uid } });
    if (!note) return json({ error: `${uid} has no note to rate` }, 404);
    await prisma.note.update({ where: { uid }, data: { importance: stars } });
    let warning;
    try {
      await exportTable("curves");
    } catch (error) {
      warning = `stars saved, but the JSON copy is stale: ${String(error.message || error)}`;
    }
    return json({ uid, stars, ...(warning ? { warning } : {}) });
  } catch (error) {
    return json({ error: String(error.message || error) }, 400);
  }
};
