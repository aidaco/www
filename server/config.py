import json
import sys
import tomllib
from datetime import timedelta
from pathlib import Path
from typing import Literal

import tomli_w
from pydantic import BaseModel, Field, parse_obj_as

from . import auth_backends


class Admin(BaseModel):
    username: str
    password_hash: str


class JWT(BaseModel):
    secret: str
    ttl: timedelta = timedelta(days=30)


class Rebuild(BaseModel):
    secret: str
    branch: str | None = None
    verify_signature: bool = True
    verify_branch: bool = True


class Locations(BaseModel):
    static: Path = Path("dist")
    database: Path = Path("aidan.software.sqlite3")


class Config(BaseModel):
    admin: Admin
    jwt: JWT
    rebuild: Rebuild | Literal[False] = False
    locations: Locations = Field(default_factory=Locations)
    zipapp: bool = sys.argv[0].endswith("pyz")


def read(path: Path):
    match path.suffix:
        case ".toml":
            load = tomllib.loads
        case ".json":
            load = json.loads
        case _:
            raise ValueError("Config file must be TOML or JSON.")
    return parse_obj_as(Config, load(path.read_text()))


def create(username: str, password: str, jwt_secret: str, path: Path):
    path.write_text(
        dumps_toml(
            Config(
                admin=Admin(
                    username=username,
                    password_hash=auth_backends.hasher().hash(password),
                ),
                jwt=JWT(secret=jwt_secret),
            )
        )
    )


def locate(name: str):
    dirs = [Path.cwd(), Path.home(), Path.home() / ".config"]
    for d in dirs:
        for f in d.glob(f"{name}.*"):
            if f.suffix in {".toml", ".json"}:
                return read(f)
    raise Exception("No config file found")


def dumps_toml(config: Config) -> str:
    return tomli_w.dumps(json.loads(config.json()))
