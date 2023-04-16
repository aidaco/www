import asyncio
import contextlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

import psutil
from fastapi import Header, Request

from .core import api


async def cancel_tasks():
    tasks = (t for t in asyncio.all_tasks() if t is not asyncio.current_task())
    [t.cancel() for t in tasks]
    await asyncio.gather(*tasks)


async def close_files():
    pid = os.getpid()
    parent = psutil.Process(pid)
    for ch in parent.children(recursive=True):
        for fd in ch.open_files() + ch.connections():
            os.fsync(fd.fd)
            os.close(fd.fd)


def rebuildpyz():
    git_dir = Path.cwd() / ".git.aidan.software"
    subprocess.run(
        f"git clone --branch github-webhook --single-branch https://github.com/aidaco/www {git_dir}",
        shell=True,
    )
    with contextlib.chdir(git_dir):
        subprocess.run("./dev.py buildpyz", shell=True, check=True)
    (git_dir / "aidan.software.pyz").replace(Path.cwd() / "aidan.software.pyz")
    shutil.rmtree(git_dir)
    os.execv(sys.executable, ["python", *sys.argv])


def rebuildstatic():
    subprocess.run("git pull", shell=True)
    subprocess.run("./dev.py buildstatic", shell=True)
    os.execv(sys.executable, ["python", *sys.argv])


@api.post("/webhook/{appname}")
async def receive_webhook(
    request: Request, appname: str, x_github_event: str = Header(...)
):
    match x_github_event:
        case "ping":
            return {"message": "pong"}
        case "push":
            pass
        case _:
            return {"message": "Unknown: no action will be taken."}
    # body = await request.json()
    # branch = body.get("ref", None)
    # main = f"refs/heads/{body['repository']['default_branch']}"
    # if branch is None or branch != main:
    #     return {"message": "Not on default branch: no action will be taken."}
    rebuildpyz()
    return {"message": "Push received, started upgrade."}
