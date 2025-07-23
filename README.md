# local-ai-chat

[日本語 Readme](./README.ja.md)

## 1. Overview

- Local AI Chat App
- Built with [Ollama](https://github.com/ollama/ollama) and [Gradio](https://www.gradio.app/)
- A local-only app that runs generative AI directly on your PC for secure chat
- It does not send any data externally, so you can handle sensitive information with confidence

![UI](images/ui.png)

## 2. Key Features

- Local AI chat using Ollama
  - Secure with no external data transfers
- Pre-input of user–AI conversation history (example dialogues)
  - Useful for guiding the content and length of the AI’s output
- Save conversation history to a file
  - When specified as the pre-input history, you can resume from the previous conversation
- Edit conversation history
  - Useful for keeping AI’s output on track when conversations become long, the number of characters increases, or the output deviates from the system prompt's instructions.
- Set the maximum number of conversation-history entries to pass to the LLM
  - Useful when model performance degrades with longer contexts
- Set the system prompt
  - Can be updated even in the middle of a conversation

## 3. Usage

1. Set up the required environment variables
2. Run the app
3. Chat with the AI via web browser

### 3.1. Environment Variables

Environment variables are required.

Create a `.env` file at the project root in your local environment and set the environment variables.  
[.env.example](./.env.example) is the template.

Available environment variables:

- LOG_LEVEL
  - Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- CHAT_HISTORY_FILE_PATH
  - Path to the user-AI conversation history (examples) file (e.g. `data/chat_history.json`)
  - Included as preceding messages passed to both the UI and the LLM
- LLM_MAX_MESSAGES
  - Maximum number of messages to pass to the LLM (<0: unlimited)
  - The most recent messages are prioritized up to the maximum count
- LLM_INSTRUCTIONS_FILE_PATH
  - Path to the system-prompt file used as instructions for the LLM (e.g. `data/llm_instructions.txt`)
- LLM_NAME
  - LLM model name (e.g. qwen2.5:32b, gemma3:27b)
- LLM_ENDPOINT
  - URL of the LLM API (e.g. `http://localhost:11434/`)
- LLM_TEMPERATURE
  - Diversity of LLM Outputs (0.0–1.0)

### 3.2. Running the App

```sh
poetry run python app/main.py
```

Or

```sh
.venv/Scripts/activate
python app/main.py
```

## 4. Dependencies & Verified Versions

Please see [pyproject.toml](./pyproject.toml).

We also use the following:

- [python-utilities/llm_chat at main · Bubbles877/python-utilities](https://github.com/Bubbles877/python-utilities/tree/main/llm_chat)
- [python-utilities/env_settings at main · Bubbles877/python-utilities](https://github.com/Bubbles877/python-utilities/tree/main/env_settings)

## 5. Repository

- [Bubbles877/local-ai-chat: Local AI Chat App / ローカル AI チャットアプリ](https://github.com/Bubbles877/local-ai-chat)

## 6. References

- [🛡 Build a Secure Local-Only AI Chat App with Ollama and Gradio!](https://zenn.dev/bubbles/articles/29e546ae7ee16d)
