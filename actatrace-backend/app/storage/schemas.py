from pydantic import BaseModel


class StorageUploadResult(BaseModel):
    provider: str
    bucket: str | None = None
    object_key: str
    storage_url: str | None = None
    size_bytes: int
    content_type: str


class PresignedUrlResult(BaseModel):
    url: str
    expires_in: int
