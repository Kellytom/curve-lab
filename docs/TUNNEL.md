# The tunnel: one URL for the phone, for good

A named Cloudflare tunnel gives the Astro app a hostname that does not change,
on your own domain, while the Mac is awake. It is not hosting: when the Mac
sleeps or the tunnel stops, the URL stops answering.

The workbench pages are already served inside the app (`/pages/<file>`), so the
whole hub works through the tunnel — no second port, no second server.

**What only you can do:** authorise the tunnel against your Cloudflare account
(`cloudflared tunnel login`) and choose the hostname. Everything else is a
command.

## Quick tunnel, while there is no domain

No domain, no account, no config — and a different address every time:

```sh
~/bin/cloudflared tunnel --url http://localhost:4321
```

It prints `https://<three-words>.trycloudflare.com`; open that on the phone.
Start the app first (`cd app && npm run dev -- --host`), or the tunnel has
nothing to serve. Stop it with Ctrl-C, or

```sh
pkill -f "cloudflared tunnel --url"
```

The address dies with the process. That is the whole trade: instant, free,
temporary. For a name that lasts, do the one-time setup below.

**Before you start: the account needs a zone.** `cloudflared tunnel login` shows
a list of domains to authorise against. With no domain on the account the list
is empty, the login sits "Waiting for login…" for about eight minutes and then
fails with `Failed to fetch resource` — it has nothing to authorise, and no
`cert.pem` is written (or your browser downloads one, which you would have to
copy to `~/.cloudflared/cert.pem` by hand). Add a domain to the Cloudflare
account first — the free plan is enough, and Registrar sells one at cost.

## One-time setup

Four commands, in order, from the repo root.

```sh
~/bin/cloudflared tunnel login
```

The browser opens. Pick the domain (zone) you want the lab on and press
**Authorize**. It writes `~/.cloudflared/cert.pem`; that file is your account
credential and is never committed.

```sh
~/bin/cloudflared tunnel create curve-lab
```

It prints a UUID and writes `~/.cloudflared/<UUID>.json`. That JSON is the
tunnel's own key: never commit it, never paste it.

```sh
~/bin/cloudflared tunnel route dns curve-lab lab.example.com
```

Use the real hostname, for example `lab.curvelab.dev`. This is the line that
makes the address permanent: it creates the CNAME in Cloudflare's DNS.

```sh
cat > ~/.cloudflared/config.yml <<'YAML'
tunnel: curve-lab
credentials-file: /Users/thomaskelly/.cloudflared/<UUID>.json

ingress:
  - hostname: lab.example.com
    service: http://localhost:4321
  - service: http_status:404
YAML
```

Replace `<UUID>` and the hostname. The last rule is the catch-all Cloudflare
requires.

## Get in

Two things must run: the app, and the tunnel.

```sh
cd app && npm run dev -- --host
```

```sh
scripts/tunnel.sh start
```

Then open `https://lab.example.com` on the phone. `scripts/tunnel.sh status`
prints the hostname and its HTTP code; 200 means end to end.

For iteration, leave `npm run dev` running. Astro reloads on save, and the
tunnel does not notice — it forwards whatever the app serves. A full page
refresh on the phone is the reliable check; live-reload over a tunnel is often
a second behind.

`app/astro.config.mjs` allows the tunnel host, and any host named in
`CURVE_LAB_HOSTS` (comma-separated), so Vite does not answer "Blocked request".

## Get out

```sh
scripts/tunnel.sh stop
```

That kills the tunnel; the URL stops answering at once. Stop the app with
Ctrl-C in its terminal. Nothing is left running in the background.

To stop for a while, that is enough. The DNS record stays; the next `start`
uses it again.

## Turning it off for good

Three things exist: the tunnel, its DNS record, and the local config.

1. Cloudflare dashboard → **Zero Trust → Networks → Tunnels** → `curve-lab` →
   **Delete**. A deleted tunnel stops working immediately.
2. **DNS** → delete the `lab` CNAME for the chosen domain.
3. On the Mac: remove `~/.cloudflared/config.yml`, the `<UUID>.json`, and
   `~/.cloudflared/cert.pem` if no other tunnel uses the account.

## When it breaks

| what you see | what it means | what to do |
|---|---|---|
| `530` or `1033` from Cloudflare | the tunnel is not connected | `scripts/tunnel.sh status`; `scripts/tunnel.sh start` |
| the page loads but is blank, or 502 | the app is not running on :4321 | `cd app && npm run dev -- --host` |
| `Blocked request. This host is not allowed.` | Vite refused the tunnel hostname | add it to `CURVE_LAB_HOSTS` and restart the app |
| works at home, not on the work Wi-Fi | the phone cannot see the Mac on that network — the tunnel is the fix, not the cause | check `status`, then reload the phone |
| works on the Mac, not on the phone | the URL is the LAN one, or DNS has not propagated (a minute or two) | open the `https://` hostname, not the IP |
| tunnel starts, then dies | port 4321 was up at start and gone later | start the app first, then the tunnel |
| `login` waits, then `Failed to fetch resource` | the account has no zone to authorise against | add a domain to Cloudflare, then run `cloudflared tunnel login` again |

## What this is not

- **Not hosting.** Mac asleep, URL down. For a page that is always up, the app
  has to be deployed — that is the "going public" task in `TODO.md`, and it
  needs the disk-reading routes (`/pages/**`, `/api/plate/**`, `/book`) moved
  or made static first.
- **Not private.** The Astro app has no login, and `POST /api/stars` writes
  `workbench/starred.json`. Anyone with the URL can see the hub and write a star
  file. That is acceptable while it is your own domain and unlisted; it is not
  acceptable once the URL is shared.
- **Not a second server.** The tunnel forwards to `:4321` only. The Python
  workbench server on `:8003` is not exposed, and does not need to be: the hub
  serves the generated pages itself.

## Files

| path | what it is | committed? |
|---|---|---|
| `scripts/tunnel.sh` | start, stop, status, log | yes |
| `~/.cloudflared/config.yml` | tunnel name, key path, hostname | **no** |
| `~/.cloudflared/cert.pem` | account credential from `login` | **no** |
| `~/.cloudflared/<UUID>.json` | tunnel key from `create` | **no** |
| `/tmp/curve-lab-tunnel.log` | the running tunnel's log | no |
