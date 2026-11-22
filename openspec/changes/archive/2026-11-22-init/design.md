# 設計書（dine-in-ordering 初期MVP）

## 1. アーキテクチャ概要
- **フレームワーク**: Python 3.12 + FastAPI + Pydantic v2 + httpx
- **アプリケーションファクトリ**: `create_app(guest_client=None, menu_client=None, order_client=None)` を提供し、テスト時に `httpx.MockTransport` や `httpx.ASGITransport` を注入可能にする。
- **モジュール構成**:
  - `src/dine_in_ordering/__init__.py`: パッケージエクスポート
  - `src/dine_in_ordering/models.py`: リクエスト・レスポンス用 Pydantic v2 モデル
  - `src/dine_in_ordering/clients.py`: 外部サービス連携クライアント（`GuestClient`, `MenuClient`, `OrderClient`）
  - `src/dine_in_ordering/main.py`: FastAPI ルーティングと `create_app` / `app`

## 2. USDM トレーサビリティ

| USDM 要求ID | 要件内容 | 対応エンドポイント / 実装 |
|---|---|---|
| `DineInOrdering_R01.DM01-01` | `POST /sessions` で席ID・QRトークンから店内注文セッションを開始・検証できる | `POST /sessions` (`GuestClient.get_table` で `GET /tables/{table_id}` を参照し、`status == "occupied"` と `qr_token` 一致を検証。未存在 404 / 不一致 403) |
| `DineInOrdering_R01.DM01-02` | `POST /dine-in/orders` で店内飲食または店内発持ち帰り注文を受け付け、注文管理（I-1）へ連携できる | `POST /dine-in/orders` (`GuestClient` で席QR検証後、`OrderClient.create_order` で `POST /orders` (`source="dine_in"`, `is_takeout_from_table`) を送信し 201 返却) |
| `DineInOrdering_R01.DM01-03` | `GET /dine-in/orders/{order_id}` で注文履歴・状況を参照できる | `GET /dine-in/orders/{order_id}` (`OrderClient.get_order` で `GET /orders/{order_id}` を参照) |
| 全体共通（I-5 / `/health`） | ヘルスチェックおよび公開メニュー参照 | `GET /health`、`GET /dine-in/menus` (`MenuClient.get_dine_in_menus` で `GET /menus/dine_in` を参照) |
