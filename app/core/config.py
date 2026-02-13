import logging
import sys
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
        if "?" in url:
            base, _ = url.split("?", 1)
            url = base + "?ssl=require"
        return url

    # App
    APP_NAME: str = "Unroll Ai"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Security
    JWT_SECRET: str = ""
    ALGORITHM: str = "HS256"


settings = Settings()


def setup_logging():
    """
    Configure logging with colored levels only (using colorlog)
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    try:
        import colorlog

        # Color only the levelname - notice %(log_color)s and %(reset)s placement
        console_formatter = colorlog.ColoredFormatter(
            "%(asctime)s [%(log_color)s%(levelname)s%(reset)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)

    except ImportError:
        # Fallback if colorlog not installed (production)
        console_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)

    # File handler (plain text, no colors)
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = logging.FileHandler("app.log")
    file_handler.setFormatter(file_formatter)

    # Configure root logger
    logging.basicConfig(level=log_level, handlers=[console_handler, file_handler])

    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured (Level: {settings.LOG_LEVEL}, Debug: {settings.DEBUG})"
    )
