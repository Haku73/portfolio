#!/usr/bin/env python3
import subprocess
import sys


def run(cmd):
    print(f"\n>>> {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print("❌ Errore comando")
        sys.exit(1)


def confirm(msg):
    ans = input(f"{msg} (yes/no): ").strip().lower()
    return ans == "yes"


def update_normal():
    run("git add -A")
    run('git commit -m "update portfolio" || echo "nothing to commit"')
    run("git push origin main")


def force_push_local_to_remote():
    if not confirm("⚠️ Sovrascrivere COMPLETAMENTE il remoto con il locale?"):
        return

    run("git checkout --orphan clean-main")
    run("git add -A")
    run('git commit -m "force sync from local"')
    run("git branch -D main")
    run("git branch -m main")
    run("git push origin main --force")


def force_pull_remote_to_local():
    if not confirm("⚠️ Sovrascrivere COMPLETAMENTE il locale con il remoto?"):
        return

    run("git fetch origin")
    run("git reset --hard origin/main")
    run("git clean -fd")


def menu():
    print("\n=== PORTFOLIO SYNC TOOL ===\n")
    print("1) Aggiorna normalmente (commit + push)")
    print("2) Sovrascrivi REMOTO con LOCALE (force push)")
    print("3) Sovrascrivi LOCALE con REMOTO (force pull)")
    print("0) Esci\n")

    choice = input("Scelta: ").strip()

    if choice == "1":
        update_normal()
    elif choice == "2":
        force_push_local_to_remote()
    elif choice == "3":
        force_pull_remote_to_local()
    elif choice == "0":
        sys.exit(0)
    else:
        print("Scelta non valida")


if __name__ == "__main__":
    menu()