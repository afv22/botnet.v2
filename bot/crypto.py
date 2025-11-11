import logging
from pathlib import Path

import nacl.signing
import nacl.encoding

logger = logging.Logger(__name__)


class Crypto:
    _verify_key = None

    KEYPATH = Path("public.key")

    def __init__(self) -> None:
        if not self.KEYPATH.exists():
            logger.error("Private key file not found")
            return

        key_bytes = self.KEYPATH.read_bytes()
        self._verify_key = nacl.signing.VerifyKey(
            key_bytes, encoder=nacl.encoding.HexEncoder
        )

    def verify(self, message: str, signature: str) -> None:
        if not self._verify_key:
            raise RuntimeError("Private key not initialized")

        self._verify_key.verify(
            message.encode("utf-8"),
            signature=bytes.fromhex(signature),
        )


crypto_manager = Crypto()
