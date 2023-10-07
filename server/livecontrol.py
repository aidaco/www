import logging

from fastapi import APIRouter, WebSocket

from .wsmanager import Chat, Rewrite, WebSocketApp

log = logging.getLogger(__name__)
api: APIRouter = APIRouter()
manager = WebSocketApp(Chat, Rewrite)


@api.websocket("/client")
async def connect_client_websocket(ws: WebSocket):
    await manager.client(ws)


@api.websocket("/controller")
async def connect_controller_websocket(ws: WebSocket):
    await manager.controller(ws)
