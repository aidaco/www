import logging

import uvicorn
from fastapi import FastAPI
from rich.logging import RichHandler

from .config import Config
from .wsmanager import WSManager

log = logging.getLogger(__name__)
log.addHandler(RichHandler())
log.setLevel(logging.INFO)

config = Config.locate("aidan.software")
manager = WSManager()
api = FastAPI()


def start():
    uvicorn.run(api, host="0.0.0.0", port=8000, log_level=logging.INFO)
