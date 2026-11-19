// The bus client: send, read, ack over HTTP + JSON.
//
//   import { send, read, ack } from "./client.mjs";
//
// The server is the Astro app. Set CURVE_LAB_BUS_URL when it is not on :4321.

const BASE = process.env.CURVE_LAB_BUS_URL || "http://127.0.0.1:4321";

async function request(path, options) {
  const response = await fetch(BASE + path, options);
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || `HTTP ${response.status}`);
  return body;
}

export async function send({ from, to, topic, body }) {
  const out = await request("/api/bus/send", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ from, to, topic, body }),
  });
  return out.id;
}

export async function read({ for: agent, wait = 0 }) {
  const out = await request(
    `/api/bus/inbox?for=${encodeURIComponent(agent)}&wait=${Number(wait) || 0}`,
  );
  return out.messages || [];
}

export async function ack(id) {
  const out = await request("/api/bus/ack", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ id }),
  });
  return out.acked;
}
