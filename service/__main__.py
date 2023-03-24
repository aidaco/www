import logging
from datetime import timedelta
from pathlib import Path
from typing import Callable, Literal

import typer

from . import core, livecontrol, requestdb, staticfiles  # noqa: F401

cli = typer.Typer()


@cli.command()
def main(
    username: str,
    password_hash: str,
    jwt_secret: str,
    jwt_expire: timedelta = timedelta(days=30),
    cache_static: bool = True,
    precache_static: bool = False,
    content: Path = Path.cwd() / "content",
    bind: str = "0.0.0.0",
    hostname: str | None = None,
    port: int = 8000,
    log_level: int = logging.INFO,
    log_path: Path = Path.cwd() / "log.log",
    log_to: Literal["stdout", "file"] = "stdout",
):
    core.config.log.level = log_level
    core.config.log.output = log_to
    core.config.log.file = log_path
    core.config.auth.username = username
    core.config.auth.password_hash = password_hash
    core.config.jwt.secret = jwt_secret
    core.config.jwt.expire = jwt_expire
    core.config.data.static = content
    core.config.data.cache_static = cache_static
    core.config.data.precache_static = precache_static
    core.config.host.bind = bind
    core.config.host.hostname = hostname if hostname is not None else bind
    core.config.host.port = port
    core.environment.running_as_pyz = Path(__file__).parent.suffix == ".pyz"

    read = (
        staticfiles.load_filesystem
        if not core.environment.running_as_pyz
        else staticfiles.load_zipfile
    )

    load: Callable[[str, str], tuple[Path, bytes]]
    if core.config.data.cache_static:
        cache = (
            staticfiles.FileCache()
            if not core.config.data.precache_static
            else staticfiles.FileCache()
        )  # TODO: impl precache static
        load = staticfiles.CachingFileLoader(read, cache).load
    else:
        load = staticfiles.FileLoader(read).load

    core.dependencies.data.load_static = load

    core.start()


if __name__ == "__main__":
    cli()
