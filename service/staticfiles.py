from pathlib import Path

from fastapi import HTTPException, Depends
from fastapi.responses import FileResponse

from .core import api
from . import auth

PUBLIC_ROOT = Path.cwd() / "public/dist"
ADMIN_ROOT = Path.cwd() / "admin/dist"


def _resolve_static_path(
    root: Path, path: str, exc: Exception = HTTPException(status_code=404, detail="Not Found.")
):
    if path.startswith("/"):
        path = path[1:]
    path = root / path

    if path.is_dir():
        path /= "index.html"
    if not path.is_file():
        raise exc
    return path


@api.get("/admin")
async def base_admin():
    return await protected_file("")


@api.get("/admin/{path:path}")
async def protected_file(path: str, auth=Depends(auth.TokenBearer(redirect=True))):
    path = _resolve_static_path(ADMIN_ROOT, path)
    return FileResponse(path)


@api.get("/{path:path}")
async def public_file(path: str):
    path = _resolve_static_path(PUBLIC_ROOT, path)
    return FileResponse(path)
