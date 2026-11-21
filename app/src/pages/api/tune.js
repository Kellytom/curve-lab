// POST /api/tune — the desk's write for the tuning pages.
//
//   ?uid=<uid>&spine=<curve>&mode=overwrite   save the four values over this curve's row
//   ?uid=<curve>&spine=<curve>&mode=new       make a new curve beside its parent
//
// A form post lands back on the page with a message; a JSON post gets JSON. The rules
// (a unique name, a kept row on overwrite, a variant with its own uid) are in
// lib/desk-tune.js.

import { DeskError, createVariant, saveTune, valuesFrom } from "../../lib/desk-tune.js";

const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json" },
});

const isFormPost = (request) =>
  String(request.headers.get("content-type") || "").includes("form");

export const POST = async ({ request, url }) => {
  const mode = url.searchParams.get("mode") || "overwrite";
  const rowId = String(url.searchParams.get("uid") || "");
  const spine = String(url.searchParams.get("spine") || rowId);
  const formPost = isFormPost(request);

  try {
    let raw;
    if (formPost) {
      const form = await request.formData();
      raw = Object.fromEntries(form.entries());
    } else {
      raw = await request.json();
    }
    const values = valuesFrom(raw || {});
    const result = mode === "new"
      ? await createVariant({ spine, name: raw?.curveName, values })
      : await saveTune({ rowId, spine, values });
    const savedUid = result.uid || result.name;

    if (formPost) {
      const message = mode === "new"
        ? `saved as new: ${result.uid} ${result.name}`
        : `saved ${savedUid}`;
      const query = new URLSearchParams({ saved: message });
      if (result.warning) query.set("warning", result.warning);
      return new Response(null, { status: 303, headers: { location: `/tune/${savedUid}?${query}` } });
    }
    return json(result);
  } catch (error) {
    const status = error instanceof DeskError ? error.status : 400;
    const message = String(error.message || error);
    if (formPost) {
      return new Response(null, {
        status: 303,
        headers: { location: `/tune/${spine || rowId}?${new URLSearchParams({ error: message })}` },
      });
    }
    return json({ error: message }, status);
  }
};
