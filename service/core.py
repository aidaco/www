import logging

import uvicorn
from fastapi import FastAPI
from rich.logging import RichHandler

from . import wsmanager
from .config import config, dependencies # noqa: F401

log = logging.getLogger(__name__)
log.addHandler(RichHandler())
log.setLevel(logging.INFO)


manager = wsmanager.WSManager()
api = FastAPI()


def start():
    log.setLevel(config.logging.level)
    uvicorn.run(
        api,
        host=config.host.hostname,
        port=config.host.port,
        log_level=config.log.level,
    )
