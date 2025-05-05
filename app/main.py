import asyncio
import json
import os
import sys
from typing import TypedDict

import aiofiles
import gradio as gr
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from loguru import logger

from app.ui import UI
from util.llm_chat import LLMChat


class ExampleMessage(TypedDict):
    role: str
    content: str


class Main:
    def __init__(self):
        load_dotenv(verbose=True)
        self._cfgs = self._load_env_vars()

        log_lv = self._cfgs.get("LOG_LEVEL", "INFO")
        logger.remove()  # default: stderr
        logger.add(sys.stdout, level=log_lv)
        logger.add(
            "log/app_{time}.log",
            level=log_lv,
            diagnose=log_lv == "DEBUG",
            enqueue=True,
            rotation="1 day",
            retention="7 days",
        )

        self._llm_name = self._cfgs.get("LLM_NAME", "")
        self._llm_endpoint = self._cfgs.get("LLM_ENDPOINT")
        self._llm_temperature = self._cfgs.get("LLM_TEMPERATURE")
        self._llm_max_msgs = int(self._cfgs.get("LLM_MAX_MESSAGES", -1))
        logger.debug(f"LLM name: {self._llm_name}")
        logger.debug(f"LLM endpoint: {self._llm_endpoint}")
        logger.debug(f"LLM temperature: {self._llm_temperature}")
        logger.debug(f"LLM max messages: {self._llm_max_msgs}")

        llm = ChatOllama(
            model=self._llm_name,
            base_url=self._llm_endpoint,
            temperature=float(self._llm_temperature) if self._llm_temperature else None,
        )
        self._llm_chat = LLMChat(
            llm, self._llm_max_msgs, enable_logging=log_lv == "DEBUG"
        )

    async def run(self) -> None:
        """実行する"""
        instructions = await self._load_instructions()
        self._llm_chat.configure(instructions)

        msg_example = await self._load_message_example()

        ui = UI(
            msg_example,
            self._chat,
            self._llm_name,
            self._llm_temperature if self._llm_temperature else "",
            self._llm_max_msgs,
            instructions,
            self._llm_chat.configure,
        )
        ui.launch()

    def _load_env_vars(self) -> dict[str, str]:
        cfgs = {
            var: val
            for var in [
                "LLM_NAME",
                "LLM_ENDPOINT",
                "LLM_TEMPERATURE",
                "LLM_INSTRUCTION_FILE_PATH",
                "LLM_MESSAGE_EXAMPLE_FILE_PATH",
                "LLM_MAX_MESSAGES",
                "LOG_LEVEL",
            ]
            if (val := os.getenv(var)) is not None
        }
        return cfgs

    async def _load_instructions(self) -> str:
        instructions = ""

        file_path = self._cfgs.get("LLM_INSTRUCTION_FILE_PATH", "")
        if not os.path.isfile(file_path):
            logger.warning(f"Instruction file not found: {file_path}")
            return instructions

        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                instructions = await f.read()
        except Exception as e:
            logger.error(f"Failed to load instructions: {e}")

        return instructions

    async def _load_message_example(self) -> list[gr.MessageDict]:
        msg_example: list[gr.MessageDict] = []

        file_path = self._cfgs.get("LLM_MESSAGE_EXAMPLE_FILE_PATH", "")
        if not os.path.isfile(file_path):
            logger.warning(f"Message example file not found: {file_path}")
            return msg_example

        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                msg_example_dict: dict = json.loads(await f.read())
                msgs: list[ExampleMessage] = msg_example_dict.get("messages", [])
                msg_example = self._to_ui_message(msgs)
        except Exception as e:
            logger.error(f"Failed to load message example: {e}")

        return msg_example

    def _chat(
        self, user_message: str, history: list[gr.MessageDict]
    ) -> tuple[str, list[gr.MessageDict]]:
        hist_len = len(history)
        logger.debug(f"{hist_len + 1}: (User) {user_message}")

        hist = self._to_llm_messages(history)
        ai_res = self._llm_chat.invoke(user_message, hist)
        logger.debug(f"{hist_len + 2}: (AI) {ai_res}")

        history.append(gr.MessageDict(role="user", content=user_message))
        history.append(gr.MessageDict(role="assistant", content=ai_res))
        # "" を返すと入力ボックスがクリアされる
        return "", history

    def _to_ui_message(self, messages: list[ExampleMessage]) -> list[gr.MessageDict]:
        msgs: list[gr.MessageDict] = []

        for msg in messages:
            role = msg.get("role", "")
            match role:
                case "user" | "assistant" | "system":
                    msgs.append(
                        gr.MessageDict(role=role, content=msg.get("content", ""))
                    )
                case _:
                    logger.warning(f"Unknown role: {role}")

        return msgs

    def _to_llm_messages(self, messages: list[gr.MessageDict]) -> list[AnyMessage]:
        msgs: list[AnyMessage] = []

        for msg in messages:
            role = msg["role"]
            content = str(msg["content"])
            match role:
                case "user":
                    msgs.append(HumanMessage(content=content))
                case "assistant":
                    msgs.append(AIMessage(content=content))
                case "system":
                    msgs.append(SystemMessage(content=content))
                case _:
                    logger.warning(f"Unknown role: {role}")

        return msgs


if __name__ == "__main__":
    main = Main()

    try:
        asyncio.run(main.run())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt: Shutting down...")
