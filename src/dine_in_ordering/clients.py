"""外部サービス（顧客管理・メニュー管理・注文管理）連携用 httpx クライアント."""

from typing import Any

import httpx


class _BaseServiceClient:
    """httpx.Client をラップし base_url / transport 注入に対応する基底クライアント."""

    def __init__(
        self,
        base_url: str = "http://localhost",
        transport: httpx.BaseTransport | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        if client is not None:
            self._client = client
        else:
            kwargs: dict[str, Any] = {"base_url": base_url}
            if transport is not None:
                kwargs["transport"] = transport
            self._client = httpx.Client(**kwargs)


class GuestClient(_BaseServiceClient):
    """顧客管理サービス（guest-management）クライアント."""

    def get_table(self, table_id: str) -> dict[str, Any] | None:
        """席情報を取得する。存在しない場合は None を返す."""
        response = self._client.get(f"/tables/{table_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    def list_tables(self) -> list[dict[str, Any]]:
        """登録済み席一覧を取得する."""
        response = self._client.get("/tables")
        response.raise_for_status()
        return response.json()


class MenuClient(_BaseServiceClient):
    """メニュー管理サービス（menu-management）クライアント."""

    def get_dine_in_menus(self) -> Any:
        """公開中の店内メニュー一覧を取得する."""
        response = self._client.get("/menus/dine_in")
        response.raise_for_status()
        return response.json()


class OrderClient(_BaseServiceClient):
    """注文管理サービス（order-management）クライアント."""

    def create_order(self, payload: dict[str, Any]) -> Any:
        """注文管理サービスへ注文を送信する."""
        response = self._client.post("/orders", json=payload)
        response.raise_for_status()
        return response.json()

    def get_order(self, order_id: str) -> dict[str, Any] | None:
        """注文詳細を取得する。存在しない場合は None を返す."""
        response = self._client.get(f"/orders/{order_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    def list_orders(self) -> list[dict[str, Any]]:
        """注文一覧を取得する."""
        response = self._client.get("/orders")
        response.raise_for_status()
        return response.json()
