import logging

from rich.logging import RichHandler

from .api import run
from .config import Config, locate

log = logging.getLogger(__name__)
log.addHandler(RichHandler())
log.setLevel(logging.INFO)

config: Config


def start():
    global config
    config = locate("aidan.software")
    run()
