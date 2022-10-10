"""Application settings."""
import os

from pydantic import BaseSettings, Field


class AppSettings(BaseSettings):
    """Application settings class."""

    http_user_agent: bytes = Field(
        default=b'Mozilla/5.0 (X11; x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/536.36"',
    )
    throttling_time: float = Field(60.0 * 15, description='Seconds between update rate tries in seconds')
    throttling_min_time: float = 10.0
    debug: bool = Field(default=False)

    avangard_http_timeout: int = Field(45, description='avangard request timeout in seconds')
    avangard_human_waiting_time: float = Field(5.0, description='waiting time for fake-hu')
    avangard_login: str
    avangard_password: str


app_settings = AppSettings(
    _env_file=os.path.join(os.path.dirname(__file__), '..', '.env'),
)
