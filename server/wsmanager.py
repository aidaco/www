import asyncio
from dataclasses import dataclass, field
import logging
from typing import Awaitable, Callable, Protocol
from uuid import uuid4
import json
from datetime import UTC, datetime

from fastapi import WebSocket, WebSocketDisconnect

log = logging.getLogger(__name__)


class WSHandler(Protocol):
    async def connect(
        self, uid: str, send: Callable[[dict], Awaitable[None]]
    ) -> None: ...

    async def message(self, uid: str, message: dict) -> None: ...

    async def disconnect(self, uid: str) -> None: ...


@dataclass
class WSManager:
    connections: dict[str, WebSocket] = field(default_factory=dict)
    handlers: dict[str, WSHandler] = field(default_factory=dict)

    async def manage(self, ws: WebSocket, uid: str | None = None) -> None:
        uid = await self.connect(ws, uid)
        await self.handle_messages(uid, ws)
        await self.disconnect(uid)

    async def connect(self, ws: WebSocket, uid: str | None = None) -> str:
        await ws.accept()
        uid = uid if uid is not None else str(uuid4())
        send = ws.send_json
        self.connections[uid] = ws
        await asyncio.gather(
            handler.connect(uid, send) for handler in self.handlers.values()
        )
        return uid

    async def handle_messages(self, uid: str, ws: WebSocket) -> None:
        try:
            while True:
                message = {}
                try:
                    async for message in ws.iter_json():
                        match message:
                            case {"handler": str(handler_name), **data}:
                                await self.handlers[handler_name].message(uid, data)
                except json.JSONDecodeError:
                    log.warning(f"Malformed message from {uid}: {message}")
        except WebSocketDisconnect:
            pass

    async def disconnect(self, uid: str) -> None:
        await asyncio.gather(
            handler.disconnect(uid) for handler in self.handlers.values()
        )
        del self.connections[uid]


@dataclass(slots=True)
class RewriteClientState:
    send: Callable
    active: bool = False
    content: str = ""


@dataclass
class RewriteState:
    clients: dict[str, RewriteClientState] = field(default_factory=dict)
    controllers: dict[str, Callable] = field(default_factory=dict)

    def connect_client(self, uid: str, send) -> None:
        self.clients[uid] = state = RewriteClientState(send)
        event = {
            "handler": "rewrite",
            "type": "connect",
            "client": uid,
            "active": state.active,
            "content": state.content,
        }
        self.clients[uid].send(event)
        for controller in self.controllers.values():
            controller(event)

    def disconnect_client(self, uid: str) -> None:
        del self.clients[uid]
        event = {"handler": "rewrite", "type": "disconnect", "client": uid}
        for controller in self.controllers.values():
            controller(event)

    def connect_controller(self, uid: str, send) -> None:
        self.controllers[uid] = send

    def disconnect_controller(self, uid: str) -> None:
        del self.controllers[uid]

    def activate(self, uid: str) -> None:
        self.clients[uid].active = True
        event = {"handler": "rewrite", "type": "activate", "client": uid}
        self.clients[uid].send(event)
        for controller in self.controllers.values():
            controller(event)

    def deactivate(self, uid: str) -> None:
        self.clients[uid].active = False
        event = {"handler": "rewrite", "type": "deactivate", "client": uid}
        self.clients[uid].send(event)
        for controller in self.controllers.values():
            controller(event)

    def update(self, uid: str, content: str) -> None:
        self.clients[uid].content = content
        event = {
            "handler": "rewrite",
            "type": "content",
            "client": uid,
            "content": content,
        }
        self.clients[uid].send(event)
        for controller in self.controllers.values():
            controller(event)


@dataclass
class RewriteClientApp:
    state: RewriteState

    async def connect(self, uid: str, send):
        self.state.connect_client(uid, send)

    async def message(self, uid: str, message: dict): ...

    async def disconnect(self, uid: str):
        self.state.disconnect_client(uid)


@dataclass
class RewriteControllerApp:
    state: RewriteState

    async def connect(self, uid: str, send):
        self.state.connect_controller(uid, send)

    async def message(self, uid: str, message: dict):
        match message:
            case {"command": "activate", "uid": client}:
                self.state.activate(client)
            case {"command": "deactivate", "uid": client}:
                self.state.deactivate(client)
            case {"command": "update", "uid": client, "content": content}:
                self.state.update(uid, content)

    async def disconnect(self, uid: str):
        self.state.disconnect_controller(uid)


@dataclass
class Message:
    author: str
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ChatClientState:
    uid: str
    active: bool = False
    messages: list[Message] = field(default_factory=list)
    subscribers: set[Callable[[dict], None]] = field(default_factory=set)

    def listen(self, fn: Callable[[dict], None]) -> None:
        self.subscribers.add(fn)
        fn(
            {
                "handler": "chat",
                "type": "value",
                "client": self.uid,
                "active": self.active,
                "messages": self.messages,
            }
        )

    def notify(self, event: dict) -> None:
        for subscriber in self.subscribers:
            subscriber(event)

    def activate(self) -> None:
        self.active = True
        self.notify({"handler": "chat", "type": "activate", "client": self.uid})

    def deactivate(self) -> None:
        self.active = False
        self.notify({"handler": "chat", "type": "deactivate", "client": self.uid})

    def message(self, author: str, content: str):
        message = Message(author, content)
        self.messages.append(message)
        self.notify(
            {
                "handler": "chat",
                "type": "message",
                "client": self.uid,
                "message": message,
            }
        )


@dataclass
class ChatState:
    clients: dict[str, ChatClientState] = field(default_factory=dict)
    controllers: dict[str, Callable] = field(default_factory=dict)

    def connect_controller(self, uid: str, send) -> None:
        send({"handler": "chat", "type": "value", "value": self.clients})
        self.controllers[uid] = send

    def disconnect_controller(self, uid: str) -> None:
        del self.controllers[uid]

    def notify_controllers(self, event: dict) -> None:
        for controller in self.controllers.values():
            controller(event)

    def connect_client(self, uid: str, send):
        self.clients[uid] = client = ChatClientState(uid)
        client.listen(send)
        client.listen(self.notify_controllers)

    def disconnect_client(self, uid: str):
        self.clients[uid].notify(
            {"handler": "chat", "type": "disconnect", "client": uid}
        )
        del self.clients[uid]


@dataclass
class ChatClientApp:
    state: ChatState

    async def connect(self, uid: str, send: Callable):
        self.state.clients[uid] = client = ChatClientState(uid)
        client.listen(send)

    async def message(self, uid: str, message: dict):
        match message:
            case {"command": "message", "content": content}:
                self.state.clients[uid].message(uid, content)

    async def disconnect(self, uid: str):
        self.state.clients[uid].notify(
            {"handler": "chat", "type": "disconnect", "client": uid}
        )
        del self.state.clients[uid]


@dataclass
class ChatControllerApp:
    state: ChatState

    async def connect(self, uid: str, send: Callable):
        self.state.connect_controller(uid, send)

    async def message(self, uid: str, message: dict):
        match message:
            case {"command": "activate", "client": client}:
                self.state.clients[client].activate()
            case {"command": "deactivate", "client": client}:
                self.state.clients[client].deactivate()
            case {"command": "message", "client": client, "content": content}:
                self.state.clients[client].message(uid, content)

    async def disconnect(self, uid: str) -> None:
        self.state.disconnect_controller(uid)
