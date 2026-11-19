// POST /api/bus/send — store one message and return its id.
import { sendMessage } from "./store.js";

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });

export const POST = async ({ request }) => {
  try {
    return json(await sendMessage(await request.json()));
  } catch (error) {
    return json({ error: String(error.message || error) }, error.status || 400);
  }
};
