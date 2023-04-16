#!/usr/bin/env -S python -B

import subprocess
import contextlib
import shutil
import zipapp
from pathlib import Path


from typer import Typer


def sh(cmd):
    subprocess.run(cmd, shell=True, check=True)


root_dir = Path.cwd()
admin_dir = root_dir / "admin"
public_dir = root_dir / "public"
dist_dir = root_dir / "dist"

cli = Typer()


@cli.command()
def clean():
    shutil.rmtree(dist_dir, ignore_errors=True)
    shutil.rmtree(admin_dir / "dist", ignore_errors=True)
    shutil.rmtree(public_dir / "dist", ignore_errors=True)


@cli.command()
def build():
    clean()
    with contextlib.chdir(admin_dir):
        sh("npm run build")
    with contextlib.chdir(public_dir):
        sh("npm run build")

    dist_dir.mkdir()
    shutil.move(admin_dir / "dist", dist_dir / "admin")
    shutil.move(public_dir / "dist", dist_dir / "public")


if __name__ == "__main__":
    cli()
