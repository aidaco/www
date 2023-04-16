from pathlib import Path

from typer import Typer

from service import core, config, livecontrol, requestdb, staticfiles  # noqa: F401

cli = Typer()


@cli.command()
def run():
    core.start()


@cli.command()
def initconfig(path: Path):
    path.write_text('\n'.join(config._dataclass_toml_template(config.Config)))


if __name__ == "__main__":
    cli()
