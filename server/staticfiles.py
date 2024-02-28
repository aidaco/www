import mimetypes
from pathlib import Path

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse

from .auth import Auth
from .config import config


def locate_static_file(directory: Path, path: str) -> Path:
    result = directory / path
    if not result.is_relative_to(directory):
        raise HTTPException(451)
    elif not result.exists():
        raise HTTPException(404)
    return result


def get_path_response(directory: Path, path: str) -> Response:
    return FileResponse(locate_static_file(directory, path))


def get_path_response_cached(
    directory: Path, path: str, cache: dict[str, tuple[bytes, str | None]] = dict()
) -> Response:
    try:
        data, mime = cache[path]
    except KeyError:
        real = locate_static_file(directory, path)
        data = real.read_bytes()
        mime = mimetypes.guess_type(real.name)[0]
        cache[path] = data, mime
    return Response(data, media_type=mime)


get_response_frontend = (
    get_path_response_cached if config.frontend.cache else get_path_response
)
get_response_admin_frontend = (
    get_path_response_cached if config.admin_frontend.cache else get_path_response
)
api: APIRouter = APIRouter()


@api.get("/admin")
def get_admin_frontend_index(auth: Auth):
    return get_admin_frontend_file(auth, "index.html")


@api.get("/admin/{path:path}")
def get_admin_frontend_file(auth: Auth, path: str):
    return get_response_admin_frontend(config.admin_frontend.directory, path)


@api.get("/{path:path}")
def get_frontend_file(path: str):
    return get_response_frontend(config.frontend.directory, path)
