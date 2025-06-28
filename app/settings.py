from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """設定

    環境変数から設定を読み込んで管理します。
    """

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    chat_history_file_path: Optional[str] = None
    llm_max_messages: int = -1
    llm_instructions_file_path: Optional[str] = None

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )
