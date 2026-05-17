from pathlib import Path

from app.storage.exceptions import StorageObjectMissing
from app.storage.provider import StorageProvider
from app.storage.schemas import StorageUploadResult


class LocalStorageProvider(StorageProvider):
    def __init__(self, base_path: str = "./storage") -> None:
        self.base_path = Path(base_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def upload_file(self, file_bytes: bytes, object_key: str, content_type: str) -> StorageUploadResult:
        target = self._resolve_object_key(object_key)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(file_bytes)
        return StorageUploadResult(
            provider="local",
            bucket=None,
            object_key=object_key,
            storage_url=str(target),
            size_bytes=len(file_bytes),
            content_type=content_type,
        )

    def get_file(self, object_key: str) -> bytes:
        target = self._resolve_object_key(object_key)
        if not target.exists():
            raise StorageObjectMissing("Document object is missing from storage")
        return target.read_bytes()

    def generate_presigned_url(self, object_key: str, expires_in: int) -> str:
        target = self._resolve_object_key(object_key)
        if not target.exists():
            raise StorageObjectMissing("Document object is missing from storage")
        return f"local://{object_key}?expires_in={expires_in}"

    def file_exists(self, object_key: str) -> bool:
        return self._resolve_object_key(object_key).exists()

    def delete_file(self, object_key: str) -> bool:
        target = self._resolve_object_key(object_key)
        if not target.exists():
            return False
        target.unlink()
        return True

    def _resolve_object_key(self, object_key: str) -> Path:
        target = (self.base_path / object_key).resolve()
        if not str(target).startswith(str(self.base_path)):
            raise StorageObjectMissing("Invalid object key")
        return target
