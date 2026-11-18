// The user directory, in SQLite through Prisma. A record, not a login: there is
// no password field. The id is derived from the name and stays fixed on rename.

import { z } from "zod";
import { prisma } from "./db.js";

export const ROLES = ["author", "editor", "viewer"];

export const userSchema = z.object({
  name: z.string().trim().min(1, "a name is required").max(80),
  email: z.preprocess(
    (value) => (value === "" || value == null ? undefined : value),
    z.string().trim().email("that is not an email address").max(200).optional(),
  ),
  role: z.enum(ROLES).default("viewer"),
  notes: z.preprocess(
    (value) => (value === "" || value == null ? undefined : value),
    z.string().trim().max(500).optional(),
  ),
});

function slug(name) {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40) || "user";
}

async function uniqueId(name) {
  const stem = slug(name);
  let id = stem;
  let n = 2;
  while (await prisma.user.findUnique({ where: { id } })) id = `${stem}-${n++}`;
  return id;
}

export async function readUsers() {
  const users = await prisma.user.findMany({ orderBy: { created: "asc" } });
  return { ok: true, users };
}

export async function findUser(id) {
  return prisma.user.findUnique({ where: { id } });
}

export async function createUser(input) {
  let user;
  try { user = userSchema.parse(input); } catch (error) {
    return { ok: false, error: error.issues[0]?.message || "check the fields" };
  }
  const record = await prisma.user.create({
    data: {
      id: await uniqueId(user.name),
      name: user.name,
      email: user.email || null,
      role: user.role,
      notes: user.notes || null,
    },
  });
  return { ok: true, user: record };
}

export async function updateUser(id, input) {
  let user;
  try { user = userSchema.parse(input); } catch (error) {
    return { ok: false, error: error.issues[0]?.message || "check the fields" };
  }
  const existing = await prisma.user.findUnique({ where: { id } });
  if (!existing) return { ok: false, error: "no user with that id" };
  const record = await prisma.user.update({
    where: { id },
    data: {
      name: user.name,
      email: user.email || null,
      role: user.role,
      notes: user.notes || null,
    },
  });
  return { ok: true, user: record };
}

export async function removeUser(id) {
  const existing = await prisma.user.findUnique({ where: { id } });
  if (!existing) return { ok: false, error: "no user with that id" };
  await prisma.user.delete({ where: { id } });
  return { ok: true };
}
