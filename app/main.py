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

        llm_name = self._cfgs.get("LLM_NAME", "")
        llm_endpoint = self._cfgs.get("LLM_ENDPOINT")
        temperature = self._cfgs.get("LLM_TEMPERATURE")
        logger.debug(f"LLM name: {llm_name}")
        logger.debug(f"LLM endpoint: {llm_endpoint}")
        logger.debug(f"LLM temperature: {temperature}")

        llm = ChatOllama(
            model=llm_name,
            base_url=llm_endpoint,
            temperature=float(temperature) if temperature else None,
        )
        self._llm_chat = LLMChat(self._cfgs, llm, enable_logging=log_lv == "DEBUG")

    async def run(self) -> None:
        """実行する"""
        instructions = await self._load_instructions()
        msg_example = await self._load_message_example()
        self._llm_chat.configure(instructions, msg_example)

        with gr.Blocks() as ui:
            chatbot = gr.Chatbot(type="messages")
            input_field = gr.Textbox()
            gr.ClearButton([input_field, chatbot])

            input_field.submit(
                self._chat, [input_field, chatbot], [input_field, chatbot]
            )

        try:
            ui.launch()
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt: Shutting down...")

        ui.close()

    def _load_env_vars(self) -> dict[str, str]:
        cfgs = {
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

    async def _load_message_example(self) -> list[AnyMessage]:
        msg_example: list[AnyMessage] = []

        file_path = self._cfgs.get("LLM_MESSAGE_EXAMPLE_FILE_PATH", "")
        if not os.path.isfile(file_path):
            logger.warning(f"Message example file not found: {file_path}")
            return msg_example

        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()
                # msg_example_dict = dict(json.loads(content))
                msg_example_dict: dict = json.loads(content)
                # if msgs := msg_example_dict.get("messages"):
                msgs: list[ExampleMessage] = msg_example_dict.get("messages", [])
                for msg in msgs:
                    role = msg.get("role")
                    content = msg.get("content", "")
                    match role:
                        case "user":
                            msg_example.append(HumanMessage(content=content))
                        case "assistant":
                            msg_example.append(AIMessage(content=content))
                        case "system":
                            msg_example.append(SystemMessage(content=content))
                        case _:
                            logger.warning(f"Unknown role: {role}")
        except Exception as e:
            logger.error(f"Failed to load message example: {e}")

        return msg_example

    def _chat(
        self, user_message: str, history: list[gr.MessageDict]
    ) -> tuple[str, list[gr.MessageDict]]:
        hist_len = len(history)
        logger.debug(f"{hist_len + 1}: (User) {user_message}")

        hist: list[AnyMessage] = []

        for msg in history:
            match msg["role"]:
                case "user":
                    hist.append(HumanMessage(content=str(msg["content"])))
                case "assistant":
                    hist.append(AIMessage(content=str(msg["content"])))
                case "system":
                    hist.append(SystemMessage(content=str(msg["content"])))

        ai_res = self._llm_chat.invoke(user_message, hist)
        logger.debug(f"{hist_len + 2}: (AI) {ai_res}")

        history.append(gr.MessageDict(role="user", content=user_message))
        history.append(gr.MessageDict(role="assistant", content=ai_res))
        # "" を返すと入力ボックスがクリアされる
        return "", history


if __name__ == "__main__":
    main = Main()
    asyncio.run(main.run())
