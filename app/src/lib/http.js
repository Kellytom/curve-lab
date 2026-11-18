// A form post must come from this app. A browser sends Origin on POST; a local
// command line tool may not, and that is allowed because the app is local.
export function sameOrigin(request, url) {
  const origin = request.headers.get("origin");
  return !origin || origin === url.origin;
}
