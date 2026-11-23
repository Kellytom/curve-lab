// Markdown to HTML for the chat pages and the chat-display appendix pages.
//
// The parser is the one Astro already carries (micromark through mdast), plus GFM-free maths:
// $inline$ and $$display$$ are rendered by KaTeX, so a formula in an answer is typeset rather
// than spelled. Bare URLs get their own colour and stay clickable; code is left alone.
import { fromMarkdown } from "mdast-util-from-markdown";
import { toHast } from "mdast-util-to-hast";
import { toHtml } from "hast-util-to-html";
import { math } from "micromark-extension-math";
import { mathFromMarkdown } from "mdast-util-math";
import katex from "katex";

const toMarkdownTree = (source) => fromMarkdown(source, {
  extensions: [math({ singleDollarTextMath: true })],
  mdastExtensions: [mathFromMarkdown({ singleDollarTextMath: true })],
});

const URL_PATTERN = /(https?:\/\/[^\s<>"'`]+)/g;

function colourUrls(html) {
  let out = "";
  let inCode = false;
  for (const chunk of html.split(/(<[^>]+>)/)) {
    if (chunk.startsWith("<")) {
      if (/^<(code|pre)[\s>]/i.test(chunk)) inCode = true;
      if (/^<\/(code|pre)>/i.test(chunk)) inCode = false;
      out += chunk;
    } else if (inCode) {
      out += chunk;
    } else {
      out += chunk.replace(URL_PATTERN, '<span class="url">$1</span>');
    }
  }
  return out;
}

function renderMath(node, displayMode) {
  try {
    return katex.renderToString(node.value, { displayMode, throwOnError: false, output: "html" });
  } catch {
    return null;
  }
}

export function renderMarkdown(text) {
  const source = String(text || "");
  if (!source.trim()) return "";
  try {
    const tree = toMarkdownTree(source);
    // KaTeX before the tree becomes HTML: a maths node is replaced by its rendered span
    const walk = (node) => {
      if (!node || !Array.isArray(node.children)) return;
      node.children = node.children.map((child) => {
        if (child.type === "inlineMath" || child.type === "math") {
          const html = renderMath(child, child.type === "math");
          if (!html) return child;
          return { type: "html", value: html };
        }
        walk(child);
        return child;
      });
    };
    walk(tree);
    // allowDangerousHtml: the maths nodes are replaced by KaTeX's own HTML
    return colourUrls(toHtml(toHast(tree, { allowDangerousHtml: true }), { allowDangerousHtml: true }));
  } catch {
    return "";
  }
}
