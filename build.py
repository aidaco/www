import os
import shutil
import typer
from pathlib import Path
import zipapp

app = typer.Typer()


@app.command()
def build():
    cwd = Path.cwd().resolve()
    public = cwd / "public"
    admin = cwd / "admin"
    service = cwd / "service"
    dist = cwd / "dist"
    pyz = cwd / "aidan.software.pyz"

    os.chdir(public)
    shutil.rmtree(public/"dist")
    os.system("npm run build")

    os.chdir(admin)
    shutil.rmtree(admin/"dist")
    os.system("npm run build")

    os.chdir(cwd)

    dist.mkdir(exist_ok=True)

    shutil.rmtree(dist, ignore_errors=True)
    shutil.copytree(public / "dist", dist / "public")
    shutil.copytree(admin / "dist", dist / "admin")
    shutil.copytree(service, dist / "service")

    zipapp.create_archive(
        source=dist,
        target=pyz,
        interpreter="/usr/bin/env python3",
        main="service.__main__:main",
    )

    print(f"Created {pyz}")


if __name__ == "__main__":
    app()
