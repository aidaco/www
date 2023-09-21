import logging
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from . import auth_backends, core

log = logging.getLogger(__name__)
hasher = auth_backends.hasher()
tokenizer = auth_backends.tokenizer()
api = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)


class AuthenticationError(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Unauthorized.")


class Authentication:
    def __call__(
        self,
        header: Annotated[str | None, Depends(oauth2_scheme)] = None,
        cookie: Annotated[str | None, Cookie(alias="Authorization")] = None,
    ) -> str:
        token = header or cookie
        if not (token and tokenizer.check(token, core.config.jwt.secret)):
            raise AuthenticationError()
        return token


Auth: TypeAlias = Annotated[str, Depends(Authentication())]


class LoginRequest:
    def __init__(self, form: Annotated[OAuth2PasswordRequestForm, Depends()]):
        self.username = form.username
        self.password = form.password
        self.scopes = form.scopes
        self.authenticated = self.authenticate()


    def authenticate(self) -> str:
        if not (
            self.username == core.config.admin.username
            and hasher.check(self.password, core.config.admin.password_hash)
        ):
            raise HTTPException(status_code=401, detail="Invalid credentials.")
        return tokenizer.tokenize(
            {"id": self.username, "scopes": str(self.scopes)},
            core.config.jwt.secret,
            core.config.jwt.ttl,
        )


class RedirectForLogin:
    async def __call__(self, request: Request, exc: AuthenticationError):
        url = request.url
        core.log.info(f"Hit {url} without authentication.")
        return RedirectResponse(url="/login")


@api.post("/login")
async def authenticate(login: Annotated[LoginRequest, Depends()]):
    return {"access_token": login.authenticate(), "token_type": "bearer"}
