import json
import sys
import tomllib
from datetime import timedelta
from pathlib import Path
from typing import Literal

import tomli_w
from pydantic import BaseModel, Field, TypeAdapter


class Admin(BaseModel):
    username: str
    password_hash: str


class JWT(BaseModel):
    secret: str
    algorithm: str = "HS256"
    access_ttl: timedelta = timedelta(minutes=10)
    refresh_ttl: timedelta = timedelta(days=30)


class Rebuild(BaseModel):
    secret: str
    branch: str | None = None
    verify_signature: bool = True
    verify_branch: bool = True


class Frontend(BaseModel):
    directory: Path = Path("static/public")
    cache: bool = True


class AdminFrontend(BaseModel):
    directory: Path = Path("static/protected")
    cache: bool = True


class Locations(BaseModel):
    database: Path = Path("aidan.software.sqlite3")


class Config(BaseModel):
    admin: Admin
    jwt: JWT
    rebuild: Rebuild | Literal[False] = False
    frontend: Frontend = Field(default_factory=Frontend)
    admin_frontend: AdminFrontend = Field(default_factory=AdminFrontend)
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
    return TypeAdapter(Config).validate_python(load(path.read_text()))


def locate(name: str):
    dirs = [Path.cwd(), Path.home(), Path.home() / ".config"]
    for d in dirs:
        for f in d.glob(f"{name}.*"):
            if f.suffix in {".toml", ".json"}:
                return read(f)
    raise Exception("No config file found")


def dumps_toml(config: Config) -> str:
    return tomli_w.dumps(json.loads(config.json()))


config = locate("aidan.software")
