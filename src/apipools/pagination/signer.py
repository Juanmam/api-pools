"""HMAC signing for opaque cursor envelope integrity."""

import hashlib
import hmac


class CursorSigner:
    """Sign and verify cursor envelope bytes."""

    def __init__(self, secret: bytes) -> None:
        self._secret = secret

    def sign(self, message: bytes) -> str:
        return hmac.new(self._secret, message, hashlib.sha256).hexdigest()

    def verify(self, message: bytes, signature: str) -> bool:
        expected = self.sign(message)
        return hmac.compare_digest(expected, signature)
