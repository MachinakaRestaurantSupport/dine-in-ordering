# dine-in-session Specification

## Purpose
席QRコードによる店内注文セッション検証、メニュー取得、店内および持ち帰り注文の受付・照会仕様を定義する。

## Requirements

### Requirement: 席QR検証
`POST /sessions` は着席かつQR一致で200、不一致で403を返す（SHALL）。

#### Scenario: 有効QR
- **WHEN** `status == "occupied"` かつ `qr_token` 一致時
- **THEN** 200 を返す

#### Scenario: 無効QR
- **WHEN** 不一致時
- **THEN** 403 を返す

### Requirement: 注文受付と照会
`POST /dine-in/orders` で送信し、`GET /dine-in/orders/{order_id}` で参照できる（MUST）。

#### Scenario: 注文作成
- **WHEN** 有効QRで注文送信時
- **THEN** 201 を返す

### Requirement: サブモジュール参照のコミット指定管理

本リポジトリは `.gitmodules` に `branch` 設定を持たせず `reference/system-integration` を確定コミット SHA（gitlink）指定で管理しなければならず（MUST）、`reference/system-integration/` 配下を読み取り専用として直接変更してはならない（SHALL）。

#### Scenario: サブモジュール参照の更新とマージ

- **WHEN** `system-integration` の確定コミット SHA（`<commit-sha>`）を `reference/system-integration` にチェックアウトし、`system-integration` PR の Merge commit マージ後に本リポジトリの PR を `main` にマージするとき
- **THEN** `.gitmodules` の書き換えやマージ後の `main` 戻し作業なしで、正しい仕様・画像参照を維持したままマージが完了する（SHALL）
