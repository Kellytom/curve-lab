// The figures sheet, split into pages.
//
// The page drew all 371 figures at once; a light browser gives up before the
// late ones. Fifty a page is the size the operator asked for; this module holds
// the arithmetic so the page and its test agree, and so no curve is lost or
// counted twice between pages.

export const PER_PAGE = 50;

export function pageCount(total, perPage = PER_PAGE) {
  return Math.max(1, Math.ceil(Math.max(0, total) / perPage));
}

export function pageSlice(items, requested = 1, perPage = PER_PAGE) {
  const total = items.length;
  const pages = pageCount(total, perPage);
  const page = Math.min(Math.max(1, Number.parseInt(requested, 10) || 1), pages);
  const start = (page - 1) * perPage;
  const end = Math.min(start + perPage, total);
  return { page, pages, start, end, total, items: items.slice(start, end) };
}
