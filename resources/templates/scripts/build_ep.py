"""
One-command episode builder:
1. Synthesize TTS + timeline.json + subtitles
2. Render Manim scene (keeping all media & temp files inside episode/build/)
3. Mux video + master audio + burned-in ASS subtitles into episode/output/<name>.mp4
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path, env: dict[str, str]):
    print(f"\n>>> {' '.join(cmd)}")
    subprocess.run(cmd, cwd=str(cwd), env=env, check=True)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/build_ep.py <episode_dir> [--quality l|m|h] [--force-tts] [--skip-tts]")
        sys.exit(1)

    repo_root = Path(__file__).resolve().parent.parent
    ep_dir = Path(sys.argv[1]).resolve()
    script_data = json.loads((ep_dir / "script.json").read_text(encoding="utf-8"))

    output_name = script_data["output_name"]
    scene_name = script_data["scene_name"]

    quality = "h"  # h = 1080p60, m = 720p30, l = 480p15
    if "--quality" in sys.argv:
        idx = sys.argv.index("--quality")
        quality = sys.argv[idx + 1]

    force_tts = "--force-tts" in sys.argv
    skip_tts = "--skip-tts" in sys.argv

    build_dir = ep_dir / "build"
    media_dir = build_dir / "media"
    tmp_dir = build_dir / "tmp"
    output_dir = ep_dir / "output"
    for d in (build_dir, media_dir, tmp_dir, output_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Keep ALL temp files strictly inside the workspace directory
    env = os.environ.copy()
    env["TEMP"] = str(tmp_dir)
    env["TMP"] = str(tmp_dir)
    env["PYTHONPATH"] = str(repo_root)

    # Step 1: TTS
    if not skip_tts:
        tts_cmd = [sys.executable, str(repo_root / "scripts" / "tts_gen.py"), str(ep_dir)]
        if force_tts:
            tts_cmd.append("--force")
        run(tts_cmd, cwd=repo_root, env=env)

    # Step 2: Manim render
    scene_file = ep_dir / "scene.py"
    manim_cmd = [
        sys.executable, "-m", "manim",
        "render",
        f"-q{quality}",
        "--media_dir", str(media_dir),
        str(scene_file),
        scene_name,
    ]
    run(manim_cmd, cwd=repo_root, env=env)

    # Locate rendered silent MP4
    quality_map = {
        "l": "480p15",
        "m": "720p30",
        "h": "1080p60",
    }
    q_folder = quality_map.get(quality, "1080p60")
    raw_mp4 = media_dir / "videos" / "scene" / q_folder / f"{scene_name}.mp4"
    if not raw_mp4.exists():
        matches = list((media_dir / "videos").rglob(f"{scene_name}.mp4"))
        if not matches:
            raise FileNotFoundError(f"Rendered video not found under {media_dir / 'videos'}")
        raw_mp4 = matches[0]

    # Step 3: Mux audio + burn ASS subtitles
    master_wav = build_dir / "master_audio.wav"
    ass_path = build_dir / "subtitles.ass"
    final_mp4 = output_dir / f"{output_name}.mp4"

    # FFmpeg subtitles filter on Windows needs forward slashes & escaped colon
    ass_filter_path = str(ass_path.resolve()).replace("\\", "/").replace(":", r"\:")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", str(raw_mp4),
        "-i", str(master_wav),
        "-vf", f"ass='{ass_filter_path}'",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        str(final_mp4),
    ]
    run(ffmpeg_cmd, cwd=repo_root, env=env)

    print(f"\n[SUCCESS] Final episode exported to:\n  {final_mp4}")


if __name__ == "__main__":
    main()
