import asyncio
from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger


class LLM:
    """LLM"""

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

        # llm_name = self._cfgs.get("LLM_NAME", "")
        # llm_endpoint = self._cfgs.get("LLM_ENDPOINT")
        # temperature = self._cfgs.get("LLM_TEMPERATURE")
        # logger.debug(f"LLM name: {llm_name}")
        # logger.debug(f"LLM endpoint: {llm_endpoint}")
        # logger.debug(f"LLM temperature: {temperature}")

        # self._llm: BaseChatModel = ChatOllama(
        #     model=llm_name,
        #     base_url=llm_endpoint,
        #     temperature=float(temperature) if temperature else None,
        # )

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
        self._msg_example = message_example

        logger.debug(f"Instructions: {self._instructions}")
        logger.debug(f"Message example: {self._msg_example}")

    # TODO: predict?
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
        # logger.debug("Invoke")

        msgs = self._msg_example if self._msg_example else []

        if history is not None:
            msgs.extend(history)

        if message:
            msgs.append(HumanMessage(content=message))

        prompt = ChatPromptTemplate.from_messages(
            [SystemMessage(content=self._instructions), *msgs]
        )
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
