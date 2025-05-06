from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """設定

    環境変数から設定を読み込んで管理します。
    """

    llm_name: str
    llm_endpoint: str
    llm_temperature: Optional[float]
    llm_instruction_file_path: Optional[str]
    llm_message_example_file_path: Optional[str]
    llm_max_messages: int = -1
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
