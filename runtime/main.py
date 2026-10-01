import os

import psutil
from fastapi import FastAPI

from runtime.services.powershell_service import run_ps
from runtime.services.windows_service import open_application
from runtime.core.intents import APP_MAP
from runtime.core.state import FENRIR_STATE

app = FastAPI(title="FENRIR Runtime", version="0.1")

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
