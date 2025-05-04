import asyncio
import os
import sys

import aiofiles
import gradio as gr
from dotenv import load_dotenv
from loguru import logger
from langchain_core.messages import AnyMessage, AIMessage, HumanMessage

from app.llm import LLM


class Main:
    def __init__(self):
        self._cfgs: dict[str, str] = {}

        load_dotenv(verbose=True)
        self._load_env_vars()

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

        self._llm = LLM(self._cfgs, enable_logging=log_lv == "DEBUG")

    async def run(self) -> None:
        """実行する"""
        instructions = await self._load_instructions()
        self._llm.configure(instructions)

        with gr.Blocks() as ui:
            chat_bot = gr.Chatbot()  # TODO: tuples -> messages
            txt_box = gr.Textbox()
            clear_btn = gr.Button("Clear")

            txt_box.submit(self._chat, [txt_box, chat_bot], [txt_box, chat_bot])
            clear_btn.click(lambda: None, None, chat_bot, queue=False)  # TODO: 不要かも

        try:
            ui.launch()
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt: Shutting down...")

        ui.close()

    def _load_env_vars(self) -> None:
        self._cfgs = {
            var: val
            for var in [
                "LLM_NAME",
                "LLM_ENDPOINT",
                "LLM_INSTRUCTION_FILE_PATH",
                "LLM_MESSAGE_EXAMPLE_FILE_PATH",
                "LLM_TEMPERATURE",
                "LLM_MAX_MESSAGES",
                "LOG_LEVEL",
            ]
            if (val := os.getenv(var)) is not None
        }

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

    def _chat(
        self, user_message: str, history: list[tuple[str, str]]
    ) -> tuple[str, list[tuple[str, str]]]:
        logger.debug(f"Chat: {user_message}")
        logger.debug(f"History: {history}")

        hist: list[AnyMessage] = []

        if history:
            # (ユーザメッセージ, AI メッセージ) のリスト
            for usr_msg, ai_msg in history:
                hist.append(HumanMessage(content=usr_msg))
                hist.append(AIMessage(content=ai_msg))

        ai_res = self._llm.invoke(user_message, hist)
        logger.debug(f"Response: {ai_res}")
        history.append((user_message, ai_res))
        # "" を返すと入力ボックスがクリアされる
        return "", history


if __name__ == "__main__":
    main = Main()
    asyncio.run(main.run())
