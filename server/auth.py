import logging
from typing import Annotated, Self, TypeAlias
from datetime import datetime, timedelta, timezone

from pydantic import BaseModel
from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    Request,
    Response,
    Form,
)
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
import argon2

from .config import config


log = logging.getLogger(__name__)


class CredentialError(Exception):
    pass


def hash_password(text: str) -> str:
    return argon2.PasswordHasher().hash(text)


def check_password(text: str, hash: str) -> None:
    try:
        argon2.PasswordHasher().verify(hash, text)
    except (argon2.exceptions.VerificationError, argon2.exceptions.InvalidHash):
        raise CredentialError("Incorrect password")


def encode_token(data: dict):
    return jwt.encode(
        data,
        config.jwt.secret,
        algorithm="HS256",
    )


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, config.jwt.secret, algorithms=["HS256"])
    except jwt.DecodeError:
        raise CredentialError("Invalid token")
    except jwt.ExpiredSignatureError:
        raise CredentialError("Expired token")


class TokenData(BaseModel):
    id: str
    exp: datetime
    scopes: list[str]

    def encode(self) -> str:
        return encode_token(
            {
                "id": self.id,
                "exp": self.exp.timestamp(),
                "scopes": " ".join(self.scopes),
            }
        )

    @classmethod
    def decode(cls, token: str) -> Self:
        data = decode_token(token)
        data["exp"] = datetime.fromtimestamp(data["exp"], timezone.utc)
        data["scopes"] = data["scopes"].split(" ")
        return cls(**data)


class UserData(BaseModel):
    username: str
    password_hash: str

    def verify(self, password: str):
        check_password(password, self.password_hash)


def get_user(username: str) -> UserData | None:
    if username == config.admin.username:
        return UserData(username=username, password_hash=config.admin.password_hash)


def authenticate_password(username: str, password: str) -> UserData:
    user = get_user(username)
    if not user:
        raise CredentialError("Invalid user.")
    user.verify(password)
    return user


def authenticate_token(token: str | None) -> UserData:
    if not token:
        raise CredentialError()
    if not TokenData.decode(token).id == config.admin.username:
        raise CredentialError()
    return UserData(
        username=config.admin.username, password_hash=config.admin.password_hash
    )


class AuthenticationError(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Unauthorized.")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token", auto_error=False)


def authenticate_request(
    header: Annotated[str | None, Depends(oauth2_scheme)] = None,
    cookie: Annotated[str | None, Cookie(alias="Authorization")] = None,
) -> UserData:
    try:
        return authenticate_token(header or cookie)
    except CredentialError:
        raise AuthenticationError()


Auth: TypeAlias = Annotated[UserData, Depends(authenticate_request)]


def redirect_for_login(request: Request, exc: AuthenticationError):
    url = request.url
    log.info(f"Hit {url} without authentication.")
    return RedirectResponse(url="/login")


api = APIRouter()


class EnhancedOAuth2PasswordRequest(OAuth2PasswordRequestForm):
    """Adds support for refresh_token grant (optionally by cookie), and optionally specifying a TTL."""

    def __init__(
        self,
        *,
        grant_type: Annotated[
            str | None,
            Form(pattern="password|refresh_token"),
        ] = None,
        username: Annotated[str | None, Form()] = None,
        password: Annotated[
            str | None,
            Form(),
        ] = None,
        refresh_token: Annotated[str | None, Form()] = None,
        refresh_token_cookie: Annotated[
            str | None, Cookie(alias="RefreshAuthorization")
        ] = None,
        scope: Annotated[
            str,
            Form(),
        ] = "",
        access_ttl: Annotated[timedelta, Form()] = config.jwt.access_ttl,
        session_ttl: Annotated[timedelta | None, Form()] = config.jwt.session_ttl,
        client_id: Annotated[
            str | None,
            Form(),
        ] = None,
        client_secret: Annotated[
            str | None,
            Form(),
        ] = None,
    ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.refresh_token = refresh_token or refresh_token_cookie
        self.scopes = scope.split()
        self.access_ttl = access_ttl
        self.session_ttl = session_ttl
        self.client_id = client_id
        self.client_secret = client_secret


@api.post("/token")
async def authenticate(
    form: Annotated[EnhancedOAuth2PasswordRequest, Depends()], response: Response
):
    if form.grant_type == "password" and form.username and form.password:
        try:
            user = authenticate_password(form.username, form.password)
        except CredentialError:
            raise AuthenticationError()
    elif form.grant_type == "refresh_token" and form.refresh_token:
        try:
            user = authenticate_token(form.refresh_token)
        except CredentialError:
            raise AuthenticationError()
    else:
        raise AuthenticationError()
    access_token = TokenData(
        id=user.username,
        exp=datetime.now(timezone.utc) + form.access_ttl,
        scopes=form.scopes,
    )
    response.set_cookie(
        "Authorization",
        f"{access_token.encode()}",
        expires=access_token.exp,
        secure=True,
        httponly=True,
    )
    if not form.session_ttl:
        return {"access_token": access_token.encode(), "token_type": "bearer"}
    refresh_token = TokenData(
        id=user.username,
        exp=datetime.now(timezone.utc) + form.session_ttl,
        scopes=form.scopes,
    )
    response.set_cookie(
        "RefreshAuthorization",
        f"{refresh_token.encode()}",
        expires=refresh_token.exp,
        secure=True,
        httponly=True,
        path="/token",
    )
    return {
        "access_token": access_token.encode(),
        "refresh_token": refresh_token.encode(),
        "token_type": "bearer",
    }
