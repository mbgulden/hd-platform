# Active Oahu Video Processing Plan (GRO-130)

**Created:** 2026-05-29
**Ticket:** GRO-130 — Video Archive Processing
**Source:** `/home/ubuntu/mounts/synology-photo/Dropbox Team Space/`

---

## 1. Current Video Inventory

From `media-inventory.json` (indexed 2026-05-29):

| Metric | Value |
|---------|-------|
| Total files (all media) | 9,592 |
| Total photos | 8,425 |
| **Total videos** | **1,167** |
| Total media size | 698.50 GB |
| Estimated video-only size | ~200+ GB |

### By Top-Level Folder

| Folder | Videos | Size | Notes |
|--------|--------|------|-------|
| Photos and Videos | 910 | ~613.43 GB (total) | Bulk of raw footage — drone, GoPro, DSLR |
| Edited Photos | 158 | 73.80 GB | Includes "Frietz Drone" (66 vids), "Drone B-roll" (92 vids) |
| Instructional Videos | 95 | 10.13 GB | Kayak/bike tutorials + 87 raw clips |
| Drone Movie | 4 | 0.99 GB | Finished/published videos |

### By Content Category (across all folders)

| Category | File Count | Size | Priority |
|----------|-----------|------|----------|
| Drone | 2,238 | 355.88 GB | **P0 — Highest** |
| GoPro | 1,014 | 147.22 GB | P1 |
| Sony/DSLR | 3,453 | 110.86 GB | P2 |
| Kaneohe Bay | 1,486 | 97.12 GB | P1 |
| Chinaman's Hat | 1,256 | 128.91 GB | P1 |
| Kahana | 1,020 | 96.61 GB | P1 |
| Mokulua | 1,271 | 55.06 GB | P1 |
| Instructional | 8 | 4.03 GB | P3 |
| Edited | 693 | 10.91 GB | P4 |

---

## 2. Video Format Analysis (Sampled 13 Files)

### Sampled Profiles

| Source | Codec | Resolution | FPS | Audio | Pixel Format |
|--------|-------|-----------|-----|-------|-------------|
| Drone (older, 2022) | H.264 | 3840×2160 (4K) | 29.97 | None | yuv420p |
| Drone (newer, 2023) | **HEVC** | 3840×2160 (4K) | 29.97 | None | yuv420p |
| Drone (Frietz) | H.264 | 2688×1512 (2.7K) | 59.94 | None | yuv420p |
| GoPro | **HEVC** | 3840×2160 (4K) | 29.97 | AAC 48kHz stereo | yuvj420p |
| Instructional (finished) | H.264 | 1920×1080 | 29.97 | AAC 44.1kHz stereo | yuv420p |
| Instructional (raw) | **HEVC** | 1920×1080 | 29.97 | AAC 44.1kHz stereo | yuv420p10le |
| Drone Movie (finished) | H.264 | 1920×1080 | 23.98–30 | AAC | yuv420p |

### Key Findings

1. **HEVC dominance in recent footage**: All drone footage from 2023+ and all GoPro footage uses HEVC (H.265). These are NOT web-playable without transcoding.
2. **High resolutions**: Most raw footage is 4K or 2.7K — massive files unsuitable for streaming.
3. **No audio on most drone clips**: Drone cameras (DJI) typically don't record audio. Must handle audio-less videos gracefully in the pipeline.
4. **Pixel format variety**: `yuv420p`, `yuvj420p`, `yuv420p10le`. All should be normalized to `yuv420p` for web compatibility.
5. **Finished videos are already web-ready**: Drone Movie folder and top-level Instructional Videos are already H.264 1080p.
6. **Variable frame rates**: Some drone clips use 59.94fps — good for slow-mo but overkill for web delivery.

---

## 3. Recommended Output Formats

### Web Delivery (Primary)

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Codec | **H.264** (libx264) | Universal browser support, hardware decoding everywhere |
| Max resolution | **1080p** (scale 4K/2.7K down) | Balance quality vs bandwidth |
| CRF | **23** | Good perceptual quality at reasonable size |
| Preset | **medium** | Reasonable encode speed |
| Pixel format | **yuv420p** | Maximum compatibility |
| Audio codec | AAC @ 128kbps | Standard web audio |
| Container | MP4 with `faststart` | Progressive download / instant playback |
| **Estimated size reduction** | **5–8×** vs 4K HEVC source | 100 MB/min → 15–20 MB/min |

### Archive (Optional, H.265)

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Codec | **H.265** (libx265) | 30–50% smaller than H.264 at same quality |
| Resolution | **Original** (4K preserved) | Future-proof, no quality loss |
| CRF | **20** | Near-transparent quality |
| Preset | **slow** | Best compression efficiency |
| Pixel format | **yuv420p** | Standardized |
| Audio | AAC @ 128kbps | Copy or re-encode |
| **Estimated size reduction** | **2–3×** vs source | Still significant for already-HEVC files |

### Thumbnails

| Parameter | Value |
|-----------|-------|
| Positions | 10%, 50%, 90% of duration |
| Format | JPEG, 640px wide (proportional height) |
| Quality | `-q:v 4` (good) |
| **Per-video** | 3 thumbnails (~15–30 KB each) |

### Watermark

| Parameter | Value |
|-----------|-------|
| Format | PNG with alpha transparency |
| Position | Bottom-right (configurable) |
| Opacity | 70% (configurable) |
| Applied to | Web output (post-transcode) |

---

## 4. Storage Estimates

### Per-Video Averages (from samples)

| Input Type | Input Size (avg) | Web Output | Archive Output | Ratio |
|-----------|-----------------|------------|----------------|-------|
| 4K HEVC drone (no audio) | ~80 MB/min | ~12 MB/min | ~35 MB/min | 6.7× / 2.3× |
| 4K HEVC GoPro (with audio) | ~45 MB/min | ~15 MB/min | ~25 MB/min | 3× / 1.8× |
| 1080p H.264 (already web) | ~20 MB/min | ~20 MB/min (copy/slight re-encode) | ~12 MB/min | 1× / 1.7× |

### Full Library Estimates

Assuming ~200 GB of video across 1,167 files:

| Output Type | Estimated Size | Notes |
|------------|---------------|-------|
| **Web only** (all 1,167) | **40–60 GB** | 1080p H.264, 3–6× reduction |
| **Archive only** (all 1,167) | **80–110 GB** | H.265, 2× reduction |
| **Web + Archive** | **120–170 GB** | Both variants |
| **Thumbnails** (3,501 images) | **~50–100 MB** | Negligible |
| **Watermarked copies** | Same as web | Additional ~40–60 GB |

### Recommended: Web-only for now (~50 GB)

The archive copies are optional — the Synology already stores the originals. Focus on web versions for the website.

---

## 5. Processing Priority Order

Ranked by content value and website needs:

### P0: Drone Footage (highest priority)
- **Folders**: All `*Drone*` subfolders in Photos and Videos, Edited Photos/Frietz Drone
- **Est. video count**: ~350–400
- **Why first**: Highest visual impact, core brand asset, already named/organized
- **Key subfolders**:
  - `6.17.23 Drone - Chinaman's Hat` (41 videos)
  - `9.30.22 Drone - 2022-09-30` (multiple subfolders, ~129 videos)
  - `11.8.23 Drone - Kalama Cole & Kody, Waimanalo` (29 videos)
  - `Frietz Drone and Stills/Drone B-roll` (92 videos)
  - `Frietz Drone` (66 videos)
  - `2.4.24 Drone - Popoia Island` (17 videos)

### P1: GoPro / Action Footage
- **Folders**: All `*Gopro*` subfolders
- **Est. video count**: ~200–250
- **Why second**: Underwater/action shots are unique, high engagement
- **Key folders**:
  - `Export 6.17.23 - Gopro` (81 videos)
  - `9.30.22 Gopro - Getting kayak on jeep` (88 videos)
  - `9.25.23 Gopro - Electric Beach, Sharks Cove` (45 videos)

### P2: Tour / Showcase Videos
- **Folders**: Drone Movie, top-level finished videos
- **Est. video count**: ~5–10
- **Why third**: Already web-ready, just need thumbnails/watermarks
- **Files**: Active Oahu Trailer.mp4, Welcome to Active Oahu.mp4, ebikes-roll-out.mp4

### P3: Instructional Videos
- **Folders**: Instructional Videos
- **Est. video count**: 95 (8 finished + 87 raw)
- **Why last**: Lower priority for public website, more for customer onboarding
- **Strategy**: Process finished videos first, raw footage only if needed

---

## 6. Output Naming Convention

```
{original_stem}_{variant}_{resolution}.mp4
```

**Examples:**
- `DJI_0554_web_1080p.mp4` — Web-optimized version
- `DJI_0554_archive_2160p.mp4` — Archive (original 4K)
- `DJI_0554_wm_1080p.mp4` — Watermarked web version
- `DJI_0554_thumb_10.jpg` — Thumbnails in `thumbnails/DJI_0554/`

**Output directory structure:**
```
output/
├── web/           # H.264 1080p MP4s for website
├── archive/       # H.265 original-res MP4s (optional)
├── thumbnails/    # Per-video subdirs with 3 JPGs each
│   ├── DJI_0554/
│   │   ├── DJI_0554_thumb_10.jpg
│   │   ├── DJI_0554_thumb_50.jpg
│   │   └── DJI_0554_thumb_90.jpg
│   └── ...
└── watermarked/   # Web videos with watermark overlay
```

---

## 7. Processing Script

**Location:** `scripts/process_videos.py`

### Usage Examples

```bash
# Dry-run: preview what would happen (safe, no encoding)
python scripts/process_videos.py \
  --source "/home/ubuntu/mounts/synology-photo/Dropbox Team Space/Photos and Videos" \
  --output ./output/videos \
  --dry-run --limit 10 --priority drone

# Process only drone footage with web output + thumbnails
python scripts/process_videos.py \
  --source "/home/ubuntu/mounts/synology-photo/Dropbox Team Space/Photos and Videos" \
  --output ./output/videos \
  --priority drone --web --thumbs

# Full archive pass (H.265, original resolution)
python scripts/process_videos.py \
  --source "/home/ubuntu/mounts/synology-photo/Dropbox Team Space/Photos and Videos" \
  --output ./output/videos \
  --archive --no-web --priority drone

# Add watermark to web videos
python scripts/process_videos.py \
  --source "/home/ubuntu/mounts/synology-photo/Dropbox Team Space/Drone Movie" \
  --output ./output/videos \
  --watermark ./assets/watermark.png --no-thumbs
```

### Script Features
- **Probe-only analysis**: Use `--dry-run` to inspect all videos without encoding
- **Priority filtering**: `--priority drone|gopro|instructional|tour`
- **Limit control**: `--limit N` for batch size control
- **Resume-friendly**: Skips already-processed files (can be extended)
- **Error handling**: Non-zero exit on failures, per-file error logging

---

## 8. Implementation Phases

### Phase 1: Infrastructure (DONE)
- [x] Install ffmpeg 7.0.2 static build
- [x] Sample and analyze 13 videos across all categories
- [x] Write `process_videos.py` pipeline script
- [x] Dry-run test (Drone Movie folder, 4 videos)
- [x] Live test (1 small video: web + thumbnails)

### Phase 2: Drone Processing (NEXT)
- [ ] Run P0 drone batch: `--priority drone --web --thumbs`
- [ ] Validate output quality on 10 random samples
- [ ] Extract drone thumbnails for website hero images
- **Est. time**: 4–8 hours for ~400 videos (depends on CPU)

### Phase 3: GoPro + Tours
- [ ] Run P1 GoPro batch
- [ ] Process tour/showcase videos (watermarks)
- **Est. time**: 3–6 hours

### Phase 4: Instructional + Archive
- [ ] Process instructional videos (P3)
- [ ] Optional: archive H.265 pass for long-term storage
- **Est. time**: 2–4 hours

---

## 9. Notes & Caveats

1. **CPU-only encoding**: No GPU acceleration detected on this server. With `libx264 medium` preset, expect ~1–2× realtime for 1080p, ~0.3–0.5× realtime for 4K→1080p.

2. **No audio drone clips**: The pipeline handles these gracefully (`-an` flag). No silent audio tracks are created.

3. **Synology mount performance**: The source is a network mount. For large batch processing, consider copying videos locally first to avoid NFS bottlenecks.

4. **Watermark not yet created**: No watermark PNG was found in the Dropbox. This is a design asset that needs to be created before watermarking can run.

5. **Finished videos may not need re-encoding**: Videos in `Drone Movie/` and top-level `Instructional Videos/` are already H.264 1080p. The script's `needs_transcode` check will skip unnecessary re-encodes, but thumbnail extraction and watermarking can still be applied.

6. **HEVC 10-bit (yuv420p10le)**: Found in iPhone-shot instructional raw footage. These will be down-converted to 8-bit yuv420p for web output, which is standard and expected.
