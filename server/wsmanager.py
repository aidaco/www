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


def notify(
    watchers: Sequence[Callable],
    **message,
):
    for watcher in watchers:
        watcher(message)


class StateProperty:
    def __init__(self, default):
        self.default = default
        self.watchers = set()
        self.name = ''

    def watch(self, fn: Callable):
        self.watchers.add(fn)
        notify([fn], event="state", value=self.value)

    def unwatch(self, fn: Callable):
        self.watchers.remove(fn)

    def __set_name__(self, cls, name):
        self.name = name

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        return getattr(obj, f'_{self.name}', self.default)

    def __set__(self, obj, value):
        setattr(obj, f'_{self.name}', value)
        notify(self.watchers, event="set", value=value)


class StateObject:
    def __init__(self, value):
        object.__setattr__(self, '__wrapped__', value)
        object.__setattr__(self, '__watchers__', set())

    def watch(self, fn: Callable):
        self.__watchers__.add(fn)
        notify([fn], event="state", value=self.__wrapped__)

    def unwatch(self, fn: Callable):
        self.__watchers__.remove(fn)

    def __getattr__(self, name):
        return getattr(self.__wrapped__, name)

    def __setattr__(self, name, value):
        object.__setattr__(self.__wrapped__, name, value)
        notify(self.watchers, event="setattr", name=name, value=value)


def _make_nested_statedict(d=None):
    d = d if d is not None else dict()
    return {
        k: (
            v
            if not isinstance(v, dict) else
            StateDict(_make_nested_statedict(v))
        )
        for k, v in d.items()
    }


class StateDict:
    def __init__(self, state: dict | None = None):
        self.state = _make_nested_statedict(state)
        self.global_watchers: set[Callable] = set()
        self.watchers: dict[str, list[Callable]] = dict()

    def watch(self, uid: str, fn: Callable):
        self.watchers.setdefault(uid, []).append(fn)
        notify([fn], event="state", value=self.state.get(uid, None))

    def unwatch(self, uid: str, fn: Callable):
        if watchers := self.watchers.get(uid, None):
            watchers.remove(fn)

    def watch_all(self, fn: Callable):
        self.global_watchers.add(fn)
        notify([fn], event="state", value=self.state)

    def unwatch_all(self, fn: Callable):
        self.global_watchers.remove(fn)

    def __getitem__(self, uid: str):
        return self.state[uid]

    def __setitem__(self, uid: str, value):
        if isinstance(value, dict):
            value = StateDict(_make_nested_statedict(value))
        self.state[uid] = value
        notify(
            [*(self.watchers.get(uid, [])), *(self.global_watchers)],
            event="set", uid=uid, value=value,
        )

    def __delitem__(self, uid: str):
        if uid not in self.state:
            return

        del self.state[uid]
        notify(
            [*self.watchers.get(uid, []), *self.global_watchers],
            event="delete", uid=uid,
        )

    def __contains__(self, uid: str):
        return uid in self.state


def _make_nested_statelist(l=None):
    l = l if l is not None else list()
    return [
        e
        if not isinstance(e, list) else
        StateList(_make_nested_statelist(e))
        for e in l
    ]


class StateList:
    def __init__(self, state: list | None = None):
        self.state = _make_nested_statelist(state)
        self.watchers: list[Callable] = list()

    def watch(self, fn: Callable):
        self.watchers.append(fn)
        notify([fn], event="state", value=self.state)

    def unwatch(self, uid: str, fn: Callable):
        self.watchers.remove(fn)

    def __getitem__(self, index: int):
        return self.state[index]

    def __setitem__(self, index: int, value):
        if isinstance(value, list):
            value = StateList(_make_nested_statelist(value))
        self.state[index] = value
        notify(self.watchers, event="update", index=index, value=value)

    def append(self, value):
        if isinstance(value, list):
            value = StateList(_make_nested_statelist(value))
        self.state.append(value)
        notify(self.watchers, event="insert", index=len(self.state)-1, value=value)

    def insert(self, index, value):
        if isinstance(value, list):
            value = StateList(_make_nested_statelist(value))
        self.state.insert(index, value)
        notify(self.watchers, event="insert", index=index, value=value)

    def pop(self, index):
        self.state.pop(index)
        notify(self.watchers, event="remove", index=index, value=value)

    def remove(self, value):
        index = self.state.index(value)
        self.state.pop(index)
        notify(self.watchers, event="remove", index=index, value=value)


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
