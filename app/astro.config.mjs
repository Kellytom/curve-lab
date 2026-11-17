import { defineConfig } from "astro/config";
import node from "@astrojs/node";
import { fileURLToPath } from "node:url";

// The Astro app lives in app/; the curve data and plate maths stay at the repo
// root so the app and the generators keep one copy of each.
const repoRoot = fileURLToPath(new URL("..", import.meta.url));

// Vite refuses a request whose Host it does not know. A Cloudflare tunnel
// (docs/TUNNEL.md) sends the tunnel hostname, so it is allowed here, plus any
// extra host named in CURVE_LAB_HOSTS.
const extraHosts = (process.env.CURVE_LAB_HOSTS || "")
  .split(",").map((host) => host.trim()).filter(Boolean);

export default defineConfig({
  output: "server",
  adapter: node({ mode: "standalone" }),
  server: { port: 4321 },
  // The dev toolbar (Menu / Inspect / Audit / Settings) is a dev-only overlay.
  // Every hub preview is an iframe, so one toolbar became a row of them; the
  // work is done from the command line, so it is off.
  devToolbar: { enabled: false },
  vite: { server: { fs: { allow: [repoRoot] },
    allowedHosts: [".trycloudflare.com", ...extraHosts] } },
});
