from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from app.config import BRIDGE_API_KEY, ML_CLIENT_ID
from app.services.mercado_livre import get_auth_url_with_pkce, exchange_code_for_token, get_user_id
from app.database import save_token, get_new_orders, ack_orders, get_all_orders
import httpx

router = APIRouter()

def check_key(x_bridge_key: str = Header(None), authorization: str = Header(None)):
    key = x_bridge_key or (authorization.replace("Bearer ", "") if authorization else "")
    if key!= BRIDGE_API_KEY:
        raise HTTPException(status_code=401, detail="BRIDGE_API_KEY invalida")
    return True

@router.get("/oauth/start")
def oauth_start():
    if not ML_CLIENT_ID:
        return JSONResponse({"erro": "ML_CLIENT_ID não configurado"}, status_code=500)
    url, state = get_auth_url_with_pkce()
    return RedirectResponse(url)

@router.get("/oauth/callback")
async def oauth_callback(code: str = None, state: str = None, error: str = None):
    if error:
        return JSONResponse({"erro": error}, status_code=400)
    if not code:
        return JSONResponse({"erro": "sem code"}, status_code=400)
    try:
        token_data = await exchange_code_for_token(code, state)
        user_id = await get_user_id(token_data["access_token"])
        save_token(token_data["access_token"], token_data["refresh_token"], token_data["expires_in"], user_id)
        return JSONResponse({"ok": True, "user_id": user_id, "msg": "Conectado com sucesso! Agora pode fechar."})
    except httpx.HTTPStatusError as e:
        try:
            detalhe = e.response.json()
        except:
            detalhe = e.response.text
        return JSONResponse({"erro": f"ML retornou {e.response.status_code}", "detalhe": detalhe}, status_code=500)
    except Exception as e:
        return JSONResponse({"erro": str(e)}, status_code=500)

@router.get("/api/new-orders")
def api_new_orders(x_bridge_key: str = Header(None), authorization: str = Header(None)):
    check_key(x_bridge_key, authorization)
    orders = get_new_orders()
    return {"orders": [{"order_id": o['order_id'],"title": o['title'],"quantity": o['quantity'],"buyer_name": o['buyer_name'],"total": o['total'],"date_created": o['date_created'],"status": o['status']} for o in orders], "count": len(orders)}

@router.post("/api/ack")
def api_ack(payload: dict, x_bridge_key: str = Header(None), authorization: str = Header(None)):
    check_key(x_bridge_key, authorization)
    ids = payload.get("order_ids", [])
    if ids:
        ack_orders(ids)
    return {"ok": True, "acked": len(ids)}

@router.get("/api/all-orders")
def api_all(x_bridge_key: str = Header(None), authorization: str = Header(None)):
    check_key(x_bridge_key, authorization)
    return {"orders": get_all_orders(50)}

@router.post("/webhooks/mercadolibre")
async def webhook_ml(request: Request):
    try:
        data = await request.json()
        print(f"[WEBHOOK] {data}")
    except:
        pass
    return {"ok": True}