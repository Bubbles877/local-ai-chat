import asyncio
import sys

import gradio as gr
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from loguru import logger

from app.resource_loader import LLMMessage, ResourceLoader
from app.settings import Settings
from app.ui import UI
from util.llm_chat import LLMChat


class Main:
    def __init__(self):
        self._settings = Settings()
        self._setup_logger(self._settings.log_level)

        logger.debug(f"LLM name: {self._settings.llm_name}")
        logger.debug(f"LLM endpoint: {self._settings.llm_endpoint}")
        logger.debug(f"LLM temperature: {self._settings.llm_temperature}")
        logger.debug(f"LLM max messages: {self._settings.llm_max_messages}")

        self._resource_loader = ResourceLoader(
            self._settings, enable_logging=self._settings.log_level == "DEBUG"
        )

        llm = ChatOllama(
            model=self._settings.llm_name,
            base_url=self._settings.llm_endpoint,
            temperature=float(self._settings.llm_temperature)
            if self._settings.llm_temperature
            else None,
        )
        self._llm_chat = LLMChat(
            llm,
            self._settings.llm_max_messages,
            enable_logging=self._settings.log_level == "DEBUG",
        )

    async def run(self) -> None:
        """実行する"""
        llm_instructions = await self._resource_loader.load_llm_instructions()
        self._llm_chat.configure(llm_instructions)

        llm_msg_example = self._to_ui_message(
            await self._resource_loader.load_llm_message_example()
        )

        ui = UI(
            llm_msg_example,
            self._chat,
            self._settings.llm_name,
            self._settings.llm_temperature,
            self._settings.llm_max_messages,
            llm_instructions,
            self._llm_chat.configure,
        )
        ui.launch()

    @staticmethod
    def _setup_logger(log_level: str) -> None:
        logger.remove()  # default: stderr
        logger.add(sys.stdout, level=log_level)
        logger.add(
            "log/app_{time}.log",
            level=log_level,
            diagnose=log_level == "DEBUG",
            enqueue=True,
            rotation="1 day",
            retention="7 days",
        )

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

    @staticmethod
    def _to_ui_message(messages: list[LLMMessage]) -> list[gr.MessageDict]:
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

    @staticmethod
    def _to_llm_messages(messages: list[gr.MessageDict]) -> list[AnyMessage]:
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
