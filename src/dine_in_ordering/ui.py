# ruff: noqa: E501
"""HTML UI router for dine-in-ordering."""

from html import escape
from typing import Any

import httpx
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from dine_in_ordering.clients import GuestClient, MenuClient, OrderClient

PORTAL_LINKS = [
    ("portal", "ポータル", "/ui/portal"),
    ("product", "商品管理", "/ui/products"),
    ("menu", "メニュー", "/ui/menus"),
    ("guest", "座席・顧客", "/ui/tables"),
    ("order", "注文かんばん", "/ui/orders/kanban"),
    ("accounting", "会計", "/ui/accounting/checkout"),
    ("sales", "売上", "/ui/sales/daily"),
    ("dine_in", "店内QR", "/ui/dine-in/session"),
    ("takeout", "持ち帰り", "/ui/takeout/login"),
]

STATUS_LABELS = {
    "received": ("受付済み", "#dbeafe", "#1e40af"),
    "preparing": ("調理中", "#fef3c7", "#92400e"),
    "ready": ("提供準備完了", "#dcfce7", "#166534"),
    "served": ("提供済み", "#f1f5f9", "#334155"),
}


def _safe_tables(guest: GuestClient) -> list[dict[str, Any]]:
    try:
        res = guest.list_tables()
        return res if isinstance(res, list) else []
    except (httpx.HTTPError, TypeError, ValueError):
        return []


def _safe_menus(menu: MenuClient) -> list[dict[str, Any]]:
    try:
        res = menu.get_dine_in_menus()
    except (httpx.HTTPError, TypeError, ValueError):
        return []
    if isinstance(res, list):
        return res
    if isinstance(res, dict) and isinstance(res.get("items"), list):
        return [{"title": "店内メニュー", "categories": [{"name": "おすすめ", "items": res["items"]}]}]
    return []


def _safe_orders(order: OrderClient) -> list[dict[str, Any]]:
    try:
        res = order.list_orders()
        if isinstance(res, list):
            return [o for o in res if o.get("source") == "dine_in"]
        return []
    except (httpx.HTTPError, TypeError, ValueError):
        return []


def _render_shell(*, title: str, subtitle: str, active_subtab: str, body_html: str) -> str:
    nav_html = "".join(
        f'<a class="nav-pill{" active" if key == "dine_in" else ""}" href="{href}">{escape(label)}</a>'
        for key, label, href in PORTAL_LINKS
    )
    subtabs = [
        ("session", "1. 席QRセッション認証", "/ui/dine-in/session"),
        ("menu", "2. 店内・席持ち帰り注文", "/ui/dine-in/menu"),
        ("status", "3. 注文・調理進行確認", "/ui/dine-in/status"),
    ]
    subtab_html = "".join(
        f'<a class="subtab{" active" if key == active_subtab else ""}" href="{href}">{escape(label)}</a>'
        for key, label, href in subtabs
    )
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)} | まちなか飲食店サポート</title>
  <style>
    :root {{ --bg:#f8fafc; --surface:#fff; --navy:#0f172a; --slate:#334155; --muted:#64748b; --border:#e2e8f0; --accent:#ea580c; --accent-soft:#fff7ed; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--navy); line-height:1.5; font-family:"Noto Sans CJK JP","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif; }}
    .topbar {{ background:var(--navy); color:#fff; padding:0 24px; height:54px; display:flex; align-items:center; justify-content:space-between; gap:16px; }}
    .brand {{ display:flex; align-items:center; gap:10px; font-weight:700; font-size:15px; white-space:nowrap; }}
    .brand-badge {{ background:var(--accent); color:#fff; padding:2px 8px; border-radius:6px; font-size:11px; }}
    .nav-links {{ display:flex; gap:4px; overflow-x:auto; }}
    .nav-pill {{ color:#cbd5e1; text-decoration:none; font-size:12px; font-weight:600; padding:6px 10px; border-radius:6px; white-space:nowrap; }}
    .nav-pill.active {{ background:var(--accent); color:#fff; }}
    .subbar {{ background:var(--surface); border-bottom:1px solid var(--border); padding:12px 24px; display:flex; align-items:center; justify-content:space-between; gap:16px; }}
    .subbar h1 {{ margin:0; font-size:18px; }}
    .subbar .subtitle {{ margin:2px 0 0; font-size:12px; color:var(--muted); }}
    .subtabs {{ display:flex; gap:8px; }}
    .subtab {{ text-decoration:none; color:var(--slate); font-size:13px; font-weight:600; padding:7px 14px; border-radius:8px; border:1px solid var(--border); background:#fff; }}
    .subtab.active {{ background:var(--accent-soft); color:var(--accent); border-color:#fdba74; }}
    .container {{ max-width:1220px; margin:0 auto; padding:20px 24px 28px; }}
    .grid-2 {{ display:grid; grid-template-columns:1.1fr 1fr; gap:18px; }}
    .card {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:16px 18px; box-shadow:0 1px 2px rgba(15,23,42,.04); }}
    .phone-frame {{ max-width:440px; margin:0 auto; border:10px solid #1e293b; border-radius:26px; background:#fff; overflow:hidden; box-shadow:0 10px 25px rgba(15,23,42,.12); }}
    .phone-top {{ background:#ea580c; color:#fff; padding:14px 16px; font-weight:700; display:flex; justify-content:space-between; align-items:center; }}
    .phone-body {{ padding:14px 16px; }}
    .badge {{ display:inline-block; padding:2px 9px; border-radius:999px; font-size:11px; font-weight:700; }}
    .btn {{ display:inline-block; text-decoration:none; font-size:13px; font-weight:700; padding:9px 15px; border-radius:8px; border:none; cursor:pointer; }}
    .btn-primary {{ background:var(--accent); color:#fff; }}
    .btn-secondary {{ background:#f1f5f9; color:var(--slate); border:1px solid var(--border); }}
    label {{ font-size:12px; font-weight:700; color:var(--slate); display:block; margin-bottom:4px; }}
    input, select {{ width:100%; padding:8px 10px; border:1px solid #cbd5e1; border-radius:8px; font-size:13px; font-family:inherit; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    th {{ text-align:left; padding:10px 12px; background:#f8fafc; color:var(--muted); font-size:12px; border-bottom:1px solid var(--border); }}
    td {{ padding:10px 12px; border-bottom:1px solid var(--border); }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand">
      <span>🍽️ まちなか飲食店サポート</span>
      <span class="brand-badge">店長・スタッフ共通ポータル</span>
    </div>
    <nav class="nav-links">{nav_html}</nav>
  </header>
  <section class="subbar">
    <div>
      <h1>{escape(title)}</h1>
      <p class="subtitle">{escape(subtitle)}</p>
    </div>
    <div class="subtabs">{subtab_html}</div>
  </section>
  <main class="container">{body_html}</main>
</body>
</html>
"""


def create_ui_router(
    guest_client: GuestClient,
    menu_client: MenuClient,
    order_client: OrderClient,
) -> APIRouter:
    """Create FastAPI router providing HTML UI screens for dine-in-ordering."""
    router = APIRouter(tags=["ui"])

    @router.get("/ui/dine-in/session", response_class=HTMLResponse)
    def session_page() -> str:
        tables = _safe_tables(guest_client)
        occ = [t for t in tables if t.get("status") == "occupied"]
        active = occ[0] if occ else (tables[0] if tables else None)
        table_id = str(active.get("id", "table-a1")) if active else "table-a1"
        table_num = str(active.get("table_number", "A-1")) if active else "A-1"
        qr_token = str(active.get("qr_token") or "qr-demo-token") if active else "qr-demo-token"
        session_id = str(active.get("current_session_id") or "sess-active") if active else "sess-active"

        table_rows = "".join(
            f"<tr><td><strong>席 {escape(str(t.get('table_number', '-')))}</strong></td>"
            f"<td>{escape(str(t.get('status', '-')))}</td>"
            f"<td><code>{escape(str(t.get('qr_token') or '-'))}</code></td>"
            f"<td><code>{escape(str(t.get('current_session_id') or '-'))}</code></td></tr>"
            for t in tables
        ) or '<tr><td colspan="4" style="text-align:center;color:#64748b">座席データがありません。</td></tr>'

        body = f"""
        <div class="grid-2">
          <div class="phone-frame">
            <div class="phone-top">
              <span>📱 席QR注文ログイン</span>
              <span>席 {escape(table_num)}</span>
            </div>
            <div class="phone-body">
              <div style="background:#dcfce7;color:#166534;padding:10px 12px;border-radius:10px;font-size:12px;font-weight:700;margin-bottom:14px">
                ✓ 座席QRコードを読み取りました（セッション有効）
              </div>
              <div style="margin-bottom:10px">
                <label>座席ID</label>
                <input type="text" id="s-table" value="{escape(table_id)}">
              </div>
              <div style="margin-bottom:10px">
                <label>QRトークン</label>
                <input type="text" id="s-qr" value="{escape(qr_token)}">
              </div>
              <div style="font-size:12px;color:#64748b;margin-bottom:14px">
                発行セッションID: <code>{escape(session_id)}</code>
              </div>
              <div style="display:flex;gap:8px">
                <button class="btn btn-primary" style="flex:1" onclick="verifySession()">QRセッション認証してメニューへ</button>
              </div>
            </div>
          </div>
          <div class="card">
            <h2 style="margin:0 0 12px;font-size:16px">連携中の座席セッション一覧（I-6）</h2>
            <table>
              <thead><tr><th>席番号</th><th>状態</th><th>QRトークン</th><th>セッションID</th></tr></thead>
              <tbody>{table_rows}</tbody>
            </table>
            <div style="margin-top:14px;text-align:right">
              <a class="btn btn-secondary" href="/ui/dine-in/menu">注文メニュー画面へ進む →</a>
            </div>
          </div>
        </div>
        """ + """
        <script>
          async function verifySession() {
            const res = await fetch('/sessions', {
              method: 'POST', headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({table_id: document.getElementById('s-table').value, qr_token: document.getElementById('s-qr').value})
            });
            if (res.ok) window.location.href = '/ui/dine-in/menu';
          }
        </script>
        """
        return _render_shell(
            title="店内注文 › 席QRセッション認証",
            subtitle="お客様が席のQRコードを読み取り、着席中の有効なセッションか検証します",
            active_subtab="session",
            body_html=body,
        )

    @router.get("/ui/dine-in/menu", response_class=HTMLResponse)
    def menu_order_page() -> str:
        menus = _safe_menus(menu_client)
        tables = _safe_tables(guest_client)
        occ = [t for t in tables if t.get("status") == "occupied"]
        active = occ[0] if occ else (tables[0] if tables else None)
        table_num = str(active.get("table_number", "A-1")) if active else "A-1"

        menu_cards = []
        for m in menus:
            m_title = escape(str(m.get("title", "店内メニュー")))
            cat_blocks = []
            for cat in m.get("categories", []):
                cname = escape(str(cat.get("name", "カテゴリ")))
                pids = cat.get("product_ids") or []
                items = cat.get("items") or [{"product_id": pid, "name": f"商品 #{pid}"} for pid in pids]
                item_html = "".join(
                    f'<div style="display:flex;justify-content:space-between;align-items:center;'
                    f'padding:9px 10px;border:1px solid #e2e8f0;border-radius:8px;margin-bottom:6px">'
                    f'<div><strong>{escape(str(it.get("name", it.get("product_id", "商品"))))}</strong>'
                    f'<div style="font-size:11px;color:#64748b">商品ID: {escape(str(it.get("product_id", "-")))}</div></div>'
                    f'<button class="btn btn-secondary" style="padding:4px 10px;font-size:12px">＋ カートに追加</button></div>'
                    for it in items
                )
                cat_blocks.append(f'<div style="margin-bottom:10px"><div style="font-size:12px;font-weight:700;color:#ea580c;margin-bottom:4px">{cname}</div>{item_html}</div>')
            menu_cards.append(f'<h3 style="margin:4px 0 8px;font-size:15px">{m_title}</h3>' + "".join(cat_blocks))
        menus_html = "".join(menu_cards) or '<p style="color:#64748b">公開中の店内メニューはありません。</p>'

        body = f"""
        <div class="grid-2">
          <div class="phone-frame">
            <div class="phone-top">
              <span>🍽️ テーブル {escape(table_num)} メニュー</span>
              <span style="font-size:11px;background:rgba(255,255,255,.2);padding:2px 8px;border-radius:999px">QR認証済</span>
            </div>
            <div class="phone-body">
              <div style="display:flex;gap:8px;margin-bottom:12px">
                <span class="badge" style="background:#fff7ed;color:#ea580c;border:1px solid #fdba74;padding:6px 10px">🍽️ 店内でお食事 (is_takeout=false)</span>
                <span class="badge" style="background:#f1f5f9;color:#334155;padding:6px 10px">🥡 席から持ち帰り (is_takeout=true)</span>
              </div>
              {menus_html}
            </div>
          </div>
          <div class="card">
            <h2 style="margin:0 0 12px;font-size:16px">注文送信カート（店内 / 店内発持ち帰り両対応）</h2>
            <p style="font-size:13px;color:#475569">
              お客様がテーブル席に着席したまま、今食べる「店内飲食注文」と食後に持ち帰る「店内発持ち帰り注文」を同一画面から注文管理へ送信できます。
            </p>
            <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:12px;margin:12px 0">
              <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px">
                <span>ボロネーゼ × 1（店内飲食）</span><strong>¥1,200</strong>
              </div>
              <div style="display:flex;justify-content:space-between;font-size:13px">
                <span>ブレンドコーヒー × 2（席発持ち帰り）</span><strong>¥900</strong>
              </div>
            </div>
            <div style="text-align:right">
              <a class="btn btn-primary" href="/ui/dine-in/status">注文送信後の進行状況を確認 →</a>
            </div>
          </div>
        </div>
        """
        return _render_shell(
            title="店内注文 › 店内メニュー＆席からの持ち帰り注文",
            subtitle="公開中の店内メニューを表示し、店内飲食と席からの持ち帰り注文を受け付けます",
            active_subtab="menu",
            body_html=body,
        )

    @router.get("/ui/dine-in/status", response_class=HTMLResponse)
    def order_status_page() -> str:
        orders = _safe_orders(order_client)
        rows = []
        for o in orders:
            st = str(o.get("status", "received"))
            label, bg, fg = STATUS_LABELS.get(st, (st, "#f1f5f9", "#334155"))
            take_tag = (
                '<span class="badge" style="background:#fef3c7;color:#92400e">席発持ち帰り</span>'
                if o.get("is_takeout_from_table")
                else '<span class="badge" style="background:#dbeafe;color:#1e40af">店内飲食</span>'
            )
            items_txt = ", ".join(
                f"{it.get('product_name', it.get('product_id'))}×{it.get('quantity')}"
                for it in o.get("items", [])
            )
            paid_tag = (
                '<span class="badge" style="background:#dcfce7;color:#166534">会計済</span>'
                if o.get("paid")
                else '<span class="badge" style="background:#fee2e2;color:#991b1b">未会計</span>'
            )
            rows.append(
                f"<tr><td><code>{escape(str(o.get('order_id', '-')))}</code></td>"
                f"<td>{escape(str(o.get('table_id', '-')))}</td>"
                f"<td>{take_tag}</td>"
                f"<td>{escape(items_txt)}</td>"
                f"<td><strong>¥{int(o.get('total_amount', 0)):,}</strong></td>"
                f'<td><span class="badge" style="background:{bg};color:{fg}">{escape(label)}</span></td>'
                f"<td>{paid_tag}</td></tr>"
            )
        rows_html = "".join(rows) or (
            '<tr><td colspan="7" style="text-align:center;color:#64748b;padding:24px">店内注文履歴はまだありません。</td></tr>'
        )
        body = f"""
        <div class="card">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
            <h2 style="margin:0;font-size:16px">テーブル注文・調理進行ステータス（I-1 連携）</h2>
            <a class="btn btn-secondary" href="/ui/dine-in/menu">追加注文へ</a>
          </div>
          <table>
            <thead><tr><th>注文ID</th><th>席ID</th><th>区分</th><th>注文明細</th><th>小計</th><th>調理状態</th><th>会計</th></tr></thead>
            <tbody>{rows_html}</tbody>
          </table>
        </div>
        """
        return _render_shell(
            title="店内注文 › 注文履歴・調理進行状況",
            subtitle="送信した店内注文と席発持ち帰り注文の調理・提供・会計状況をリアルタイム表示します",
            active_subtab="status",
            body_html=body,
        )

    return router
