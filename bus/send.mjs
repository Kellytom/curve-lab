#!/usr/bin/env node
// Send one message.
//
//   node bus/send.mjs --from deepseek1 --to deepseek2 --topic job --body '{"text":"hello"}'
//
// Prints the message id on success.

import { send } from "./client.mjs";

const args = process.argv.slice(2);
const get = (name, fallback) => {
  const at = args.indexOf(`--${name}`);
  return at >= 0 && at + 1 < args.length ? args[at + 1] : fallback;
};

const from = get("from");
const to = get("to");
const topic = get("topic", "job");
const raw = get("body", "{}");

if (!from || !to) {
  console.error("usage: node bus/send.mjs --from <agent> --to <agent> --topic <topic> --body '<json>'");
  process.exit(2);
}

let body;
try {
  body = JSON.parse(raw);
} catch (error) {
  console.error(`body is not JSON: ${error.message}`);
  process.exit(2);
}

const id = await send({ from, to, topic, body });
console.log(id);
