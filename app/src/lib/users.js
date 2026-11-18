import { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import path from "node:path";
import { z } from "zod";

// A user record, not a login. There are no passwords here: this is a directory
// the lab can read, and authentication is a separate, deliberate step.
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

export const FORMAT = "curve-lab.users/1";

export function dataDir(base) {
  return base || process.env.CURVE_LAB_DATA || path.join(process.cwd(), "data");
}

function storePath(base) {
  return path.join(dataDir(base), "users.json");
}

// A failed read is never an empty list: the caller is told, and no write follows.
export function readUsers(base) {
  const file = storePath(base);
  if (!existsSync(file)) return { ok: true, users: [] };
  try {
    const parsed = JSON.parse(readFileSync(file, "utf8"));
    if (parsed?.format !== FORMAT || !Array.isArray(parsed.users)) {
      return { ok: false, users: [], error: "users.json has the wrong shape" };
    }
    return { ok: true, users: parsed.users };
  } catch (error) {
    return { ok: false, users: [], error: `users.json cannot be read: ${error.message}` };
  }
}

// Every write keeps the previous value, so a bad edit can be undone by hand.
export function writeUsers(users, base) {
  const dir = dataDir(base);
  mkdirSync(dir, { recursive: true });
  const file = path.join(dir, "users.json");
  if (existsSync(file)) writeFileSync(path.join(dir, "users.backup.json"), readFileSync(file));
  const tmp = `${file}.tmp`;
  writeFileSync(tmp, `${JSON.stringify({ format: FORMAT, users }, null, 2)}\n`);
  renameSync(tmp, file);
}

function slug(name) {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40) || "user";
}

function uniqueId(name, users) {
  const stem = slug(name);
  let id = stem;
  let n = 2;
  while (users.some((user) => user.id === id)) id = `${stem}-${n++}`;
  return id;
}

export function createUser(input, base) {
  const state = readUsers(base);
  if (!state.ok) return { ok: false, error: state.error };
  let user;
  try {
    user = userSchema.parse(input);
  } catch (error) {
    return { ok: false, error: error.issues[0]?.message || "check the fields" };
  }
  const record = {
    id: uniqueId(user.name, state.users),
    name: user.name,
    email: user.email || "",
    role: user.role,
    notes: user.notes || "",
    created: new Date().toISOString(),
  };
  writeUsers([...state.users, record], base);
  return { ok: true, user: record };
}

export function updateUser(id, input, base) {
  const state = readUsers(base);
  if (!state.ok) return { ok: false, error: state.error };
  const index = state.users.findIndex((user) => user.id === id);
  if (index < 0) return { ok: false, error: "no user with that id" };
  let user;
  try {
    user = userSchema.parse(input);
  } catch (error) {
    return { ok: false, error: error.issues[0]?.message || "check the fields" };
  }
  const record = {
    ...state.users[index],
    name: user.name,
    email: user.email || "",
    role: user.role,
    notes: user.notes || "",
    updated: new Date().toISOString(),
  };
  const users = [...state.users];
  users[index] = record;
  writeUsers(users, base);
  return { ok: true, user: record };
}

export function removeUser(id, base) {
  const state = readUsers(base);
  if (!state.ok) return { ok: false, error: state.error };
  const users = state.users.filter((user) => user.id !== id);
  if (users.length === state.users.length) return { ok: false, error: "no user with that id" };
  writeUsers(users, base);
  return { ok: true };
}

export function findUser(id, base) {
  const state = readUsers(base);
  return state.users.find((user) => user.id === id) || null;
}
