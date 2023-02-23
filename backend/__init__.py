import asyncio
import logging
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

from . import auth

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)


class WSManager:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}
        self.state: dict[str, tuple[bool, str]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        uid = str(uuid4())
        try:
            await websocket.send_text("CONNECT")
            self.connections[uid] = websocket
            self.state[uid] = (False, "")
            log.info(f"Connected {uid}")
            return uid
        except WebSocketDisconnect:
            return None

    def disconnect(self, uid: str):
        if uid in self.connections:
            del self.connections[uid]
            del self.state[uid]
        log.info(f"Disconnected {uid}")
        return uid

    async def activate(self, uid: str):
        try:
            await self.connections[uid].send_text("ACTIVATE")
            self.state[uid] = (True, self.state[uid][1])
        except KeyError:
            raise HTTPException(404, "Not found.")
        except WebSocketDisconnect:
            self.disconnect(uid)

    async def deactivate(self, uid: str):
        try:
            await self.connections[uid].send_text("DEACTIVATE")
            self.state[uid] = (False, self.state[uid][1])
        except KeyError:
            raise HTTPException(404, "Not found.")
        except WebSocketDisconnect:
            self.disconnect(uid)

    async def update(self, uid: str, content: str):
        try:
            await self.connections[uid].send_text(f"UPDATE {content}")
            self.state[uid] = (self.state[uid][0], content)
        except KeyError:
            raise HTTPException(404, "Not found.")
        except WebSocketDisconnect:
            self.disconnect(uid)


manager = WSManager()
api = FastAPI()


@api.get("/login")
async def login():
    return await public_file("login.html")


@api.post("/login")
async def authenticate(request: auth.LoginRequest = Depends()):
    log.info(f"AUTH REQUEST {request.username} {request.password}")
    if request.authenticated:
        log.info(f"AUTH SUCCESS {request.token}")
        return {"access_token": request.token, "token_type": "bearer"}
    log.info("AUTH FAILURE")
    raise HTTPException(400, "Invalid credentials.")


@api.exception_handler(auth.LoginRequired)
async def login_redirect(request: Request, exc: auth.LoginRequired):
    return RedirectResponse(url="/login")


@api.get("/madness")
async def index(auth=Depends(auth.TokenBearer(redirect=True))):
    return await protected_file("admin.html")


@api.websocket("/api/live")
async def ws_connect(websocket: WebSocket):
    uid = await manager.connect(websocket)
    while uid in manager.connections:
        try:
            await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(uid)
        await asyncio.sleep(0.5)


@api.get("/api/state")
async def active(response: Response, auth=Depends(auth.TokenBearer())):
    return manager.state


class Command(BaseModel):
    command: str
    uid: str
    content: str = ""


@api.post("/api/dispatch")
async def dispatch_command(
    response: Response,
    command: Command,
    auth=Depends(auth.TokenBearer()),
):
    log.info(f"Dispatching {command}")
    match command.command:
        case "ACTIVATE":
            await manager.activate(command.uid)
        case "UPDATE":
            await manager.update(command.uid, command.content)
        case "DEACTIVATE":
            await manager.deactivate(command.uid)


@api.get("/protected/{path:path}")
async def protected_file(path: str, auth=Depends(auth.TokenBearer())):
    path = Path("protected") / path

    if not path.is_file():
        raise HTTPException(status_code=404, detail="Not Found.")
    return FileResponse(path)


@api.get("/{path:path}")
async def public_file(path: str):
    if path == "":
        path = "index.html"
    path = Path("public") / path

    if not path.is_file():
        raise HTTPException(status_code=404, detail="Not Found.")
    return FileResponse(path)


def main(username: str, password_hash: str, jwt_secret: str):
    auth.USERNAME = username
    auth.PASSWORD_HASH = password_hash
    auth.JWT_SECRET = jwt_secret
    uvicorn.run(api, host="0.0.0.0", port=8000, log_level=logging.INFO)
