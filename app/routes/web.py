from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.database import get_token, get_all_orders
from app.config import ML_CLIENT_ID, ML_REDIRECT_URI
from app.services.mercado_livre import get_auth_url

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def home():
    token = get_token()
    orders = get_all_orders(5)
    status = "CONECTADO 🟢" if token else "DESCONECTADO 🔴 - Precisa conectar no /oauth/start"
    html_orders = "".join([f"<li>{o['order_id']} - {o['title']} - {o['buyer_name']} - R${o['total']}</li>" for o in orders])
    auth_url = get_auth_url() if ML_CLIENT_ID else "#"
    return f"""
    <html><head><title>Bridge PRO</title>
    <style>body{{font-family:Arial;padding:30px;background:#0a0a0a;color:#00ff88}}a{{color:#00ff88}} .card{{border:1px solid #333;padding:20px;border-radius:10px;margin:10px 0;background:#111}}</style>
    </head><body>
    <h1>🚀 MERCADO LIVRE BRIDGE PRO - ONLINE</h1>
    <div class="card"><b>Status ML:</b> {status}<br>
    <b>Client ID:</b> {ML_CLIENT_ID[:6]+'...' if ML_CLIENT_ID else 'NAO CONFIGURADO'}<br>
    <b>Redirect:</b> {ML_REDIRECT_URI}</div>
    <div class="card"><h3>Conectar Conta</h3>
    <a href="/oauth/start" style="padding:10px 20px;background:#00ff88;color:#000;text-decoration:none;border-radius:5px;">CONECTAR MERCADO LIVRE</a>
    <br><br><small>Auth URL: {auth_url}</small></div>
    <div class="card"><h3>Últimas vendas cacheadas ({len(orders)})</h3><ul>{html_orders or '<li>Nenhuma ainda</li>'}</ul></div>
    <div class="card"><h3>Endpoints para Monitor Local</h3>
    <code>GET /api/new-orders (Header: X-Bridge-Key: SUA_BRIDGE_API_KEY)<br>POST /api/ack {{"order_ids":[...]}}<br>GET /health</code></div>
    </body></html>
    """
