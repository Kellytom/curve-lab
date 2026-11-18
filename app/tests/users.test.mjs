import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import {
  createUser, findUser, readUsers, removeUser, updateUser, writeUsers,
} from "../src/lib/users.js";

function fresh() {
  return mkdtempSync(path.join(tmpdir(), "curve-lab-users-"));
}

test("create writes the record and the id comes from the name", () => {
  const dir = fresh();
  try {
    const result = createUser({ name: "Ada Lovelace", email: "ada@example.com", role: "author" }, dir);
    assert.equal(result.ok, true);
    assert.equal(result.user.id, "ada-lovelace");
    const state = readUsers(dir);
    assert.equal(state.ok, true);
    assert.equal(state.users.length, 1);
    assert.equal(findUser("ada-lovelace", dir).email, "ada@example.com");
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("a second person with the same name gets a distinct id", () => {
  const dir = fresh();
  try {
    createUser({ name: "Ada", role: "viewer" }, dir);
    const second = createUser({ name: "Ada", role: "viewer" }, dir);
    assert.equal(second.user.id, "ada-2");
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("the previous value is kept before every write", () => {
  const dir = fresh();
  try {
    createUser({ name: "One" }, dir);
    createUser({ name: "Two" }, dir);
    const backup = JSON.parse(readFileSync(path.join(dir, "users.backup.json"), "utf8"));
    assert.equal(backup.users.length, 1);
    assert.equal(backup.users[0].name, "One");
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("a damaged file is reported and never overwritten", () => {
  const dir = fresh();
  try {
    writeFileSync(path.join(dir, "users.json"), "{ not json");
    const state = readUsers(dir);
    assert.equal(state.ok, false);
    const result = createUser({ name: "Should not land" }, dir);
    assert.equal(result.ok, false);
    assert.match(result.error, /cannot be read|wrong shape/);
    assert.equal(readFileSync(path.join(dir, "users.json"), "utf8"), "{ not json");
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("an empty or invalid field is refused", () => {
  const dir = fresh();
  try {
    assert.equal(createUser({ name: "" }, dir).ok, false);
    assert.equal(createUser({ name: "Ada", email: "not-an-address" }, dir).ok, false);
    assert.equal(createUser({ name: "Ada", role: "king" }, dir).ok, false);
    assert.equal(readUsers(dir).users.length, 0);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("update keeps the id and the created date", () => {
  const dir = fresh();
  try {
    const made = createUser({ name: "Ada", role: "viewer" }, dir);
    const changed = updateUser(made.user.id, { name: "Ada L", role: "editor" }, dir);
    assert.equal(changed.ok, true);
    assert.equal(changed.user.id, made.user.id);
    assert.equal(changed.user.created, made.user.created);
    assert.equal(changed.user.role, "editor");
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("remove deletes one record and leaves the rest", () => {
  const dir = fresh();
  try {
    createUser({ name: "One" }, dir);
    createUser({ name: "Two" }, dir);
    assert.equal(removeUser("one", dir).ok, true);
    assert.deepEqual(readUsers(dir).users.map((user) => user.name), ["Two"]);
    assert.equal(removeUser("missing", dir).ok, false);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("writeUsers keeps the format stamp", () => {
  const dir = fresh();
  try {
    writeUsers([], dir);
    const parsed = JSON.parse(readFileSync(path.join(dir, "users.json"), "utf8"));
    assert.equal(parsed.format, "curve-lab.users/1");
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
