// POST /api/tune — the desk's write for the tuning pages.
//
//   ?uid=<row>&spine=<curve>&mode=overwrite   save over this row
//   ?uid=<curve>&spine=<curve>&mode=new       save a new named version of this spine
//
// A form post lands back on the page with a message; a JSON post gets JSON. The rules
// (a unique name, a refused collision, a kept row on overwrite) are in lib/desk-tune.js.

import { DeskError, saveTune, valuesFrom } from "../../lib/desk-tune.js";

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
    const result = await saveTune({ mode, rowId, spine, curveName: raw?.curveName, values });

    if (formPost) {
      const query = new URLSearchParams({
        saved: result.created ? `saved as new: ${result.name}` : `saved ${result.name}`,
      });
      if (result.warning) query.set("warning", result.warning);
      return new Response(null, { status: 303, headers: { location: `/tune/${result.name}?${query}` } });
    }
    return json(result);
  } catch (error) {
    const status = error instanceof DeskError ? error.status : 400;
    const message = String(error.message || error);
    if (formPost) {
      const back = spine || rowId;
      return new Response(null, {
        status: 303,
        headers: { location: `/tune/${back}?${new URLSearchParams({ error: message })}` },
      });
    }
    return json({ error: message }, status);
  }
};
