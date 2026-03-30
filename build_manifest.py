#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path.home() / "cv"
PORTFOLIO = ROOT / "portfolio"
OUT = ROOT / "manifest.json"

allowed_suffixes = {
    ".png", ".jpg", ".jpeg", ".webp", ".gif",
    ".mp4", ".webm", ".mov", ".m4v",
    ".md", ".txt", ".json"
}

files: list[str] = []

if PORTFOLIO.exists():
    for p in sorted(PORTFOLIO.rglob("*")):
        if p.is_file() and p.suffix.lower() in allowed_suffixes:
            files.append(p.relative_to(ROOT).as_posix())

OUT.write_text(
    json.dumps({"files": files}, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"Wrote {OUT} with {len(files)} files.")
