import mimetypes
import sys
import zipfile
from typing import Protocol

from fastapi import Depends, HTTPException, Response
from fastapi.responses import FileResponse, StreamingResponse

from . import auth, core
from .core import api


class PathLoader:
    def __init__(
        self,
        group: str,
        exc: Exception = HTTPException(status_code=404, detail="Not Found."),
    ):
        self.group = group
        self.exc = exc

    def resolve(self, path: str):
        if path.startswith("/"):
            path = path[1:]
        _path = core.config.locations.static / self.group / path

        if _path.is_dir():
            _path /= "index.html"
        if not _path.is_file():
            raise self.exc
        return _path

    def response(self, path: str):
        return FileResponse(self.resolve(path))


class PyzPathLoader:
    def __init__(
        self,
        group: str,
        exc: Exception = HTTPException(status_code=404, detail="Not Found."),
    ):
        self.pyz = zipfile.ZipFile(sys.argv[0])
        self.group = group
        self.exc = exc

    def resolve(self, path: str):
        if path.startswith("/"):
            _path = path[1:]
        _path = self.group + "/" + path

        try:
            zinfo = self.pyz.getinfo(_path)
        except KeyError:
            try:
                _path += "/index.html"
                zinfo = self.pyz.getinfo(_path)
            except KeyError:
                raise self.exc

        if zinfo.is_dir():
            try:
                zinfo = self.pyz.getinfo(_path + "index.html")
            except KeyError:
                raise self.exc
        return zinfo

    def response(self, path: str):
        zinfo = self.resolve(path)

        def it():
            with self.pyz.open(zinfo) as f:
                yield from f

        return StreamingResponse(
            it(), media_type=mimetypes.guess_type(zinfo.filename)[0]
        )


class Loader(Protocol):
    def response(self, path: str) -> Response:
        ...


public_loader: Loader
protected_loader: Loader

if core.config.zipapp:
    public_loader = PyzPathLoader("public")
    protected_loader = PyzPathLoader("protected")
else:
    public_loader = PathLoader("public")
    protected_loader = PathLoader("protected")


@api.get("/admin")
async def base_admin(auth=Depends(auth.TokenBearer(redirect=True))):
    return await protected_file("", auth)


@api.get("/admin/{path:path}")
async def protected_file(path: str, auth=Depends(auth.TokenBearer(redirect=True))):
    return protected_loader.response(path)


@api.get("/{path:path}")
async def public_file(path: str):
    return public_loader.response(path)
