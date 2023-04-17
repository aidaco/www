import mimetypes
import sys
import zipfile
from typing import Protocol

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, StreamingResponse

from . import core
from .auth import Auth


class FileNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Not Found.")


class FSLoader:
    def response(self, prefix: str, path: str):
        if path.startswith("/"):
            path = path[1:]
        _path = core.config.locations.static / prefix / path

        if _path.is_dir():
            _path /= "index.html"
        if not _path.is_file():
            raise FileNotFound()
        return FileResponse(_path)


class PYZLoader:
    def __init__(
        self,
    ):
        self.pyz = zipfile.ZipFile(sys.argv[0])

    def streamfile(self, zinfo):
        with self.pyz.open(zinfo) as f:
            yield from f

    def response(self, prefix: str, path: str):
        if path.startswith("/"):
            _path = path[1:]
        _path = prefix + "/" + path

        try:
            zinfo = self.pyz.getinfo(_path)
        except KeyError:
            try:
                _path += "/index.html"
                zinfo = self.pyz.getinfo(_path)
            except KeyError:
                raise FileNotFound()

        if zinfo.is_dir():
            try:
                zinfo = self.pyz.getinfo(_path + "index.html")
            except KeyError:
                raise FileNotFound()

        return StreamingResponse(
            self.streamfile(zinfo), media_type=mimetypes.guess_type(zinfo.filename)[0]
        )


class Loader(Protocol):
    def response(self, prefix: str, path: str) -> Response:
        ...


_loader: Loader


def loader():
    global _loader
    try:
        return _loader
    except NameError:
        if core.config.zipapp:
            _loader = PYZLoader()
        else:
            _loader = FSLoader()
        return _loader


api = APIRouter()


@api.get("/admin")
async def base_admin(auth: Auth):
    return await protected_file(auth, "")


@api.get("/admin/{path:path}")
async def protected_file(auth: Auth, path: str):
    return loader().response("protected", path)


@api.get("/{path:path}")
async def public_file(path: str):
    return loader().response("public", path)
