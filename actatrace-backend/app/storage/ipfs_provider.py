from app.storage.exceptions import InvalidStorageConfiguration
from app.storage.provider import StorageProvider
from app.storage.schemas import StorageUploadResult


class IPFSStorageProvider(StorageProvider):
    def upload_file(self, file_bytes: bytes, object_key: str, content_type: str) -> StorageUploadResult:
        raise InvalidStorageConfiguration("IPFS storage is a Phase 4 placeholder and is not enabled")

    def get_file(self, object_key: str) -> bytes:
        raise InvalidStorageConfiguration("IPFS storage is a Phase 4 placeholder and is not enabled")

    def generate_presigned_url(self, object_key: str, expires_in: int) -> str:
        raise InvalidStorageConfiguration("IPFS storage is a Phase 4 placeholder and is not enabled")

    def file_exists(self, object_key: str) -> bool:
        raise InvalidStorageConfiguration("IPFS storage is a Phase 4 placeholder and is not enabled")

    def delete_file(self, object_key: str) -> bool:
        raise InvalidStorageConfiguration("IPFS storage is a Phase 4 placeholder and is not enabled")
