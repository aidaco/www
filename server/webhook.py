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
    core.log.info("Successfully rebuilt. Restarting...")
    os.execv(sys.executable, ["python", *sys.argv])


def rebuild_static():
    subprocess.run("git pull", shell=True, check=True, capture_output=True)
    subprocess.run(
        f"{Path.cwd()/'dev.py'} buildstatic",
        shell=True,
        check=True,
        capture_output=True,
    )
    core.log.info("Successfully rebuilt. Restarting...")
    args = (sys.executable, (sys.executable, "-m", "server", *sys.argv[1:]))
    os.execv(*args)


async def rebuild():
    global rebuild_task
    # await cleanup()
    core.log.info("Push received. Starting rebuild...")
    if core.config.zipapp:
        rebuild_pyz()
    else:
        rebuild_static()


def verify_signature(body: bytes, signature: str, secret: str) -> None:
    if not signature:
        raise HTTPException(status_code=403, detail="Missing payload signature.")
    expected = (
        "sha256="
        + hmac.new(
            secret.encode("utf-8"),
            msg=body,
            digestmod=hashlib.sha256,
        ).hexdigest()
    )
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=403, detail="Failed to verify signature.")


def verify_branch(body: bytes, branch: str | None = None) -> bool:
    try:
        data = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=403, detail="Invalid request body.")
    requested = data.get("ref", None)
    expected = (
        f"refs/heads/{branch}"
        if branch
        else f"refs/heads/{data['repository']['default_branch']}"
    )
    if requested is None or requested != expected:
        return False
    return True


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
    body = await request.body()
    if core.config.rebuild is False:
        return {"message": "Rebuild disabled."}
    if core.config.rebuild.verify_signature:
        verify_signature(body, x_hub_signature_256, core.config.rebuild.secret)
    if core.config.rebuild.verify_branch and not verify_branch(
        body, core.config.rebuild.branch
    ):
        return {"message": "Not on default branch: no action will be taken."}
    background.add_task(rebuild)
    return {"message": "Push received, started upgrade."}
