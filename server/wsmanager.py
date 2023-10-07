import asyncio
import json
import logging
from typing import Awaitable, Callable, Protocol, Sequence
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect

log = logging.getLogger(__name__)


class Connection:
    def __init__(self, ws: WebSocket):
        self.active = True
        self.ws = ws

    async def send(self, message: dict):
        if not self.active:
            return
        try:
            await self.ws.send_json(message)
        except WebSocketDisconnect:
            self.active = False

    async def receive(self):
        if not self.active:
            return
        while self.active:
            try:
                yield await self.ws.receive_json()
                await asyncio.sleep(0)
            except WebSocketDisconnect:
                self.active = False
            except json.JSONDecodeError:
                log.warn("invalid message")


class WebSocketPool:
    def __init__(self):
        self.connections = {}

    async def connect(self, ws: WebSocket) -> tuple[str, Connection]:
        await ws.accept()
        uid = str(uuid4())
        self.connections[uid] = connection = Connection(ws)
        return uid, connection

    async def disconnect(self, uid: str) -> str:
        if uid in self.connections:
            del self.connections[uid]
        return uid


async def notify(
    message: dict,
    watchers: Sequence[Callable[..., Awaitable]],
):
    if watchers:
        await asyncio.gather(*(watcher(message) for watcher in watchers))


class StateValue:
    def __init__(self, value):
        self.value = value
        self.watchers = set()

    async def watch(self, corofn: Callable[..., Awaitable]):
        self.watchers.add(corofn)
        await corofn(dict(event="state", value=self.value))

    def unwatch(self, corofn: Callable[..., Awaitable]):
        self.watchers.remove(corofn)

    def get(self):
        return self.value

    async def set(self, value):
        self.value = value
        await notify(dict(event="set", value=value), *self.watchers)


class StateDict:
    def __init__(self, state: dict | None = None):
        self.state = {} if state is None else state
        self.global_watchers: set[Callable[..., Awaitable]] = set()
        self.watchers: dict[str, list[Callable[..., Awaitable]]] = dict()

    async def watch(self, uid: str, corofn: Callable[..., Awaitable]):
        self.watchers.setdefault(uid, []).append(corofn)
        await corofn(dict(event="state", value=self.state.get(uid, None)))

    def unwatch(self, uid: str, corofn: Callable[..., Awaitable]):
        if watchers := self.watchers.get(uid, None):
            watchers.remove(corofn)

    async def watch_all(self, corofn: Callable[..., Awaitable]):
        self.global_watchers.add(corofn)
        await corofn(dict(event="state", value=self.state))

    def unwatch_all(self, corofn: Callable[..., Awaitable]):
        self.global_watchers.remove(corofn)

    def get(self, uid: str):
        return self.state[uid]

    def contains(self, uid: str):
        return uid in self.state

    __contains__ = contains
    __getitem__ = get

    async def set(self, uid: str, value):
        self.state[uid] = value
        await notify(
            dict(event="set", uid=uid, value=value),
            [*(self.watchers.get(uid, [])), *(self.global_watchers)],
        )

    async def delete(self, uid: str):
        if uid not in self.state:
            return

        del self.state[uid]
        await notify(
            dict(event="delete", uid=uid),
            [*self.watchers.get(uid, []), *self.global_watchers],
        )


class StateList:
    def __init__(self, state: list | None = None):
        self.state = [] if state is None else state
        self.watchers: list[Callable[..., Awaitable]] = list()

    async def watch(self, corofn: Callable[..., Awaitable]):
        self.watchers.append(corofn)
        await corofn(dict(event="state", value=self.state))

    def unwatch(self, uid: str, corofn: Callable[..., Awaitable]):
        self.watchers.remove(corofn)

    def get(self, index: int):
        return self.state[index]

    async def append(self, value):
        self.state.append(value)
        await notify(dict(event="append", value=value), self.watchers)

    async def insert(self, index, value):
        self.state.insert(index, value)
        await notify(dict(event="insert", index=index, value=value), self.watchers)

    async def remove(self, value):
        self.state.remove(value)
        await notify(dict(event="remove", value=value), self.watchers)


class WebSocketAppProtocol(Protocol):
    def __init__(self, pool: WebSocketPool):
        ...

    async def client(self, uid: str, connection: Connection, command: dict):
        ...

    async def controller(self, uid: str, connection: Connection, command: dict):
        ...


class WebSocketApp:
    def __init__(self, *appclasses: type[WebSocketAppProtocol]):
        self.pool = WebSocketPool()
        self.apps = {
            f"{appcls.__module__}.{appcls.__qualname__}": appcls(self.pool)
            for appcls in appclasses
        }

    async def client(self, ws: WebSocket):
        uid, connection = await self.pool.connect(ws)
        async for cmd in connection.receive():
            match cmd:
                case {"app": app}:
                    await self.apps[app].client(uid, connection, cmd)

    async def controller(self, ws: WebSocket):
        uid, connection = await self.pool.connect(ws)
        async for cmd in connection.receive():
            match cmd:
                case {"app": app}:
                    await self.apps[app].controller(uid, connection, cmd)


class Rewrite:
    def __init__(self, pool: WebSocketPool):
        self.pool = pool
        self.controllers: set[str] = set()
        self.state = StateDict()

    async def connect_client(self, uid: str, connection: Connection):
        active, content = StateValue(False), StateValue("")
        await asyncio.gather(
            self.state.set(uid, (active, content)),
            active.watch(connection.send),
            content.watch(connection.send),
        )

    async def connect_controller(self, uid: str, connection: Connection):
        await self.state.watch_all(connection.send)

    async def client(self, uid: str, connection: Connection, command: dict):
        if uid not in self.state:
            await self.connect_client(uid, connection)

    async def controller(self, uid: str, connection: Connection, command: dict):
        if uid not in self.controllers:
            await self.connect_controller(uid, connection)
        match command:
            case {"command": "activate", "uid": uid}:
                await self.state.get(uid)[0].set(True)
            case {"command": "deactivate", "uid": uid}:
                await self.state.get(uid)[0].set(False)
            case {"command": "update", "uid": uid, "value": value}:
                await self.state.get(uid)[1].set(value)


class Chat:
    def __init__(self, pool: WebSocketPool):
        self.pool = pool
        self.controllers: set[str] = set()
        self.state = StateDict()

    async def connect_client(self, uid: str, connection: Connection):
        active, messages = StateValue(False), StateList()
        await asyncio.gather(
            self.state.set(uid, (active, messages)),
            active.watch(connection.send),
            messages.watch(connection.send),
        )

    async def client(self, uid: str, connection: Connection, command: dict):
        if uid not in self.state:
            await self.connect_client(uid, connection)
        match command:
            case {"command": "message", "text": text}:
                await self.state.get(uid)[1].append(dict(uid=uid, text=text))

    async def connect_controller(self, uid: str, connection: Connection):
        self.controllers.add(uid)
        await self.state.watch_all(connection.send)

    async def controller(self, uid: str, connection: Connection, command: dict):
        if uid not in self.controllers:
            await self.connect_controller(uid, connection)
        match command:
            case {"command": "activate", "uid": uid}:
                await self.state.get(uid)[0].set(True)
            case {"command": "deactivate", "uid": uid}:
                await self.state.get(uid)[0].set(False)
            case {"command": "message", "uid": uid, "text": text}:
                await self.state.get(uid)[1].append(dict(uid=uid, text=text))
