from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore", env_file_encoding="utf-8"
    )

    # Database
    DATABASE_URL: str = ""

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Convert postgresql:// to postgresql+asyncpg:// for async driver"""
        url = self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        # asyncpg doesn't support sslmode/channel_binding as query params;
        # strip them and use ssl=require instead
        if "?" in url:
            base, _ = url.split("?", 1)
            url = base + "?ssl=require"
        return url

    # App
    APP_NAME: str = "Unroll Ai"
    DEBUG: bool = False


settings = Settings()
