from typing import Callable, Optional, cast

import gradio as gr
from gradio.components.chatbot import Message


class UI:
    def __init__(
        self,
        chat_history: list[gr.MessageDict],
        chat_callback: Callable[
            [str, list[gr.MessageDict]], tuple[str, list[gr.MessageDict]]
        ],
        save_chat_history_callback: Callable[[list[gr.MessageDict]], None],
        llm_name: str,
        llm_temperature: Optional[float],
        llm_max_messages: int,
        llm_instructions: str,
        update_llm_instructions_callback: Callable[[str], None],
    ):
        """初期化

        Args:
            chat_history (list[gr.MessageDict]): ユーザーと AI の会話履歴 (会話例)
            chat_callback (Callable[ [str, list[gr.MessageDict]], tuple[str, list[gr.MessageDict]] ]): 会話のコールバック
            save_history_callback (Callable[[list[gr.MessageDict]], None]): 会話履歴保存のコールバック
            llm_name (str): LLM 名
            llm_temperature (Optional[float]): LLM が生成する出力のランダム性、創造性
            llm_max_messages (int): LLM に渡す会話履歴の最大数
            llm_instructions (str): LLM への指示 (システムプロンプト)
            update_llm_instructions_callback (Callable[[str], None]): LLM への指示 (システムプロンプト) 更新のコールバック
        """
        self._chat_history = chat_history
        self._chat_callback = chat_callback
        self._save_chat_history_callback = save_chat_history_callback
        self._llm_name = llm_name
        self._llm_temperature = llm_temperature
        self._llm_max_messages = llm_max_messages
        self._instructions = llm_instructions
        self._update_llm_instructions_callback = update_llm_instructions_callback

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
                                str(self._llm_max_messages),
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
                            lambda txt: self._update_llm_instructions_callback(txt),
                            inputs=instructions_box,
                        )

                with gr.Column(scale=4):
                    chatbot = gr.Chatbot(
                        cast(list[gr.MessageDict | Message], self._chat_history),
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
                    with gr.Row():
                        gr.ClearButton([input_box, chatbot], value="Clear", scale=1)
                        gr.Button("Save", scale=1).click(
                            lambda hist: self._save_chat_history_callback(hist),
                            inputs=chatbot,
                        )

                    input_box.submit(
                        self._chat_callback,
                        inputs=[input_box, chatbot],
                        outputs=[input_box, chatbot],
                    )

        ui.launch(inbrowser=True, share=False, pwa=True)
        ui.close()
