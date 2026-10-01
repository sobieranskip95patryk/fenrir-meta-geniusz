import os

import psutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from runtime.core.interpreter import detect_intent
from runtime.database.db import get_connection
from runtime.database.init_db import init_db

from runtime.services.powershell_service import run_ps
from runtime.services.windows_service import open_application
from runtime.core.intents import APP_MAP
from runtime.core.state import FENRIR_STATE

app = FastAPI(title="FENRIR Runtime", version="0.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["null", "http://127.0.0.1:5500", "http://localhost:5500"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
init_db()

@app.get("/")
def root():
    return {"system": "FENRIR", "brand": "META-GENIUSZ™", "status": "ONLINE"}

@app.get("/system/status")
def system_status():
    return {"cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage(os.environ.get("SystemDrive", "C:") + "\\").percent}

@app.get("/powershell/test")
def powershell_test():
    return run_ps("Get-Date")


@app.get("/open/{app}")
def open_app(app: str):
    target = APP_MAP.get(app.lower().strip())
    if not target:
        return {"success": False, "error": "unknown_app"}
    return open_application(target)


@app.get("/fenrir")
def fenrir():
    return FENRIR_STATE


@app.get("/intent/{text}")
def intent(text: str):
    return {"intent": detect_intent(text)}


@app.post("/memory")
def save_memory(data: dict):
    content = str(data.get("content", "")).strip()
    if not content:
        return {"status": "error", "error": "content_required"}
    with get_connection() as conn:
        cursor = conn.execute("INSERT INTO memories(content) VALUES(?)", (content,))
        return {"status": "saved", "id": cursor.lastrowid, "content": content}


@app.get("/memory")
def list_memory():
    with get_connection() as conn:
        rows = conn.execute("SELECT id, content FROM memories ORDER BY id").fetchall()
    return [{"id": row[0], "content": row[1]} for row in rows]
