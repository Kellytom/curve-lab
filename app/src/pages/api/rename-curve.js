// POST /api/rename-curve?uid=<uid>  { name }  (or a form field `rename`)
//
// Rename a curve. The uid and the geometry stay; the name changes everywhere it is a key:
// the registry seed, the database rows, the exports and the figure's label. The old name is
// kept as an alias. A collision is refused with the owner named — a name is never silently
// suffixed.
//
// A form post lands back on the tuning page with a message; a JSON post gets JSON.

import { DeskError, renameCurve } from "../../lib/desk-tune.js";

const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json" },
});

const isFormPost = (request) =>
  String(request.headers.get("content-type") || "").includes("form");

export const POST = async ({ request, url }) => {
  const uid = String(url.searchParams.get("uid") || "");
  const formPost = isFormPost(request);
  try {
    const raw = formPost
      ? Object.fromEntries((await request.formData()).entries())
      : await request.json().catch(() => ({}));
    const name = raw?.rename ?? raw?.name ?? "";
    const result = await renameCurve({ uid, name });
    if (formPost) {
      const message = `renamed to ${result.name}`;
      const query = new URLSearchParams({ saved: message });
      if (result.warning) query.set("warning", result.warning);
      return new Response(null, {
        status: 303, headers: { location: `/tune/${uid}?${query}` },
      });
    }
    return json(result);
  } catch (error) {
    const status = error instanceof DeskError ? error.status : 400;
    const message = String(error.message || error);
    if (formPost) {
      return new Response(null, {
        status: 303,
        headers: { location: `/tune/${uid}?${new URLSearchParams({ error: message })}` },
      });
    }
    return json({ error: message }, status);
  }
};
