// GET  /api/finder-stars — the current list and its hash.
// POST /api/finder-stars — save the finder's starred curves to
// workbench/finder-stars.json. The logic is src/lib/finder-stars.js so a Next
// or Hono route can reuse it.

import { readFinderStars, saveFinderStars } from "../../lib/finder-stars.js";

const base = () => process.env.CURVE_LAB_ROOT || process.cwd();
const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });

export const GET = async () => {
  try {
    return json({ format: "curve-lab.finder-stars/1", ...(await readFinderStars()) });
  } catch (error) {
    return json({ error: String(error.message || error) }, 500);
  }
};

export const POST = async ({ request }) => {
  try {
    const payload = await request.json();
    const result = await saveFinderStars(payload, base());
    return json(result);
  } catch (error) {
    return json({ error: String(error.message || error) }, error.status || 400);
  }
};
