# Web MVP

A zero-dependency local web harness around the existing Python + native engine.
One page: pick a preset or a cap, edit the design JSON, watch the SVG redraw.

## Run it

From the repository root, with the native library already built
(`bash scripts/build-native.sh` if not):

```sh
.venv/bin/python web/server.py
open http://127.0.0.1:8000/
```

Use a different port with `PORT=9000 .venv/bin/python web/server.py`.

The server binds `127.0.0.1` by default. It serves the page, the example caps,
and one endpoint:

```sh
curl -s http://127.0.0.1:8000/api/render \
  -H 'content-type: application/json' \
  -d '{"design":{"segments":[{"kd":0.001,"length":40}],"stroke":0.8},"width":10,"page":[200,250]}' \
  | jq -r .report
```

## What it is not

This is a feel-it-now MVP, not the final architecture:

- no auth, no persistence, no job queue;
- one process, one render at a time per request thread;
- the design JSON is the editor (the PWA gets proper controls);
- it uses the Python policy layer and the `ctypes` native backend, so the
  host must run Linux and have `libclothoidlab.so` for a public deploy.

## Container

The root `Dockerfile` builds the Linux `.so` in a Debian stage and copies only
the runtime pieces into `python:3.12-slim`:

```sh
docker build -t clothoid-web .
docker run --rm -p 8080:8080 clothoid-web
# open http://127.0.0.1:8080/
```

That image is the shape Cloud Run wants: it listens on `$PORT`, is stateless,
and has the `.so` inside. Set concurrency to 1–2 on Cloud Run because rendering
is CPU-bound.
