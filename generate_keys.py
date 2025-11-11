#!/usr/bin/env python3
"""
Generate Ed25519 key pair for signing updates.
Saves private key to private.key and public key to public.key
"""

import nacl.signing
import nacl.encoding


def generate_keys():
    # Generate new signing key pair
    signing_key = nacl.signing.SigningKey.generate()

    # Get private key bytes (hex encoded for easy storage)
    private_key_hex = signing_key.encode(encoder=nacl.encoding.HexEncoder)

    # Get public key bytes (hex encoded)
    verify_key = signing_key.verify_key
    public_key_hex = verify_key.encode(encoder=nacl.encoding.HexEncoder)

    # Save private key
    with open("c2/private.key", "wb") as f:
        f.write(private_key_hex)
    print(f"Private key saved to private.key")

    # Save public key
    with open("bot/public.key", "wb") as f:
        f.write(public_key_hex)
    print(f"\nPublic key saved to public.key")

    print("\n⚠️  IMPORTANT:")
    print("- Keep private.key SECRET (use on server only)")
    print("- Distribute public.key to IoT devices")
    print("- Add private.key to .gitignore")


if __name__ == "__main__":
    generate_keys()
