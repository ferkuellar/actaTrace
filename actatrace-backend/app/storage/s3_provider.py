from app.storage.exceptions import StorageObjectMissing, StorageProviderError, StorageUploadFailed
from app.storage.provider import StorageProvider
from app.storage.schemas import StorageUploadResult


class S3StorageProvider(StorageProvider):
    def __init__(
        self,
        *,
        endpoint_url: str | None,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        region_name: str,
        use_ssl: bool,
    ) -> None:
        import boto3
        from botocore.client import Config

        self.bucket_name = bucket_name
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name,
            use_ssl=use_ssl,
            config=Config(signature_version="s3v4"),
        )

    def upload_file(self, file_bytes: bytes, object_key: str, content_type: str) -> StorageUploadResult:
        from botocore.exceptions import ClientError

        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=file_bytes,
                ContentType=content_type,
                ServerSideEncryption="AES256",
            )
        except ClientError as exc:
            raise StorageUploadFailed("Failed to upload document to object storage") from exc
        return StorageUploadResult(
            provider="s3",
            bucket=self.bucket_name,
            object_key=object_key,
            storage_url=None,
            size_bytes=len(file_bytes),
            content_type=content_type,
        )

    def get_file(self, object_key: str) -> bytes:
        from botocore.exceptions import ClientError

        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=object_key)
            return response["Body"].read()
        except ClientError as exc:
            raise StorageObjectMissing("Document object is missing from storage") from exc

    def generate_presigned_url(self, object_key: str, expires_in: int) -> str:
        from botocore.exceptions import ClientError

        try:
            return self.client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.bucket_name, "Key": object_key},
                ExpiresIn=expires_in,
            )
        except ClientError as exc:
            raise StorageProviderError("Failed to generate document access URL") from exc

    def file_exists(self, object_key: str) -> bool:
        from botocore.exceptions import ClientError

        try:
            self.client.head_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError:
            return False

    def delete_file(self, object_key: str) -> bool:
        from botocore.exceptions import ClientError

        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError:
            return False
