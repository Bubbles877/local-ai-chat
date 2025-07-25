﻿# local-ai-chat

[English Readme](./README.md)

## 1. 概要

- ローカル AI チャットアプリ
- [Ollama](https://github.com/ollama/ollama)、[Gradio](https://www.gradio.app/) を利用
- 手元の PC 内で直接生成 AI を動かしてセキュアにチャットができる、ローカル専用アプリです
- 外部にはデータを一切送信しないので、例えば機密情報みたいなものも安心して扱えます

![UI](images/ui.png)

## 2. 主な機能

- Ollama を利用したローカル AI チャット
  - 外部には一切データを送信しない安全性
- ユーザーと AI の会話履歴 (会話例) の事前入力
  - AI の出力の内容、文字数などの誘導に有用
- 会話履歴のファイル保存
  - 事前入力の会話履歴として指定すると、前回の会話の続きから再開
- 会話履歴の編集
  - 会話が長くなると文字数が増えて来たり、システムプロンプトの指示からブレて来るケースなど、  
    AI の出力を軌道修正するのに有用
- LLM に渡す会話履歴の最大数の設定
  - コンテキストが長くなるとモデルの性能が低下する場合に有用
- システムプロンプトの設定
  - 会話の途中でも更新可能

## 3. 使い方

1. 環境変数を設定する
2. アプリを実行する
3. Web ブラウザで AI とチャットする

### 3.1. 環境変数

環境変数の設定が必要です。

ローカル環境ではプロジェクトのルートに `.env` を作成して環境変数を設定してください。  
[.env.example](./.env.example) がテンプレートです。

以下の環境変数があります。

- LOG_LEVEL
  - ログレベル (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- CHAT_HISTORY_FILE_PATH
  - ユーザーと AI の会話履歴 (会話例) のファイルのパス (e.g. `data/chat_history.json`)
  - 先行するメッセージとして UI と LLM に渡す会話履歴に含められる
- LLM_MAX_MESSAGES
  - LLM に渡すメッセージの最大数 (<0: 無制限)
  - より新しいメッセージを優先に最大数まで渡す
- LLM_INSTRUCTIONS_FILE_PATH
  - LLM への指示 (システムプロンプト) の設定ファイルのパス (e.g. `data/llm_instructions.txt`)
- LLM_NAME
  - LLM のモデル名 (e.g. qwen2.5:32b, gemma3:27b)
- LLM_ENDPOINT
  - LLM API の URL (e.g. `http://localhost:11434/`)
- LLM_TEMPERATURE
  - LLM の出力の多様性 (0.0-1.0)

### 3.2. プログラムの実行

```sh
poetry run python app/main.py
```

もしくは

```sh
.venv/Scripts/activate
python app/main.py
```

## 4. 依存関係 & 動作確認済みバージョン

[pyproject.toml](./pyproject.toml) を参照してください。

また、以下を利用しています。

- [python-utilities/llm_chat at main · Bubbles877/python-utilities](https://github.com/Bubbles877/python-utilities/tree/main/llm_chat)
- [python-utilities/env_settings at main · Bubbles877/python-utilities](https://github.com/Bubbles877/python-utilities/tree/main/env_settings)

## 5. リポジトリ

- [Bubbles877/local-ai-chat: Local AI Chat App / ローカル AI チャットアプリ](https://github.com/Bubbles877/local-ai-chat)

## 6. 関連・参考

- [🛡 Ollama × Gradio で作る！ セキュアなローカル専用 AI チャットアプリ](https://zenn.dev/bubbles/articles/29e546ae7ee16d)
