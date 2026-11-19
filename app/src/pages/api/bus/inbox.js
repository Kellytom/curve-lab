// GET /api/bus/inbox?for=<agent>&wait=<ms> — the unacked messages for an agent.
//
// `wait` is a long-poll: the request holds for up to 30 s and returns as soon
// as a message arrives. A wait of 0 is one read.
import { readMessages } from "./store.js";

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });

export const GET = async ({ request }) => {
  try {
    const url = new URL(request.url);
    const to = url.searchParams.get("for");
    if (!to) return json({ error: "missing ?for=agent" }, 400);
    const wait = Math.min(30000, Math.max(0, Number(url.searchParams.get("wait")) || 0));
    return json({ messages: await readMessages(to, wait) });
  } catch (error) {
    return json({ error: String(error.message || error) }, 500);
  }
};
