// Markdown to HTML for the chat pages.
//
// The parser is the one Astro already carries (micromark through mdast), so there is no new
// dependency and no second dialect of Markdown in the project.
import { fromMarkdown } from "mdast-util-from-markdown";
import { toHast } from "mdast-util-to-hast";
import { toHtml } from "hast-util-to-html";

// A bare URL pasted into a message is shown in its own colour, outside code. Markdown links
// keep the same colour, so a link reads as a link whether it was written [like this](url) or
// pasted plainly. They stay clickable because the browser makes them so.
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

export function renderMarkdown(text) {
  const source = String(text || "");
  if (!source.trim()) return "";
  try {
    return colourUrls(toHtml(toHast(fromMarkdown(source))));
  } catch {
    // a message that will not parse is shown as plain text rather than lost
    return "";
  }
}
