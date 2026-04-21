from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_key: str = "dev-key"
    fmcsa_webkey: str = ""
    database_url: str = "sqlite:///./data/app.db"
    allowed_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env.local", extra="ignore")


settings = Settings()
