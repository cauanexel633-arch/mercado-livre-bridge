import os
from dotenv import load_dotenv
load_dotenv()

def required(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Variável obrigatória não configurada: {name}")
    return v

def optional(name: str, default: str = "") -> str:
    return os.getenv(name, default)

BRIDGE_API_KEY = required("BRIDGE_API_KEY")
SESSION_SECRET = required("SESSION_SECRET")

ML_CLIENT_ID = optional("ML_CLIENT_ID", "")
ML_CLIENT_SECRET = optional("ML_CLIENT_SECRET", "")
ML_REDIRECT_URI = optional("ML_REDIRECT_URI", "")

DATABASE_PATH = optional("DATABASE_PATH", "data/bridge.db")
POLL_INTERVAL_SECONDS = int(optional("POLL_INTERVAL_SECONDS", "30"))
ML_SITE_ID = optional("ML_SITE_ID", "MLB")
