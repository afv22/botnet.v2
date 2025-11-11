import logging
from pathlib import Path

import nacl.signing
import nacl.encoding

logger = logging.Logger(__name__)


class Crypto:
    _signing_key = None

    KEYPATH = Path("private.key")

    def __init__(self) -> None:
        if self.KEYPATH.exists():
            key_bytes = self.KEYPATH.read_bytes()
            self._signing_key = nacl.signing.SigningKey(
                key_bytes, encoder=nacl.encoding.HexEncoder
            )
        else:
            logger.error("Private key file not found")

    def sign(self, message: str) -> str:
        if not self._signing_key:
            raise RuntimeError("Private key not initialized")

        signed = self._signing_key.sign(
            message.encode("utf-8"),
            encoder=nacl.encoding.HexEncoder,
        )

        return signed.signature.decode()
