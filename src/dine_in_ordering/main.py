"""店内注文（dine-in-ordering）FastAPI アプリケーション."""

import os
from typing import Any

from fastapi import FastAPI, HTTPException, status

from dine_in_ordering.clients import GuestClient, MenuClient, OrderClient
from dine_in_ordering.models import (
    DineInOrderRequest,
    HealthResponse,
    SessionVerifyRequest,
    SessionVerifyResponse,
)


def _verify_table_session(
    guest_client: GuestClient,
    table_id: str,
    qr_token: str,
) -> dict[str, Any]:
    """席情報とQRトークンを検証し、有効な席情報を返す."""
    table = guest_client.get_table(table_id)
    if table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found",
        )
    if table.get("status") != "occupied" or table.get("qr_token") != qr_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid table session or QR token",
        )
    return table


def create_app(
    guest_client: GuestClient | None = None,
    menu_client: MenuClient | None = None,
    order_client: OrderClient | None = None,
) -> FastAPI:
    """店内注文サービスの FastAPI アプリケーションを生成する."""
    guest = guest_client or GuestClient(base_url=os.getenv("GUEST_SERVICE_URL", "http://localhost"))
    menu = menu_client or MenuClient(base_url=os.getenv("MENU_SERVICE_URL", "http://localhost"))
    order = order_client or OrderClient(base_url=os.getenv("ORDER_SERVICE_URL", "http://localhost"))

    fastapi_app = FastAPI(title="Dine-In Ordering Service", version="0.1.0")

    @fastapi_app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok", service="dine-in-ordering")

    @fastapi_app.post("/sessions", response_model=SessionVerifyResponse)
    def verify_session(request: SessionVerifyRequest) -> SessionVerifyResponse:
        table = _verify_table_session(guest, request.table_id, request.qr_token)
        return SessionVerifyResponse(
            session_id=table.get("current_session_id"),
            table_id=request.table_id,
            valid=True,
        )

    @fastapi_app.get("/dine-in/menus")
    def get_dine_in_menus() -> Any:
        return menu.get_dine_in_menus()

    @fastapi_app.post("/dine-in/orders", status_code=status.HTTP_201_CREATED)
    def create_dine_in_order(request: DineInOrderRequest) -> Any:
        table = _verify_table_session(guest, request.table_id, request.qr_token)
        order_payload = {
            "source": "dine_in",
            "table_id": request.table_id,
            "session_id": table.get("current_session_id"),
            "is_takeout_from_table": request.is_takeout_from_table,
            "items": [item.model_dump() for item in request.items],
        }
        return order.create_order(order_payload)

    @fastapi_app.get("/dine-in/orders/{order_id}")
    def get_dine_in_order(order_id: str) -> Any:
        result = order.get_order(order_id)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )
        return result

    return fastapi_app


app = create_app()
