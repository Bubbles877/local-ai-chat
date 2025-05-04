import os
import sys

from dotenv import load_dotenv
from loguru import logger
import gradio as gr


class Main:
    def __init__(self):
        self._cfgs: dict[str, str] = {}

        load_dotenv(verbose=True)
        self._load_env_vars()

        # ロギングの設定をする
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

    def run(self) -> None:
        """実行する"""
        demo = gr.Interface(
            fn=self._greet,
            inputs=["text", "slider"],
            outputs=["text"],
        )

        try:
            demo.launch()
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt: Shutting down...")

        demo.close()

    def _load_env_vars(self) -> None:
        self._cfgs = {
            var: val
            for var in [
                "LLM_NAME",
                "LLM_ENDPOINT",
                "LLM_INSTRUCTION_FILE_PATH",
                "LLM_MESSAGE_EXAMPLE_FILE_PATH",
                "LLM_MAX_MESSAGES",
                "LOG_LEVEL",
            ]
            if (val := os.getenv(var)) is not None
        }

    def _greet(self, name: str, intensity: float) -> str:
        return "Hello, " + name + "!" * int(intensity)


if __name__ == "__main__":
    main = Main()
    main.run()
