// Navigate in a browser check without failing on a dev-server reload.
//
// The Astro dev server reloads itself when a source file changes — another agent
// editing `app/src`, or a data write. That can abort a navigation mid-flight
// (`net::ERR_ABORTED`, "Execution context was destroyed"). It is not a page
// fault. Retry the move once; a real refusal or a real failure still throws.

const TRANSIENT = /ERR_ABORTED|Execution context was destroyed|net::ERR_CONNECTION_RESET|Timeout .* exceeded/i;

export async function gotoStable(page, url, options = {}) {
  const settings = { waitUntil: "domcontentloaded", timeout: 90000, ...options };
  let last;
  for (let attempt = 1; attempt <= 2; attempt += 1) {
    try {
      return await page.goto(url, settings);
    } catch (error) {
      last = error;
      if (attempt === 2 || !TRANSIENT.test(String(error))) throw error;
      await page.waitForTimeout(700);
    }
  }
  throw last;
}
