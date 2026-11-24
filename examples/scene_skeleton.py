"""
Reusable Manim SyncedScene skeleton for any Textbook Speedrun Course episode.
Demonstrates:
- Persistent studio backdrop + animated top HUD
- Chapter-opener roadmap (`make_knowledge_map`) vs standard cover-card opening
- 100% standalone problem statement + step-by-step `pace_to` animated solution
- Safe `clear_stage` at `pace_to(seg, 0.995)`
"""

from __future__ import annotations

from pathlib import Path
from manim import *

from common.audio_sync import SyncedScene
from common.theme import (
    ACCENT_BLUE,
    ACCENT_CYAN,
    ACCENT_GOLD,
    ACCENT_GREEN,
    ACCENT_PURPLE,
    ACCENT_RED,
    BORDER_COLOR,
    TEXT_MUTED,
    TEXT_PRIMARY,
    make_badge,
    make_card,
    make_knowledge_map,
    make_section_header,
    make_studio_backdrop,
    make_top_hud,
    math_tex,
    zh_tex,
    zh_text,
)

EP_DIR = Path(__file__).resolve().parent

# Top HUD section tabs (4~6 short labels)
CHAPTERS = ["破冰", "核心定义", "例题实战", "避坑总结"]

# Full-book roadmap (ONLY used in the first episode of each chapter)
BOOK_CHAPTERS = [
    ("第一章", "基础概念"),
    ("第二章", "核心方法"),
    ("第三章", "结构理论"),
    ("第四章", "综合应用"),
]


class Ep01SampleTopic(SyncedScene):
    TIMELINE_PATH = EP_DIR / "build" / "timeline.json"

    def construct(self):
        self.backdrop = make_studio_backdrop()
        self.add(self.backdrop)

        self.hud = None
        self.current_chapter = -1

        self.act0_intro()
        self.act1_definition()
        self.act2_example1()
        self.act3_summary()

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------
    def set_chapter(self, idx: int, run_time: float = 0.4):
        new_hud = make_top_hud("1-1", "核心概念示例", CHAPTERS, active_idx=idx)
        if self.hud is None:
            self.hud = new_hud
            self.play(FadeIn(self.hud, shift=DOWN * 0.2), run_time=run_time)
        else:
            self.play(ReplacementTransform(self.hud, new_hud), run_time=run_time)
            self.hud = new_hud
        self.current_chapter = idx

    def clear_stage(self, *mobjects, run_time: float = 0.35):
        valid = [m for m in mobjects if m is not None]
        if valid:
            self.play(
                *[FadeOut(m, shift=DOWN * 0.14) for m in valid],
                run_time=run_time,
                rate_func=rate_functions.ease_in_cubic,
            )

    # ------------------------------------------------------------------
    # ACT 0: Chapter-Opener Roadmap (use cover + contrast card for non-opener eps)
    # ------------------------------------------------------------------
    def act0_intro(self):
        with self.segment("s01_intro") as seg:
            badge = make_badge("EP01 · 第一章 开篇", color=ACCENT_BLUE)
            main_t = zh_text("1-1 核心概念示例", font_size=42, weight=BOLD, color=TEXT_PRIMARY)
            sub_t = zh_text("一句话概括本节核心目标", font_size=20, color=ACCENT_GOLD)
            t_grp = VGroup(badge, main_t, sub_t).arrange(DOWN, buff=0.20).move_to(UP * 1.85)

            self.play(FadeIn(t_grp, shift=UP * 0.2), run_time=0.6)

            roadmap = make_knowledge_map(BOOK_CHAPTERS, highlight_idx=0).move_to(DOWN * 0.85)
            self.pace_to(seg, 0.35)
            self.play(FadeIn(roadmap, shift=UP * 0.15), run_time=0.7)

            self.pace_to(seg, 0.995)
            self.clear_stage(t_grp, roadmap)

    # ------------------------------------------------------------------
    # ACT 1: Definition
    # ------------------------------------------------------------------
    def act1_definition(self):
        with self.segment("s02_definition") as seg:
            self.set_chapter(1)
            hdr = make_section_header("教材核心定义", color=ACCENT_BLUE, y=2.55)
            self.play(FadeIn(hdr, shift=DOWN * 0.1), run_time=0.45)

            def_lines = VGroup(
                zh_tex(r"\textbf{定义 1}：完整写出教材前提条件（如 $x \in \mathbb{R}$ 且非空）", font_size=22, color=TEXT_PRIMARY),
                zh_tex(r"1. 条件一：公式与限定词写全", font_size=21, color=ACCENT_CYAN),
                zh_tex(r"2. 条件二：公式与限定词写全", font_size=21, color=ACCENT_GOLD),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
            card = make_card(def_lines, width=11.6, height=3.2, border_color=ACCENT_BLUE, accent_bar="left")
            card.move_to(DOWN * 0.15)

            self.pace_to(seg, 0.25)
            self.play(FadeIn(card, shift=UP * 0.12), run_time=0.65)

            self.pace_to(seg, 0.995)
            self.clear_stage(hdr, card)

    # ------------------------------------------------------------------
    # ACT 2: Standalone Example + Step-by-Step Animated Solution
    # ------------------------------------------------------------------
    def act2_example1(self):
        with self.segment("s03_example1") as seg:
            self.set_chapter(2)
            hdr = make_section_header("教材例 1 · 完整实战", color=ACCENT_GOLD, y=2.55)
            self.play(FadeIn(hdr, shift=DOWN * 0.1), run_time=0.4)

            # Top card: 100% complete problem statement
            ex_badge = make_badge("教材例 1", color=ACCENT_GOLD, font_size=18)
            q_txt = zh_tex(r"已知 $a = 1,\; b = 2$，求 $a + b$ 的值。", font_size=22, color=TEXT_PRIMARY)
            q_row = VGroup(ex_badge, q_txt).arrange(RIGHT, buff=0.28)
            q_card = make_card(q_row, width=11.8, height=1.05, border_color=ACCENT_GOLD)
            q_card.move_to(UP * 1.45)
            self.play(FadeIn(q_card, shift=UP * 0.1), run_time=0.5)

            # Bottom 3 step cards revealed in sync with narration
            s1 = make_card(zh_tex(r"第一步：代入 $a=1, b=2$", font_size=20, color=ACCENT_BLUE), width=3.6, height=2.2, border_color=ACCENT_BLUE)
            s2 = make_card(zh_tex(r"第二步：化简 $1 + 2$", font_size=20, color=ACCENT_CYAN), width=3.6, height=2.2, border_color=ACCENT_CYAN)
            s3 = make_card(zh_tex(r"第三步：得结果 $= 3$", font_size=20, color=ACCENT_GREEN), width=3.6, height=2.2, border_color=ACCENT_GREEN)
            steps_row = VGroup(s1, s2, s3).arrange(RIGHT, buff=0.42).move_to(DOWN * 0.85)

            self.pace_to(seg, 0.30)
            self.play(FadeIn(s1, shift=UP * 0.12), run_time=0.5)
            self.pace_to(seg, 0.55)
            self.play(FadeIn(s2, shift=UP * 0.12), run_time=0.5)
            self.pace_to(seg, 0.78)
            self.play(FadeIn(s3, shift=UP * 0.12), run_time=0.5)

            self.pace_to(seg, 0.995)
            self.clear_stage(hdr, q_card, steps_row)

    # ------------------------------------------------------------------
    # ACT 3: Summary
    # ------------------------------------------------------------------
    def act3_summary(self):
        with self.segment("s04_summary") as seg:
            self.set_chapter(3)
            hdr = make_section_header("一屏速通卡（建议截图）", color=ACCENT_GREEN, y=2.55)
            self.play(FadeIn(hdr, shift=DOWN * 0.1), run_time=0.45)

            sum_grp = VGroup(
                zh_tex(r"1. 核心定义：前提条件一 + 前提条件二", font_size=22, color=ACCENT_BLUE),
                zh_tex(r"2. 标准解法：代入 $\to$ 化简 $\to$ 结论", font_size=22, color=ACCENT_GOLD),
                zh_tex(r"下集预告：1-2 下一节主题", font_size=21, color=ACCENT_GREEN),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
            card = make_card(sum_grp, width=11.4, height=3.2, border_color=ACCENT_GREEN, accent_bar="top")
            card.move_to(DOWN * 0.15)
            self.play(FadeIn(card, shift=UP * 0.12), run_time=0.6)
            # Keep final summary on screen through end of episode
