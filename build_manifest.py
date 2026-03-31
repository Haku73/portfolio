#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path.home() / "cv"
PORTFOLIO = ROOT / "portfolio"
OUT = ROOT / "manifest.json"

ALLOWED_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".webp", ".gif",
    ".mp4", ".webm", ".mov", ".m4v",
    ".md", ".txt", ".json"
}


def load_existing_manifest():
    if not OUT.exists():
        return []

    try:
        data = json.loads(OUT.read_text(encoding="utf-8"))
        return data.get("files", [])
    except Exception:
        return []


def scan_files():
    found = []
    if PORTFOLIO.exists():
        for p in sorted(PORTFOLIO.rglob("*")):
            if not p.is_file():
                continue
            if p.name == ".DS_Store":
                continue
            if p.suffix.lower() not in ALLOWED_SUFFIXES:
                continue
            found.append(p.relative_to(ROOT).as_posix())
    return found


def main():
    existing_entries = load_existing_manifest()
    scanned_paths = scan_files()
    scanned_set = set(scanned_paths)

    # 1. conserva gli entry esistenti ancora validi, nello stesso ordine
    result = []
    already_added = set()

    for entry in existing_entries:
        if isinstance(entry, str):
            path = entry
            if path in scanned_set:
                result.append(path)
                already_added.add(path)
        elif isinstance(entry, dict):
            path = entry.get("path")
            if isinstance(path, str) and path in scanned_set:
                result.append(entry)
                already_added.add(path)

    # 2. aggiungi eventuali nuovi file non ancora presenti
    for path in scanned_paths:
        if path not in already_added:
            result.append(path)

    OUT.write_text(
        json.dumps({"files": result}, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"Wrote {OUT} with {len(result)} files.")


if __name__ == "__main__":
    main()