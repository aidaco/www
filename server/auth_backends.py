import binascii
import hashlib
import logging
import os
from datetime import datetime, timedelta

log = logging.getLogger(__name__)


import jwt  # PyJWT: https://github.com/jpadilla/pyjwt

try:
    import argon2  # argon2-cffi: https://github.com/hynek/argon2-cffi

    USE_HASHLIB = False
except ImportError:
    USE_HASHLIB = True


def hasher():
    if USE_HASHLIB:
        return HashlibSHA512()
    else:
        return Argon2CFFI()


def tokenizer():
    return PyJWT()


class Argon2CFFI:
    def __init__(self):
        self.hasher = argon2.PasswordHasher()

    def hash(self, text: str) -> str:
        return self.hasher.hash(text)

    def check(self, text: str, hash: str) -> bool:
        try:
            return self.hasher.verify(hash, text)
        except (argon2.exceptions.VerificationError, argon2.exceptions.InvalidHash):
            return False


class HashlibSHA512:
    def hash(self, text: str) -> str:
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
        pwdhash = hashlib.pbkdf2_hmac("sha512", text.encode("utf-8"), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode("ascii")

    def check(self, text: str, hash: str) -> bool:
        salt = hash[:64]
        stored_password = hash[64:]
        hash_bytes = hashlib.pbkdf2_hmac(
            "sha512", text.encode("utf-8"), salt.encode("ascii"), 100000
        )
        pwdhash = binascii.hexlify(hash_bytes).decode("ascii")
        return pwdhash == stored_password


class PyJWT:
    def tokenize(self, data: dict[str, str], secret: str, ttl: timedelta):
        return jwt.encode(
            data | {"exp": round((datetime.now() + ttl).timestamp())},
            secret,
            algorithm="HS256",
        )

    def check(self, token: str, secret: str) -> bool:
        try:
            return bool(jwt.decode(token, secret, algorithms=["HS256"]))
        except jwt.DecodeError:
            log.info("Invalid token.")
            return False
        except jwt.ExpiredSignatureError:
            log.info("Expired token.")
            return False
