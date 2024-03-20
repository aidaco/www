from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from typing import Self

import argon2
import jwt
import pydantic

from server.config import config


class CredentialError(Exception):
    pass


def hash_password(text: str) -> str:
    return argon2.PasswordHasher().hash(text)


def check_password(text: str, hash: str) -> None:
    try:
        argon2.PasswordHasher().verify(hash, text)
    except (argon2.exceptions.VerificationError, argon2.exceptions.InvalidHash):
        raise CredentialError("Incorrect password")


def encode_token(data: dict, secret: str, algorithm: str) -> str:
    return jwt.encode(
        data,
        secret,
        algorithm=algorithm,
    )


def decode_token(token: str, secret: str, algorithm: str) -> str:
    try:
        return jwt.decode(
            token,
            secret,
            algorithms=[algorithm],
        )
    except jwt.DecodeError as e:
        raise CredentialError(f"Invalid token {e}")
    except jwt.ExpiredSignatureError as e:
        raise CredentialError(f"Expired token {e}")


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
