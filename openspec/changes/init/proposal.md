# Proposal: 店内注文（dine-in-ordering）初期MVP構築

## 概要
MachinakaRestaurantSupportTools のサブシステム「店内注文（dine-in-ordering）」の初期 MVP を構築する。
席QRコードによる着席セッション検証、公開メニューの取得、店内飲食および店内発持ち帰り注文の受付・注文管理サービス（I-1）への連携、注文状況参照 API を FastAPI + Pydantic v2 + httpx で提供する。

## 背景・目的
- USDM `DineInOrdering_R01`（`DineInOrdering_R01.DM01-01`〜`03`）に基づき、非接触の店内セルフオーダー基盤を整備する。
- 顧客管理・メニュー管理・注文管理とは `httpx.Client` を通じて疎結合に連携し、`MockTransport` / `ASGITransport` による単体・結合試験を容易にする。

## スコープ
- Python プロジェクト基盤（`pyproject.toml`）の整備
- 席QR検証・メニュー取得・注文作成・注文参照の API 実装
- `httpx.MockTransport` を用いた単体試験の整備
