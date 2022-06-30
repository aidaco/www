#! /bin/python
import sys
import asyncio
from uuid import uuid4
import logging
from datetime import datetime, timedelta

import uvicorn
import jwt
from jinja2 import Template
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse


log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)
api = FastAPI()


class ConMan:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}
        self.active: dict[str, str] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        uid = str(uuid4())
        try:
            await websocket.send_text(f"CONNECT {uid}")
            self.connections[uid] = websocket
            log.info(f"Connected {uid}")
            return uid
        except WebSocketDisconnect:
            return None

    def disconnect(self, uid: str):
        if uid in self.connections:
            del self.connections[uid]
        if uid in self.active:
            del self.active[uid]
        log.info(f"Disconnected {uid}")
        return uid

    async def activate(self, uid: str):
        try:
            await self.connections[uid].send_text(f"ACTIVATE")
            self.active[uid] = ""
            log.info(f"Activated {uid}")
        except WebSocketDisconnect:
            self.disconnect(uid)

    async def deactivate(self, uid: str):
        try:
            await self.connections[uid].send_text(f"DEACTIVATE")
            log.info(f"Deactivated {uid}")
        except WebSocketDisconnect:
            self.disconnect(uid)
        finally:
            if uid in self.active:
                del self.active[uid]

    async def update(self, uid: str, content: str):
        try:
            await self.connections[uid].send_text(f"UPDATE {content}")
            self.active[uid] = content
        except WebSocketDisconnect:
            self.disconnect(uid)

    async def append(self, uid: str, content: str):
        try:
            await self.connections[uid].send_text(f"APPEND {content}")
            self.active[uid] += content
        except WebSocketDisconnect:
            self.disconnect(uid)

    async def clear(self, uid: str):
        try:
            await self.connections[uid].send_text(f"CLEAR")
            self.active[uid] = ""
        except WebSocketDisconnect:
            self.disconnect(uid)


manager = ConMan()

dashboard_jinja = Template(
    """
<!DOCTYPE html>
<html lang="en">
<script>
    function activate(uid) {
        const response = fetch(`/madness/dispatch?command=ACTIVATE&uid=${uid}`, {method: 'POST'})
        location.reload()
    }
    function update(uid) {
        const content = document.getElementById(uid).value
        const response = fetch(`/madness/dispatch?command=UPDATE&uid=${uid}&content=${content}`, {method: 'POST'})
    }
    function deactivate(uid) {
        const response = fetch(`/madness/dispatch?command=DEACTIVATE&uid=${uid}`, {method: 'POST'})
        location.reload()
    }
</script>
<head>
    <title>🐵</title>
</head>
<body>
    {% for item in connections %}
        {% if item not in active %}
            <button onClick="activate('{{item}}')">{{ item }}</button>
        {% endif %}
    {% endfor %}
    <hr>
    {% for uid, content in active.items() %}
        <div>
            <button id='deactivate-{{ uid }}' onClick="deactivate('{{ uid }}')">{{ uid }}</button>
            <input type='text' id='{{ uid }}' name='{{ uid }}' value='{{ content }}'>
            <script>document.getElementById('{{ uid }}').oninput = (event) => {update('{{ uid }}')}</script>
        </div>
    {% endfor %}
</body>
</html>
"""
)


login_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>🐵</title>
</head>
<body>
    <form action="/madness/auth">
        <input type='text' name='username'><br>
        <input type='password' name='password'><br>
        <input type='submit' value='Submit'>
    </form>
</body>
</html>
"""


CREDENTIALS = ("username", "password")
JWT_SECRET = "secret"


@api.get("/madness/login")
async def login():
    return HTMLResponse(login_html)


@api.get("/madness/auth")
async def authenticate(response: Response, username: str, password: str):
    if (username, password) == CREDENTIALS:
        response = RedirectResponse("/madness")
        response.set_cookie(
            key="madness-login",
            value=jwt.encode(
                {"exp": datetime.now() + timedelta(days=30)}, JWT_SECRET, algorithm="HS256"
            ),
        )
        log.info("AUTH SUCCESS")
        return response
    response.status_code = 403
    log.info("AUTH FAIL")
    return response


def require_auth(token: str = Cookie(default=None, alias="madness-login")):
    try:
        jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return True
    except jwt.DecodeError:
        return False
    except jwt.ExpiredSignatureError:
        return False


@api.get("/madness")
async def dashboard(auth=Depends(require_auth)):
    if not auth:
        return RedirectResponse("/login")

    return HTMLResponse(
        dashboard_jinja.render(connections=manager.connections, active=manager.active)
    )


@api.get("/madness/connections")
async def connections(response: Response, auth=Depends(require_auth)):
    if not auth:
        response.status_code = 403
        return response
    return [
        {"id": con, "active": (con in manager.active), "content": manager.active.get(con, "")}
        for con in manager.connections
    ]


@api.post("/madness/dispatch")
async def dispatch_command(
    response: Response, command: str, uid: str, content: str = "", auth=Depends(require_auth)
):
    if not auth:
        response.status_code = 403
        return response
    match command:
        case "ACTIVATE":
            await manager.activate(uid)
        case "DEACTIVATE":
            await manager.deactivate(uid)
        case "UPDATE":
            await manager.update(uid, content)
        case "APPEND":
            await manager.append(uid, content)
        case "CLEAR":
            await manager.clear(uid, content)


@api.websocket("/madness/live")
async def ws_connect(websocket: WebSocket):
    uid = await manager.connect(websocket)
    while uid in manager.connections:
        try:
            data = await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(uid)
        await asyncio.sleep(0.5)


def main(username: str, password: str, jwt_secret: str):
    global CREDENTIALS, JWT_SECRET
    CREDENTIALS = (username, password)
    JWT_SECRET = jwt_secret

    uvicorn.run(api, host="0.0.0.0", port=8000, log_level=logging.WARNING)


if __name__ == "__main__":
    args = sys.argv
    main(args[1], args[2], args[3])
