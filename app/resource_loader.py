import json
import os
from typing import TypedDict

import aiofiles
from loguru import logger

from app.settings import Settings


class LLMMessage(TypedDict):
    role: str
    content: str


class ResourceLoader:
    def __init__(self, settings: Settings, enable_logging: bool = False):
        """初期化

        Args:
            settings (Settings): 設定
            enable_logging (bool, optional): ログ出力を有効にするかどうか, Defaults to False.
        """
        if enable_logging:
            logger.enable(__name__)
        else:
            logger.disable(__name__)

        self._settings = settings

    async def load_llm_instructions(self) -> str:
        """設定ファイルから LLM への指示 (システムプロンプト) を読み込む

        Returns:
            str: 指示
        """
        instructions = ""

        if not (file_path := self._settings.llm_instruction_file_path):
            logger.info("Instruction file path not set")
            return instructions

        if not os.path.isfile(file_path):
            logger.warning(f"Instruction file not found: {file_path}")
            return instructions

        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                instructions = await f.read()
        except Exception as e:
            logger.error(f"Failed to load instructions: {e}")

        return instructions

    async def load_llm_message_example(self) -> list[LLMMessage]:
        """設定ファイルから ユーザーと AI の会話例を読み込む

        Returns:
            list[gr.MessageDict]: 会話例
        """
        msg_example: list[LLMMessage] = []

        if not (file_path := self._settings.llm_message_example_file_path):
            logger.info("Message example file path not set")
            return msg_example

        if not os.path.isfile(file_path):
            logger.warning(f"Message example file not found: {file_path}")
            return msg_example

        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                msg_example_dict: dict = json.loads(await f.read())
                msg_example = msg_example_dict.get("messages", [])
        except Exception as e:
            logger.error(f"Failed to load message example: {e}")

        return msg_example
