from pathlib import Path

from rich import print
from typer import Typer

from server import api, config, auth_base

cli = Typer()


@cli.command()
def run():
    api.run()


@cli.command()
def initconfig(path: Path = Path("aidan.software.toml")):
    path.write_text(
        config.dumps_toml(
            config.Config(
                admin=config.Admin(
                    username=input("Admin username:"),
                    password_hash=auth_base.hash_password(input("Admin password:")),
                ),
                jwt=config.JWT(secret=input("JWT Secret:")),
            )
        )
    )


@cli.command()
def checkconfig(path: Path = Path("aidan.software.toml")):
    print(config.read(path))


if __name__ == "__main__":
    cli()
