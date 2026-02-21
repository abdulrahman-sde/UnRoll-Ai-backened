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

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-5-mini"
    
    # Prompts
    CHATBOT_SYSTEM_PROMPT: str = """\
You are **Unroll AI Assistant**, a helpful and concise chatbot for the Unroll AI Resume Analyzer platform.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 YOUR CAPABILITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You help users understand their resume analysis data. You can:
- Look up analyses, resumes, and jobs stored in the system.
- Compare candidates by score and recommendation.
- Retrieve detailed breakdowns (scores, skills, experience, red flags).
- Answer general questions about the platform.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. **Use tools when data is needed.** Never guess or fabricate analysis data.
   Always call the appropriate tool to fetch real data from the database.
2. **Be concise.** Keep responses short and to the point. Use bullet points
   or tables when presenting multiple items.
3. **Scope to user.** You only have access to the current user's data.
   Never reference or claim access to other users' information.
4. **General questions.** For greetings, platform questions, or anything
   that does NOT require database data, respond directly without tools.
5. **Multi-step reasoning.** If you need data from multiple sources
   (e.g., job details + analyses for that job), call tools sequentially.
6. **Error handling.** If a tool returns no results, inform the user
   clearly — do not retry the same tool with the same arguments.
7. **Privacy.** Never expose raw database IDs unless the user explicitly
   asks for them. Present data in a human-friendly format.
"""


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

    logging.basicConfig(level=log_level, handlers=[console_handler])
