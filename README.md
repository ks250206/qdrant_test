# Embed + Qdrant サンプル

ローカルで OpenAI 互換の埋め込み API を叩きながら、Qdrant にベクトルを保存・検索する最小構成のデモです。`main.py` を実行すると数個のサンプル文をベクトル化して Qdrant に格納し、標準入力から受け取ったテキストに最も近い文とスコアを表示します。

## 必要環境

- Python 3.14 以上（`pyproject.toml` に合わせています。別バージョンを使う場合は適宜変更してください）
- `uv` など PEP 621/pyproject に対応したパッケージマネージャ、もしくは `pip`
- Docker / Docker Compose（Qdrant をローカルで立ち上げるため）
- OpenAI 互換の埋め込みエンドポイント（例: LM Studio、Ollama + openai-server 等）
  - `main.py` では `http://localhost:1234/v1` に API が立っている前提です

## セットアップ

1. 依存関係をインストール

   ```bash
   # uv を使う場合
   uv sync

   ```

2. Qdrant を起動（永続化は `./qdrant_data` に保存されます）
   ```bash
   docker compose up -d 
   ```
3. OpenAI 互換の埋め込み API を `http://localhost:1234/v1` で起動し、`text-embedding-qwen3-embedding-0.6b` が呼べる状態にしておきます。
   API キーは任意ですが、コードでは `not-needed` を渡しています。

## 使い方

```bash
uv run python main.py

```

1. サンプル文がベクトル化され `my_collection` コレクションに格納されます。
2. プロンプトが表示されたら任意のテキストを入力してください。
3. 入力文に最も近い文と類似度スコア、ID、ペイロードが標準出力に表示されます。
4. 入力した文自体も Qdrant に追加されるため、次回以降の検索対象になります。

## 構成メモ

- `main.py`：Qdrant の初期化、埋め込み生成、検索処理をまとめたスクリプト
- `compose.yaml`：Qdrant サービス定義（`qdrant_data/` を永続ボリュームにマウント）
- `pyproject.toml` / `uv.lock`：Python 依存関係の管理

## Qdrant Web UI

`docker compose up -d qdrant` で Qdrant を起動すると、Web UI（Dashboard）が `http://localhost:6333/dashboard` で利用できます。
主な使い方:

1. ブラウザで URL を開くと現在のコレクション一覧が表示されます（初期サンプルでは `my_collection`）。
2. コレクションを選ぶと登録済みポイントやペイロードを GUI で確認できます。
3. `Search` タブからクエリベクトルを入力し、サーバー API を叩かずに検索動作を試せます。
   （GUI 上で直接ベクトルを貼り付ける場合は、`main.py` で出力された埋め込みをそのまま利用できます）

API の状態を確認したりベクターストレージの中身を手早く確認したいときに便利です。

## カスタマイズのヒント

- `sentences` の初期文を入れ替えて独自コーパスを登録できます。
- `text-embedding-qwen3-embedding-0.6b` を他モデルに差し替える場合は、ベクトル次元（`VectorParams.size`）をモデル仕様に合わせて変更してください。
- Qdrant のホストやポートを変更したい場合は `init_qdrant()` 内の接続情報を調整してください。

必要に応じて README をベースに自分のワークフローへ拡張してみてください。
