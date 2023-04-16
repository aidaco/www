import asyncio
import contextlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

import psutil
from fastapi import Header, Request

from . import core
from .core import api


async def cleanup():
    return
    # TODO: throws lots of CancelledErrors
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [t.cancel() for t in tasks]
    await asyncio.gather(*tasks)

    pid = os.getpid()
    parent = psutil.Process(pid)
    for ch in parent.children(recursive=True):
        for fd in ch.open_files() + ch.connections():
            os.fsync(fd.fd)
            os.close(fd.fd)


async def rebuild_pyz():
    git_dir = Path.cwd() / "git.aidan.software"
    subprocess.run(
        f"git clone --branch main --single-branch https://github.com/aidaco/www {git_dir}",
        shell=True,
    )
    with contextlib.chdir(git_dir):
        subprocess.run("./dev.py buildpyz", shell=True, check=True)
    (git_dir / "aidan.software.pyz").replace(Path.cwd() / "aidan.software.pyz")
    shutil.rmtree(git_dir)
    os.execv(sys.executable, ["python", *sys.argv])


async def rebuild_static():
    subprocess.run("git pull", shell=True)
    subprocess.run("./dev.py buildstatic", shell=True)
    argv = ["python", "-m", "server", *sys.argv[1:]]
    os.execv(sys.executable, argv)


rebuild_task = None


async def rebuild():
    global rebuild_task
    await asyncio.sleep(0.5)
    await cleanup()
    if core.config.zipapp:
        rebuild_task = asyncio.create_task(rebuild_pyz())
    else:
        rebuild_task = asyncio.create_task(rebuild_static())


@api.post("/webhook/{appname}")
async def receive_webhook(
    request: Request, appname: str, x_github_event: str = Header(...)
):
    global rebuild_task
    match x_github_event:
        case "ping":
            return {"message": "pong"}
        case "push":
            pass
        case _:
            return {"message": "Unknown: no action will be taken."}
    body = await request.json()
    branch = body.get("ref", None)
    main = f"refs/heads/{body['repository']['default_branch']}"
    if branch is None or branch != main:
        return {"message": "Not on default branch: no action will be taken."}
    await rebuild()
    return {"message": "Push received, started upgrade."}
