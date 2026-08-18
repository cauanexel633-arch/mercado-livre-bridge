import sqlite3, json, time
from pathlib import Path
from app.config import DATABASE_PATH

def get_conn():
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS tokens (id INTEGER PRIMARY KEY, access_token TEXT, refresh_token TEXT, expires_at INTEGER, user_id TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS orders_cache (order_id TEXT PRIMARY KEY, title TEXT, quantity INTEGER, buyer_name TEXT, total REAL, date_created TEXT, status TEXT, acknowledged INTEGER DEFAULT 0, raw_json TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS pkce (state TEXT PRIMARY KEY, verifier TEXT, created_at INTEGER)''')
    conn.commit()
    conn.close()

def save_pkce(state, verifier):
    conn=get_conn();cur=conn.cursor();cur.execute("INSERT OR REPLACE INTO pkce (state, verifier, created_at) VALUES (?,?,?)",(state, verifier, int(time.time())));conn.commit();conn.close()

def get_pkce(state):
    conn=get_conn();cur=conn.cursor();cur.execute("SELECT verifier FROM pkce WHERE state=?",(state,));row=cur.fetchone()
    if row:
        cur.execute("DELETE FROM pkce WHERE state=?",(state,));conn.commit()
    conn.close()
    return row["verifier"] if row else None

def save_token(a,r,e,u):
    conn=get_conn();cur=conn.cursor();cur.execute("DELETE FROM tokens");cur.execute("INSERT INTO tokens (access_token, refresh_token, expires_at, user_id) VALUES (?,?,?,?)",(a,r,int(time.time())+int(e)-60,str(u)));conn.commit();conn.close()
def get_token():
    conn=get_conn();cur=conn.cursor();cur.execute("SELECT * FROM tokens LIMIT 1");row=cur.fetchone();conn.close();return dict(row) if row else None
def save_order(order):
    conn=get_conn();cur=conn.cursor();cur.execute('''INSERT OR REPLACE INTO orders_cache (order_id, title, quantity, buyer_name, total, date_created, status, raw_json, acknowledged) VALUES (?,?,?,?,?,?,?,?, COALESCE((SELECT acknowledged FROM orders_cache WHERE order_id=?),0))''',(order['order_id'],order['title'],order['quantity'],order['buyer_name'],order['total'],order['date_created'],order['status'],json.dumps(order),order['order_id']));conn.commit();conn.close()
def get_new_orders():
    conn=get_conn();cur=conn.cursor();cur.execute("SELECT * FROM orders_cache WHERE acknowledged=0 ORDER BY date_created ASC");rows=[dict(r) for r in cur.fetchall()];conn.close();return rows
def ack_orders(ids):
    conn=get_conn();cur=conn.cursor();cur.executemany("UPDATE orders_cache SET acknowledged=1 WHERE order_id=?",[(i,) for i in ids]);conn.commit();conn.close()
def get_all_orders(limit=50):
    conn=get_conn();cur=conn.cursor();cur.execute("SELECT * FROM orders_cache ORDER BY date_created DESC LIMIT?", (limit,));rows=[dict(r) for r in cur.fetchall()];conn.close();return rows