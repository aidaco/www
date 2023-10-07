from pathlib import Path

from rich import print
from typer import Typer

from server import api, config

cli = Typer()


@cli.command()
def run():
    api.run()


@cli.command()
def initconfig(path: Path = Path("aidan.software.toml")):
    config.create(
        input("Admin username:"), input("Admin password:"), input("JWT secret:"), path
    )


@cli.command()
def checkconfig(path: Path = Path("aidan.software.toml")):
    print(config.read(path))


if __name__ == "__main__":
    cli()
