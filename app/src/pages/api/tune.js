// POST /api/tune?uid=c-0001  — save the four character values and re-render that plate.
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const run = promisify(execFile);
import path from "node:path";
import { repoRoot } from "../../lib/gallery.js";
import { prisma } from "../../lib/db.js";

const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json" },
});

export const POST = async ({ request, url }) => {
  try {
    const uid = String(url.searchParams.get("uid") || "");
    if (!/^[a-z0-9-]+$/.test(uid)) return json({ error: "bad uid" }, 400);
    const form = await request.formData();
    const data = {
      widthPct: Number(form.get("widthPct") || 6),
      plus: Number(form.get("plus") || 2),
      minus: Number(form.get("minus") || 2),
      profile: String(form.get("profile") || "bow"),
      transform: { degrees: Number(form.get("degrees") || 0) },
      tune: true,
    };
    await prisma.sandboxCurve.upsert({
      where: { name: uid },
      create: { name: uid, data: JSON.stringify(data) },
      update: { data: JSON.stringify(data) },
    });
    // render before redirecting: the page you land on shows the plate that was just made
    await run(process.execPath, [path.join(repoRoot(), "scripts", "print_plates.mjs"), "--only", uid],
      { cwd: repoRoot(), timeout: 120000 });
    return new Response(null, { status: 303, headers: { location: `/tune/${uid}?saved=1` } });
  } catch (error) {
    return json({ error: String(error.message || error) }, 400);
  }
};
