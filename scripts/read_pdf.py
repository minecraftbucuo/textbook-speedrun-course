"""
Inspect a textbook PDF using PyMuPDF (fitz):
- Print embedded TOC / bookmarks (`--toc`)
- Dump textbook pages with automatic page-offset translation (`--pages 1-7 --offset 7`)
- Search keywords across the book (`--search "特征值"`)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import fitz


def parse_page_range(spec: str) -> list[int]:
    pages: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            pages.extend(range(int(a), int(b) + 1))
        else:
            pages.append(int(part))
    return pages


def main():
    parser = argparse.ArgumentParser(description="Textbook PDF reader for speedrun courses")
    parser.add_argument("pdf", help="Path to the textbook PDF file")
    parser.add_argument("--toc", action="store_true", help="Print PDF bookmarks / table of contents")
    parser.add_argument("--pages", help="Page numbers or ranges, e.g. '1-7' or '12,14-16'")
    parser.add_argument("--offset", type=int, default=0, help="PDF_page = textbook_page + offset")
    parser.add_argument("--search", help="Search keyword across all pages")
    parser.add_argument("--max-chars", type=int, default=4000, help="Max chars printed per page")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"[ERROR] PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    doc = fitz.open(str(pdf_path))
    print(f"[PDF] {pdf_path.name} | Total PDF pages: {len(doc)}")

    if args.toc:
        toc = doc.get_toc()
        if not toc:
            print("[TOC] No embedded bookmarks found. Inspect front-matter pages with `--pages 1-15 --offset 0`.")
        else:
            print(f"[TOC] {len(toc)} entries:")
            for level, title, page in toc:
                indent = "  " * (level - 1)
                book_p = f" (book p.{page - args.offset})" if args.offset else ""
                print(f"{indent}- {title}  [PDF p.{page}{book_p}]")

    if args.search:
        kw = args.search
        hits = 0
        for idx in range(len(doc)):
            txt = doc[idx].get_text()
            if kw in txt:
                hits += 1
                pdf_p = idx + 1
                book_p = f" / book p.{pdf_p - args.offset}" if args.offset else ""
                pos = txt.find(kw)
                snippet = txt[max(0, pos - 40): pos + 80].replace("\n", " ")
                print(f"  [PDF p.{pdf_p}{book_p}] ...{snippet}...")
                if hits >= 30:
                    print("  (truncated at 30 hits)")
                    break
        if hits == 0:
            print(f"[SEARCH] No matches for '{kw}'.")

    if args.pages:
        for p in parse_page_range(args.pages):
            pdf_p = p + args.offset
            if pdf_p < 1 or pdf_p > len(doc):
                print(f"[WARN] Textbook p.{p} -> PDF p.{pdf_p} out of range (1..{len(doc)})")
                continue
            txt = doc[pdf_p - 1].get_text().strip()
            header = f"=== Book p.{p} (PDF p.{pdf_p}) ===" if args.offset else f"=== PDF p.{pdf_p} ==="
            print(f"\n{header}")
            if len(txt) > args.max_chars:
                print(txt[:args.max_chars] + "\n... [truncated]")
            else:
                print(txt)


if __name__ == "__main__":
    main()
