import logging

from fastapi import APIRouter, WebSocket

from .wsmanager import (
    RewriteState,
    RewriteClientApp,
    RewriteControllerApp,
    ChatState,
    ChatClientApp,
    ChatControllerApp,
    WSManager,
)

log = logging.getLogger(__name__)
api: APIRouter = APIRouter()

rewrite_state = RewriteState()
chat_state = ChatState()
manager = WSManager(
    handlers={
        "rewrite": RewriteClientApp(rewrite_state),
        "chat": ChatClientApp(chat_state),
    }
)
controller_manager = WSManager(
    handlers={
        "rewrite": RewriteControllerApp(rewrite_state),
        "chat": ChatControllerApp(chat_state),
    }
)


@api.websocket("/client")
async def connect_client_websocket(ws: WebSocket):
    await manager.manage(ws)


@api.websocket("/controller")
async def connect_controller_websocket(ws: WebSocket):
    await controller_manager.manage(ws)
