// The bus: the envelope is validated, an unacked message is redelivered, an
// acked one is gone, and two messages keep their send order.

import { test, after } from "node:test";
import assert from "node:assert/strict";
import {
  sendMessage, readMessages, ackMessage, validateMessage,
} from "../src/pages/api/bus/store.js";
import { prisma } from "../src/lib/db.js";

const FROM = "bus-test";
const TO = `bus-test-${Date.now()}`;

after(async () => {
  await prisma.message.deleteMany({ where: { toAgent: TO } });
  await prisma.$disconnect();
});

test("the envelope is validated before storage", () => {
  assert.throws(() => validateMessage({ from: "", to: TO, topic: "t", body: {} }));
  assert.throws(() => validateMessage({ from: FROM, to: TO, topic: "", body: {} }));
});

test("a message is delivered, redelivered until acked, then gone", async () => {
  const { id } = await sendMessage({ from: FROM, to: TO, topic: "job", body: { text: "hello" } });
  assert.ok(id > 0);

  const first = await readMessages(TO, 0);
  assert.equal(first.length, 1);
  assert.equal(first[0].id, id);
  assert.deepEqual(first[0].body, { text: "hello" });

  const again = await readMessages(TO, 0);
  assert.equal(again.length, 1, "an unacked message is redelivered");
  assert.ok(again[0].attempts >= 2);

  const acked = await ackMessage(id);
  assert.equal(acked.acked, true);
  const afterAck = await readMessages(TO, 0);
  assert.equal(afterAck.length, 0, "an acked message is not redelivered");
});

test("two messages keep their send order", async () => {
  const one = await sendMessage({ from: FROM, to: TO, topic: "job", body: { n: 1 } });
  const two = await sendMessage({ from: FROM, to: TO, topic: "job", body: { n: 2 } });
  const messages = await readMessages(TO, 0);
  assert.deepEqual(messages.map((message) => message.id), [one.id, two.id]);
  for (const message of messages) await ackMessage(message.id);
});
