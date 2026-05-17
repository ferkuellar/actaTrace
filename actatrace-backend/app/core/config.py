from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./actatrace_local.db", alias="DATABASE_URL")
    jwt_secret_key: str = Field(default="change-me", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_issuer: str = Field(default="actatrace", alias="JWT_ISSUER")
    jwt_audience: str = Field(default="actatrace-api", alias="JWT_AUDIENCE")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    password_min_length: int = Field(default=12, alias="PASSWORD_MIN_LENGTH")
    password_require_special: bool = Field(default=True, alias="PASSWORD_REQUIRE_SPECIAL")
    environment: str = Field(default="local", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    backend_cors_origins: str = Field(default="", alias="BACKEND_CORS_ORIGINS")
    cors_allowed_origins: str = Field(default="http://localhost:3010,http://localhost:3000", alias="CORS_ALLOWED_ORIGINS")
    blockchain_provider: str = Field(default="mock", alias="BLOCKCHAIN_PROVIDER")
    fabric_connection_profile: str = Field(default="", alias="FABRIC_CONNECTION_PROFILE")
    fabric_wallet_path: str = Field(default="", alias="FABRIC_WALLET_PATH")
    fabric_identity: str = Field(default="", alias="FABRIC_IDENTITY")
    fabric_channel_name: str = Field(default="actatrace-channel", alias="FABRIC_CHANNEL_NAME")
    fabric_chaincode_name: str = Field(default="actatrace-chaincode", alias="FABRIC_CHAINCODE_NAME")
    fabric_org_name: str = Field(default="", alias="FABRIC_ORG_NAME")
    blockchain_network_name: str = Field(default="local-fabric", alias="BLOCKCHAIN_NETWORK_NAME")
    storage_provider: str = Field(default="local", alias="STORAGE_PROVIDER")
    local_storage_path: str = Field(default="./storage", alias="LOCAL_STORAGE_PATH")
    s3_endpoint_url: str = Field(default="http://minio:9000", alias="S3_ENDPOINT_URL")
    s3_access_key: str = Field(default="minioadmin", alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(default="minioadmin", alias="S3_SECRET_KEY")
    s3_bucket_name: str = Field(default="actatrace-documents", alias="S3_BUCKET_NAME")
    s3_region: str = Field(default="us-east-1", alias="S3_REGION")
    s3_use_ssl: bool = Field(default=False, alias="S3_USE_SSL")
    max_document_upload_mb: int = Field(default=25, alias="MAX_DOCUMENT_UPLOAD_MB")
    document_presigned_url_expire_seconds: int = Field(default=300, alias="DOCUMENT_PRESIGNED_URL_EXPIRE_SECONDS")
    enable_auto_blockchain_anchor: bool = Field(default=False, alias="ENABLE_AUTO_BLOCKCHAIN_ANCHOR")
    custody_reception_threshold_hours: int = Field(default=4, alias="CUSTODY_RECEPTION_THRESHOLD_HOURS")
    enable_alert_generation: bool = Field(default=True, alias="ENABLE_ALERT_GENERATION")
    enable_public_traceability: bool = Field(default=True, alias="ENABLE_PUBLIC_TRACEABILITY")
    audit_log_retention_days: int = Field(default=2555, alias="AUDIT_LOG_RETENTION_DAYS")
    public_traceability_rate_limit_per_minute: int = Field(default=60, alias="PUBLIC_TRACEABILITY_RATE_LIMIT_PER_MINUTE")
    enable_security_headers: bool = Field(default=True, alias="ENABLE_SECURITY_HEADERS")
    enable_rate_limiting: bool = Field(default=True, alias="ENABLE_RATE_LIMITING")
    rate_limit_login_per_minute: int = Field(default=5, alias="RATE_LIMIT_LOGIN_PER_MINUTE")
    rate_limit_public_search_per_minute: int = Field(default=60, alias="RATE_LIMIT_PUBLIC_SEARCH_PER_MINUTE")
    rate_limit_public_verify_per_minute: int = Field(default=60, alias="RATE_LIMIT_PUBLIC_VERIFY_PER_MINUTE")
    rate_limit_document_download_per_minute: int = Field(default=20, alias="RATE_LIMIT_DOCUMENT_DOWNLOAD_PER_MINUTE")
    rate_limit_blockchain_anchor_per_minute: int = Field(default=10, alias="RATE_LIMIT_BLOCKCHAIN_ANCHOR_PER_MINUTE")
    enable_audit_hash_chain: bool = Field(default=True, alias="ENABLE_AUDIT_HASH_CHAIN")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        configured = self.backend_cors_origins or self.cors_allowed_origins
        return [origin.strip() for origin in configured.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
