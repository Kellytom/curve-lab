import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import path from "node:path";
import test from "node:test";

const ROOT = path.resolve(import.meta.dirname, "../..");

test("the repo root is found from any working directory", () => {
  // The built server was started from app/ and from the repo root; the second
  // resolved one level too high, so /names and /illuminations answered 500 with
  // a path of /Users/<name>/developer/workbench/curve-registry.json.
  const script = `import { repoRoot } from ${JSON.stringify(path.join(ROOT, "app/src/lib/gallery.js"))}; console.log(repoRoot());`;
  for (const cwd of [ROOT, path.join(ROOT, "app"), "/"]) {
    const out = execFileSync(process.execPath, ["--input-type=module", "-e", script], {
      cwd,
      env: { ...process.env, CURVE_LAB_ROOT: "" },
      encoding: "utf8",
    }).trim();
    assert.equal(out, ROOT, `from ${cwd}`);
  }
});
