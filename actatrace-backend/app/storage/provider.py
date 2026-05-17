from abc import ABC, abstractmethod

from app.storage.schemas import StorageUploadResult


class StorageProvider(ABC):
    @abstractmethod
    def upload_file(self, file_bytes: bytes, object_key: str, content_type: str) -> StorageUploadResult:
        raise NotImplementedError

    @abstractmethod
    def get_file(self, object_key: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def generate_presigned_url(self, object_key: str, expires_in: int) -> str:
        raise NotImplementedError

    @abstractmethod
    def file_exists(self, object_key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def delete_file(self, object_key: str) -> bool:
        raise NotImplementedError
