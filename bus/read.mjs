#!/usr/bin/env node
// Read an agent's inbox, or acknowledge one message.
//
//   node bus/read.mjs --for deepseek2
//   node bus/read.mjs --for deepseek2 --wait 25000
//   node bus/read.mjs --ack 42
//
// `--wait` long-polls the server, so it blocks rather than spins. Each message
// is printed as one JSON line.

import { ack, read } from "./client.mjs";

const args = process.argv.slice(2);
const get = (name, fallback) => {
  const at = args.indexOf(`--${name}`);
  return at >= 0 && at + 1 < args.length ? args[at + 1] : fallback;
};

const forAgent = get("for");
const ackId = get("ack");

if (ackId) {
  const ok = await ack(Number(ackId));
  console.log(ok ? `acked ${ackId}` : `not acked: ${ackId}`);
  process.exit(ok ? 0 : 1);
}

if (!forAgent) {
  console.error("usage: node bus/read.mjs --for <agent> [--wait <ms>] [--ack <id>]");
  process.exit(2);
}

const wait = Number(get("wait", "0")) || 0;
const messages = await read({ for: forAgent, wait });
if (!messages.length) {
  console.log("no messages");
  process.exit(0);
}
for (const message of messages) console.log(JSON.stringify(message));
