import logging
from typing import Annotated, TypeAlias, Self
from datetime import timedelta, datetime, timezone

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    Response,
    Form,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import pydantic

from .config import config
from .auth_base import check_password, encode_token, decode_token, CredentialError


log = logging.getLogger(__name__)


class TokenData(pydantic.BaseModel):
    userid: str
    scopes: list[str]
    exp: datetime

    @classmethod
    def accesstoken(
        cls, userid: str, scopes: list[str] | None = None, dur: timedelta | None = None
    ) -> Self:
        return TokenData(
            userid=userid,
            scopes=scopes if scopes is not None else [],
            exp=datetime.now(tz=timezone.utc) + (dur or config.jwt.access_ttl),
        )

    @classmethod
    def refreshtoken(
        cls, userid: str, scopes: list[str] | None = None, dur: timedelta | None = None
    ) -> Self:
        return TokenData(
            userid=userid,
            scopes=scopes if scopes is not None else [],
            exp=datetime.now(tz=timezone.utc) + (dur or config.jwt.refresh_ttl),
        )

    def encode(self, secret: str | None = None, algorithm: str | None = None) -> str:
        return encode_token(
            self.model_dump(),
            secret or config.jwt.secret,
            algorithm or config.jwt.algorithm,
        )

    @classmethod
    def decode(
        cls, token: str, secret: str | None = None, algorithm: str | None = None
    ) -> Self:
        try:
            return cls.model_validate(
                decode_token(
                    token,
                    secret or config.jwt.secret,
                    algorithm or config.jwt.algorithm,
                )
            )
        except pydantic.ValidationError:
            raise CredentialError("Malformed token")


class UserData(pydantic.BaseModel):
    username: str
    password_hash: str

    def verify(self, password: str):
        check_password(password, self.password_hash)


def get_user(username: str) -> UserData:
    if username != config.admin.username:
        raise CredentialError("Invalid user.")
    return UserData(username=username, password_hash=config.admin.password_hash)


def authenticate_password(username: str, password: str) -> UserData:
    user = get_user(username)
    user.verify(password)
    return user


def authenticate_token(token: str) -> tuple[TokenData, UserData]:
    tokendata = TokenData.decode(token)
    userdata = get_user(tokendata.userid)
    return tokendata, userdata


class AuthenticationError(HTTPException):
    def __init__(self, msg=None):
        super().__init__(
            status_code=401, detail="Unauthorized" + (f": {msg}." if msg else ".")
        )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token", auto_error=False)


def authenticate_request(
    header: Annotated[str | None, Depends(oauth2_scheme)] = None,
    cookie: Annotated[str | None, Cookie(alias="Authorization")] = None,
) -> tuple[TokenData, UserData]:
    try:
        token = TokenData.decode(header or cookie or "")
        user = get_user(token.userid)
        return token, user
    except CredentialError as e:
        raise AuthenticationError(e)


def authenticate_request_or_redirect(
    header: Annotated[str | None, Depends(oauth2_scheme)] = None,
    cookie: Annotated[str | None, Cookie(alias="Authorization")] = None,
) -> tuple[TokenData, UserData]:
    try:
        token = TokenData.decode(header or cookie or "")
        user = get_user(token.userid)
        return token, user
    except CredentialError as e:
        raise HTTPException(307, f"Unauthorized: {e}.", headers={"Location": "/login"})


Auth: TypeAlias = Annotated[tuple[TokenData, UserData], Depends(authenticate_request)]
AuthRedirect: TypeAlias = Annotated[
    tuple[TokenData, UserData], Depends(authenticate_request_or_redirect)
]


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
        response_type: Annotated[
            str,
            Form(pattern="json|cookie"),
        ] = "json",
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
        access_ttl: Annotated[timedelta | None, Form()] = None,
        provide_refresh: Annotated[bool, Form()] = True,
        refresh_ttl: Annotated[timedelta | None, Form()] = None,
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
        self.response_type = response_type
        self.username = username
        self.password = password
        self.refresh_token = refresh_token or refresh_token_cookie
        self.scopes = scope.split()
        self.access_ttl = access_ttl
        self.provide_refresh = provide_refresh
        self.refresh_ttl = refresh_ttl
        self.client_id = client_id
        self.client_secret = client_secret


@api.post("/auth/token")
async def authenticate(
    form: Annotated[EnhancedOAuth2PasswordRequest, Depends()], response: Response
):
    if form.grant_type == "password" and form.username and form.password:
        try:
            user = authenticate_password(form.username, form.password)
        except CredentialError as e:
            raise AuthenticationError(e)
    elif form.grant_type == "refresh_token" and form.refresh_token:
        try:
            token, user = authenticate_token(form.refresh_token)
        except CredentialError as e:
            raise AuthenticationError(e)
    else:
        raise AuthenticationError(
            'allowed grant_type options are "password" or "refresh_token"'
        )
    access_token = TokenData.accesstoken(
        userid=user.username,
        scopes=form.scopes,
    )

    if form.response_type == "cookie":
        response.set_cookie(
            "Authorization",
            access_token.encode(),
            expires=access_token.exp,
            secure=True,
            httponly=True,
            samesite="strict",
        )
        if not form.provide_refresh:
            return
    if not form.provide_refresh:
        return {
            "access_token": access_token.encode(),
            "token_type": "bearer",
        }

    refresh_token = TokenData.refreshtoken(
        userid=user.username,
        scopes=form.scopes,
    )
    if form.response_type == "cookie":
        response.set_cookie(
            "RefreshAuthorization",
            refresh_token.encode(),
            expires=refresh_token.exp,
            secure=True,
            httponly=True,
            samesite="strict",
            path="/auth",
        )
        return
    return {
        "access_token": access_token.encode(),
        "refresh_token": refresh_token.encode(),
        "token_type": "bearer",
    }


@api.post("/auth/logout")
def logout(auth: Auth, response: Response):
    response.delete_cookie(
        "Authorization", secure=True, httponly=True, samesite="strict"
    )
    response.delete_cookie(
        "RefreshAuthorization",
        path="/auth",
        secure=True,
        httponly=True,
        samesite="strict",
    )
