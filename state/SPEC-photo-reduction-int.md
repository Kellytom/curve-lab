# SPEC — photo reduction: mirror the Photos folders, reduce the copies, keep a manifest

Status: **spec, not built.** Written 2026-11-26 for the session after `/fhandoff`.
Owner of the first build: whoever picks up `next-fhandoff-int.md` first. Read this whole file
before running anything against the library.

The operator's words, 2026-11-26:

> "photos take up too much room. taking the photos and pngs on this macbook pro and reducing them
> by half or more… set up a file system to mirror the photos app folders, and begin to transfer
> copies in, keeping track of what has been transferred. some might be in the cloud and have to be
> downloaded… once they are reduced i will check them quickly using apple finder, then we can delete
> the originals."

## 1. What this does, in one paragraph

Read the album and folder names out of Photos, recreate that tree on disk under
`~/Pictures/photo-reduced/`, export each photo there one at a time, recompress it to at most half
its bytes, record every asset in an append-only manifest, and leave the Photos library untouched.
The operator checks the copies in Finder. Only then are the Photos originals deleted, by the
operator, not by a script.

## 2. The facts this Mac gives us (measured today, not assumed)

| fact | value | where |
|---|---|---|
| library | `~/Pictures/Photos Library.photoslibrary` exists | `ls` |
| library contents | **not readable: `Operation not permitted`** | TCC protects it |
| free space | about **112 GiB** available | `df -h /` |
| `sips` | `/usr/bin/sips`; reads and writes `heic`, `jpeg`, `png`, `tiff` | `sips --formats` |
| mozjpeg | `cjpeg`, `djpeg`, `jpegtran` in `/usr/local/bin` | `command -v` |
| pngquant / oxipng / optipng / zopflipng | all in `/usr/local/bin` | `command -v` |
| **not available** | `jpegoptim`, `heif-convert`, ImageMagick, `exiftool` | `command -v` |

Two consequences:

1. **The library cannot be read from the shell.** macOS TCC blocks it. The supported door is
   AppleScript into Photos, which also triggers iCloud downloads for cloud-only assets. Direct
   reading of `originals/` and `database/Photos.sqlite` needs Full Disk Access granted to the
   terminal app in System Settings → Privacy & Security.
2. **The library size is unknown**, because it cannot be measured until access is granted. Space is
   the first thing the next session must establish, before exporting anything.

### The reduction chain, measured

On a 1600 px project plate (172,823 bytes, line art — a hard case for JPEG):

| step | bytes | share of source |
|---|---|---|
| `sips -s format jpeg -s formatOptions 80` | 117,201 | 68 % |
| `sips … formatOptions 60` | 94,171 | 54 % |
| `djpeg … \| cjpeg -quality 80` (mozjpeg) | **85,322** | **49 %** |

**mozjpeg wins at equal quality.** Use it when `sips` cannot reach the target; use `sips` when
metadata fidelity matters, because `cjpeg` drops EXIF and orientation unless the date is restored.

A mistake to encode as a rule: `sips -Z 2400` on a 1600 px file made it **larger** (194,192
bytes). Never upscale; resize only when the long side is above the cap.

### The PNG half, using the setting this project already settled

The operator's "photos and pngs" is two toolchains, not one. For PNG the project already measured the
answer in `state/PNG-COMPRESSION-int.md`: **`pngquant --quality 70-95 --speed 1`**, which took the
plate set from 17.8 MB to 6.0 MB (112.7 s, about 0.28 s/plate) with a measured maximum pixel
difference recorded per plate. Do not re-litigate that setting; reuse it, and then run `oxipng -o 2
--strip safe` if the file is still large (it is lossless and this machine has it).

A PNG in the photo set is a screenshot or an exported graphic: it will usually beat 50 % on the first
pass, and it must never be converted to JPEG (line art shows ringing). Same manifest, same rules,
`engine: "pngquant"`.

## 3. Decisions to take before the first export

Each has a recommendation; the operator may overrule.

| # | decision | recommendation | why |
|---|---|---|---|
| D1 | what "mirror the folders" means | **albums and folders as directories**, top-level folder as parent; anything in no album goes to `_by-year/YYYY/` | Photos' albums are the folders the operator sees; the library's own `originals/` is a hash tree with no names |
| D2 | export the **original** or the **edited** version | edited (the version they see) | `using originals true` exports the pre-edit file, which will not match the album on screen |
| D3 | output format | keep the source format: HEIC stays HEIC, JPEG stays JPEG; PNG stays PNG | converting HEIC→JPEG loses the format's size advantage; keeping it is smaller |
| D4 | the size target | **≤ 50 % of the original bytes**, long side ≤ 3000 px | the operator's "reduced by half or more"; 3000 px matches the project's image limit |
| D5 | quality floor | JPEG/HEIC quality 80 first; if that misses 50 %, try 70 once; if it still misses, keep the 80 copy and record `over-target` | never chase a number into visible mush |
| D6 | small files | anything already under 400 KB is **copied without re-encoding** and marked `skipped-small` | re-encoding a small file costs quality and saves nothing |
| D7 | Live Photos, videos | copy the still; record the `.MOV` companion as `skipped-video` and say so | the motion is not recoverable from the still, and the operator decides separately |
| D8 | duplicates and bursts | one manifest row per Photos asset id; never merge | deleting a duplicate is the operator's call |

## 4. The pipeline

```
Photos library  --AppleScript export-->  staging/<album>/<file>
                                                |
                                         reduce (sips / cjpeg)
                                                |
                          ~/Pictures/photo-reduced/<album>/<file>
                                                |
                                     one manifest row (JSONL)
                                                |
                                    delete the staged file
```

**One asset at a time.** Never parallel: Photos is a single application, and a failure must cost
one file, not an album.

### Where things live

| path | what |
|---|---|
| `~/Pictures/photo-reduced/` | the mirror the operator browses in Finder |
| `~/Pictures/photo-reduced/manifest.jsonl` | **the record**: append-only, one row per asset |
| `~/Pictures/photo-reduced/_staging/` | one file at a time; emptied after each success |
| `state/PHOTO-REDUCTION-int.md` | progress notes for the next session (counts, blockers) |
| `state/PROBLEMS-photo-reduction-int.md` | every fault, the operator's words, and the guard |

### The manifest row

```json
{"asset_id":"…","album":"Holiday 2019","filename":"IMG_1234.HEIC","kind":"photo",
 "original_bytes":4821330,"reduced_bytes":1912044,"ratio":0.397,
 "out_path":"Holiday 2019/IMG_1234.HEIC","sha256":"…","width":4032,"height":3024,
 "taken_at":"2019-07-14T10:22:11Z","quality":80,"engine":"sips",
 "status":"reduced","error":null,"done_at":"2026-11-27T09:14:02Z"}
```

`status` is terminal for every value except `failed`. **Resume reads the manifest and skips every
asset id already present with a terminal status** — there is no second state file to drift.

Rules the writer must hold:
- **Append, never rewrite.** A row is a fact about one attempt; a retry adds a row.
- **Never overwrite a different file.** If `out_path` exists with a different `sha256`, stop and
  record `failed: collision`.
- **Never write inside `*.photoslibrary`.** It is Photos' file, not ours.
- **Never delete anything in Photos.** The operator deletes; that is the point of the Finder check.

## 5. The order of work, and the finish line for each step

| # | step | `Proves:` |
|---|---|---|
| 1 | **Grant access.** Automation for the terminal → Photos; optionally Full Disk Access to read the library directly | `osascript -e 'tell application "Photos" to get name'` returns `Photos` without a dialog |
| 2 | **Inventory.** Album names, asset counts, local versus cloud-only, and the true library size | a printed table: N albums, M assets, X GB local, Y assets needing download |
| 3 | **Pilot: one album of about 20 assets.** Export, reduce, manifest | 20 manifest rows; every file opens (`sips -g pixelWidth`); total bytes at least halved; the operator checks that album in Finder |
| 4 | **Full run**, album by album, resumable | manifest row count equals asset count; no `failed` rows left unexplained |
| 5 | **Hand back for deletion.** A per-album summary: bytes before, after, saved | the operator deletes in Photos; the reduced tree is the archive |

**Do not run step 4 before the operator has looked at step 3.** The pilot exists so a wrong quality
setting costs twenty photos, not a library.

## 6. Risks, and what the spec does about each

| risk | what happens | guard |
|---|---|---|
| **Space** — two copies will not fit | mirror plus reduced set exceeds 112 GiB | stream one file at a time and delete the staged original immediately; refuse to start an album if free space < 1.5 × its estimated output |
| **Cloud-only assets** | export stalls while iCloud downloads | export `using originals true`; run with Photos open; one asset at a time; log a `download-slow` note instead of hanging silently |
| **Metadata loss** | `cjpeg` drops EXIF and the capture date | use `sips` by default; when mozjpeg is used, write `taken_at` into the manifest and `touch -t` the file |
| **Orientation** | a rotated photo shows sideways | never strip EXIF with `jpegtran -copy none`; after any mozjpeg path, verify one rotated photo by eye in the pilot |
| **HEIC conversion** | sips may re-encode rather than pass through | keep the format (D3); verify the first HEIC in the pilot by opening it |
| **Live Photos** | the `.MOV` is lost when the still is kept | record `skipped-video` rows so nothing is silently dropped |
| **Duplicates** | the same photo appears twice | one row per asset id; never merge |
| **A partial run** | a crash mid-album leaves a half-filled folder | the manifest is the truth; a file with no row is staged, not kept, and is deleted on the next start |
| **Deleting too early** | the originals go before the check | no script deletes from Photos, ever |

## 7. What "done" means

- Every asset in the library has a manifest row, with a terminal status.
- Each reduced file opens, and its long side is ≤ 3000 px.
- Total bytes at least halved over the whole library.
- The operator has checked the tree in Finder and said so.
- The Photos originals are then deleted by the operator, and the reduced tree plus manifest is what
  remains.

## 8. The first action of the next session

Grant the permission and measure the library — nothing else:

```sh
osascript -e 'tell application "Photos" to get name'
osascript -e 'tell application "Photos" to count (every media item)'
```

Then, before any export, run a dry inventory that prints album names and counts and writes nothing.
The number that decides the plan is **total library bytes and assets needing download**; without it
the space argument in §6 is a guess.
