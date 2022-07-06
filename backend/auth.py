import logging
from datetime import datetime, timedelta

import jwt
from fastapi import Cookie, Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from rich.logging import RichHandler

log = logging.getLogger(__name__)
log.addHandler(RichHandler())
log.setLevel(logging.INFO)
api = FastAPI()

CREDENTIALS = ("username", "password")
JWT_SECRET = "supersecretvalue"
JWT_EXPIRE = timedelta(days=1)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)


class LoginRequired(Exception):
    pass


def make_token(data: dict[str, str]):
    return jwt.encode(
        data | {"exp": round((datetime.now() + JWT_EXPIRE).timestamp())},
        JWT_SECRET,
        algorithm="HS256",
    )


def check_token(token: str) -> bool:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        return None


class LoginRequest:
    def __init__(self, form: OAuth2PasswordRequestForm = Depends()):
        self.username = form.username
        self.password = form.password
        self.scopes = form.scopes
        self.authenticated = self.authenticate()
        self.token = self.tokenize()

    def authenticate(self) -> bool:
        return (self.username, self.password) == CREDENTIALS

    def tokenize(self) -> str | None:
        if self.authenticated:
            return make_token({"id": self.username})
        return None


class TokenBearer:
    def __init__(self, redirect: bool = False):
        self.redirect = redirect

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
            else:
                raise HTTPException(status_code=400, detail="Unauthorized.")
