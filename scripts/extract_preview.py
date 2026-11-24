"""
Extract preview PNG frames for every segment in an episode's timeline.json
so visual QA can inspect every slide for tofu, overlap, clipping, and completeness.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Extract per-segment preview frames via FFmpeg")
    parser.add_argument("episode_dir", help="Path to episode directory, e.g. episodes/ep01_1_1_intro")
    parser.add_argument(
        "--frac",
        default="0.96",
        help="Comma-separated fraction(s) of audio_duration per segment (default: '0.96', e.g. '0.5,0.96')",
    )
    parser.add_argument(
        "--video",
        help="Optional explicit MP4 path (defaults to episode/output/<output_name>.mp4)",
    )
    args = parser.parse_args()

    ep_dir = Path(args.episode_dir).resolve()
    timeline_path = ep_dir / "build" / "timeline.json"
    if not timeline_path.exists():
        print(f"[ERROR] timeline.json not found: {timeline_path}", file=sys.stderr)
        sys.exit(1)

    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    ep_name = timeline["episode"]

    if args.video:
        video_path = Path(args.video).resolve()
    else:
        video_path = ep_dir / "output" / f"{ep_name}.mp4"
    if not video_path.exists():
        print(f"[ERROR] Video not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    out_dir = ep_dir / "build" / "preview_frames"
    out_dir.mkdir(parents=True, exist_ok=True)

    fracs = [float(x.strip()) for x in args.frac.split(",") if x.strip()]
    saved: list[Path] = []

    for seg in timeline["segments"]:
        seg_id = seg["id"]
        start = float(seg["start"])
        audio_dur = float(seg["audio_duration"])
        for frac in fracs:
            ts = start + audio_dur * frac
            suffix = "" if len(fracs) == 1 else f"_{int(round(frac * 100)):02d}"
            png_path = out_dir / f"{seg_id}{suffix}.png"
            cmd = [
                "ffmpeg", "-y", "-v", "error",
                "-ss", f"{ts:.3f}",
                "-i", str(video_path),
                "-frames:v", "1",
                str(png_path),
            ]
            subprocess.run(cmd, check=True)
            saved.append(png_path)
            print(f"  + {png_path.name}  (@ {ts:.2f}s)")

    print(f"\n[PREVIEW] Extracted {len(saved)} frames to:\n  {out_dir}")


if __name__ == "__main__":
    main()
