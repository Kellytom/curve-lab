import assert from "node:assert/strict";
import test from "node:test";
import { ROLES, userSchema } from "../src/lib/users.js";

test("a name is required, and the role is one of the three", () => {
  assert.throws(() => userSchema.parse({ name: "" }));
  assert.throws(() => userSchema.parse({ name: "Ada", role: "king" }));
  for (const role of ROLES) assert.equal(userSchema.parse({ name: "Ada", role }).role, role);
});

test("an empty address is allowed; a malformed one is not", () => {
  assert.equal(userSchema.parse({ name: "Ada", email: "" }).email, undefined);
  assert.throws(() => userSchema.parse({ name: "Ada", email: "not-an-address" }));
  assert.equal(userSchema.parse({ name: "Ada", email: "ada@example.com" }).email, "ada@example.com");
});
