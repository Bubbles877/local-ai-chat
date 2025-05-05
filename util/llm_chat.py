import asyncio
from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    SystemMessage,
    trim_messages,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from loguru import logger


class LLMChat:
    """LLM チャット"""

    def __init__(self, configs: dict, llm: BaseChatModel, enable_logging: bool = False):
        """初期化

        Args:
            configs (dict): 設定
            llm (BaseChatModel): LLM
            enable_logging (bool, optional): ログ出力を有効にするかどうか, Defaults to False.
        """
        if enable_logging:
            logger.enable(__name__)
        else:
            logger.disable(__name__)

        self._cfgs = configs
        self._llm = llm

        self._trimmer: Optional[RunnableLambda[list[AnyMessage], list[AnyMessage]]] = (
            None
        )
        try:
            max_msgs = int(self._cfgs.get("LLM_MAX_MESSAGES", -1))
            if max_msgs >= 0:
                # システムメッセージ含めて max_msgs 件残す
                self._trimmer = trim_messages(
                    max_tokens=max_msgs,
                    token_counter=len,
                    strategy="last",
                    allow_partial=False,
                    # start_on=HumanMessage,
                    include_system=True,
                )
        except ValueError:
            logger.warning(
                f"Invalid LLM_MAX_MESSAGES value: {self._cfgs.get('LLM_MAX_MESSAGES')}"
            )

        self._instructions: str = ""
        self._msg_example: Optional[list[AnyMessage]] = None

    def configure(
        self, instructions: str, message_example: Optional[list[AnyMessage]] = None
    ) -> None:
        """設定する

        Args:
            instructions (str): 指示
            message_example (Optional[list[AnyMessage]]): メッセージの例
        """
        self._instructions = instructions
        logger.debug(f"Instructions: {self._instructions}")

        if message_example:
            self._msg_example = message_example
            logger.debug(f"Message example: {self._msg_example}")

    def invoke(
        self,
        message: Optional[str] = None,
        history: Optional[list[AnyMessage]] = None,
    ) -> str:
        """LLM を呼び出す

        Args:
            message (Optional[str]): メッセージ
            history (Optional[list[AnyMessage]]): 会話履歴

        Returns:
            str: 結果
        """
        msgs: list[AnyMessage] = []
        msgs.append(SystemMessage(content=self._instructions))

        if self._msg_example is not None:
            msgs.extend(self._msg_example)
        if history is not None:
            msgs.extend(history)
        if message:
            msgs.append(HumanMessage(content=message))

        if self._trimmer:
            msgs = self._trimmer.invoke(msgs)

        # logger.debug(f"Messages: {msgs}")
        logger.debug(f"Messages: {len(msgs)}")

        prompt = ChatPromptTemplate.from_messages(msgs)
        chain = prompt | self._llm | StrOutputParser()
        result = chain.invoke({})
        return result

    async def ainvoke(
        self,
        history: list[AnyMessage],
        message: Optional[str] = None,
    ) -> str:
        """LLM を呼び出す (非同期)

        Args:
            message (Optional[str]): メッセージ
            history (list[AnyMessage]): 会話履歴

        Returns:
            str: 結果
        """
        return await asyncio.to_thread(self.invoke, message, history)
