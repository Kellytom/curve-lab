import { defineConfig } from "astro/config";
import node from "@astrojs/node";
import starlight from "@astrojs/starlight";
import { fileURLToPath } from "node:url";

// The Astro app lives in app/; the curve data and plate maths stay at the repo
// root so the app and the generators keep one copy of each.
const repoRoot = fileURLToPath(new URL("..", import.meta.url));

// Vite refuses a request whose Host it does not know. A Cloudflare tunnel
// (the tunnel page in the book) sends the tunnel hostname, so it is allowed
// here, plus any extra host named in CURVE_LAB_HOSTS.
const extraHosts = (process.env.CURVE_LAB_HOSTS || "")
  .split(",").map((host) => host.trim()).filter(Boolean);

// The book: Starlight renders the Markdown under src/content/docs/docs at
// /docs/. The order below is the reading order, not the file order.
const sidebar = [
  {
    label: "Start here",
    items: [
      "docs",
      "docs/concepts",
      "docs/worked-example",
      "docs/state-of-the-work",
      "docs/structure",
      "docs/verify",
      "docs/fidelity",
    ],
  },
  {
    label: "The engine",
    items: [
      "docs/architecture",
      "docs/curve-model",
      "docs/curvature-power-curves",
      "docs/ph-integer",
      "docs/integer-cubic",
      "docs/g3-showcase-docs",
      "docs/pythagorean-families",
      "docs/spine",
      "docs/glossary",
      "docs/self-intersection-references",
      "docs/web-guide",
      "docs/hub",
    ],
  },
  {
    label: "Design",
    items: [
      "docs/philosophy",
      "docs/clearance",
      "docs/junction",
      "docs/primal",
      "docs/caps",
      "docs/clothoid-grid-3125",
    ],
  },
  {
    label: "Record",
    items: [
      "docs/corpus",
      "docs/handover",
      "docs/credits",
      "docs/project",
      "docs/todo",
      "docs/web",
    ],
  },
  {
    label: "Reviews",
    items: ["docs/review", "docs/ph-quintic-review"],
  },
  {
    label: "Operations",
    items: ["docs/tunnel"],
  },
];

export default defineConfig({
  output: "server",
  adapter: node({ mode: "standalone" }),
  server: { port: 4321 },
  // The dev toolbar (Menu / Inspect / Audit / Settings) is a dev-only overlay.
  // Every hub preview is an iframe, so one toolbar became a row of them; the
  // work is done from the command line, so it is off.
  devToolbar: { enabled: false },
  integrations: [
    starlight({
      title: "curve-lab",
      description:
        "Exact integer and Euler curves for ornament: a Python engine, a browser lab, and an Astro app.",
      sidebar,
      social: [
        { icon: "github", label: "GitHub", href: "https://github.com/Kellytom/curve-lab" },
      ],
      editLink: {
        baseUrl: "https://github.com/Kellytom/curve-lab/edit/main/app/",
      },
    }),
  ],
  vite: { server: { fs: { allow: [repoRoot] },
    allowedHosts: [".trycloudflare.com", ...extraHosts] } },
});
