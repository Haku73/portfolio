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

VIDEO_SUFFIXES = {".mp4", ".webm", ".mov", ".m4v"}


def load_existing_manifest() -> dict[str, dict]:
    """
    Restituisce una mappa:
      path -> metadata esistente (es. {"preview": 8})
    leggendo il manifest attuale.
    """
    if not OUT.exists():
        return {}

    try:
        data = json.loads(OUT.read_text(encoding="utf-8"))
    except Exception:
        return {}

    result: dict[str, dict] = {}

    for item in data.get("files", []):
        if isinstance(item, str):
            result[item] = {}
        elif isinstance(item, dict):
            path = item.get("path")
            if isinstance(path, str) and path:
                meta = {k: v for k, v in item.items() if k != "path"}
                result[path] = meta

    return result


def main() -> None:
    existing = load_existing_manifest()
    files: list[str | dict] = []

    if PORTFOLIO.exists():
        for p in sorted(PORTFOLIO.rglob("*")):
            if not p.is_file():
                continue
            if p.name == ".DS_Store":
                continue
            if p.suffix.lower() not in ALLOWED_SUFFIXES:
                continue

            rel_path = p.relative_to(ROOT).as_posix()
            meta = existing.get(rel_path, {})

            # Se c'è metadata da preservare, scrive oggetto
            if meta:
                entry = {"path": rel_path, **meta}
                files.append(entry)
            else:
                files.append(rel_path)

    OUT.write_text(
        json.dumps({"files": files}, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"Wrote {OUT} with {len(files)} files.")


if __name__ == "__main__":
    main()