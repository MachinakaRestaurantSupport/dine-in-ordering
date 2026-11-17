# dine-in-ordering

席QRコードから席ごとの注文ページにアクセスし、店内飲食のメニュー注文や店内からの持ち帰り注文を行うツールです。  
顧客管理・メニュー管理・注文管理（I-1, I-5, I-6）および店長・スタッフ共通ポータル（[ポータル画面イメージ](reference/system-integration/docs/images/portal/01-portal-dashboard.png)）と連携します。

## 画面遷移図

縮小画面キャプチャを用いた `dine-in-ordering` の画面遷移図です（draw.io 編集用ソース: [transition.drawio](reference/system-integration/docs/images/dine_in_ordering/transition.drawio)）。

![dine-in-ordering 画面遷移図](reference/system-integration/docs/images/dine_in_ordering/transition.svg)

## 代表機能イメージ

### 1. 席QRセッション認証 (`GET /ui/dine-in/session`)
テーブル上のQRコードを読み取り、顧客管理サービスの着席セッションおよびQRトークンの有効性を検証（`POST /sessions`）します。

![席QRセッション認証](reference/system-integration/docs/images/dine_in_ordering/01-qr-session.png)

### 2. 店内メニュー・席発持ち帰り注文 (`GET /ui/dine-in/menu`)
公開中の店内メニューを表示し、テーブルで食べる「店内飲食（`is_takeout_from_table=false`）」と「席からの持ち帰り注文（`is_takeout_from_table=true`）」を切り替えて注文できます。

![店内メニュー注文](reference/system-integration/docs/images/dine_in_ordering/02-order-menu.png)

### 3. 注文履歴・調理進行状況確認 (`GET /ui/dine-in/status`)
送信した注文明細の受付・調理中・提供可能・提供完了ステータスと会計状況をテーブルからリアルタイムに確認できます。

![注文履歴・調理進行状況](reference/system-integration/docs/images/dine_in_ordering/03-order-status.png)

## 提供 API・UI エンドポイント

| 種別 | メソッド & パス | 機能概要 |
|---|---|---|
| API | `GET /health` | ヘルスチェック |
| API | `POST /sessions` | 席QRトークン・着席セッション検証 |
| API | `GET /dine-in/menus` | 公開中店内メニュー取得 (I-5) |
| API | `POST /dine-in/orders` | 店内注文・席発持ち帰り注文送信 (I-1) |
| API | `GET /dine-in/orders/{order_id}` | 注文ステータス取得 |
| UI | `GET /ui/dine-in/session` | 席QRセッション認証画面 |
| UI | `GET /ui/dine-in/menu` | 店内・席持ち帰り注文画面 |
| UI | `GET /ui/dine-in/status` | 注文履歴・調理進行確認画面 |

## テスト・静的解析の実行

```bash
../.venv/bin/python3 -m pytest -v
../.venv/bin/ruff check .
```
