#!/usr/bin/env python3
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
MANIFEST_SCRIPT = REPO_ROOT / "build_manifest.py"


def run(cmd: str) -> None:
    print(f"\n>>> {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=REPO_ROOT)
    if result.returncode != 0:
        print("❌ Errore comando")
        sys.exit(1)


def confirm(msg: str) -> bool:
    ans = input(f"{msg} (yes/no): ").strip().lower()
    return ans == "yes"


def ensure_git_repo() -> None:
    if not (REPO_ROOT / ".git").exists():
        print(f"❌ Questa cartella non sembra un repo Git: {REPO_ROOT}")
        sys.exit(1)


def ensure_manifest() -> None:
    if MANIFEST_SCRIPT.exists():
        print("\n>>> Rigenero manifest.json")
        run(f'"{sys.executable}" "{MANIFEST_SCRIPT.name}"')
    else:
        print("\n⚠️ build_manifest.py non trovato: salto rigenerazione manifest.json")


def update_normal() -> None:
    ensure_manifest()
    run("git add -A")
    run('git commit -m "update portfolio" || echo "nothing to commit"')
    run("git push origin main")


def force_push_local_to_remote() -> None:
    if not confirm("⚠️ Sovrascrivere COMPLETAMENTE il remoto con il locale?"):
        return

    ensure_manifest()
    run("git checkout --orphan clean-main")
    run("git add -A")
    run('git commit -m "force sync from local"')
    run("git branch -D main")
    run("git branch -m main")
    run("git push origin main --force")


def force_pull_remote_to_local() -> None:
    if not confirm("⚠️ Sovrascrivere COMPLETAMENTE il locale con il remoto?"):
        return

    run("git fetch origin")
    run("git reset --hard origin/main")
    run("git clean -fd")


def show_status() -> None:
    run("git status --short")
    manifest_path = REPO_ROOT / "manifest.json"
    if manifest_path.exists():
        print(f"\n✅ manifest.json trovato: {manifest_path}")
    else:
        print("\n⚠️ manifest.json non trovato")


def menu() -> None:
    print("\n=== PORTFOLIO SYNC TOOL ===\n")
    print("1) Aggiorna normalmente (rigenera manifest + commit + push)")
    print("2) Sovrascrivi REMOTO con LOCALE (rigenera manifest + force push)")
    print("3) Sovrascrivi LOCALE con REMOTO (force pull)")
    print("4) Mostra stato repo")
    print("0) Esci\n")

    choice = input("Scelta: ").strip()

    if choice == "1":
        update_normal()
    elif choice == "2":
        force_push_local_to_remote()
    elif choice == "3":
        force_pull_remote_to_local()
    elif choice == "4":
        show_status()
    elif choice == "0":
        sys.exit(0)
    else:
        print("Scelta non valida")
        sys.exit(1)


if __name__ == "__main__":
    ensure_git_repo()
    menu()