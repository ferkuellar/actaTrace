from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./actatrace_local.db", alias="DATABASE_URL")
    jwt_secret_key: str = Field(default="change-me", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    environment: str = Field(default="local", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    backend_cors_origins: str = Field(default="", alias="BACKEND_CORS_ORIGINS")
    blockchain_provider: str = Field(default="mock", alias="BLOCKCHAIN_PROVIDER")
    fabric_connection_profile: str = Field(default="", alias="FABRIC_CONNECTION_PROFILE")
    fabric_wallet_path: str = Field(default="", alias="FABRIC_WALLET_PATH")
    fabric_identity: str = Field(default="", alias="FABRIC_IDENTITY")
    fabric_channel_name: str = Field(default="actatrace-channel", alias="FABRIC_CHANNEL_NAME")
    fabric_chaincode_name: str = Field(default="actatrace-chaincode", alias="FABRIC_CHAINCODE_NAME")
    fabric_org_name: str = Field(default="", alias="FABRIC_ORG_NAME")
    blockchain_network_name: str = Field(default="local-fabric", alias="BLOCKCHAIN_NETWORK_NAME")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
