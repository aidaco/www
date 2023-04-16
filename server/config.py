import json
import sys
import tomllib
from dataclasses import _MISSING_TYPE, dataclass, fields, is_dataclass
from datetime import timedelta
from pathlib import Path


@dataclass
class Admin:
    username: str
    password_hash: str


@dataclass
class JWT:
    secret: str
    expiration: timedelta


@dataclass
class Locations:
    static: Path
    database: Path


@dataclass
class Config:
    admin: Admin
    jwt: JWT
    locations: Locations
    zipapp: bool = sys.argv[0].endswith("pyz")

    @staticmethod
    def read(path: Path):
        match path.suffix:
            case ".toml":
                load = tomllib.loads
            case ".json":
                load = json.loads
            case _:
                raise ValueError("Config file must be TOML or JSON.")
        return _dataclass_fromdict(Config, load(path.read_text()))

    @staticmethod
    def locate(name: str):
        dirs = [Path.cwd(), Path.home(), Path.home() / ".config"]
        for d in dirs:
            for f in d.glob(f"{name}.*"):
                if f.suffix in {".toml", ".json"}:
                    return Config.read(f)
        raise Exception("No config file found")


def _dataclass_toml_template(dcls):
    for field in fields(dcls):
        if is_dataclass(field.type):
            yield f"[ {field.name} ]"
            yield from _dataclass_toml_template(field.type)
        else:
            value = repr(field.default) if field.default is not _MISSING_TYPE else "''"
            yield f"{field.name} = {value}"


def _dataclass_fromdict(dcls, data):
    kwargs = {}
    for field in fields(dcls):
        value = data.get(field.name, field.default)
        if value is _MISSING_TYPE:
            raise ValueError(f"Required field not found: {field.name}")
        if is_dataclass(field.type):
            kwargs[field.name] = _dataclass_fromdict(field.type, value)
        else:
            if not isinstance(value, field.type):
                value = field.type(value)
            kwargs[field.name] = value
    return dcls(**kwargs)
