import asyncio
from datetime import timedelta
import logging
import re
from pathlib import Path
from uuid import uuid4

import uvicorn
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
    Response,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
from rich.logging import RichHandler

from . import wsmanager

log = logging.getLogger(__name__)
log.addHandler(RichHandler())
log.setLevel(logging.INFO)

USERNAME, PASSWORD_HASH = None, None
JWT_SECRET, JWT_EXPIRE = None, timedelta(days=30)
manager = wsmanager.WSManager()
api = FastAPI()


def main(username: str, password_hash: str, jwt_secret: str):
    global USERNAME, PASSWORD_HASH, JWT_SECRET
    USERNAME = username
    PASSWORD_HASH = password_hash
    JWT_SECRET = jwt_secret
    log.info(f'Started with: {USERNAME=} {PASSWORD_HASH=} {JWT_SECRET=}')
    uvicorn.run(api, host="0.0.0.0", port=8000, log_level=logging.INFO)
