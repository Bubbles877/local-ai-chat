# local-ai-chat

[日本語 Readme](./README.ja.md)

## 1. Overview

- Local AI Chat App
- Built with [Ollama](https://github.com/ollama/ollama) and [Gradio](https://www.gradio.app/)
- Secure local-only app with no external data transfers

![UI](images/ui.png)

## 2. Key Features

- Local AI chat using Ollama
  - Secure with no external data transfers
- Feature to set the system prompt
  - Can be updated even in the middle of a conversation
- Feature to set the maximum number of conversation history entries to pass to the LLM
  - Useful when model performance degrades with longer contexts
- Feature to pre-input example conversations between user and AI
  - Useful for guiding the content and length of AI output
- Conversation history editing feature
  - Useful for correcting the AI's output when conversations become long, the number of characters increases, or the output deviates from the system prompt's instructions.

## 3. Usage

1. Set up environment variables
2. Run the app
3. Chat with the AI via web browser

### 3.1. Environment Variables

Environment variables are required.

Create a `.env` file at the project root in your local environment and set the environment variables.  
[.env.example](./.env.example) is the template.

Available environment variables:

- LOG_LEVEL
  - Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- LLM_INSTRUCTION_FILE_PATH
  - File path for the system prompt file used as instructions for the LLM (e.g. `data/llm_instruction.txt`)
- LLM_MESSAGE_EXAMPLE_FILE_PATH
  - File path for the example conversation between user and AI (e.g. `data/llm_message_example.json`)
  - Included in the conversation history as preceding messages
- LLM_MAX_MESSAGES
  - Maximum number of messages to include in the conversation history passed to the LLM (<0: unlimited)
  - The most recent messages are prioritized up to the maximum count
- LLM_NAME
  - Name of the LLM (e.g. qwen2.5:32b, gemma3:27b)
- LLM_ENDPOINT
  - URL of the LLM API (e.g. `http://localhost:11434/`)
- LLM_TEMPERATURE
  - Sampling temperature of the LLM (randomness and creativity of the generated output) (0.0-1.0)

### 3.2. Running the App

```sh
poetry run python app/main.py
```

Or

```sh
.venv/Scripts/activate
python app/main.py
```

## 4. Repository

- [Bubbles877/local-ai-chat](https://github.com/Bubbles877/local-ai-chat)
