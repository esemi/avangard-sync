"""Application settings."""
import os

from pydantic import BaseSettings, Field


class AppSettings(BaseSettings):
    """Application settings class."""

    avangard_http_timeout: int = Field(45, description='avangard request timeout')
    http_user_agent: bytes = Field(
        default=b'Mozilla/5.0 (X11; x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/536.36"',
    )
    throttling_time: float = Field(60.0 * 15, description='Seconds between update rate tries in seconds')
    throttling_min_time: float = 10.0
    debug: bool = Field(default=False)


app_settings = AppSettings(
    _env_file=os.path.join(os.path.dirname(__file__), '..', '.env'),
)
