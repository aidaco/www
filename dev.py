#!/usr/bin/env -S python3 -B

import subprocess
import shutil
from pathlib import Path

from typer import Typer


def sh(cmd):
    subprocess.run(cmd, shell=True, check=False)


PROJ_DIR = Path.cwd()
BUILD_DIR = PROJ_DIR / "build"
DIST_DIR = PROJ_DIR / "dist"

cli = Typer()


@cli.command()
def test():
    sh("python -m pytest")


@cli.command()
def fix():
    sh("python -m black .")
    sh("python -m isort .")
    sh("python -m ruff . --fix")


@cli.command()
def check():
    sh("python -m mypy .")


@cli.command()
def clean(
    dry: bool = False,
    dist: bool = True,
    build: bool = True,
    patterns: list[str] = [
        ".mypy_cache",
        ".ruff_cache",
        ".pytest_cache",
        "*.egg-info",
        "**/__pycache__",
    ],
):
    targets = []
    if dist and DIST_DIR.exists():
        targets.append(DIST_DIR)
    if build and BUILD_DIR.exists():
        targets.append(BUILD_DIR)
    for pattern in patterns:
        targets.extend(PROJ_DIR.glob(pattern))

    print(*(target.resolve() for target in targets), sep="\n")

    if dry:
        return

    for target in targets:
        shutil.rmtree(target, ignore_errors=True)


@cli.command()
def build():
    clean()
    sh("python -m build")


if __name__ == "__main__":
    cli()
