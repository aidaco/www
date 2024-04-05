import argon2
import jwt


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
