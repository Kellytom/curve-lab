// POST /api/bus/ack — mark one message as acknowledged.
import { ackMessage } from "./store.js";

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });

export const POST = async ({ request }) => {
  try {
    const { id } = await request.json();
    return json(await ackMessage(id));
  } catch (error) {
    return json({ error: String(error.message || error) }, 400);
  }
};
