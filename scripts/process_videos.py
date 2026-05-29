#!/usr/bin/env python3
"""
Active Oahu Video Processing Pipeline (GRO-130)
================================================
Handles transcoding, thumbnail extraction, and watermarking for 1,167 videos
(~200+ GB) from the Synology mount.

Pipeline capabilities:
  - Web-optimized H.264 (1080p max) with AAC audio
  - Archive-grade H.265 (original resolution) with AAC audio
  - Thumbnail extraction at key moments (10%, 50%, 90%)
  - Watermark overlay (optional PNG/SVG)
  - Dry-run mode for planning
  - Priority queue ordering (drone -> tours -> instructional)

Dependencies:
  - ffmpeg >= 4.x (static binary at ~/.local/bin/ffmpeg)
  - ffprobe (bundled with ffmpeg)
  - Python 3.8+

Usage:
  python scripts/process_videos.py --source /path/to/videos --output /path/to/output
  python scripts/process_videos.py --dry-run --limit 5 --priority drone
  python scripts/process_videos.py --watermark /path/to/watermark.png --thumbs
"""

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ─── Config (mutable via set_config / CLI args) ─────────────────────────────

_FFMPEG = os.path.expanduser("~/.local/bin/ffmpeg")
_FFPROBE = os.path.expanduser("~/.local/bin/ffprobe")


def set_binaries(ffmpeg_path: str, ffprobe_path: str):
    global _FFMPEG, _FFPROBE
    _FFMPEG = ffmpeg_path
    _FFPROBE = ffprobe_path


def ffmpeg_bin() -> str:
    return _FFMPEG


def ffprobe_bin() -> str:
    return _FFPROBE


# ─── Transcoding constants ──────────────────────────────────────────────────

WEB_MAX_HEIGHT = 1080
WEB_CODEC = "libx264"
WEB_CRF = 23
WEB_PRESET = "medium"
WEB_PIX_FMT = "yuv420p"

ARCHIVE_CODEC = "libx265"
ARCHIVE_CRF = 20
ARCHIVE_PRESET = "slow"
ARCHIVE_PIX_FMT = "yuv420p"

AUDIO_CODEC = "aac"
AUDIO_BITRATE = "128k"

THUMBNAIL_TIMES = [0.10, 0.50, 0.90]
THUMBNAIL_WIDTH = 640

# Priority groups (processing order, lowest first)
PRIORITY_ORDER = {
    "drone": 0,
    "gopro": 1,
    "tour": 2,
    "instructional": 3,
    "edited": 4,
    "other": 99,
}


@dataclass
class VideoInfo:
    """Parsed ffprobe output for a single video file."""

    path: str
    format_name: str = ""
    duration: float = 0.0
    bitrate: int = 0
    size_bytes: int = 0
    width: int = 0
    height: int = 0
    codec: str = ""
    pix_fmt: str = ""
    fps: float = 0.0
    has_audio: bool = False
    audio_codec: str = ""
    audio_channels: int = 0
    audio_sample_rate: int = 0
    category: str = "other"
    errors: list = field(default_factory=list)

    @property
    def is_4k(self) -> bool:
        return self.width >= 3840 or self.height >= 2160

    @property
    def is_hevc(self) -> bool:
        return "hevc" in self.codec.lower() or "h265" in self.codec.lower()

    @property
    def needs_transcode(self) -> bool:
        if self.is_hevc:
            return True
        if self.height > WEB_MAX_HEIGHT:
            return True
        if self.pix_fmt not in ("yuv420p",):
            return True
        return False

    def summary(self) -> str:
        return (
            f"{self.width}x{self.height} {self.codec} "
            f"{self.fps:.1f}fps {self.duration:.1f}s "
            f"({self.size_bytes / 1e6:.1f}MB) "
            f"[{'audio:' + self.audio_codec if self.has_audio else 'no audio'}]"
        )


# ─── Probe ──────────────────────────────────────────────────────────────────


def probe_video(path: str) -> VideoInfo:
    """Run ffprobe on a video file, return structured info."""
    info = VideoInfo(path=path)

    try:
        info.size_bytes = os.path.getsize(path)
    except OSError:
        pass

    try:
        result = subprocess.run(
            [
                ffprobe_bin(),
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            info.errors.append(f"ffprobe failed: {result.stderr.strip()}")
            return info

        data = json.loads(result.stdout)
        fmt = data.get("format", {})
        info.format_name = fmt.get("format_name", "")
        info.duration = float(fmt.get("duration", 0))
        info.bitrate = int(fmt.get("bit_rate", 0))

        for stream in data.get("streams", []):
            if stream["codec_type"] == "video":
                info.codec = stream.get("codec_name", "")
                info.width = int(stream.get("width", 0))
                info.height = int(stream.get("height", 0))
                info.pix_fmt = stream.get("pix_fmt", "")
                fps_str = stream.get("r_frame_rate", "0/1")
                if "/" in fps_str:
                    num, den = fps_str.split("/")
                    info.fps = float(num) / float(den) if float(den) != 0 else 0
                else:
                    info.fps = float(fps_str)
            elif stream["codec_type"] == "audio":
                info.has_audio = True
                info.audio_codec = stream.get("codec_name", "")
                info.audio_channels = int(stream.get("channels", 0))
                info.audio_sample_rate = int(stream.get("sample_rate", 0))

    except subprocess.TimeoutExpired:
        info.errors.append("ffprobe timed out")
    except json.JSONDecodeError as e:
        info.errors.append(f"ffprobe JSON parse error: {e}")
    except Exception as e:
        info.errors.append(f"probe error: {e}")

    return info


# ─── FFmpeg runner ──────────────────────────────────────────────────────────


def run_ffmpeg(cmd: list, dry_run: bool = False, timeout: int = 600) -> bool:
    """Execute an ffmpeg command. Returns True on success."""
    if dry_run:
        print(f"  [DRY-RUN] {' '.join(cmd[:8])}...")
        return True

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            tail = result.stderr.strip()[-300:] if result.stderr else "(no output)"
            print(f"  [ERROR] ffmpeg: {tail}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print(f"  [ERROR] ffmpeg timed out after {timeout}s")
        return False
    except FileNotFoundError:
        print(f"  [ERROR] ffmpeg not found at {ffmpeg_bin()}")
        return False


# ─── Transcoding ────────────────────────────────────────────────────────────


def transcode_web(
    input_path: str,
    output_path: str,
    info: Optional[VideoInfo] = None,
    dry_run: bool = False,
) -> bool:
    """Transcode to web-optimized H.264 MP4 (1080p max, yuv420p, faststart)."""
    if info is None:
        info = probe_video(input_path)

    if info.height > WEB_MAX_HEIGHT and info.width > 0:
        scale_factor = WEB_MAX_HEIGHT / info.height
        out_width = max(2, int(info.width * scale_factor) // 2 * 2)
        scale_filter = f"scale={out_width}:{WEB_MAX_HEIGHT}"
    else:
        scale_filter = None

    cmd = [
        ffmpeg_bin(), "-y",
        "-i", input_path,
        "-c:v", WEB_CODEC,
        "-crf", str(WEB_CRF),
        "-preset", WEB_PRESET,
        "-pix_fmt", WEB_PIX_FMT,
    ]

    if scale_filter:
        cmd += ["-vf", scale_filter]

    if info.has_audio:
        cmd += ["-c:a", AUDIO_CODEC, "-b:a", AUDIO_BITRATE]
    else:
        cmd += ["-an"]

    cmd += ["-movflags", "+faststart", output_path]
    return run_ffmpeg(cmd, dry_run=dry_run)


def transcode_archive(
    input_path: str,
    output_path: str,
    info: Optional[VideoInfo] = None,
    dry_run: bool = False,
) -> bool:
    """Transcode to archive-grade H.265 MP4 (original resolution, CRF 20)."""
    if info is None:
        info = probe_video(input_path)

    cmd = [
        ffmpeg_bin(), "-y",
        "-i", input_path,
        "-c:v", ARCHIVE_CODEC,
        "-crf", str(ARCHIVE_CRF),
        "-preset", ARCHIVE_PRESET,
        "-pix_fmt", ARCHIVE_PIX_FMT,
    ]

    if info.has_audio:
        cmd += ["-c:a", AUDIO_CODEC, "-b:a", AUDIO_BITRATE]
    else:
        cmd += ["-an"]

    cmd += ["-movflags", "+faststart", output_path]
    return run_ffmpeg(cmd, dry_run=dry_run)


# ─── Thumbnails ─────────────────────────────────────────────────────────────


def extract_thumbnails(
    input_path: str,
    output_dir: str,
    info: Optional[VideoInfo] = None,
    dry_run: bool = False,
) -> list:
    """Extract thumbnail frames at 10%, 50%, 90% of duration. Returns paths."""
    if info is None:
        info = probe_video(input_path)

    if info.duration <= 0:
        return []

    os.makedirs(output_dir, exist_ok=True)
    base_name = Path(input_path).stem
    output_paths = []

    for frac in THUMBNAIL_TIMES:
        timestamp = info.duration * frac
        thumb_name = f"{base_name}_thumb_{int(frac * 100):02d}.jpg"
        thumb_path = os.path.join(output_dir, thumb_name)

        cmd = [
            ffmpeg_bin(), "-y",
            "-ss", str(timestamp),
            "-i", input_path,
            "-vframes", "1",
            "-vf", f"scale={THUMBNAIL_WIDTH}:-1",
            "-q:v", "4",
            thumb_path,
        ]

        if run_ffmpeg(cmd, dry_run=dry_run, timeout=30):
            output_paths.append(thumb_path)

    return output_paths


# ─── Watermark ──────────────────────────────────────────────────────────────


def add_watermark(
    input_path: str,
    output_path: str,
    watermark_path: str,
    position: str = "bottom-right",
    opacity: float = 0.7,
    dry_run: bool = False,
) -> bool:
    """Overlay a watermark PNG onto a video."""
    if not os.path.exists(watermark_path):
        print(f"  [ERROR] Watermark not found: {watermark_path}")
        return False

    pos_map = {
        "top-left": "10:10",
        "top-right": "W-w-10:10",
        "bottom-left": "10:H-h-10",
        "bottom-right": "W-w-10:H-h-10",
        "center": "(W-w)/2:(H-h)/2",
    }
    overlay_pos = pos_map.get(position, "W-w-10:H-h-10")
    overlay_filt = (
        f"[1:v]format=rgba,colorchannelmixer=aa={opacity}[wm];"
        f"[0:v][wm]overlay={overlay_pos}"
    )

    cmd = [
        ffmpeg_bin(), "-y",
        "-i", input_path,
        "-i", watermark_path,
        "-filter_complex", overlay_filt,
        "-c:v", "libx264",
        "-crf", "23",
        "-c:a", "copy",
        output_path,
    ]
    return run_ffmpeg(cmd, dry_run=dry_run)


# ─── Classification ─────────────────────────────────────────────────────────


def classify_video(path: str) -> str:
    """Classify video by directory path for priority ordering."""
    path_lower = path.lower()
    if "drone" in path_lower:
        return "drone"
    if "gopro" in path_lower:
        return "gopro"
    if "instructional" in path_lower:
        return "instructional"
    if "tour" in path_lower or "trailer" in path_lower or "welcome" in path_lower:
        return "tour"
    if "edited" in path_lower:
        return "edited"
    return "other"


def output_name(input_path: str, variant: str, suffix: str = "") -> str:
    """Generate output filename: {stem}_{variant}_{suffix}.mp4"""
    stem = Path(input_path).stem.replace(" ", "_")
    if suffix:
        return f"{stem}_{variant}_{suffix}.mp4"
    return f"{stem}_{variant}.mp4"


# ─── Video discovery ────────────────────────────────────────────────────────


def find_videos(
    source_dir: str,
    extensions: tuple = (".mp4", ".mov", ".MP4", ".MOV"),
) -> list:
    """Recursively find all video files, skipping Synology @eaDir."""
    videos = []
    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d != "@eaDir"]
        for f in files:
            if f.endswith(extensions):
                videos.append(os.path.join(root, f))
    return videos


# ─── Batch processor ────────────────────────────────────────────────────────


def process_batch(
    source_dir: str,
    output_dir: str,
    watermark_path: Optional[str] = None,
    thumbs: bool = True,
    web: bool = True,
    archive: bool = False,
    limit: int = 0,
    dry_run: bool = False,
    priority_filter: Optional[str] = None,
) -> dict:
    """Main batch processing routine. Returns stats dict."""
    videos = find_videos(source_dir)
    print(f"\nFound {len(videos)} video files in {source_dir}")

    # Classify and sort by priority
    classified = []
    for v in videos:
        cat = classify_video(v)
        prio = PRIORITY_ORDER.get(cat, 99)
        classified.append((prio, cat, v))

    classified.sort(key=lambda x: (x[0], x[2]))

    if priority_filter:
        classified = [c for c in classified if c[1] == priority_filter]

    if limit > 0:
        classified = classified[:limit]

    stats = {
        "total_found": len(videos),
        "to_process": len(classified),
        "processed": 0,
        "web_success": 0,
        "archive_success": 0,
        "thumb_success": 0,
        "watermark_success": 0,
        "skipped": 0,
        "errors": 0,
        "total_input_bytes": 0,
        "total_output_bytes": 0,
    }

    print(f"Processing {stats['to_process']} videos (dry_run={dry_run})")
    print(f"{'='*60}")

    for i, (prio, category, video_path) in enumerate(classified):
        info = probe_video(video_path)
        if info.errors:
            print(f"[{i+1}/{stats['to_process']}] SKIP: {os.path.basename(video_path)}")
            stats["skipped"] += 1
            continue

        stats["total_input_bytes"] += info.size_bytes
        stem = Path(video_path).stem

        print(f"\n[{i+1}/{stats['to_process']}] [{category.upper()}] "
              f"{os.path.basename(video_path)}")
        print(f"  {info.summary()}")

        # ── Web transcode ──
        if web and (info.needs_transcode or dry_run):
            web_out = os.path.join(output_dir, "web",
                                   output_name(video_path, "web", "1080p"))
            os.makedirs(os.path.dirname(web_out), exist_ok=True)
            if transcode_web(video_path, web_out, info, dry_run=dry_run):
                stats["web_success"] += 1
                if not dry_run and os.path.exists(web_out):
                    stats["total_output_bytes"] += os.path.getsize(web_out)
                print(f"  [OK] Web: {os.path.basename(web_out)}")
            else:
                stats["errors"] += 1
                print(f"  [FAIL] Web transcode")
        elif web:
            print(f"  [SKIP] Already web-compatible")

        # ── Archive transcode ──
        if archive:
            archive_out = os.path.join(
                output_dir, "archive",
                output_name(video_path, "archive", f"{info.height}p"))
            os.makedirs(os.path.dirname(archive_out), exist_ok=True)
            if transcode_archive(video_path, archive_out, info, dry_run=dry_run):
                stats["archive_success"] += 1
                if not dry_run and os.path.exists(archive_out):
                    stats["total_output_bytes"] += os.path.getsize(archive_out)
                print(f"  [OK] Archive: {os.path.basename(archive_out)}")
            else:
                stats["errors"] += 1
                print(f"  [FAIL] Archive transcode")

        # ── Thumbnails ──
        if thumbs:
            thumb_dir = os.path.join(output_dir, "thumbnails", stem)
            paths = extract_thumbnails(video_path, thumb_dir, info, dry_run=dry_run)
            if paths:
                stats["thumb_success"] += len(paths)
                print(f"  [OK] Thumbnails: {len(paths)} extracted")
            else:
                print(f"  [WARN] No thumbnails")

        # ── Watermark ──
        if watermark_path and web:
            web_out = os.path.join(output_dir, "web",
                                   output_name(video_path, "web", "1080p"))
            wm_out = os.path.join(output_dir, "watermarked",
                                  output_name(video_path, "wm", "1080p"))
            os.makedirs(os.path.dirname(wm_out), exist_ok=True)
            if add_watermark(web_out, wm_out, watermark_path, dry_run=dry_run):
                stats["watermark_success"] += 1
                print(f"  [OK] Watermarked: {os.path.basename(wm_out)}")
            else:
                print(f"  [FAIL] Watermark")

        stats["processed"] += 1

    return stats


# ─── CLI ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Active Oahu Video Processing Pipeline (GRO-130)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run 5 drone videos
  python process_videos.py --source /mnt/videos --output ./out --dry-run --limit 5 --priority drone

  # Full batch with web + archive + thumbnails
  python process_videos.py --source /mnt/videos --output ./out --web --archive --thumbs

  # Add watermarks to already-transcoded web videos
  python process_videos.py --source /mnt/videos --output ./out --watermark logo.png --no-thumbs
        """,
    )

    parser.add_argument("--source", required=True,
                        help="Source directory with videos")
    parser.add_argument("--output", required=True,
                        help="Output directory for processed files")
    parser.add_argument("--web", action="store_true", default=True,
                        help="Transcode to web H.264 (default)")
    parser.add_argument("--no-web", dest="web", action="store_false",
                        help="Skip web transcode")
    parser.add_argument("--archive", action="store_true",
                        help="Transcode to archive H.265")
    parser.add_argument("--thumbs", action="store_true", default=True,
                        help="Extract thumbnails (default)")
    parser.add_argument("--no-thumbs", dest="thumbs", action="store_false",
                        help="Skip thumbnails")
    parser.add_argument("--watermark",
                        help="Path to watermark overlay image (PNG)")
    parser.add_argument("--priority", choices=list(PRIORITY_ORDER.keys()),
                        help="Process only this priority group")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max videos to process (0 = all)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show commands without executing")
    parser.add_argument("--ffmpeg", default=ffmpeg_bin(),
                        help="Path to ffmpeg binary")
    parser.add_argument("--ffprobe", default=ffprobe_bin(),
                        help="Path to ffprobe binary")

    args = parser.parse_args()

    set_binaries(args.ffmpeg, args.ffprobe)

    if not os.path.exists(ffmpeg_bin()):
        print(f"ERROR: ffmpeg not found at {ffmpeg_bin()}")
        sys.exit(1)

    start_time = time.time()
    stats = process_batch(
        source_dir=args.source,
        output_dir=args.output,
        watermark_path=args.watermark,
        thumbs=args.thumbs,
        web=args.web,
        archive=args.archive,
        limit=args.limit,
        dry_run=args.dry_run,
        priority_filter=args.priority,
    )

    elapsed = time.time() - start_time

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"  Total found:     {stats['total_found']}")
    print(f"  To process:      {stats['to_process']}")
    print(f"  Processed:       {stats['processed']}")
    print(f"  Web success:     {stats['web_success']}")
    print(f"  Archive success: {stats['archive_success']}")
    print(f"  Thumbnails:      {stats['thumb_success']}")
    print(f"  Watermarked:     {stats['watermark_success']}")
    print(f"  Skipped:         {stats['skipped']}")
    print(f"  Errors:          {stats['errors']}")
    print(f"  Input size:      {stats['total_input_bytes'] / 1e9:.2f} GB")
    print(f"  Output size:     {stats['total_output_bytes'] / 1e9:.2f} GB")
    print(f"  Elapsed:         {elapsed:.1f}s")
    print(f"  Mode:            {'DRY-RUN' if args.dry_run else 'LIVE'}")

    if stats["errors"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
