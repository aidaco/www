import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from . import auth, livecontrol, requestdb, staticfiles, webhook


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await requestdb.opendb()
        yield
    finally:
        await requestdb.closedb()


api = FastAPI(lifespan=lifespan)
api.add_middleware(requestdb.LogRequests)
api.include_router(webhook.api)
api.add_exception_handler(auth.AuthenticationError, auth.RedirectForLogin())
api.include_router(auth.api)
api.include_router(livecontrol.api)
api.include_router(staticfiles.api)


def run():
    uvicorn.run(api, host="0.0.0", port=8000, log_level=logging.INFO)
