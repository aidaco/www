from pathlib import Path

from typer import Typer

from server import auth_backends, config, core

cli = Typer()


@cli.command()
def run():
    core.start()


@cli.command()
def initconfig(path: Path):
    path.write_text("\n".join(config._dataclass_toml_template(config.Config)))


@cli.command()
def hashpwd(text: str):
    hasher = auth_backends.hasher()
    print(hasher.hash(text))


if __name__ == "__main__":
    cli()
