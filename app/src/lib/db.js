// One Prisma client for the server process. The database is the record for
// everything a human edits; the JSON files are seed and export.
import { PrismaClient } from "@prisma/client";

// The CLI and the app read .env; a plain node test does not. One default keeps
// the read paths (the gallery, the pages) working without a second setting.
if (!process.env.DATABASE_URL) process.env.DATABASE_URL = "file:./prisma/dev.db";

const globalForPrisma = globalThis;

export const prisma = globalForPrisma.__prisma || new PrismaClient();

if (process.env.NODE_ENV !== "production") globalForPrisma.__prisma = prisma;

// WAL lets a reader and a writer work at the same time without locking the
// whole file; it is the normal mode for a small server-side SQLite database.
prisma.$executeRawUnsafe("PRAGMA journal_mode=WAL;").catch(() => {});
