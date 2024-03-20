import mimetypes
from pathlib import Path

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse

from .auth import AuthRedirect
from .config import config


def locate_static_file(directory: Path, path: str) -> Path:
    result = directory / path
    if not result.is_relative_to(directory):
        raise HTTPException(451)
    elif not result.exists():
        if not result.name.endswith(".html"):
            return locate_static_file(directory, f"{path}.html")
        raise HTTPException(404)
    elif result.is_dir():
        return locate_static_file(result, "index.html")
    return result.resolve()


def get_path_response(directory: Path, path: str) -> Response:
    return FileResponse(locate_static_file(directory, path))


def get_path_response_cached(
    directory: Path, path: str, cache: dict[str, tuple[bytes, str | None]]
) -> Response:
    try:
        data, mime = cache[path]
    except KeyError:
        real = locate_static_file(directory, path)
        data = real.read_bytes()
        mime = mimetypes.guess_type(real.name)[0]
        cache[str(real.relative_to(directory))] = data, mime
    return Response(data, media_type=mime)


api: APIRouter = APIRouter()
frontend_cache: dict[str, tuple[bytes, str | None]] = dict()
admin_frontend_cache: dict[str, tuple[bytes, str | None]] = dict()


def get_response_frontend(
    path: str, directory: Path = config.frontend.directory.resolve()
):
    if config.frontend.cache:
        return get_path_response_cached(directory, path, frontend_cache)
    else:
        return get_path_response(directory, path)


def get_response_admin_frontend(
    path: str, directory: Path = config.admin_frontend.directory.resolve()
):
    if config.admin_frontend.cache:
        return get_path_response_cached(directory, path, admin_frontend_cache)
    else:
        return get_path_response(directory, path)


@api.get("/admin")
def get_admin_frontend_index(auth: AuthRedirect):
    return get_response_admin_frontend("index.html")


@api.get("/admin/{path:path}")
def get_admin_frontend_file(auth: AuthRedirect, path: str):
    return get_response_admin_frontend(path)


@api.get("/{path:path}")
def get_frontend_file(path: str):
    return get_response_frontend(path)
