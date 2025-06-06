﻿# local-ai-chat

[English Readme](./README.md)

## 1. 概要

- ローカル AI チャットアプリ
- [Ollama](https://github.com/ollama/ollama)、[Gradio](https://www.gradio.app/) を利用
- 外部には一切データを送信しないセキュアなローカル専用アプリです

![UI](images/ui.png)

## 2. 主な機能

- Ollama を利用したローカル AI チャット
  - 外部には一切データを送信しない安全性
- システムプロンプトの設定機能
  - 会話の途中でも更新可能
- LLM に渡す会話履歴の最大数の設定機能
  - コンテキストが長くなるとモデルの性能が低下する場合に有用
- ユーザーと AI の会話例の事前入力機能
  - AI の出力の内容、文字数などの誘導に有用
- 会話履歴の編集機能
  - 会話が長くなると文字数が増えて来たり、システムプロンプトの指示からブレて来るケースなど、  
    AI の出力を軌道修正するのに有用

## 3. 使い方

1. 環境変数を設定する
2. アプリを実行する
3. Web ブラウザで AI とチャットする

### 3.1. 環境変数

環境変数の設定が必要です。

ローカル環境ではプロジェクトのルートに`.env`を作成して環境変数を設定してください。  
[.env.example](./.env.example) がテンプレートです。

以下の環境変数があります。

- LOG_LEVEL
  - ログレベル (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- LLM_INSTRUCTION_FILE_PATH
  - LLM への指示 (システムプロンプト) の設定ファイルのパス (e.g. `data/llm_instruction.txt`)
- LLM_MESSAGE_EXAMPLE_FILE_PATH
  - ユーザーと AI の会話例の設定ファイルのパス (e.g. `data/llm_message_example.json`)
  - 先行するメッセージとして会話履歴に含められる
- LLM_MAX_MESSAGES
  - LLM に渡す会話履歴の最大数 (<0: 無制限)
  - より新しいメッセージを優先に最大数まで渡す
- LLM_NAME
  - LLM 名 (e.g. qwen2.5:32b, gemma3:27b)
- LLM_ENDPOINT
  - LLM API の URL (e.g. `http://localhost:11434/`)
- LLM_TEMPERATURE
  - LLM の温度 (生成する出力のランダム性、創造性) (0.0-1.0)

### 3.2. プログラムの実行

```sh
poetry run python app/main.py
```

もしくは

```sh
.venv/Scripts/activate
python app/main.py
```

## 4. リポジトリ

- [Bubbles877/local-ai-chat](https://github.com/Bubbles877/local-ai-chat)
