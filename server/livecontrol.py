import asyncio
import logging

from fastapi import APIRouter, Response, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from .auth import Auth
from .wsmanager import WSManager

log = logging.getLogger(__name__)
api: APIRouter = APIRouter()
manager = WSManager()


class Command(BaseModel):
    command: str
    uid: str
    content: str = ""


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
async def active(auth: Auth, response: Response):
    return manager.state


@api.post("/api/dispatch")
async def dispatch_command(
    auth: Auth,
    command: Command,
    response: Response,
):
    log.info(f"Dispatching {command}")
    match command.command:
        case "ACTIVATE":
            await manager.activate(command.uid)
        case "UPDATE":
            await manager.update(command.uid, command.content)
        case "DEACTIVATE":
            await manager.deactivate(command.uid)
