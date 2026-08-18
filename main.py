from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes.web import router as web_router
from app.routes.api import router as api_router
from app.services.poller import start_poller

app = FastAPI(title="Mercado Livre Bridge PRO", version="2.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

init_db()
app.include_router(web_router)
app.include_router(api_router)

@app.on_event("startup")
async def startup():
    start_poller(app)

@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0 PRO"}
