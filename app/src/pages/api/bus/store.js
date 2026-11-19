// The bus data layer: one row per message, SQLite through Prisma.
//
// The body is JSON text in the row and is validated before it is written. An
// unacked row is the inbox; an acked row stays as history. Ordering per
// (fromAgent, toAgent) is the row id.

import { z } from "zod";
import { prisma } from "../../../lib/db.js";

const Message = z.object({
  from: z.string().min(1).max(40),
  to: z.string().min(1).max(40),
  topic: z.string().min(1).max(80),
  body: z.any(),
});

export function validateMessage(payload) {
  return Message.parse(payload);
}

export async function sendMessage(payload) {
  const { from, to, topic, body } = validateMessage(payload);
  const row = await prisma.message.create({
    data: {
      fromAgent: from,
      toAgent: to,
      topic,
      body: JSON.stringify(body),
    },
  });
  return { id: row.id };
}

export async function readMessages(toAgent, waitMs = 0) {
  const deadline = Date.now() + Math.max(0, waitMs);
  for (;;) {
    const rows = await prisma.message.findMany({
      where: { toAgent, ackedAt: null },
      orderBy: { id: "asc" },
    });
    if (rows.length) {
      await prisma.$transaction(rows.map((row) => prisma.message.update({
        where: { id: row.id },
        data: { attempts: { increment: 1 } },
      })));
      return rows.map((row) => ({
        id: row.id,
        from: row.fromAgent,
        to: row.toAgent,
        topic: row.topic,
        body: JSON.parse(row.body),
        createdAt: row.createdAt,
        attempts: row.attempts + 1,
      }));
    }
    if (Date.now() >= deadline) return [];
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
}

export async function ackMessage(id) {
  const result = await prisma.message.updateMany({
    where: { id: Number(id), ackedAt: null },
    data: { ackedAt: new Date() },
  });
  return { acked: result.count > 0 };
}
