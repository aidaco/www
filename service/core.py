import logging

import uvicorn
from fastapi import FastAPI
from rich.logging import RichHandler

from .wsmanager import WSManager
from .config import Config

log = logging.getLogger(__name__)
log.addHandler(RichHandler())
log.setLevel(logging.INFO)

config: Config
manager = WSManager()
api = FastAPI()


def start():
    global config
    config = Config.locate(".aidan.software")
    uvicorn.run(api, host="0.0.0.0", port=8000, log_level=logging.INFO)
