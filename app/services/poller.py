import asyncio, time
from app.database import get_token, save_token, save_order
from app.services.mercado_livre import refresh_access_token, get_user_id, fetch_recent_orders

task = None

def start_poller(app):
    global task
    if task: return
    async def loop():
        while True:
            try:
                token_row = get_token()
                if not token_row:
                    await asyncio.sleep(30)
                    continue
                # refresh se expirou
                if token_row['expires_at'] < int(time.time()):
                    try:
                        new_data = await refresh_access_token(token_row['refresh_token'])
                        save_token(new_data['access_token'], new_data['refresh_token'], new_data['expires_in'], token_row['user_id'])
                        token_row = get_token()
                        print("[POLLER] Token renovado")
                    except Exception as e:
                        print(f"[POLLER] Falha refresh: {e}")
                        await asyncio.sleep(60)
                        continue
                # busca vendas
                seller_id = token_row['user_id']
                orders = await fetch_recent_orders(token_row['access_token'], seller_id)
                for od in orders:
                    save_order(od)
                if orders:
                    print(f"[POLLER] {len(orders)} pedidos verificados")
            except Exception as e:
                print(f"[POLLER] Erro: {e}")
            await asyncio.sleep(30)
    task = asyncio.create_task(loop())
