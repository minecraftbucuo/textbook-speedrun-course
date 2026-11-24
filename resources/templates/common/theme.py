"""
Studio Visual Theme (v2) for Textbook Speedrun Courses.
Features:
- Clean ambient studio dot-grid backdrop
- Layered glass-style cards with subtle outer glow & optional accent strip
- Animated chapter progress bar in the top HUD
- Crisp XeLaTeX mixed Chinese + Math rendering (zero tofu)
- Auto-fitting horizontal course roadmap for any number of chapters
"""

import re
from manim import *

# =============================================================================
# Color Palette (Deep Cinema Slate - 3B1B x Apple Keynote)
# =============================================================================
BG_COLOR = "#0B1120"         # Richer deep midnight navy
SURFACE_COLOR = "#131C31"    # Elevated dark slate card fill
SURFACE_ELEV = "#1A2540"     # Highlighted card fill
BORDER_COLOR = "#2A3955"     # Refined subtle border
TEXT_PRIMARY = "#F8FAFC"     # Crisp off-white
TEXT_MUTED = "#94A3B8"       # Muted slate gray

ACCENT_BLUE = "#38BDF8"      # Sky blue: primary concept / input / highlight A
ACCENT_GOLD = "#FBBF24"      # Amber gold: emphasis / key takeaway / highlight B
ACCENT_GREEN = "#34D399"     # Emerald green: result / conclusion / verified
ACCENT_RED = "#F87171"       # Coral red: pitfall / warning / counterexample
ACCENT_PURPLE = "#A78BFA"    # Soft violet: intuition / geometry / abstraction
ACCENT_CYAN = "#22D3EE"      # Bright cyan: progress & secondary highlight

FONT_ZH = "Noto Sans SC"

# =============================================================================
# LaTeX / XeLaTeX Templates
# =============================================================================
def get_math_tex_template() -> TexTemplate:
    return TexTemplate(
        preamble=r"""
\usepackage[english]{babel}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{xcolor}
""",
    )


def get_zh_tex_template() -> TexTemplate:
    return TexTemplate(
        tex_compiler="xelatex",
        output_format=".xdv",
        preamble=r"""
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{xcolor}
\usepackage{xeCJK}
\setCJKmainfont{Noto Sans SC}
""",
    )


MATH_TEX_TEMPLATE = get_math_tex_template()
ZH_TEX_TEMPLATE = get_zh_tex_template()


# =============================================================================
# Ambient Studio Backdrop
# =============================================================================
def make_studio_backdrop() -> VGroup:
    """Clean, subtle dot matrix backdrop (no distracting glow circles)."""
    bg_group = VGroup()

    dots = VGroup()
    for x in range(-6, 7):
        for y in range(-3, 4):
            dots.add(
                Dot(
                    point=[x * 1.05, y * 1.05, 0],
                    radius=0.016,
                    color="#475569",
                    fill_opacity=0.28,
                )
            )
    bg_group.add(dots)
    bg_group.set_z_index(-100)
    return bg_group


# =============================================================================
# Typography Helpers
# =============================================================================
def zh_text(
    text: str,
    font_size: int = 28,
    color=TEXT_PRIMARY,
    weight=NORMAL,
    **kwargs,
) -> Text:
    return Text(
        text,
        font=FONT_ZH,
        font_size=font_size,
        color=color,
        weight=weight,
        **kwargs,
    )


def _normalize_tex_colors(s: str) -> str:
    return re.sub(r"\\color\{#([0-9A-Fa-f]{6})\}", r"\\textcolor[HTML]{\1}", s)


def zh_tex(tex_string: str, font_size: int = 30, color=TEXT_PRIMARY, **kwargs) -> Tex:
    """Render mixed Chinese + inline $math$ using XeLaTeX (zero tofu)."""
    fixed = _normalize_tex_colors(tex_string)
    if "tex_template" not in kwargs:
        kwargs["tex_template"] = ZH_TEX_TEMPLATE
    return Tex(
        fixed,
        font_size=font_size,
        color=color,
        **kwargs,
    )


def math_tex(*tex_strings, font_size: int = 38, color=TEXT_PRIMARY, **kwargs) -> MathTex:
    fixed = tuple(_normalize_tex_colors(s) for s in tex_strings)
    has_cjk = any(any("\u4e00" <= ch <= "\u9fff" for ch in s) for s in fixed)
    if "tex_template" not in kwargs:
        kwargs["tex_template"] = ZH_TEX_TEMPLATE if has_cjk else MATH_TEX_TEMPLATE
    return MathTex(
        *fixed,
        font_size=font_size,
        color=color,
        **kwargs,
    )


# =============================================================================
# Reusable Studio UI Components
# =============================================================================
def make_card(
    content: Mobject,
    width: float = None,
    height: float = None,
    pad_x: float = 0.45,
    pad_y: float = 0.32,
    border_color=BORDER_COLOR,
    fill_color=SURFACE_COLOR,
    fill_opacity: float = 0.90,
    corner_radius: float = 0.18,
    stroke_width: float = 1.8,
    accent_bar: str | None = None,  # "top" | "left" | None
    glow: bool = True,
) -> VGroup:
    w = width if width is not None else content.width + 2 * pad_x
    h = height if height is not None else content.height + 2 * pad_y

    layers = VGroup()

    if glow and border_color != BORDER_COLOR:
        outer_glow = RoundedRectangle(
            width=w + 0.08,
            height=h + 0.08,
            corner_radius=corner_radius + 0.03,
            fill_opacity=0,
            stroke_color=border_color,
            stroke_width=5.5,
            stroke_opacity=0.14,
        )
        layers.add(outer_glow)

    box = RoundedRectangle(
        width=w,
        height=h,
        corner_radius=corner_radius,
        fill_color=fill_color,
        fill_opacity=fill_opacity,
        stroke_color=border_color,
        stroke_width=stroke_width,
        stroke_opacity=0.88,
    )
    layers.add(box)

    if accent_bar == "top":
        bar = RoundedRectangle(
            width=w * 0.42,
            height=0.06,
            corner_radius=0.03,
            fill_color=border_color,
            fill_opacity=0.95,
            stroke_width=0,
        ).move_to(box.get_top() + DOWN * 0.03)
        layers.add(bar)
    elif accent_bar == "left":
        bar = RoundedRectangle(
            width=0.075,
            height=h * 0.62,
            corner_radius=0.035,
            fill_color=border_color,
            fill_opacity=0.95,
            stroke_width=0,
        ).move_to(box.get_left() + RIGHT * 0.04)
        layers.add(bar)

    content.move_to(box.get_center())
    layers.add(content)
    return layers


def make_badge(
    label: str,
    color=ACCENT_BLUE,
    font_size: int = 20,
    fill_opacity: float = 0.16,
) -> VGroup:
    txt = zh_text(label, font_size=font_size, color=color, weight=BOLD)
    w = txt.width + 0.42
    h = txt.height + 0.22
    glow = RoundedRectangle(
        width=w + 0.06,
        height=h + 0.06,
        corner_radius=0.18,
        fill_opacity=0,
        stroke_color=color,
        stroke_width=4.0,
        stroke_opacity=0.14,
    )
    box = RoundedRectangle(
        width=w,
        height=h,
        corner_radius=0.16,
        fill_color=color,
        fill_opacity=fill_opacity,
        stroke_color=color,
        stroke_width=1.5,
    )
    txt.move_to(box.get_center())
    return VGroup(glow, box, txt)


def make_section_header(title_text: str, color=ACCENT_BLUE, y: float = 2.60) -> VGroup:
    """Sleek section title with subtle accent underline."""
    t = zh_text(title_text, font_size=30, color=color, weight=BOLD)
    line = Line(LEFT * (t.width * 0.35), RIGHT * (t.width * 0.35), stroke_width=3.0)
    line.set_color_by_gradient(color, ACCENT_CYAN if color != ACCENT_GOLD else ACCENT_GOLD)
    line.next_to(t, DOWN, buff=0.10)
    return VGroup(t, line).move_to(UP * y)


def make_top_hud(ep_tag: str, ep_title: str, chapters: list[str], active_idx: int = 0) -> VGroup:
    """Top persistent studio header bar with glowing progress track."""
    tag = make_badge(ep_tag, color=ACCENT_BLUE, font_size=18)
    title = zh_text(ep_title, font_size=22, color=TEXT_PRIMARY, weight=BOLD)
    left = VGroup(tag, title).arrange(RIGHT, buff=0.18)
    left.to_edge(LEFT, buff=0.45).set_y(3.60)

    pills = VGroup()
    for i, name in enumerate(chapters):
        is_active = i == active_idx
        is_done = i < active_idx
        c = ACCENT_GOLD if is_active else (ACCENT_BLUE if is_done else TEXT_MUTED)
        w = BOLD if is_active else NORMAL
        t = zh_text(name, font_size=16, color=c, weight=w)
        if is_active:
            dot = Dot(radius=0.045, color=ACCENT_GOLD).next_to(t, LEFT, buff=0.07)
            underline = Line(
                t.get_left() + DOWN * 0.16,
                t.get_right() + DOWN * 0.16,
                color=ACCENT_GOLD,
                stroke_width=2.6,
            )
            pills.add(VGroup(dot, t, underline))
        else:
            pills.add(t)
    pills.arrange(RIGHT, buff=0.28)
    pills.to_edge(RIGHT, buff=0.45).set_y(3.60)

    # Full-width subtle track + glowing progress fill
    track_left = LEFT * 6.75 + UP * 3.24
    track_right = RIGHT * 6.75 + UP * 3.24
    track = Line(track_left, track_right, color=BORDER_COLOR, stroke_width=1.6)

    frac = (active_idx + 1) / max(1, len(chapters))
    prog_end = interpolate(track_left, track_right, frac)
    prog = Line(track_left, prog_end, stroke_width=2.8)
    prog.set_color_by_gradient(ACCENT_BLUE, ACCENT_CYAN, ACCENT_GOLD)

    return VGroup(left, pills, track, prog)


def make_knowledge_map(
    chapters_all: list[tuple[str, str]],
    highlight_idx: int = 0,
    max_width: float = 12.6,
) -> VGroup:
    """
    Horizontal course roadmap that automatically fits any number of chapters
    inside the safe canvas width (x in [-6.4, +6.4]).
    """
    n = max(1, len(chapters_all))
    buff = 0.38 if n <= 5 else 0.28
    card_w = min(2.28, (max_width - (n - 1) * buff) / n)
    tag_fs = 18 if n <= 5 else 16
    name_fs = 19 if n <= 5 else 16

    nodes = VGroup()
    for i, (tag, name) in enumerate(chapters_all):
        active = i == highlight_idx
        c = ACCENT_BLUE if active else BORDER_COLOR
        tc = TEXT_PRIMARY if active else TEXT_MUTED
        fill_op = 0.96 if active else 0.55

        t1 = zh_text(tag, font_size=tag_fs, color=ACCENT_GOLD if active else TEXT_MUTED, weight=BOLD)
        t2 = zh_text(name, font_size=name_fs, color=tc, weight=BOLD if active else NORMAL)
        if t2.width > card_w - 0.24:
            t2.scale_to_fit_width(card_w - 0.24)
        inner = VGroup(t1, t2).arrange(DOWN, buff=0.08)
        card = make_card(
            inner,
            width=card_w,
            height=1.12,
            border_color=c,
            fill_color="#172554" if active else SURFACE_COLOR,
            fill_opacity=fill_op,
            stroke_width=2.4 if active else 1.2,
            accent_bar="top" if active else None,
            glow=active,
        )
        nodes.add(card)

    nodes.arrange(RIGHT, buff=buff)
    arrows = VGroup()
    for i in range(len(nodes) - 1):
        arr = Arrow(
            nodes[i].get_right() + RIGHT * 0.02,
            nodes[i + 1].get_left() + LEFT * 0.02,
            buff=0.02,
            stroke_width=2.4,
            max_tip_length_to_length_ratio=0.35,
            color=ACCENT_BLUE if i == highlight_idx else TEXT_MUTED,
        )
        arrows.add(arr)

    group = VGroup(nodes, arrows).move_to(ORIGIN)
    if group.width > max_width:
        group.scale_to_fit_width(max_width)
    return group
