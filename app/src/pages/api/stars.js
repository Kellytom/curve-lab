// POST /api/stars — save the lab's stars to workbench/starred.json.
// The logic is src/lib/stars.js so a Next or Hono route can reuse it.

import { saveStars } from "../../lib/stars.js";

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
