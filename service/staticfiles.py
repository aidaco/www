from pathlib import Path
from typing import Callable

from fastapi import Depends, HTTPException
from fastapi.responses import Response

from . import auth
from .core import api, config, dependencies


class FileCache:
    def __init__(self) -> None:
        self.files: dict[Path, bytes] = {}

    def __getitem__(self, key: Path) -> bytes:
        return self.files[key]

    def __setitem__(self, key: Path, value: bytes) -> None:
        self.files[key] = value


class FileLoader:
    def __init__(
        self,
        load: Callable[[Path, Exception], bytes],
        exc: Exception = HTTPException(status_code=404, detail="Not Found."),
    ):
        self.loader = load
        self.exc = exc

    def load(self, root: str, asset: str) -> tuple[Path, bytes]:
        if asset.endswith("/"):
            asset += "index.html"
        path = Path(root) / asset
        return path, self.loader(path, self.exc)


class CachingFileLoader:
    def __init__(
        self,
        load: Callable[[Path, Exception], bytes],
        cache: FileCache,
        exc: Exception = HTTPException(status_code=404, detail="Not Found."),
    ):
        self.loader = load
        self.cache = cache
        self.exc = exc

    def load(self, root: str, asset: str) -> tuple[Path, bytes]:
        if asset.endswith("/"):
            asset += "index.html"
        path = Path(root) / asset
        try:
            return path, self.cache[path]
        except KeyError:
            data = self.cache[path] = self.loader(path, self.exc)
            return path, data


def load_filesystem(path: Path, exc: Exception) -> bytes:
    abs_path = (config.data.static / path).resolve()
    if config.data.static not in abs_path.parents:
        raise exc
    try:
        return abs_path.read_bytes()
    except IOError:
        raise exc


def load_zipfile(path: Path, exc: Exception) -> bytes:
    # TODO
    return b""


@api.get("/admin")
async def base_admin(auth=Depends(auth.TokenBearer(redirect=True))):
    return await protected_file("", auth)


@api.get("/admin/{path:path}")
async def protected_file(path: str, auth=Depends(auth.TokenBearer(redirect=True))):

    data = dependencies.data.load_static("admin", path)
    return Response(data)


@api.get("/{path:path}")
async def public_file(path: str):
    data = dependencies.data.load_static("public", path)

    return Response(data)
