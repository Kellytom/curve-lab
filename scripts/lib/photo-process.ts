/**
 * photo-process.ts — one file through the reduction rules, in one place.
 *
 * Both doors use it: the Photos export (one asset at a time) and a folder tree
 * copied off a phone. Keeping the rules here is what stops the two doors
 * drifting — the inflation guard and the chmod were both learned the hard way
 * and must not exist twice.
 *
 * The rules, from state/SPEC-photo-reduction-int.md:
 *   - under 400 KB is copied untouched (re-encoding it saves nothing);
 *   - video is left alone unless a transcoder is supplied;
 *   - a reduction that inflates keeps the original;
 *   - every written file is 0644 and its folder 0755.
 */

import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { chmodSync, existsSync, mkdirSync, readFileSync, rmSync, statSync } from "node:fs";
import path from "node:path";

export type Point = [number, number];

export type ProcessOptions = {
  src: string;
  outDir: string;
  stem: string;
  maxLongSide: number;
  quality: number;
  smallBytes?: number;
  videoPreset?: string | null;
  seen?: Map<string, string>;
};

export type ProcessResult = {
  status: "reduced" | "over-target" | "skipped-small" | "skipped-larger" | "skipped-video" | "duplicate" | "failed";
  outPath: string;
  originalBytes: number;
  reducedBytes: number;
  ratio: number;
  engine: string | null;
  quality: number | null;
  width: number | null;
  height: number | null;
  sha256: string | null;
  originalSha256: string;
  error: string | null;
};

const IMAGE = [".heic", ".heif", ".jpg", ".jpeg", ".png", ".tif", ".tiff"];
const VIDEO = [".mov", ".mp4", ".m4v"];
/** Formats we keep byte-for-byte: re-encoding them loses animation or gains nothing. */
const PASSTHROUGH = [".gif", ".webp", ".bmp", ".heic", ".heif"];

/** Accepts a file name or a bare extension; both are normalised to ".png"-style. */
const extOf = (file: string) => {
  const ext = path.extname(file).toLowerCase();
  return ext || (file.startsWith(".") ? file.toLowerCase() : "");
};
export const isImage = (file: string) => IMAGE.includes(extOf(file));
export const isVideo = (file: string) => VIDEO.includes(extOf(file));

const hashOf = (file: string): string => createHash("sha256").update(readFileSync(file)).digest("hex");

export function imageSize(file: string): { width: number; height: number } | null {
  try {
    const out = execFileSync("sips", ["-g", "pixelWidth", "-g", "pixelHeight", file], { encoding: "utf8" });
    const w = /pixelWidth:\s*(\d+)/.exec(out);
    const h = /pixelHeight:\s*(\d+)/.exec(out);
    return w && h ? { width: Number(w[1]), height: Number(h[1]) } : null;
  } catch {
    return null;
  }
}

/** Next free name in `outDir`, never overwriting a different file. */
export function freshPath(outDir: string, stem: string, ext: string): string {
  let candidate = path.join(outDir, stem + ext);
  let n = 2;
  while (existsSync(candidate)) {
    candidate = path.join(outDir, `${stem} (${n})${ext}`);
    n += 1;
  }
  return candidate;
}

export function processOne(options: ProcessOptions): ProcessResult {
  const { src, outDir, stem, maxLongSide, quality, smallBytes = 400 * 1024, videoPreset = null, seen } = options;
  const ext = path.extname(src).toLowerCase();
  const originalBytes = statSync(src).size;
  const originalSha256 = hashOf(src);
  const base: Omit<ProcessResult, "status"> = {
    outPath: "", originalBytes, reducedBytes: originalBytes, ratio: 1,
    engine: null, quality: null, width: null, height: null,
    sha256: null, originalSha256, error: null,
  };

  if (seen && seen.has(originalSha256)) {
    return { ...base, status: "duplicate", outPath: seen.get(originalSha256) ?? "", reducedBytes: 0, ratio: 0 };
  }
  if (seen) seen.set(originalSha256, "");

  if (isVideo(ext)) {
    if (!videoPreset) return { ...base, status: "skipped-video" };
    const outPath = freshPath(outDir, stem, ".mov");
    try {
      mkdirSync(outDir, { recursive: true });
      execFileSync("avconvert", ["--preset", videoPreset, "--source", src, "--output", outPath, "--replace"], { stdio: "ignore" });
      chmodSync(outPath, 0o644);
      const bytes = statSync(outPath).size;
      const dim = null;
      return {
        ...base, status: "reduced", outPath, reducedBytes: bytes, ratio: +(bytes / originalBytes).toFixed(3),
        engine: "avconvert", width: dim, sha256: hashOf(outPath),
      };
    } catch (error) {
      rmSync(outPath, { force: true });
      return { ...base, status: "skipped-video", error: (error as Error).message };
    }
  }

  if (PASSTHROUGH.includes(ext)) {
    const outPath = freshPath(outDir, stem, ext);
    mkdirSync(outDir, { recursive: true });
    execFileSync("cp", [src, outPath]);
    chmodSync(outPath, 0o644);
    return { ...base, status: "skipped-small", outPath, reducedBytes: originalBytes, sha256: hashOf(outPath), engine: "copy" };
  }
  if (!isImage(ext)) return { ...base, status: "failed", error: `not an image or video: ${ext}` };

  if (originalBytes < smallBytes) {
    const outPath = freshPath(outDir, stem, ext);
    mkdirSync(outDir, { recursive: true });
    execFileSync("cp", [src, outPath]);
    chmodSync(outPath, 0o644);
    return { ...base, status: "skipped-small", outPath, reducedBytes: originalBytes, sha256: hashOf(outPath), engine: "copy" };
  }

  const outPath = freshPath(outDir, stem, ext);
  try {
    mkdirSync(outDir, { recursive: true });
    let engine = "sips";
    let usedQuality: number | null = quality;

    if (ext === ".png") {
      execFileSync("pngquant", ["--quality", "70-95", "--speed", "1", "--force", "--output", outPath, src], { stdio: "ignore" });
      try {
        execFileSync("oxipng", ["-o", "2", "--strip", "safe", "--quiet", outPath], { stdio: "ignore" });
      } catch {
        /* lossless and optional */
      }
      engine = "pngquant";
      usedQuality = null;
    } else {
      const dim = imageSize(src);
      const args = ["-s", "formatOptions", String(quality)];
      if (dim && Math.max(dim.width, dim.height) > maxLongSide) args.push("-Z", String(maxLongSide));
      execFileSync("sips", [...args, src, "--out", outPath], { stdio: "ignore" });
    }

    // second attempt, only when the first missed the target by a lot
    if (engine === "sips" && statSync(outPath).size > originalBytes / 2 && quality > 70) {
      rmSync(outPath, { force: true });
      const dim = imageSize(src);
      const args = ["-s", "formatOptions", "70"];
      if (dim && Math.max(dim.width, dim.height) > maxLongSide) args.push("-Z", String(maxLongSide));
      execFileSync("sips", [...args, src, "--out", outPath], { stdio: "ignore" });
      usedQuality = 70;
    }

    // a reduction that inflates is not a reduction
    if (statSync(outPath).size >= originalBytes) {
      rmSync(outPath, { force: true });
      execFileSync("cp", [src, outPath]);
      chmodSync(outPath, 0o644);
      return {
        ...base, status: "skipped-larger", outPath, reducedBytes: originalBytes,
        engine: "copy", sha256: hashOf(outPath),
      };
    }

    chmodSync(outPath, 0o644);
    chmodSync(outDir, 0o755);
    const bytes = statSync(outPath).size;
    const dim = imageSize(outPath);
    return {
      ...base, status: bytes <= originalBytes / 2 ? "reduced" : "over-target",
      outPath, reducedBytes: bytes, ratio: +(bytes / originalBytes).toFixed(3),
      engine, quality: usedQuality, width: dim?.width ?? null, height: dim?.height ?? null,
      sha256: hashOf(outPath),
    };
  } catch (error) {
    rmSync(outPath, { force: true });
    return { ...base, status: "failed", error: (error as Error).message };
  }
}

/** "Hotels mexico" -> "hotels-mexico"; used for file stems, not folder names. */
export function slug(text: string): string {
  return (
    text
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 40) || "album"
  );
}
