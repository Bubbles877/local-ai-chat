from typing import Callable, Optional, cast

import gradio as gr
from gradio.components.chatbot import Message


class UI:
    def __init__(
        self,
        llm_message_example: list[gr.MessageDict],
        chat_callback: Callable[
            [str, list[gr.MessageDict]], tuple[str, list[gr.MessageDict]]
        ],
        llm_name: str,
        llm_temperature: Optional[float],
        llm_max_msgs: int,
        llm_instructions: str,
        setting_updated_callback: Callable[[str], None],
    ):
        """初期化

        Args:
            llm_message_example (list[gr.MessageDict]): ユーザーと AI の会話例
            chat_callback (Callable[ [str, list[gr.MessageDict]], tuple[str, list[gr.MessageDict]] ]): 会話のコールバック
            llm_name (str): LLM 名
            llm_temperature (Optional[float]): LLM が生成する出力のランダム性、創造性
            llm_max_msgs (int): LLM に渡す会話履歴の最大数
            llm_instructions (str): LLM への指示 (システムプロンプト)
            setting_updated_callback (Callable[[str], None]): 設定更新のコールバック
        """
        self._msg_example = llm_message_example
        self._chat_callback = chat_callback
        self._llm_name = llm_name
        self._llm_temperature = llm_temperature
        self._llm_max_msgs = llm_max_msgs
        self._instructions = llm_instructions
        self._setting_updated_callback = setting_updated_callback

    def launch(self) -> None:
        """UI を起動する"""
        with gr.Blocks(theme=gr.themes.Ocean(), title="AI Chat") as ui:
            gr.Markdown("## 💬 Local AI Chat")

            with gr.Row():
                with gr.Column(scale=1):
                    with gr.Accordion("Settings", open=False):
                        with gr.Column():
                            gr.Textbox(
                                self._llm_name,
                                lines=1,
                                max_lines=1,
                                label="LLM Name",
                                interactive=False,
                            )
                            gr.Textbox(
                                str(self._llm_temperature)
                                if self._llm_temperature
                                else "Default",
                                lines=1,
                                max_lines=1,
                                label="Temperature",
                                interactive=False,
                            )
                            gr.Textbox(
                                str(self._llm_max_msgs),
                                lines=1,
                                max_lines=1,
                                label="Max Messages",
                                interactive=False,
                            )
                        instructions_box = gr.Textbox(
                            self._instructions,
                            lines=10,
                            max_lines=20,
                            label="Instructions (editable)",
                            interactive=True,
                        )
                        gr.Button("Update").click(
                            lambda txt: self._setting_updated_callback(txt),
                            inputs=instructions_box,
                        )

                with gr.Column(scale=4):
                    chatbot = gr.Chatbot(
                        cast(list[gr.MessageDict | Message], self._msg_example),
                        type="messages",
                        label="History",
                        container=True,
                        height=600,
                        resizable=True,
                        editable="all",
                        show_copy_button=True,
                        show_copy_all_button=True,
                    )
                    input_box = gr.Textbox(
                        placeholder="Shift + Enter で改行", show_label=False
                    )
                    gr.ClearButton([input_box, chatbot])

                    input_box.submit(
                        self._chat_callback,
                        inputs=[input_box, chatbot],
                        outputs=[input_box, chatbot],
                    )

        ui.launch(inbrowser=True, share=False, pwa=True)
        ui.close()
