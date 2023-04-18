import asyncio
import contextlib
import hashlib
import hmac
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Annotated

import psutil
from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

from . import core

api = APIRouter()


async def cleanup():
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [t.cancel() for t in tasks]
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        pass

    pid = os.getpid()
    parent = psutil.Process(pid)
    for ch in parent.children(recursive=True):
        for fd in ch.open_files() + ch.connections():
            try:
                os.fsync(fd.fd)
                os.close(fd.fd)
            except OSError:
                pass


def rebuild_pyz():
    git_dir = Path.cwd() / "git.aidan.software"
    subprocess.run(
        f"git clone --branch main --single-branch https://github.com/aidaco/www {git_dir}",
        shell=True,
        capture_output=True,
        check=True,
    )
    with contextlib.chdir(git_dir):
        subprocess.run("./dev.py buildpyz", shell=True, capture_output=True, check=True)
    (git_dir / "aidan.software.pyz").replace(Path.cwd() / "aidan.software.pyz")
    shutil.rmtree(git_dir)
    os.execv(sys.executable, ["python", *sys.argv])


def rebuild_static():
    subprocess.run("git pull", shell=True, check=True, capture_output=True)
    subprocess.run(
        f"{Path.cwd()/'dev.py'} buildstatic",
        shell=True,
        check=True,
        capture_output=True,
    )
    print(sys.executable)
    args = (sys.executable, (sys.executable, "-m", "server", *sys.argv[1:]))
    print(f"os.execv{args}")
    os.execv(*args)


async def rebuild():
    global rebuild_task
    # await cleanup()
    core.log.info("Push received. Starting rebuild...")
    if core.config.zipapp:
        rebuild_pyz()
    else:
        rebuild_static()


def verify_signature(body, signature) -> str:
    if core.config.admin.verify_rebuild_signature:
        if not signature:
            raise HTTPException(status_code=403, detail="Missing payload signature.")
        expected = (
            "sha256="
            + hmac.new(
                core.config.admin.rebuild_secret.encode("utf-8"),
                msg=body,
                digestmod=hashlib.sha256,
            ).hexdigest()
        )
        if not hmac.compare_digest(expected, signature):
            raise HTTPException(status_code=403, detail="Failed to verify signature.")
    return body.decode("utf-8")


@api.post("/webhook/{appname}")
async def receive_webhook(
    request: Request,
    appname: str,
    x_github_event: Annotated[str, Header()],
    x_hub_signature_256: Annotated[str, Header()],
    background: BackgroundTasks,
):
    global rebuild_task
    match x_github_event:
        case "ping":
            return {"message": "pong"}
        case "push":
            pass
        case _:
            return {"message": "Unknown: no action will be taken."}
    try:
        body = json.loads(verify_signature(await request.body(), x_hub_signature_256))
    except json.JSONDecodeError:
        raise HTTPException(status_code=403, detail="Invalid request body.")
    branch = body.get("ref", None)
    main = f"refs/heads/{body['repository']['default_branch']}"
    if branch is None or branch != main:
        return {"message": "Not on default branch: no action will be taken."}
    background.add_task(rebuild)
    return {"message": "Push received, started upgrade."}
