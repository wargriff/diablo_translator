from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DT_", extra="ignore")

    app_name: str = "Diablo Translator API"
    version: str = "2.1.0"
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["*"]


def get_settings() -> Settings:
    return Settings()
