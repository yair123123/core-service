import base64
import hashlib
import hmac
import json
import os
from datetime import UTC, datetime, timedelta


PBKDF2_ITERATIONS = 100_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        PBKDF2_ITERATIONS,
        base64.urlsafe_b64encode(salt).decode("utf-8"),
        base64.urlsafe_b64encode(digest).decode("utf-8"),
    )


def verify_password(password: str, encoded_password: str) -> bool:
    try:
        _, iterations_str, salt_b64, digest_b64 = encoded_password.split("$")
        iterations = int(iterations_str)
        salt = base64.urlsafe_b64decode(salt_b64.encode("utf-8"))
        expected_digest = base64.urlsafe_b64decode(digest_b64.encode("utf-8"))
    except (ValueError, TypeError):
        return False

    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(digest, expected_digest)


def create_access_token(user_id: int, secret_key: str, algorithm: str, expires_in_seconds: int) -> str:
    if algorithm != "HS256":
        raise ValueError("Only HS256 is supported")
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in_seconds)).timestamp()),
    }
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode("utf-8")).decode("utf-8").rstrip("=")
    signature = hmac.new(secret_key.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")
    return f"{payload_b64}.{signature_b64}"


def decode_token(token: str, secret_key: str, algorithm: str) -> dict:
    if algorithm != "HS256":
        raise ValueError("Only HS256 is supported")
    try:
        payload_b64, signature_b64 = token.split(".", maxsplit=1)
        expected_signature = hmac.new(secret_key.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest()
        actual_signature = base64.urlsafe_b64decode(signature_b64 + "=" * (-len(signature_b64) % 4))
        if not hmac.compare_digest(expected_signature, actual_signature):
            raise ValueError("Invalid signature")

        payload_json = base64.urlsafe_b64decode(payload_b64 + "=" * (-len(payload_b64) % 4)).decode("utf-8")
        payload = json.loads(payload_json)
    except Exception as exc:
        raise ValueError("Invalid token") from exc

    exp = payload.get("exp")
    if not isinstance(exp, int) or exp < int(datetime.now(UTC).timestamp()):
        raise ValueError("Token expired")
    return payload
