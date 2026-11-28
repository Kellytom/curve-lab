/**
 * photo-upload.ts — a phone uploads photos to this Mac over the local network.
 *
 *   node scripts/photo-upload.ts                 # prints the URL to open on the phone
 *   node scripts/photo-upload.ts --port 8080
 *
 * Why this exists: the Samsung on this desk would not expose adb (no Developer
 * options, `*#0808#` would not take), and macOS cannot mount MTP without a
 * third-party app whose download host is blocked. A phone browser needs no
 * install on either side and no cable.
 *
 * The page is one file picker. Each chosen file is sent with PUT to
 * /u/<relative path>, streamed straight to disk in ~/Pictures/photo-inbox, so a
 * 4 GB video never sits in memory. Only the local network can reach it, and the
 * URL carries a token that changes on every start.
 *
 * After the upload: node scripts/photo-reduce.ts --from-dir ~/Pictures/photo-inbox
 */

import { createWriteStream, existsSync, mkdirSync } from "node:fs";
import { createHash, randomBytes } from "node:crypto";
import { createServer } from "node:http";
import { homedir, networkInterfaces } from "node:os";
import path from "node:path";

const argv = process.argv.slice(2);
const flag = (name: string, fallback: string): string => {
  const i = argv.indexOf(name);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : fallback;
};

const PORT = Number(flag("--port", "8080"));
const INBOX = flag("--inbox", path.join(homedir(), "Pictures", "photo-inbox"));
const TOKEN = randomBytes(6).toString("hex");
const MAX_BYTES = 8 * 1024 * 1024 * 1024;

mkdirSync(INBOX, { recursive: true });

function address(): string {
  for (const list of Object.values(networkInterfaces())) {
    for (const net of list ?? []) {
      if (net.family === "IPv4" && !net.internal) return net.address;
    }
  }
  return "127.0.0.1";
}

const page = `<!doctype html><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>send photos</title>
<style>
 body{font:16px -apple-system,system-ui,sans-serif;margin:0;padding:1.2rem;background:#111;color:#eee}
 h1{font-size:1.1rem;margin:0 0 .3rem}
 p{color:#aaa;font-size:13px;margin:.2rem 0 1rem}
 label{display:block;background:#1e1e1e;border:1px dashed #555;border-radius:8px;padding:1.2rem;text-align:center}
 input{display:none}
 button{margin-top:1rem;width:100%;padding:.9rem;font-size:1rem;border:0;border-radius:8px;background:#2f6df6;color:#fff}
 button:disabled{background:#333;color:#888}
 progress{width:100%;margin-top:1rem}
 #log{font-family:ui-monospace,monospace;font-size:12px;color:#9c9;white-space:pre-wrap;margin-top:1rem;max-height:40vh;overflow:auto}
</style>
<h1>Send photos to the Mac</h1>
<p>Pick a whole folder (DCIM/Camera, or an album). Every file inside is sent; the folder name is kept.</p>
<label>Tap to choose a folder<input id=f type=file multiple webkitdirectory accept="image/*,video/*"></label>
<button id=go disabled>Upload</button>
<progress id=p max=100 value=0></progress>
<div id=log></div>
<script>
const f=document.getElementById('f'),go=document.getElementById('go'),log=document.getElementById('log'),bar=document.getElementById('p');
let files=[];
f.onchange=()=>{files=[...f.files];go.disabled=!files.length;go.textContent='Upload '+files.length+' file'+(files.length>1?'s':'');log.textContent='';};
go.onclick=async()=>{
  go.disabled=true;let done=0,sent=0;
  for(const file of files){
    const rel=(file.webkitRelativePath||file.name).split('/').map(encodeURIComponent).join('/');
    try{
      const r=await fetch('/u/'+rel+'?t=${TOKEN}',{method:'PUT',body:file});
      if(!r.ok)throw new Error(await r.text());
      done++;sent+=file.size;
      log.textContent+=file.name+'  '+Math.round(file.size/1024)+' KB\\n';
    }catch(e){log.textContent+='FAILED '+file.name+' '+e.message+'\\n';}
    bar.value=Math.round(100*done/files.length);
    go.textContent=done+' / '+files.length;
  }
  log.textContent+='\\ndone: '+done+' files, '+(sent/1e9).toFixed(2)+' GB\\n';
  go.disabled=false;
};
</script>`;

const server = createServer((req, res) => {
  const url = new URL(req.url ?? "/", `http://${req.headers.host ?? "localhost"}`);
  const tokenOk = url.searchParams.get("t") === TOKEN;

  if (req.method === "GET" && url.pathname === "/") {
    if (!tokenOk) {
      res.writeHead(403, { "content-type": "text/plain" });
      res.end("open the URL with the token\n");
      return;
    }
    res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
    res.end(page);
    return;
  }

  if (req.method === "PUT" && url.pathname.startsWith("/u/")) {
    if (!tokenOk) {
      res.writeHead(403);
      res.end("bad token\n");
      return;
    }
    const rel = decodeURIComponent(url.pathname.slice(3));
    const safe = path.normalize(rel).replace(/^([/\\])+/, "");
    if (safe.includes("..") || path.isAbsolute(safe)) {
      res.writeHead(400);
      res.end("bad path\n");
      return;
    }
    const target = path.join(INBOX, safe);
    mkdirSync(path.dirname(target), { recursive: true });
    let bytes = 0;
    const out = createWriteStream(target);
    req.on("data", (chunk) => {
      bytes += chunk.length;
      if (bytes > MAX_BYTES) req.destroy();
    });
    req.pipe(out);
    out.on("finish", () => {
      console.log(`  ${(bytes / 1e6).toFixed(1)} MB  ${safe}`);
      res.writeHead(201, { "content-type": "text/plain" });
      res.end(`ok ${bytes}\n`);
    });
    out.on("error", (error) => {
      console.error(`  FAILED ${safe}: ${error.message}`);
      res.writeHead(500);
      res.end("write failed\n");
    });
    return;
  }

  res.writeHead(404);
  res.end("not found\n");
});

server.listen(PORT, "0.0.0.0", () => {
  const host = address();
  console.log(`listening on ${host}:${PORT}`);
  console.log(`inbox: ${INBOX}`);
  console.log(`\nopen this on the phone:\n  http://${host}:${PORT}/?t=${TOKEN}\n`);
  console.log("then: node scripts/photo-reduce.ts --from-dir " + INBOX);
});
