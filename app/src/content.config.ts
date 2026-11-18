import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";
import { docsLoader } from "@astrojs/starlight/loaders";
import { docsSchema } from "@astrojs/starlight/schema";

// The prose book lives in app/src/content/docs/docs, so every page is served
// under /docs/. The Markdown files are the source; Starlight renders them.
const docs = defineCollection({ loader: docsLoader(), schema: docsSchema() });

// A blog, framed but empty. A new file in src/content/blog is a new note.
// Files whose name starts with an underscore are ignored, so _README.md can
// explain the folder without becoming a post.
const blog = defineCollection({
  loader: glob({ pattern: "[!_]*.md", base: "./src/content/blog" }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    date: z.coerce.date(),
    draft: z.boolean().default(true),
  }),
});

export const collections = { docs, blog };
