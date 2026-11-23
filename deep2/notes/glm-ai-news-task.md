# Task for GLM — the AI-news scan (2026-11-23)

*Paste this after switching the model. It is self-contained; it needs no
project context. Return the findings as a short report; do not edit any
project files.*

---

**Your task: scan the last three months of AI news and judge what matters for
one project.** Spend at most ~30 minutes and ~15 searches/fetches. Quality of
judgement beats coverage.

**The project, in one paragraph:** a private lab building *exact* mathematical
curves (integer/rational coefficients, no floating point in the record) for
ornament design — Christian iconography and plant-form ornament — rendered as
cubic Bézier spans for Inkscape, font/glyph editors and a print book. It runs
on OpenCode with two agents on a shared repo, a Python engine, a TypeScript
site, and a strict data contract. The operator is a designer, not a
mathematician; plain English always.

**What to look for, in priority order:**

1. **Models and pricing relevant to running OpenCode agents.** Any new model
   with much cheaper long-context or cached-input pricing (the bill is
   dominated by cache reads on long agent sessions). Name the price per
   million tokens for input / output / cached-read if published.
2. **Tools for curves and type.** Anything new for Bézier/spiral/PH curves,
   font or glyph design automation, Inkscape/vector extensions, or
   exact-arithmetic geometry libraries.
3. **Agent tooling.** New capabilities in OpenCode itself (or a competitor)
   that would change how a two-agent shared-repo workflow runs: compaction,
   subagents, memory, skills, notifications.
4. **Anything on constructing human figures or faces from curves** (line art,
   engraving, iconography digitisation).

**Output format** — for each finding, at most three lines:

    - **Headline** · date · source URL
      What it is, in one plain sentence.
      Relevance: <high/medium/low> — <one sentence, naming the project part it touches>.

End with: **the three things you would act on first**, and one line on what
you found *nothing* about (that is useful too). No hype words. If a claim has
no source, leave it out.
