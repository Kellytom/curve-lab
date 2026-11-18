# Security policy

> **draft A** — a working draft, not a final text.

## Reporting a vulnerability

Use GitHub's private reporting: open the **Security** tab, then **Report a
vulnerability**. That opens a private advisory visible only to the maintainer.

Please do not open a public issue for a security problem, and do not include a
working exploit in a public issue.

## What is in scope

- the web server (`web/server.py`) and its shared-token gate;
- the Astro app's save route (`app/src/pages/api/`) and the file it writes;
- path handling in the routes that serve pages and plates;
- any place a token, key or personal path could be exposed.

## Not a vulnerability

- the app has no login. It is a local drawing tool. Do not expose it on a public
  hostname; that is a deployment choice, not a bug.
- the quick Cloudflare tunnel URL is random and temporary. Sharing it shares the
  app; that is expected.
- a curve that is wrong. Open a normal issue with the command you ran.

## Supported versions

There are no releases yet. The `main` branch is the only supported version.
