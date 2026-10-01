import os

import psutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from runtime.core.interpreter import detect_intent
from runtime.database.db import get_connection
from runtime.database.init_db import init_db
from runtime.services.workspace_service import open_project

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
        cursor = conn.execute("INSERT INTO memories(category, title, content) VALUES(?,?,?)",
                              (data.get("category", "fact"), data.get("title", ""), content))
        return {"status": "saved", "id": cursor.lastrowid, "content": content}


@app.get("/memory")
def list_memory():
    with get_connection() as conn:
        rows = conn.execute("SELECT id, category, title, content, created_at, updated_at FROM memories ORDER BY id").fetchall()
    return [{"id": r[0], "category": r[1], "title": r[2], "content": r[3], "created_at": r[4], "updated_at": r[5]} for r in rows]


@app.post("/projects")
def save_project(data: dict):
    name, path = str(data.get("name", "")).strip().lower(), str(data.get("path", "")).strip()
    if not name or not path:
        return {"status": "error", "error": "name_and_path_required"}
    with get_connection() as conn:
        conn.execute("""INSERT INTO projects(name, path, ide, terminal, notes) VALUES(?,?,?,?,?)
            ON CONFLICT(name) DO UPDATE SET path=excluded.path, ide=excluded.ide,
            terminal=excluded.terminal, notes=excluded.notes""",
            (name, path, data.get("ide", "code"), data.get("terminal", "powershell"), data.get("notes", "")))
    return {"status": "saved", "name": name, "path": path}


@app.get("/projects")
def list_projects():
    with get_connection() as conn:
        rows = conn.execute("SELECT id, name, path, ide, terminal, notes FROM projects ORDER BY name").fetchall()
    return [{"id": r[0], "name": r[1], "path": r[2], "ide": r[3], "terminal": r[4], "notes": r[5]} for r in rows]


@app.post("/projects/open/{name}")
def launch_project(name: str):
    with get_connection() as conn:
        row = conn.execute("SELECT name, path, ide, terminal, notes FROM projects WHERE name = ?", (name.lower(),)).fetchone()
    if not row:
        return {"success": False, "error": "project_not_found"}
    return open_project(dict(zip(("name", "path", "ide", "terminal", "notes"), row)))


@app.get("/system/dashboard")
def system_dashboard():
    with get_connection() as conn:
        projects = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        memories = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
    skills = sum(1 for path in (os.path.join(os.path.dirname(__file__), "..", "..", "skills"),) for _ in __import__("pathlib").Path(path).rglob("*.json"))
    status = system_status()
    return {**status, "projects": projects, "skills": skills, "memories": memories}
