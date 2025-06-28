import asyncio
import json
import os
import sys
from datetime import datetime

import gradio as gr
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from loguru import logger

from app.resource_loader import LLMMessage, ResourceLoader
from app.settings import Settings
from app.ui import UI
from util.llm_chat import LLMChat
from util.setting.llm_settings import LLMSettings


class Main:
    def __init__(self):
        self._settings = Settings()
        self._llm_settings = LLMSettings()

        self._setup_logger(self._settings.log_level)

        logger.debug(f"Settings:\n{self._settings.model_dump_json(indent=2)}")
        logger.debug(f"LLM Settings:\n{self._llm_settings.model_dump_json(indent=2)}")

        self._resource_loader = ResourceLoader(enable_logging=True)

        llm = ChatOllama(
            model=self._llm_settings.name,
            base_url=self._llm_settings.endpoint,
            temperature=self._llm_settings.temperature,
        )
        self._llm_chat = LLMChat(
            llm, self._settings.llm_max_messages, enable_logging=True
        )

    async def run(self) -> None:
        """実行する"""
        llm_instructions = await self._resource_loader.load_plane_text(
            self._settings.llm_instructions_file_path
        )
        self._llm_chat.configure(llm_instructions)

        chat_history = self._to_ui_messages(
            await self._resource_loader.load_chat_history(
                self._settings.chat_history_file_path
            )
        )

        ui = UI(
            chat_history,
            self._chat,
            self._save_chat_history,
            self._llm_settings.name,
            self._llm_settings.temperature,
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

    def _save_chat_history(self, history: list[gr.MessageDict]) -> None:
        try:
            os.makedirs("data", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join("data", f"chat_history_{timestamp}.json")
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(
                    self._to_json_messages(history), file, ensure_ascii=False, indent=2
                )
            logger.info(f"Chat history saved to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save chat history: {e}")

    @staticmethod
    def _to_ui_messages(messages: list[LLMMessage]) -> list[gr.MessageDict]:
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
    def _to_json_messages(
        messages: list[gr.MessageDict],
    ) -> dict[str, list[LLMMessage]]:
        msgs: list[LLMMessage] = []

        for msg in messages:
            role = msg.get("role", "")
            content = str(msg.get("content", ""))
            msgs.append({"role": role, "content": content})
        return {"messages": msgs}

    @staticmethod
    def _to_llm_messages(messages: list[gr.MessageDict]) -> list[AnyMessage]:
        msgs: list[AnyMessage] = []

        for msg in messages:
            role = msg.get("role", "")
            content = str(msg.get("content", ""))
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
    except Exception as e:
        logger.error(f"Error: {e}")
