"""
Audio-driven synchronization utilities for Manim scenes.
Uses Manim's native `self.renderer.time` clock to guarantee zero drift
between edge-tts audio segments and rendered video frames.
"""

from __future__ import annotations

import json
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from manim import Scene

from common.theme import BG_COLOR


@dataclass
class SegmentTiming:
    id: str
    section: str
    start: float
    audio_duration: float
    pause_after: float
    total_duration: float
    end: float


class SyncedScene(Scene):
    """
    Base Scene that reads `build/timeline.json` and synchronizes every spoken
    segment to the exact cumulative clock of the master audio track.
    """

    TIMELINE_PATH: Path | None = None

    def setup(self):
        self.camera.background_color = BG_COLOR
        self._timings: dict[str, SegmentTiming] = {}
        self._load_timeline()

    def _load_timeline(self):
        if self.TIMELINE_PATH is None:
            return
        path = Path(self.TIMELINE_PATH)
        if not path.exists():
            raise FileNotFoundError(
                f"Timeline not found: {path}. Run scripts/tts_gen.py first."
            )
        data = json.loads(path.read_text(encoding="utf-8"))
        for item in data["segments"]:
            self._timings[item["id"]] = SegmentTiming(
                id=item["id"],
                section=item.get("section", ""),
                start=float(item["start"]),
                audio_duration=float(item["audio_duration"]),
                pause_after=float(item["pause_after"]),
                total_duration=float(item["total_duration"]),
                end=float(item["end"]),
            )

    @property
    def current_time(self) -> float:
        return float(self.renderer.time)

    def pace_to(self, seg: SegmentTiming, frac: float):
        """
        Hold until the video clock reaches `seg.start + seg.audio_duration * frac`.
        Prevents animations from rushing ahead of narration.
        """
        target = seg.start + seg.audio_duration * frac
        dt = target - self.current_time
        if dt > 0.04:
            self.wait(dt)

    @contextmanager
    def segment(self, seg_id: str):
        """
        Context manager for one narrated segment.
        Yields SegmentTiming; on exit, pads with self.wait() so `self.renderer.time`
        lands exactly on `seg.end`.
        """
        if seg_id not in self._timings:
            raise KeyError(f"Segment '{seg_id}' not found in timeline.json")
        seg = self._timings[seg_id]
        seg_start_clock = self.current_time
        yield seg
        remaining = seg.end - self.current_time
        if remaining > 0.03:
            self.wait(remaining)
        elif remaining < -0.20:
            used = self.current_time - seg_start_clock
            print(
                f"[SYNC WARNING] Segment '{seg_id}' overran by {-remaining:.2f}s "
                f"(used {used:.2f}s vs budget {seg.total_duration:.2f}s)"
            )
