import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { figureFor } from "../../app/src/lib/bordered.js";

// The operator, 2026-11-24: c-0022 "looks wrong ... before any trimming".
// A rows record stores its two speed rows and no path. `branchesOf` reads only a
// path, so the central design came back empty, `half[0]` threw, and the catch
// drew the bare half-curve. The old diamond figure is the curve and its mirror.

const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url), "utf8")) as {
  curves: Array<Record<string, unknown> & { uid: string }>;
};
const byUid = new Map(registry.curves.map((row) => [row.uid, row]));

test("c-0022's rows record gets its leaf, not the error fallback", () => {
  const figure = figureFor(byUid.get("c-0022"));
  assert.equal(figure.failed, false, figure.reason);
  assert.equal(figure.centralCount, 2, "the rows curve and its mirror");
});

test("the figure index no longer carries a failed record", () => {
  const index = JSON.parse(readFileSync(new URL("../../app/public/figures/index.json", import.meta.url), "utf8")) as {
    curves: Array<{ failed?: boolean; uid: string; reason?: string }>;
  };
  const failed = index.curves.filter((row) => row.failed);
  assert.deepEqual(failed.map((row) => `${row.uid}: ${row.reason}`), []);
});
