"""
Generate per-segment narration via edge-tts, concatenate a drift-free master WAV,
and output timeline.json + SRT + styled ASS subtitles.
All artifacts stay strictly inside the episode directory.
"""

from __future__ import annotations

import asyncio
import json
import re
import subprocess
import sys
from pathlib import Path

import edge_tts


def probe_duration(media_path: Path) -> float:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(media_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def format_srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, rem = divmod(ms, 3600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def format_ass_time(seconds: float) -> str:
    cs = int(round(seconds * 100))
    h, rem = divmod(cs, 3600_00)
    m, rem = divmod(rem, 60_00)
    s, cs = divmod(rem, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def text_to_verbatim_subtitle(text: str) -> str:
    """
    Convert spoken TTS text into clean verbatim subtitles (100% word-for-word match,
    only tightening TTS spacing between math letters/digits like 'A B' -> 'AB').
    """
    s = text.strip()
    for _ in range(3):
        s = re.sub(r"(?<=[A-Za-z0-9])\s+(?=[A-Za-z0-9])", "", s)
    return s


def split_subtitle_chunks(text: str, max_chars: int = 24) -> list[str]:
    """Split Chinese subtitle text cleanly at punctuation so each line stays compact."""
    text = text.strip()
    if len(text) <= max_chars:
        return [text]

    parts = [p.strip() for p in re.split(r"[，。！？；：、]", text) if p.strip()]
    chunks: list[str] = []
    buf = ""
    for p in parts:
        if not buf:
            buf = p
        elif len(buf) + 1 + len(p) <= max_chars:
            buf = buf + "，" + p
        else:
            chunks.append(buf)
            buf = p
    if buf:
        chunks.append(buf)

    final: list[str] = []
    for c in chunks:
        while len(c) > max_chars + 4:
            final.append(c[:max_chars])
            c = c[max_chars:]
        if c:
            final.append(c)
    return final


async def synthesize_segment(text: str, out_mp3: Path, voice: str, rate: str):
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(str(out_mp3))


async def generate_all_tts(ep_dir: Path, force: bool = False):
    script_path = ep_dir / "script.json"
    data = json.loads(script_path.read_text(encoding="utf-8"))

    voice = data.get("voice", "zh-CN-YunxiNeural")
    rate = data.get("rate", "+8%")
    output_name = data.get("output_name", ep_dir.name)
    ep_title = data.get("title", output_name)

    build_dir = ep_dir / "build"
    audio_dir = build_dir / "audio"
    output_dir = ep_dir / "output"
    audio_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    segments = data["segments"]
    print(f"[TTS] Generating {len(segments)} segments using {voice} ({rate})...")

    # 1. Generate MP3s
    for seg in segments:
        seg_id = seg["id"]
        mp3_path = audio_dir / f"{seg_id}.mp3"
        if force or not mp3_path.exists() or mp3_path.stat().st_size == 0:
            await synthesize_segment(seg["text"], mp3_path, voice, rate)
            print(f"  + {seg_id}.mp3")
        else:
            print(f"  = {seg_id}.mp3 (cached)")

    # 2. Convert each MP3 -> padded 48kHz stereo WAV and measure exact durations
    timeline_segments = []
    wav_list_lines = []
    srt_entries = []
    ass_events = []

    cursor = 0.0
    srt_idx = 1

    for seg in segments:
        seg_id = seg["id"]
        mp3_path = audio_dir / f"{seg_id}.mp3"
        wav_path = audio_dir / f"{seg_id}.wav"
        pause_after = float(seg.get("pause_after", 0.45))

        raw_dur = probe_duration(mp3_path)

        cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(mp3_path),
            "-af", f"apad=pad_dur={pause_after:.4f}",
            "-ar", "48000", "-ac", "2",
            str(wav_path),
        ]
        subprocess.run(cmd, check=True)
        exact_total = probe_duration(wav_path)

        seg_start = cursor
        seg_end = cursor + exact_total

        timeline_segments.append({
            "id": seg_id,
            "section": seg.get("section", ""),
            "start": round(seg_start, 4),
            "audio_duration": round(raw_dur, 4),
            "pause_after": round(exact_total - raw_dur, 4),
            "total_duration": round(exact_total, 4),
            "end": round(seg_end, 4),
        })

        escaped = str(wav_path.resolve()).replace("\\", "/").replace("'", r"\'")
        wav_list_lines.append(f"file '{escaped}'")

        # Subtitles: ALWAYS 100% verbatim from spoken text
        sub_text = text_to_verbatim_subtitle(seg["text"])
        chunks = split_subtitle_chunks(sub_text, max_chars=24)
        total_weight = sum(max(1, len(c)) for c in chunks)
        sub_cursor = seg_start
        for chunk in chunks:
            chunk_dur = raw_dur * (max(1, len(chunk)) / total_weight)
            c_start = sub_cursor
            c_end = min(seg_start + raw_dur, sub_cursor + chunk_dur)
            sub_cursor = c_end

            srt_entries.append(
                f"{srt_idx}\n{format_srt_time(c_start)} --> {format_srt_time(c_end)}\n{chunk}\n"
            )
            srt_idx += 1

            ass_text = chunk.replace("\n", r"\N")
            ass_events.append(
                f"Dialogue: 0,{format_ass_time(c_start)},{format_ass_time(c_end)},Default,,0,0,0,,{ass_text}"
            )

        cursor = seg_end

    # 3. Concatenate all WAVs into master_audio.wav
    concat_file = build_dir / "audio_concat.txt"
    concat_file.write_text("\n".join(wav_list_lines), encoding="utf-8")
    master_wav = build_dir / "master_audio.wav"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-c:a", "pcm_s16le",
            str(master_wav),
        ],
        check=True,
    )
    master_dur = probe_duration(master_wav)

    # 4. Write timeline.json
    timeline = {
        "episode": output_name,
        "voice": voice,
        "rate": rate,
        "total_duration": round(master_dur, 4),
        "segments": timeline_segments,
    }
    timeline_path = build_dir / "timeline.json"
    timeline_path.write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")

    # 5. Write SRT & styled ASS
    srt_path = output_dir / f"{output_name}.srt"
    srt_path.write_text("\n".join(srt_entries), encoding="utf-8")

    ass_header = f"""[Script Info]
Title: {ep_title}
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Noto Sans SC,42,&H00F8FAFC,&H000000FF,&H0018100A,&H70000000,0,0,0,0,100,100,1.2,0,1,2.6,1.4,2,90,90,34,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass_path = build_dir / "subtitles.ass"
    ass_path.write_text(ass_header + "\n".join(ass_events) + "\n", encoding="utf-8")

    print(f"[TTS] Done! Total duration: {master_dur:.2f}s ({master_dur/60:.2f} min)")
    print(f"      Timeline : {timeline_path}")
    print(f"      Audio    : {master_wav}")
    print(f"      Subtitles: {srt_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/tts_gen.py <episode_dir> [--force]")
        sys.exit(1)
    ep_dir = Path(sys.argv[1]).resolve()
    force = "--force" in sys.argv
    asyncio.run(generate_all_tts(ep_dir, force=force))


if __name__ == "__main__":
    main()
