import logging
from datetime import datetime

import argon2
import jwt
from fastapi import Cookie, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from . import core

log = logging.getLogger(__name__)
hasher = argon2.PasswordHasher()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)


def make_token(data: dict[str, str]):
    return jwt.encode(
        data | {"exp": round((datetime.now() + core.JWT_EXPIRE).timestamp())},
        core.JWT_SECRET,
        algorithm="HS256",
    )


def check_token(token: str) -> bool:
    try:
        return jwt.decode(token, core.JWT_SECRET, algorithms=["HS256"])
    except jwt.DecodeError:
        log.info("Invalid token.")
        return None
    except jwt.ExpiredSignatureError:
        log.info("Expired token.")
        return None


class LoginRequest:
    def __init__(self, form: OAuth2PasswordRequestForm = Depends()):
        self.username = form.username
        self.password = form.password
        self.scopes = form.scopes
        self.authenticated = self.authenticate()
        self.token = self.tokenize()

    def authenticate(self) -> bool:
        return self.username == core.USERNAME and hasher.verify(
            core.PASSWORD_HASH, self.password
        )

    def tokenize(self) -> str | None:
        if self.authenticated:
            return make_token({"id": self.username})
        return None


class LoginRequired(Exception):
    pass


class TokenBearer:
    def __init__(
        self,
        exc: HTTPException = HTTPException(status_code=400, detail="Unauthorized."),
        redirect: bool = False,
    ):
        self.redirect = redirect
        self.exc = exc

    def __call__(
        self,
        header: str | None = Depends(oauth2_scheme),
        cookie: str | None = Cookie(default=None, alias="Authorization"),
    ):
        token = (
            cookie if check_token(cookie) else (header if check_token(header) else None)
        )
        if not bool(token):
            if self.redirect:
                raise LoginRequired()
            raise self.exc


@core.api.post("/login")
async def authenticate(request: LoginRequest = Depends()):
    if request.authenticated:
        return {"access_token": request.token, "token_type": "bearer"}
    raise HTTPException(400, "Invalid credentials.")


@core.api.exception_handler(LoginRequired)
async def login_redirect(request: Request, exc: LoginRequired):
    return RedirectResponse(url="/login")
