"""店内注文（dine-in-ordering）単体試験."""

import json
from typing import Any

import httpx
from fastapi.testclient import TestClient

from dine_in_ordering.clients import GuestClient, MenuClient, OrderClient
from dine_in_ordering.main import create_app


def _make_test_client(
    tables: dict[str, dict[str, Any]] | None = None,
    menus: list[dict[str, Any]] | None = None,
    orders: dict[str, dict[str, Any]] | None = None,
    recorded_order_requests: list[dict[str, Any]] | None = None,
) -> TestClient:
    """MockTransport を注入した TestClient を構築する."""
    table_store = tables or {
        "T1": {
            "table_id": "T1",
            "status": "occupied",
            "qr_token": "qr-secret-t1",
            "current_session_id": "S-001",
        },
        "T2": {
            "table_id": "T2",
            "status": "available",
            "qr_token": "qr-secret-t2",
            "current_session_id": None,
        },
    }
    menu_store = menus or [
        {"product_id": "P1", "name": "ハンバーグランチ", "price": 1200},
        {"product_id": "P2", "name": "アイスコーヒー", "price": 450},
    ]
    order_store = orders if orders is not None else {}
    captured = recorded_order_requests if recorded_order_requests is not None else []

    def guest_handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET" and request.url.path.startswith("/tables/"):
            table_id = request.url.path.removeprefix("/tables/")
            if table_id not in table_store:
                return httpx.Response(404, json={"detail": "Table not found"})
            return httpx.Response(200, json=table_store[table_id])
        return httpx.Response(404)

    def menu_handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET" and request.url.path == "/menus/dine_in":
            return httpx.Response(200, json={"items": menu_store})
        return httpx.Response(404)

    def order_handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/orders":
            payload = json.loads(request.content.decode("utf-8"))
            captured.append(payload)
            order_id = f"ORD-{len(order_store) + 1:03d}"
            created = {"order_id": order_id, "status": "received", **payload}
            order_store[order_id] = created
            return httpx.Response(201, json=created)
        if request.method == "GET" and request.url.path.startswith("/orders/"):
            order_id = request.url.path.removeprefix("/orders/")
            if order_id not in order_store:
                return httpx.Response(404, json={"detail": "Order not found"})
            return httpx.Response(200, json=order_store[order_id])
        return httpx.Response(404)

    app = create_app(
        guest_client=GuestClient(transport=httpx.MockTransport(guest_handler)),
        menu_client=MenuClient(transport=httpx.MockTransport(menu_handler)),
        order_client=OrderClient(transport=httpx.MockTransport(order_handler)),
    )
    return TestClient(app)


def test_health() -> None:
    """ヘルスチェックが ok を返す."""
    client = _make_test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "dine-in-ordering"}


def test_verify_session_valid() -> None:
    """着席中かつQRトークン一致時に有効なセッション情報を返す."""
    client = _make_test_client()
    response = client.post(
        "/sessions",
        json={"table_id": "T1", "qr_token": "qr-secret-t1"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "session_id": "S-001",
        "table_id": "T1",
        "valid": True,
    }


def test_verify_session_invalid_qr_returns_403() -> None:
    """QRトークン不一致時に 403 を返す."""
    client = _make_test_client()
    response = client.post(
        "/sessions",
        json={"table_id": "T1", "qr_token": "wrong-token"},
    )
    assert response.status_code == 403


def test_verify_session_not_occupied_returns_403() -> None:
    """席状態が occupied でない場合は 403 を返す."""
    client = _make_test_client()
    response = client.post(
        "/sessions",
        json={"table_id": "T2", "qr_token": "qr-secret-t2"},
    )
    assert response.status_code == 403


def test_verify_session_unknown_table_returns_404() -> None:
    """存在しない席IDの場合は 404 を返す."""
    client = _make_test_client()
    response = client.post(
        "/sessions",
        json={"table_id": "T999", "qr_token": "any"},
    )
    assert response.status_code == 404


def test_get_dine_in_menus() -> None:
    """店内公開メニューを取得できる."""
    client = _make_test_client()
    response = client.get("/dine-in/menus")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["items"][0]["product_id"] == "P1"


def test_create_dine_in_order() -> None:
    """有効なQRで店内飲食注文を送信すると 201 が返り注文管理へ連携される."""
    recorded: list[dict[str, Any]] = []
    client = _make_test_client(recorded_order_requests=recorded)

    response = client.post(
        "/dine-in/orders",
        json={
            "table_id": "T1",
            "qr_token": "qr-secret-t1",
            "is_takeout_from_table": False,
            "items": [{"product_id": "P1", "quantity": 2}],
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["order_id"] == "ORD-001"
    assert body["source"] == "dine_in"
    assert body["is_takeout_from_table"] is False
    assert recorded[0] == {
        "source": "dine_in",
        "table_id": "T1",
        "session_id": "S-001",
        "is_takeout_from_table": False,
        "items": [{"product_id": "P1", "quantity": 2}],
    }


def test_create_takeout_from_table_order() -> None:
    """店内発持ち帰り注文（is_takeout_from_table=True）を送信できる."""
    recorded: list[dict[str, Any]] = []
    client = _make_test_client(recorded_order_requests=recorded)

    response = client.post(
        "/dine-in/orders",
        json={
            "table_id": "T1",
            "qr_token": "qr-secret-t1",
            "is_takeout_from_table": True,
            "items": [{"product_id": "P2", "quantity": 1}],
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["is_takeout_from_table"] is True
    assert recorded[0]["is_takeout_from_table"] is True
    assert recorded[0]["source"] == "dine_in"


def test_create_order_invalid_qr_returns_403() -> None:
    """無効なQRでの注文送信は 403 となり注文管理へ送信されない."""
    recorded: list[dict[str, Any]] = []
    client = _make_test_client(recorded_order_requests=recorded)

    response = client.post(
        "/dine-in/orders",
        json={
            "table_id": "T1",
            "qr_token": "invalid-qr",
            "items": [{"product_id": "P1", "quantity": 1}],
        },
    )
    assert response.status_code == 403
    assert recorded == []


def test_get_dine_in_order() -> None:
    """作成した注文を GET /dine-in/orders/{order_id} で参照できる."""
    client = _make_test_client()
    create_res = client.post(
        "/dine-in/orders",
        json={
            "table_id": "T1",
            "qr_token": "qr-secret-t1",
            "items": [{"product_id": "P1", "quantity": 1}],
        },
    )
    order_id = create_res.json()["order_id"]

    get_res = client.get(f"/dine-in/orders/{order_id}")
    assert get_res.status_code == 200
    assert get_res.json()["order_id"] == order_id

    not_found = client.get("/dine-in/orders/ORD-999")
    assert not_found.status_code == 404
