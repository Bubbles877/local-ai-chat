import json
import os
from typing import Optional, TypedDict

import aiofiles
from loguru import logger


class LLMMessage(TypedDict):
    role: str
    content: str


class ResourceLoader:
    def __init__(self, enable_logging: bool = False):
        """初期化

        Args:
            enable_logging (bool, optional): ログ出力を有効にするかどうか, Defaults to False.
        """
        if enable_logging:
            logger.enable(__name__)
        else:
            logger.disable(__name__)

    async def load_plane_text(self, file_path: Optional[str]) -> str:
        """ファイルからプレーンテキストを読み込む

        Args:
            file_path (Optional[str]): ファイルパス

        Returns:
            str: テキスト
        """
        txt = ""

        if not file_path:
            logger.info("File path not set")
            return txt

        if not os.path.isfile(file_path):
            logger.warning(f"File not found: {file_path}")
            return txt

        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
                txt = await file.read()
        except Exception as e:
            logger.error(f"Failed to load file: {e}")

        return txt

    async def load_chat_history(self, file_path: Optional[str]) -> list[LLMMessage]:
        """ファイルからユーザーと AI の会話履歴 (会話例) を読み込む

        Returns:
            list[gr.MessageDict]: 会話例
        """
        history: list[LLMMessage] = []

        if not file_path:
            logger.info("Chat history file path not set")
            return history

        if not os.path.isfile(file_path):
            logger.warning(f"Chat history file not found: {file_path}")
            return history

        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
                history_dict: dict = json.loads(await file.read())
                history = history_dict.get("messages", [])
        except Exception as e:
            logger.error(f"Failed to load chat history: {e}")

        return history
