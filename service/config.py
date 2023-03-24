from dataclasses import dataclass, fields, is_dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any, Callable, Type


@dataclass
class Logging:
    level: int
    output: str
    file: Path | None


@dataclass
class Host:
    bind: str
    hostname: str
    port: int


@dataclass
class SingleUser:
    username: str
    password_hash: str


@dataclass
class JWT:
    secret: str
    expire: timedelta


@dataclass
class DataStructure:
    static: Path
    cache_static: bool
    precache_static: bool


@dataclass
class DataAccess:
    load_static: Callable[[str, str], tuple[Path, bytes]]


@dataclass
class Config:
    log: Logging
    host: Host
    data: DataStructure
    auth: SingleUser
    jwt: JWT


@dataclass
class Environment:
    running_as_pyz: bool


@dataclass
class Dependencies:
    data: DataAccess


_DEFAULT_MAPPING: dict[Type, Callable[[], Any]] = {
    int: int,
    str: str,
    bytes: bytes,
    bool: bool,
    list: list,
    dict: dict,
    tuple: tuple,
}


def _default_init_dataclass(
    cls,
    default_mapping: dict[Type, Callable[[], Any]] = _DEFAULT_MAPPING,
):
    return cls(**{f.name: _default_init(f, default_mapping) for f in fields(cls)})


def _default_init_from_mapping(
    cls,
    default_mapping: dict[Type, Callable[[], Any]] = _DEFAULT_MAPPING,
):
    return default_mapping.get(cls, None) is not None


def _default_init(src, default_mapping: dict[Type, Callable] = _DEFAULT_MAPPING):
    if src in default_mapping:  # can default map
        return _default_init_from_mapping(src, default_mapping)
    elif is_dataclass(src):  # Is Dataclass
        return _default_init_dataclass(src, default_mapping)
    elif (cls := getattr(src, "type", None)) is not None:  # Is field
        return _default_init(cls)
    else:
        raise ValueError(f"Couldn't default initialize {src=}")


config: Config = _default_init_dataclass(Config)
environment: Environment = _default_init_dataclass(Environment)
dependencies: Dependencies = _default_init_dataclass(Dependencies)
