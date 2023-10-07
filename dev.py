#!/usr/bin/env -S python3 -B

import subprocess
import contextlib
import shutil
import zipapp
from pathlib import Path
import tempfile

from typer import Typer


def sh(cmd, ck=True):
    subprocess.run(cmd, shell=True, check=ck)


root_dir = Path.cwd()
dist_dir = root_dir / 'dist'
cache_dirs = [
    root_dir/'.mypy_cache',
    root_dir/'.ruff_cache',
    root_dir/'.pytest_cache',
    *root_dir.glob('*.egg-info'),
    *root_dir.rglob("__pycache__"),
]

cli = Typer()


@cli.command()
def test():
    sh("python -m pytest")


@cli.command()
def fix():
    sh("python -m black server")
    sh("python -m isort server")
    sh("python -m ruff server --fix", ck=False)


@cli.command()
def check():
    sh("python -m mypy server", ck=False)


@cli.command()
def clean(
    dry: bool = False,
    dist: bool = True,
    caches: bool = True,
):
    dirs = []
    if dist:
        dirs.append(dist_dir)
    if caches:
        dirs.extend(cache_dirs)

    if dry:
        print(*dirs, sep="\n")
        return
    for d in dirs:
        shutil.rmtree(d, ignore_errors=True)


@cli.command()
def build():
    clean()
    sh('python -m build')


if __name__ == "__main__":
    cli()
