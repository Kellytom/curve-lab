import { defineConfig } from "astro/config";
import node from "@astrojs/node";
import { fileURLToPath } from "node:url";

// The Astro app lives in app/; the curve data and plate maths stay at the repo
// root so the app and the generators keep one copy of each.
const repoRoot = fileURLToPath(new URL("..", import.meta.url));

export default defineConfig({
  output: "server",
  adapter: node({ mode: "standalone" }),
  server: { port: 4321 },
  vite: { server: { fs: { allow: [repoRoot] } } },
});
