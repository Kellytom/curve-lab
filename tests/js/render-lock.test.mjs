import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { withLock } from "../../scripts/lib/render-lock.mjs";

// Two saves can overlap (each renders in a detached child). If both write the figure index at
// once, one list wins and the other's curves vanish — register 29. The lock must serialise them.

test("two locked jobs never run at the same time", async () => {
  const dir = path.join(mkdtempSync(path.join(tmpdir(), "render-lock-")), "lock");
  let inside = 0;
  let most = 0;
  const order = [];
  const job = (name) => withLock(dir, async () => {
    inside += 1;
    most = Math.max(most, inside);
    order.push(`${name}:in`);
    await new Promise((resolve) => setTimeout(resolve, 40));
    order.push(`${name}:out`);
    inside -= 1;
  });
  await Promise.all([job("a"), job("b"), job("c")]);
  assert.equal(most, 1, "two jobs were inside the lock together");
  assert.deepEqual(order, ["a:in", "a:out", "b:in", "b:out", "c:in", "c:out"]);
});

test("a held lock is waited for and then released cleanly", async () => {
  const dir = path.join(mkdtempSync(path.join(tmpdir(), "render-lock-")), "lock");
  const first = withLock(dir, async () => { await new Promise((resolve) => setTimeout(resolve, 60)); });
  const second = withLock(dir, async () => "second ran");
  assert.equal(await second, "second ran");
  await first;
  // the directory is gone, so a third job takes the lock at once
  assert.equal(await withLock(dir, async () => "third ran"), "third ran");
});
