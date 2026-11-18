// POST /api/finder-stars — save the finder's starred curves to
// workbench/finder-stars.json. The logic is src/lib/finder-stars.js so a Next
// or Hono route can reuse it.

import { saveFinderStars } from "../../lib/finder-stars.js";

export const POST = async ({ request }) => {
  try {
    const payload = await request.json();
    const result = await saveFinderStars(payload, process.env.CURVE_LAB_ROOT || process.cwd());
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
