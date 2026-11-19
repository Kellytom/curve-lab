// GET  /api/stars — the starred plates from the database.
// POST /api/stars — save them; workbench/starred.json is written as an export.
// The logic is src/lib/stars.js so a Next or Hono route can reuse it.

import { readStars, saveStars } from "../../lib/stars.js";

export const GET = async () => {
  try {
    return new Response(JSON.stringify({ format: "starred/1", ...(await readStars()) }), {
      status: 200, headers: { "content-type": "application/json" },
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: String(error.message || error) }), { status: 500 });
  }
};

export const POST = async ({ request }) => {
  try {
    const payload = await request.json();
    const result = await saveStars(payload, process.env.CURVE_LAB_ROOT || process.cwd());
    return new Response(JSON.stringify(result), {
      status: 200,
      headers: { "content-type": "application/json" },
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: String(error.message || error) }), {
      status: 400,
      headers: { "content-type": "application/json" },
    });
  }
};
