// GET  /api/curve-notes — every name and rating a human has set.
// POST /api/curve-notes — merge one or more {uid, name, importance} rows.

import { readNotes, saveNotes } from "../../lib/curve-notes.js";

const base = () => process.env.CURVE_LAB_ROOT || process.cwd();
const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });

export const GET = async () => {
  try {
    return json({ format: "curve-lab.curve-notes/1", ...readNotes(base()) });
  } catch (error) {
    return json({ error: String(error.message || error) }, 500);
  }
};

export const POST = async ({ request }) => {
  try {
    const payload = await request.json();
    return json(await saveNotes(payload, base()));
  } catch (error) {
    return json({ error: String(error.message || error) }, error.status || 400);
  }
};
