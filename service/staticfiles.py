from pathlib import Path

from fastapi import Depends, HTTPException
from fastapi.responses import FileResponse

from . import auth, core
from .core import api


def _resolve_static_path(
    root: Path,
    path: str,
    exc: Exception = HTTPException(status_code=404, detail="Not Found."),
):
    if path.startswith("/"):
        _path = path[1:]
    _path = root / path

    if _path.is_dir():
        _path /= "index.html"
    if not _path.is_file():
        raise exc
    return _path


@api.get("/admin")
async def base_admin(auth=Depends(auth.TokenBearer(redirect=True))):
    return await protected_file("", auth)


@api.get("/admin/{path:path}")
async def protected_file(path: str, auth=Depends(auth.TokenBearer(redirect=True))):

    _path = _resolve_static_path(core.config.locations.protected, path)
    return FileResponse(_path)


@api.get("/{path:path}")
async def public_file(path: str):
    _path = _resolve_static_path(core.config.locations.public, path)
    return FileResponse(_path)
