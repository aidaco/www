import json
import sys
import tomllib
from datetime import timedelta
from pathlib import Path
from typing import Literal

import tomli_w
from pydantic import BaseModel, Field, TypeAdapter

from server.auth_base import hash_password


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


def create(
    username: str,
    password: str,
    jwt_secret: str,
    jwt_algorithm: str = "HS256",
    jwt_access_ttl: timedelta = timedelta(minutes=10),
    jwt_refresh_ttl: timedelta = timedelta(days=30),
    rebuild: Rebuild | Literal[False] = False,
    rebuild_secret: str | None = None,
    rebuild_branch: str | None = None,
    rebuild_verify_signature: bool = True,
    rebuild_verify_branch: bool = True,
    static_directory: Path = Path("static/public"),
    static_cache: bool = True,
    admin_static_directory: Path = Path("static/protected"),
    admin_static_cache: bool = True,
    database: Path = Path("aidan.software.sqlite3"),
) -> Config:
    return Config(
        admin=Admin(username=username, password_hash=hash_password(password)),
        jwt=JWT(
            secret=jwt_secret,
            algorithm=jwt_algorithm,
            access_ttl=jwt_access_ttl,
            refresh_ttl=jwt_refresh_ttl,
        ),
        rebuild=Rebuild(
            secret=rebuild_secret,
            branch=rebuild_branch,
            verify_signature=rebuild_verify_signature,
            verify_branch=rebuild_verify_branch,
        )
        if rebuild and rebuild_secret and rebuild_branch
        else False,
        frontend=Frontend(directory=static_directory, cache=static_cache),
        admin_frontend=AdminFrontend(
            directory=admin_static_directory, cache=admin_static_cache
        ),
        locations=Locations(database=database),
    )


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
    return tomli_w.dumps(json.loads(config.model_dump_json()))


config = locate("aidan.software")
