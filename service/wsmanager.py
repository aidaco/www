import logging
from uuid import uuid4
from fastapi import WebSocket, WebSocketDisconnect, HTTPException

log = logging.getLogger(__name__)

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
