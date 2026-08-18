import httpx
from urllib.parse import urlencode
from app.config import ML_CLIENT_ID, ML_CLIENT_SECRET, ML_REDIRECT_URI

AUTH_URL = "https://auth.mercadolivre.com.br/authorization"
TOKEN_URL = "https://api.mercadolibre.com/oauth/token"
API_BASE = "https://api.mercadolibre.com"

def get_auth_url():
    params = {
        "response_type": "code",
        "client_id": ML_CLIENT_ID,
        "redirect_uri": ML_REDIRECT_URI
    }
    return f"{AUTH_URL}?{urlencode(params)}"

async def exchange_code_for_token(code: str):
    async with httpx.AsyncClient() as client:
        data = {
            "grant_type": "authorization_code",
            "client_id": ML_CLIENT_ID,
            "client_secret": ML_CLIENT_SECRET,
            "code": code,
            "redirect_uri": ML_REDIRECT_URI
        }
        r = await client.post(TOKEN_URL, data=data, headers={"Accept": "application/json"})
        r.raise_for_status()
        return r.json()

async def refresh_access_token(refresh_token: str):
    async with httpx.AsyncClient() as client:
        data = {
            "grant_type": "refresh_token",
            "client_id": ML_CLIENT_ID,
            "client_secret": ML_CLIENT_SECRET,
            "refresh_token": refresh_token
        }
        r = await client.post(TOKEN_URL, data=data, headers={"Accept": "application/json"})
        r.raise_for_status()
        return r.json()

async def get_user_id(access_token: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_BASE}/users/me", headers={"Authorization": f"Bearer {access_token}"})
        r.raise_for_status()
        return r.json()["id"]

async def fetch_recent_orders(access_token: str, seller_id: str):
    async with httpx.AsyncClient(timeout=30) as client:
        # Pega pedidos pagos dos ultimos 30 dias
        url = f"{API_BASE}/orders/search?seller={seller_id}&order.status=paid&sort=date_desc&limit=20"
        r = await client.get(url, headers={"Authorization": f"Bearer {access_token}"})
        r.raise_for_status()
        data = r.json()
        orders = []
        for o in data.get("results", []):
            try:
                item = o["order_items"][0]["item"] if o.get("order_items") else {}
                buyer = o.get("buyer", {})
                title = item.get("title", "Produto sem titulo")
                qty = o["order_items"][0].get("quantity", 1) if o.get("order_items") else 1
                orders.append({
                    "order_id": str(o["id"]),
                    "title": title,
                    "quantity": qty,
                    "buyer_name": f"{buyer.get('first_name','')} {buyer.get('last_name','')}".strip() or buyer.get('nickname','Cliente'),
                    "total": o.get("total_amount", 0),
                    "date_created": o.get("date_created", ""),
                    "status": o.get("status", ""),
                    "pack_id": o.get("pack_id"),
                    "buyer": buyer,
                    "raw": o
                })
            except Exception as e:
                print(f"Erro parse order {o.get('id')}: {e}")
        return orders
