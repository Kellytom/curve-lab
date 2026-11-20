import { readFileSync, writeFileSync } from "node:fs";

// PNG dpi stamping: a pHYs chunk, inserted after IHDR.

const CRC = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n += 1) {
    let c = n;
    for (let k = 0; k < 8; k += 1) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[n] = c >>> 0;
  }
  return table;
})();

function crc32(buffer) {
  let c = 0xffffffff;
  for (const byte of buffer) c = CRC[(c ^ byte) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function chunk(type, body) {
  const length = Buffer.alloc(4);
  length.writeUInt32BE(body.length);
  const typeBuffer = Buffer.from(type, "ascii");
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(Buffer.concat([typeBuffer, body])));
  return Buffer.concat([length, typeBuffer, body, crc]);
}

export function setDpi(path, dpi = 300) {
  const data = readFileSync(path);
  const metres = Math.round(dpi / 0.0254);
  const body = Buffer.alloc(9);
  body.writeUInt32BE(metres, 0);
  body.writeUInt32BE(metres, 4);
  body[8] = 1;
  const parts = [data.subarray(0, 8)];
  let offset = 8;
  let inserted = false;
  while (offset < data.length) {
    const length = data.readUInt32BE(offset);
    const type = data.toString("ascii", offset + 4, offset + 8);
    if (type !== "pHYs") {
      if (type === "IDAT" && !inserted) { parts.push(chunk("pHYs", body)); inserted = true; }
      parts.push(data.subarray(offset, offset + 12 + length));
    }
    offset += 12 + length;
  }
  writeFileSync(path, Buffer.concat(parts));
}


