import base64
import hashlib
from pathlib import Path


class HashService:
    algorithm = "sha256"

    def generate_sha256_from_bytes(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def generate_sha256_from_file(self, path: str) -> str:
        digest = hashlib.sha256()
        with Path(path).open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def verify_sha256(self, content: bytes, expected_hash: str) -> bool:
        return self.generate_sha256_from_bytes(content) == expected_hash.lower()

    def decode_base64(self, value: str) -> bytes:
        return base64.b64decode(value, validate=True)
