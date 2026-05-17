class StorageProviderError(Exception):
    code = "DOCUMENT_STORAGE_FAILED"

    def __init__(self, message: str, code: str | None = None) -> None:
        self.message = message
        if code:
            self.code = code
        super().__init__(message)


class StorageObjectMissing(StorageProviderError):
    code = "DOCUMENT_STORAGE_MISSING"


class StorageUploadFailed(StorageProviderError):
    code = "DOCUMENT_UPLOAD_FAILED"


class InvalidStorageConfiguration(StorageProviderError):
    code = "DOCUMENT_STORAGE_FAILED"
