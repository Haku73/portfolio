#!/usr/bin/env python3
import shutil
import subprocess
import sys
from pathlib import Path
import time

REPO_ROOT = Path(__file__).resolve().parent
MANIFEST_SCRIPT = REPO_ROOT / "build_manifest.py"

# === CONFIGURA QUI ===
OFFICIAL_REMOTE = "origin"
OFFICIAL_BRANCH = "main"

# preview: puoi usare un secondo remote oppure un secondo branch
PREVIEW_REMOTE = "preview"
PREVIEW_BRANCH = "main"

# cartella/file del CV latex
CV_TEX = REPO_ROOT / "cv.tex"
CV_PDF = REPO_ROOT / "cv.pdf"
# =====================


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


def ensure_latex() -> None:
    if not CV_TEX.exists():
        print(f"❌ File LaTeX non trovato: {CV_TEX}")
        sys.exit(1)

    if shutil.which("latexmk") is None and shutil.which("pdflatex") is None:
        print("❌ Non trovo né latexmk né pdflatex nel sistema.")
        sys.exit(1)


def git_commit_if_needed(message: str) -> None:
    run("git add -A")
    run(f'git commit -m "{message}" || echo "nothing to commit"')


def update_official() -> None:
    if not confirm("⚠️ Stai per aggiornare il sito OFFICIAL. Continuare?"):
        print("❌ Operazione annullata")
        return

    ensure_manifest()
    git_commit_if_needed("update portfolio")
    run(f"git push {OFFICIAL_REMOTE} {OFFICIAL_BRANCH}")

def update_preview() -> None:
    ensure_manifest()
    git_commit_if_needed("update portfolio preview")
    run(f"git push {PREVIEW_REMOTE} {PREVIEW_BRANCH}")


def force_push_local_to_official() -> None:
    if not confirm("⚠️ Sovrascrivere COMPLETAMENTE il remoto OFFICIAL con il locale?"):
        return

    ensure_manifest()
    run("git checkout --orphan clean-main")
    run("git add -A")
    run('git commit -m "force sync from local to official"')
    run("git branch -D main")
    run("git branch -m main")
    run(f"git push {OFFICIAL_REMOTE} {OFFICIAL_BRANCH} --force")


def force_push_local_to_preview() -> None:
    if not confirm("⚠️ Sovrascrivere COMPLETAMENTE il remoto PREVIEW con il locale?"):
        return

    ensure_manifest()
    run("git checkout --orphan clean-main")
    run("git add -A")
    run('git commit -m "force sync from local to preview"')
    run("git branch -D main")
    run("git branch -m main")
    run(f"git push {PREVIEW_REMOTE} {PREVIEW_BRANCH} --force")


def force_pull_official_to_local() -> None:
    if not confirm("⚠️ Sovrascrivere COMPLETAMENTE il locale con OFFICIAL?"):
        return

    run(f"git fetch {OFFICIAL_REMOTE}")
    run(f"git reset --hard {OFFICIAL_REMOTE}/{OFFICIAL_BRANCH}")
    run("git clean -fd")


def promote_preview_to_official() -> None:
    if not confirm("⚠️ Promuovere PREVIEW -> OFFICIAL sovrascrivendo il sito ufficiale?"):
        return

    # Push dello stato locale attuale su official.
    # L'idea è: pubblichi e testi su preview, poi quando va bene lanci questo.
    ensure_manifest()
    git_commit_if_needed("promote preview to official")
    run(f"git push {OFFICIAL_REMOTE} {OFFICIAL_BRANCH} --force")


def build_cv_pdf() -> None:
    ensure_latex()

    if shutil.which("latexmk") is not None:
        run(f'latexmk -pdf -interaction=nonstopmode -halt-on-error "{CV_TEX.name}"')
    else:
        run(f'pdflatex -interaction=nonstopmode "{CV_TEX.name}"')
        run(f'pdflatex -interaction=nonstopmode "{CV_TEX.name}"')

    if not CV_PDF.exists():
        print(f"❌ PDF non generato: {CV_PDF}")
        sys.exit(1)

    print(f"\n✅ PDF generato: {CV_PDF}")


def open_cv_pdf() -> None:
    if not CV_PDF.exists():
        print(f"❌ PDF non trovato: {CV_PDF}")
        sys.exit(1)

    if sys.platform == "darwin":
        run(f'open "{CV_PDF.name}"')
    else:
        print(f"✅ PDF pronto: {CV_PDF}")

def cache_busted(url: str) -> str:
    return f"{url}?nocache={int(time.time())}"

def open_preview_site() -> None:
    url = "https://haku73.github.io/portfolio-preview/"
    if sys.platform == "darwin":
        run(f'open "{cache_busted(url)}"')
    else:
        print(f"Apri manualmente: {url}")


def open_official_site() -> None:
    url = "https://haku73.github.io/portfolio/"
    if sys.platform == "darwin":
        run(f'open "{cache_busted(url)}"')
    else:
        print(f"Apri manualmente: {url}")

def open_cv_tex() -> None:
    if not CV_TEX.exists():
        print(f"❌ File LaTeX non trovato: {CV_TEX}")
        sys.exit(1)

    if sys.platform == "darwin":
        run(f'open "{CV_TEX.name}"')
    else:
        print(f"✅ File TeX pronto: {CV_TEX}")

def build_and_open_cv() -> None:
    build_cv_pdf()
    open_cv_pdf()


def show_status() -> None:
    run("git status --short")
    manifest_path = REPO_ROOT / "manifest.json"
    if manifest_path.exists():
        print(f"\n✅ manifest.json trovato: {manifest_path}")
    else:
        print("\n⚠️ manifest.json non trovato")

    print(f"\nRepo root: {REPO_ROOT}")
    print(f"Official -> {OFFICIAL_REMOTE}/{OFFICIAL_BRANCH}")
    print(f"Preview  -> {PREVIEW_REMOTE}/{PREVIEW_BRANCH}")
    print(f"CV tex   -> {CV_TEX}")
    print(f"CV pdf   -> {CV_PDF}")

def menu() -> None:
    while True:
        print("1) Aggiorna OFFICIAL (manifest + commit + push)")
        print("2) Aggiorna PREVIEW (manifest + commit + push)")
        print("3) Sovrascrivi OFFICIAL con LOCALE (force push)")
        print("4) Sovrascrivi PREVIEW con LOCALE (force push)")
        print("5) Sovrascrivi LOCALE con OFFICIAL")
        print("6) Promuovi PREVIEW -> OFFICIAL")
        print("7) Rigenera manifest.json")
        print("==========================")
        print("8) Apri file CV LaTeX")
        print("9) Compila CV LaTeX -> PDF")
        print("10) Compila CV LaTeX -> PDF e apri PDF")
        print("11) Apri PDF CV esistente")
        print("==========================")
        print("12) Apri sito PREVIEW")
        print("13) Apri sito OFFICIAL")
        print("==========================")
        print("14) Mostra stato repo")
        print("==========================")
        print("0) Esci\n")
        
        choice = input("Scelta: ").strip()

        if choice == "1":
            update_official()
        elif choice == "2":
            update_preview()
        elif choice == "3":
            force_push_local_to_official()
        elif choice == "4":
            force_push_local_to_preview()
        elif choice == "5":
            force_pull_official_to_local()
        elif choice == "6":
            promote_preview_to_official()
        elif choice == "7":
            ensure_manifest()
        elif choice == "8":
            open_cv_tex()
        elif choice == "9":
            build_cv_pdf()
        elif choice == "10":
            build_and_open_cv()
        elif choice == "11":
            open_cv_pdf()
        elif choice == "12":
            open_preview_site()
        elif choice == "13":
            open_official_site()
        elif choice == "14":
            show_status()
        elif choice == "0":
            print("👋 Uscita")
            sys.exit(0)
        else:
            print("❌ Scelta non valida")

        input("\nPremi invio per tornare al menu...")
                
if __name__ == "__main__":
    ensure_git_repo()
    menu()
