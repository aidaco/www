import logging
import asyncio
from pydantic import BaseModel
from fastapi import WebSocket, WebSocketDisconnect, Depends, Response

from .core import api, manager
from . import auth

log = logging.getLogger(__name__)

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
async def active(response: Response, auth=Depends(auth.TokenBearer())):
    return manager.state

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

