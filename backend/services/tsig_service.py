import base64
import secrets


def generate_tsig_secret(length: int = 32) -> str:
    return base64.b64encode(secrets.token_bytes(length)).decode("ascii")
