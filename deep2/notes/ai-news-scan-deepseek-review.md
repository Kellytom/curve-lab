# AI-news scan — DeepSeek review

*Run 2026-11-23 13:22 on `deepseek-v4.1-flash`, not GLM: `opencode run` ignored the agent file's `model:` line. Kept as the baseline the GLM pass is compared against. 12 searches, ~10 min. Sources are the scan's own; not re-verified here.*

---

I'll start by checking what browsing/search tools are available, then run a focused scan.
# Scan: 23 Aug – 23 Nov 2026, for the exact-curve ornament lab

Budget note: 12 tool calls, ~10 searches plus one direct page read of DeepSeek's pricing.

## 1. Models and pricing for OpenCode agents

- **DeepSeek V4.1 Flash — the model running this session — has the cheapest cache reads of anything I found** · price list read 23 Nov · https://api-docs.deepseek.com/quick_start/pricing
  Per million tokens, off-peak: cache hit $0.003, cache miss $0.15, output $0.60. Peak (01:00–04:00 and 06:00–10:00 UTC, Mon–Fri) doubles all three. 1M context, 384K max output.
  Relevance: **high** — this is the baseline your bill is already built on; a cache read here costs 3,000× less than Opus 5.5's.

- **DeepSeek moved search and fetch from per-call billing into tokens** · 18 Nov · https://api-docs.deepseek.com/quick_start/pricing
  Hosted search/fetch was $0.75 per 1,000 calls. From 18 Nov, tool calls triggered by the model are free and their results are billed as normal input. The separate Search/Fetch API is still $0.75 per 1,000.
  Relevance: **medium** — agent sessions that read sources now show up in the token line, which changes how you read `opencode stats`.

- **Claude Fable 5.2 launched 20% cheaper, with cache reads at 2.5% of input** · 9 Nov · https://www.datastudios.org/post/ai-api-pricing-this-week-claude-fable-5-2-gemini-4-hydrogen-muse-ember
  $8 input / $40 output / $0.20 cache read. Cache write $10 for 5 minutes, $16 for 1 hour. Batch is half. Fable 5.1 was $10/$50.
  Relevance: **medium** — a high-ceiling model whose cache read is 67× your current one; only worth it if a task really fails on Flash.

- **GPT-6.2 Sol: $2 / $10 / $0.10 and a 1.05M window, with a penalty above 272K** · 17 Nov · https://apidog.com/blog/gpt-6-2-astra-pricing/
  Sol and Astra share the same window, output cap and tools. Above 272K input tokens, input and cache rates double and output rises 1.5× for the whole request. Astra is $8/$40/$0.40.
  Relevance: **medium** — Sol is the obvious mid-tier alternative, but the 272K cliff punishes exactly the long sessions you run.

- **Gemini 4 Hydrogen: one flat rate across a 1M window** · 12 Nov · https://www.requesty.ai/blog/gemini-api-pricing
  $1.50 input / $7.50 output / $0.075 cached read, flat to 1,048,576 tokens. No long-context step. Note: Gemini 4 Carbon doubles to $4/$20 on 1 Dec, and 3.8 Flash doubles on 1 Jan 2027.
  Relevance: **high** — flat pricing to 1M is the only offering here with no cliff, so it is the safe pick for the deepest sessions.

- **Muse Ember: $0.10 / $0.50 / $0.004, but the threshold is low** · 9 Nov · https://marginaltoken.com/notes/ai-model-releases-2026-11-09/
  Cheapest new model. Up to 200K input tokens. Above that, every rate triples for the whole request, cache reads included.
  Relevance: **low** — cheap for short mechanical passes over the curve table; unusable for a long editor session.

- **Haiku 5.5 cache reads cost $0.01, or $0.05 once the prompt passes 100K** · pricing as of 16 Nov · https://www.requesty.ai/blog/claude-api-pricing
  $0.10 input / $0.50 output under 100K prompt tokens; $0.50 / $2.50 above. Cache write is $0.125.
  Relevance: **medium** — a cheap summariser or checker, but the 100K step lands in the middle of your sessions.

- **Qwen4-Max: $1.50 / $4.50 / $0.075 with explicit 1-hour caching** · 16 Nov · https://www.maximem.ai/blog/qwen-api-pricing-2026
  Flat across a 1M input range, same price with thinking on or off. Cache hit is 5% of input.
  Relevance: **low** — a fourth flat-price option; nothing about it touches your problem specifically.

## 2. Curves, type and exact arithmetic

- **csgrs now reads SVG path numbers as exact decimals instead of binary64** · 8–10 Nov · https://github.com/timschmidt/csgrs/blob/main/docs/MIGRATIONS.md
  `.1` is stored as 1/10. Integers above 2^53 stay distinct. It says outright that this changes previously rounded geometry. Hidden paths now need a validated `d` attribute.
  Relevance: **high** — this is the exact failure your data contract exists to prevent, and it is the one worked example of how to do it.

- **hypercurve 0.3.0 keeps rational Bézier spans exact and reports what it cannot decide** · ~Jul 2026 · https://crates.io/crates/hypercurve
  Rust. Exact rational Bézier extraction, exact signed area for polynomial loops, and an explicit "unresolved" result instead of a polyline. Rational conic area is declared unsupported.
  Relevance: **medium** — outside the three-month window, but it is the closest existing design to your record; read it as a spec, not a dependency.

- **iCurve 0.2.0 does Bézier booleans on an integer grid, not exactly** · 19 Sep · https://lib.rs/crates/i_curve
  Union/intersection/difference on lines, quadratic and cubic Béziers and elliptic arcs, with i16/i32/i64 topology engines. Its own notes say rational arcs may no longer lie exactly on their ellipse after snapping.
  Relevance: **medium** — the topology idea (integer engines, curves preserved in the output) is worth copying; the snapping is exactly what you cannot accept.

- **Meshfont: a browser font editor that hands glyphs to an MCP agent** · 18 Nov · https://abduzeedo.com/meshfont-browser-font-editor-ai-agent-support
  Bézier and warp editing, and an MCP server so Claude Code, Cursor or Codex can read outlines, spacing and kerning and draft missing glyphs as proposals you accept or reject.
  Relevance: **medium** — the proposal-and-accept pattern over outlines is the workflow you want for the site and font output; the tool itself is not exact.

- **No Inkscape release in the window; 1.5 is still a development branch** · 23 Nov · https://inkscape.org/en/release
  Current stable is 1.4.4 (6 May 2026). The 1.5 notes in development list GTK 4, a new PDF exporter (CapyPDF), and an extensions change that lets extensions receive document updates.
  Relevance: **low** — nothing to adopt now; the async extension change is the only item that would touch your export path later.

- **W3C published an SVG Paths editor's draft with more stroking features** · 14 Oct · https://w3c.github.io/svgwg/specs/paths
  It is an early draft, explicitly not normative; the SVG 2 Paths chapter still governs. SVG 2 itself went to Candidate Recommendation on 6 Oct.
  Relevance: **low** — a signal about future path syntax, not something Inkscape or a print pipeline will accept soon.

- **Two new Python curve packages, both floating point** · 10 and 17 Nov · https://pypi.org/project/planarcurve/
  nurbspy 1.7.1 (NURBS, rational Bézier, complex-step derivatives) and planarcurve 0.1.3 (Bézier, B-splines, SVG path adapters, fitting). Neither offers rational or exact arithmetic.
  Relevance: **low** — usable for throwaway fitting experiments; keep them out of the record path.

## 3. Agent tooling (OpenCode and what hangs off it)

- **OpenCode 2.3.0: subagents run in the background and report when idle** · 13 Nov · https://opencode.ai/changelog/v2.3.0
  A subagent call returns a session ID at once. The parent gets a report each time the child goes idle, and again after later work. If a child still has background work, its report says so, and the parent waits.
  Relevance: **high** — your two agents no longer queue behind each other; the shared repo becomes the coordination point instead of the turn.

- **OpenCode 2.3.1: compaction is written in the background, and timed-out shells keep running** · 18 Nov · https://opencode.ai/changelog/v2.3.1
  A summary is prepared before the threshold is hit, so the swap is instant. An unused summary still costs tokens. `compaction.background: false` turns it off. A shell that passes its timeout moves to the background instead of being killed.
  Relevance: **high** — the shell change means a command can edit files after you believe the turn ended, which matters more with two agents on one repo.

- **OpenCode automations: a prompt on a clock, an interval, a cron or an MCP event** · 18 Nov · https://opencode.ai/changelog.xml
  Behind the `automations` flag. A trigger can prompt the creating session, another session, or a new subagent, or run a Code Mode program that decides whether to prompt at all.
  Relevance: **medium** — a nightly run of the exactness check over the curve table becomes a config line rather than a script.

- **OpenCode stopped re-billing the system prompt as uncached input on GPT-6.2 routes** · 18 Nov · https://github.com/anomalyco/opencode/releases
  On GitHub Copilot `gpt-6.2-sol`, uncached input per step fell from about 14,000 tokens to 3. Compaction through `/responses/compact` now reads the same cached prefix.
  Relevance: **medium** — evidence that the per-step cache behaviour is where a long-session bill is won or lost, and that it is version-dependent.

- **Skills can live in the repo under `.agents/skills/`, and a personal skill overrides a repo skill** · updated 13 Oct · https://everpod.ai/guides/opencode-skills
  OpenCode reads `.opencode/skills/`, `.claude/skills/` and `.agents/skills/`, project and home. When two share an ID, the later registration wins, and your home folder beats the repo's.
  Relevance: **medium** — the data contract belongs in a repo skill, but a stray personal copy of the same name would silently replace it for one agent only.

## 4. Figures and faces from curves

Nothing in the window. No library, paper or tool constructs a face or a figure from controlled curves.

## The three things I would act on first

1. **Judge every model by its cache-read price, and price one week of real sessions before switching.** Your current model reads cache at $0.003–$0.006. Sol is $0.10, Sonnet 5.5 is $0.10, Opus 5.5 and Fable 5.2 are $0.20, Hydrogen is $0.075. Hydrogen is the only one of these with no long-context cliff.
2. **Turn off `compaction.background` and log the background job list at the end of each turn.** An unused summary costs tokens, and after 2.3.1 a timed-out shell can still be writing files while the other agent reads them.
3. **Parse Inkscape path numbers as exact decimals, the way csgrs started doing on 8 Nov.** Every `d` string that goes through float64 is a place the record stops being exact, and this is one change that closes all of them.

**Nothing found about:** constructing human figures or faces from curves — the only adjacent work is raster-to-vector tracing of photographs and line art, which fits outlines to pixels rather than building curves from stated rules, and none of it is new, exact, or aimed at iconography.
