#!/usr/bin/env -S python3 -B

import subprocess
import contextlib
import shutil
import zipapp
from pathlib import Path


from typer import Typer

import server.__main__


def sh(cmd, ck=True):
    subprocess.run(cmd, shell=True, check=ck)


root_dir = Path.cwd()
protected_dir = root_dir / "protected"
protected_dist_dir = protected_dir / "dist"
public_dir = root_dir / "public"
public_dist_dir = public_dir / "dist"
dist_dir = root_dir / "dist"
build_dir = root_dir / "build"

cli = Typer()


@cli.command()
def fix():
    sh("python -m black server")
    sh("python -m isort server")
    sh("python -m ruff server --fix", ck=False)
    sh("python -m mypy server", ck=False)


@cli.command()
def clean(
    dry: bool = False,
    build: bool = True,
    dist: bool = True,
    caches: list[str] = ["__pycache__", ".mypy_cache", ".ruff_cache"],
):
    dirs = []
    if build:
        dirs.append(build_dir)
    if dist:
        dirs += [dist_dir, public_dist_dir, protected_dist_dir]

    for pattern in caches:
        for directory in root_dir.rglob(pattern):
            dirs.append(directory)

    if dry:
        print(*dirs, sep="\n")
    else:
        for d in dirs:
            shutil.rmtree(d, ignore_errors=True)


@cli.command()
def buildstatic():
    clean()
    with contextlib.chdir(protected_dir):
        sh("npm ci")
        sh("npm run build")
    with contextlib.chdir(public_dir):
        sh("npm ci")
        sh("npm run build")

    dist_dir.mkdir(exist_ok=True)
    shutil.move(protected_dir / "dist", dist_dir / "protected")
    shutil.move(public_dir / "dist", dist_dir / "public")


@cli.command()
def buildpyz():
    buildstatic()
    build_dir.mkdir(exist_ok=True)
    shutil.copytree(root_dir / "server", build_dir / "server")
    shutil.copytree(dist_dir / "protected", build_dir / "protected")
    shutil.copytree(dist_dir / "public", build_dir / "public")
    sh("python -m poetry export -f requirements.txt --output requirements.txt")
    sh(f"python -m pip install -r requirements.txt -t {build_dir}")
    (root_dir / "requirements.txt").unlink()
    zipapp.create_archive(
        build_dir,
        "aidan.software.pyz",
        interpreter="/usr/bin/env python",
        main="server.__main__:cli",
    )
    shutil.rmtree(build_dir)


if __name__ == "__main__":
    cli()
