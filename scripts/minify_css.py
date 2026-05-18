#!/usr/bin/env python3
"""Minify static/css/style.css -> static/css/style.min.css for production."""
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "static" / "css"
SRC = BASE / "style.css"
DST = BASE / "style.min.css"


def minify_css(text: str) -> str:
    try:
        import rcssmin
        return rcssmin.cssmin(text)
    except ImportError:
        # Fallback: strip comments and extra whitespace
        import re
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\s*([{}:;,>+~])\s*", r"\1", text)
        return text.strip()


def main():
    if not SRC.exists():
        print(f"Skip: {SRC} not found")
        return
    raw = SRC.read_text(encoding="utf-8")
    out = minify_css(raw)
    DST.write_text(out, encoding="utf-8")
    pct = 100 - (len(out) * 100 // max(len(raw), 1))
    print(f"CSS minified: {len(raw):,} -> {len(out):,} bytes (~{pct}% smaller) -> {DST.name}")


if __name__ == "__main__":
    main()
