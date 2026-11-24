"""
Bootstrap a brand-new Textbook Speedrun Course project in any target directory.
Copies the generalized visual theme, audio-sync engine, TTS/build/QA scripts,
.gitignore, and generates a starter GEMINI.md populated with the user's
onboarding Q&A preferences and custom requirements.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def copy_file(src: Path, dst: Path, force: bool = False):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not force:
        print(f"  = {dst} (exists, skipped)")
        return
    shutil.copy2(src, dst)
    print(f"  + {dst}")


def main():
    parser = argparse.ArgumentParser(description="Initialize a reusable textbook speedrun course repo")
    parser.add_argument("target_dir", help="Target project directory (created if missing)")
    parser.add_argument("--course-name", default="教材速通课", help="Course display name, e.g. '高等数学速通课'")
    parser.add_argument("--pdf", default="", help="Textbook PDF filename (auto-detected in target_dir if omitted)")
    parser.add_argument("--offset", type=int, default=0, help="PDF_page - textbook_page offset (default: 0)")
    parser.add_argument("--voice", default="zh-CN-YunxiNeural", help="edge-tts voice (default: zh-CN-YunxiNeural)")
    parser.add_argument("--rate", default="+8%", help="edge-tts speech rate (default: +8%)")
    parser.add_argument(
        "--style",
        default="直觉 4 : 应试 6（平衡理解与例题实战）",
        help="Teaching style & intuition/exam ratio",
    )
    parser.add_argument(
        "--tone",
        default="平实、干练、准确的讲师口吻（去 AI 味，严禁浮夸网感词句）",
        help="Narration tone & style",
    )
    parser.add_argument(
        "--pacing",
        default="按教材一节一集（常规 4~6 分钟，短节 3 分钟精华版）",
        help="Episode granularity & duration target",
    )
    parser.add_argument(
        "--standalone",
        default="独立成课 + 保留原书题号（画面写全完整题干与定义，不翻书也能看懂）",
        help="Textbook dependency & problem-statement mode",
    )
    parser.add_argument(
        "--quality",
        choices=["h", "m", "l"],
        default="h",
        help="Final video quality flag: h=1080p60 (default), m=720p30, l=480p15",
    )
    parser.add_argument(
        "--custom-reqs",
        default="无额外补充（按默认规范执行）。",
        help="User's free-form custom requirements",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing scaffold files")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parent.parent
    tpl_root = skill_root / "resources" / "templates"
    target = Path(args.target_dir).resolve()
    target.mkdir(parents=True, exist_ok=True)

    # Auto-detect PDF in target directory if not provided
    book_filename = args.pdf
    if not book_filename:
        pdfs = sorted(target.glob("*.pdf"))
        if pdfs:
            book_filename = pdfs[0].name
            print(f"[INIT] Auto-detected textbook PDF: {book_filename}")
        else:
            book_filename = "<请放入教材.pdf>"

    quality_labels = {
        "h": "1080p 60fps（高清成片）+ 逐字内嵌字幕",
        "m": "720p 30fps（快速轻量）+ 逐字内嵌字幕",
        "l": "480p 15fps（极速预览）+ 逐字内嵌字幕",
    }

    print(f"[INIT] Bootstrapping '{args.course_name}' in {target} ...")

    # 1. Copy common/
    for name in ("__init__.py", "audio_sync.py", "theme.py"):
        copy_file(tpl_root / "common" / name, target / "common" / name, force=args.force)

    # 2. Copy scripts/ (core builders + PDF reader + preview extractor)
    for name in ("tts_gen.py", "build_ep.py"):
        copy_file(tpl_root / "scripts" / name, target / "scripts" / name, force=args.force)
    for name in ("read_pdf.py", "extract_preview.py"):
        copy_file(skill_root / "scripts" / name, target / "scripts" / name, force=args.force)

    # 3. Copy .gitignore
    copy_file(tpl_root / "gitignore.template", target / ".gitignore", force=args.force)

    # 4. Generate GEMINI.md with user's preferences
    gemini_dst = target / "GEMINI.md"
    if gemini_dst.exists() and not args.force:
        print(f"  = {gemini_dst} (exists, skipped)")
    else:
        tpl_text = (tpl_root / "GEMINI.md.template").read_text(encoding="utf-8")
        rendered = (
            tpl_text
            .replace("{COURSE_NAME}", args.course_name)
            .replace("{BOOK_FILENAME}", book_filename)
            .replace("{PAGE_OFFSET}", str(args.offset))
            .replace("{VOICE}", args.voice)
            .replace("{RATE}", args.rate)
            .replace("{TEACHING_STYLE}", args.style)
            .replace("{NARRATION_TONE}", args.tone)
            .replace("{PACING_RULE}", args.pacing)
            .replace("{STANDALONE_MODE}", args.standalone)
            .replace("{VIDEO_QUALITY}", quality_labels[args.quality])
            .replace("{QUALITY_FLAG}", args.quality)
            .replace("{CUSTOM_REQUIREMENTS}", args.custom_reqs.strip() or "无额外补充（按默认规范执行）。")
        )
        gemini_dst.write_text(rendered, encoding="utf-8")
        print(f"  + {gemini_dst}")

    # 5. Create episodes/ directory
    (target / "episodes").mkdir(parents=True, exist_ok=True)

    print("\n[DONE] Project scaffold ready! Next steps:")
    print(f'  1. Inspect textbook TOC: python scripts\\read_pdf.py "{book_filename}" --toc')
    print("  2. Determine page offset (PDF_page - textbook_page) and fill episode table in GEMINI.md")
    print("  3. Start producing EP01 under episodes/ep01_1_1_slug/")


if __name__ == "__main__":
    main()
