"""店内注文サービスの Pydantic v2 リクエスト・レスポンスモデル定義."""

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """ヘルスチェックレスポンス."""

    status: str
    service: str


class SessionVerifyRequest(BaseModel):
    """席QRセッション検証リクエスト."""

    table_id: str
    qr_token: str


class SessionVerifyResponse(BaseModel):
    """席QRセッション検証レスポンス."""

    session_id: str | None = None
    table_id: str
    valid: bool


class OrderItemInput(BaseModel):
    """注文明細入力モデル."""

    model_config = ConfigDict(extra="allow")

    product_id: str
    quantity: int = Field(..., ge=1)


class DineInOrderRequest(BaseModel):
    """店内注文・店内発持ち帰り注文リクエスト."""

    table_id: str
    qr_token: str
    is_takeout_from_table: bool = False
    items: list[OrderItemInput] = Field(..., min_length=1)
