import mimetypes
import sys
import zipfile
import re
from importlib.resources import files
from pathlib import Path
from typing import Protocol

from fastapi import APIRouter, Response
from fastapi.responses import FileResponse, StreamingResponse

from .auth import Auth
from .config import config


class ImportLoader:
    def __init__(self, prefix: str):
        self.base = files("server.static").joinpath(prefix)

    def response(self, path: str):
        return Response(
            self.base.joinpath(path).read_bytes(),
            media_type=mimetypes.guess_type(path)[0],
        )


class FileLoader:
    def __init__(self, prefix: str):
        assert config.locations.static is not None
        self.base = config.locations.static / prefix

    def response(self, path: str):
        return FileResponse(self.base / path)


class ZipLoader:
    def __init__(self, prefix: str):
        self.pyz = zipfile.ZipFile(sys.argv[0])
        self.prefix = prefix

    def streamfile(self, zinfo):
        with self.pyz.open(zinfo) as f:
            yield from f

    def response(self, path: str):
        zinfo = self.pyz.getinfo(f"{self.prefix}/{path}")
        return StreamingResponse(
            self.streamfile(zinfo), media_type=mimetypes.guess_type(zinfo.filename)[0]
        )


class Loader(Protocol):
    def __init__(self, prefix: str):
        ...

    def response(self, path: str) -> Response:
        ...


def loader(prefix: str):
    match config.locations.static:
        case Path() as p if p.suffix == ".zip":
            return ZipLoader(prefix)
        case Path():
            return FileLoader(prefix)
        case None:
            return ImportLoader(prefix)


public: Loader = loader("public")
protected: Loader = loader("protected")
api: APIRouter = APIRouter()


@api.get("/admin")
async def base_admin(auth: Auth):
    return await protected_file(auth, "index.html")


@api.get("/admin/{path:path}")
async def protected_file(auth: Auth, path: str):
    try:
        return protected.response(path)
    except Exception:
        try:
            return protected.response(path+'.html')
        except Exception:
            return protected.response("index.html")


@api.get("/{path:path}")
async def public_file(path: str):
    try:
        return public.response(path)
    except Exception:
        try:
            return public.response(path+'.html')
        except Exception:
            return public.response("index.html")

_SUFF_RE = re.compile(r'^[^\.]*(\.[^\.]+)+$')


def _has_suff(path: str):
    return bool(_SUFF_RE.fullmatch(path))
