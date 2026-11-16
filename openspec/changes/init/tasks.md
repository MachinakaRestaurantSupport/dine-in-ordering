# タスク一覧（init）

## 0. 初期設定・仕様策定
- [x] 0.1 初期ファイル・submodule・`.gitignore` のコミット
- [x] 0.2 OpenSpec `init` 変更の作成と厳格検証（`openspec validate init --strict`）

## 1. プロジェクト基盤・実装
- [x] 1.1 `pyproject.toml` の作成（`dine-in-ordering` パッケージ、pytest・ruff 設定）
- [x] 1.2 Pydantic モデル（`src/dine_in_ordering/models.py`）の実装
- [x] 1.3 外部サービスクライアント（`src/dine_in_ordering/clients.py`）の実装
- [x] 1.4 FastAPI アプリケーションとエンドポイント（`src/dine_in_ordering/main.py`, `__init__.py`）の実装

## 2. 単体試験・品質検証
- [x] 2.1 `httpx.MockTransport` を用いた単体試験（`tests/test_dine_in.py`）の作成と `pytest` 実行
- [ ] 2.2 `ruff` による静的解析・フォーマット確認
