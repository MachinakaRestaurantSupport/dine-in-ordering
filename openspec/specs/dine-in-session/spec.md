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
