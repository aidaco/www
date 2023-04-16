import binascii
import hashlib
import os

try:
    import argon2

    USE_HASHLIB = False
except ImportError:
    USE_HASHLIB = True


class Argon2CFFI:
    def __init__(self):
        self.hasher = argon2.PasswordHasher()

    def hash(self, text: str) -> str:
        return self.hasher.hash(text)

    def check(self, text: str, hash: str) -> bool:
        try:
            return self.hasher.verify(text, hash)
        except argon2.exceptions.VerificationError:
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


def hasher():
    if USE_HASHLIB:
        return HashlibSHA512()
    else:
        return Argon2CFFI()
