import os
import subprocess
from pathlib import Path


def open_project(project: dict) -> dict:
    path = Path(project["path"])
    if not path.is_dir():
        return {"success": False, "error": "project_path_not_found", "path": str(path)}
    launched = []
    commands = [(project.get("ide"), [project.get("ide", "code"), str(path)]),
                (project.get("terminal"), ["powershell", "-NoExit", "-Command", f"Set-Location -LiteralPath '{path}'"])]
    for name, command in commands:
        if not name:
            continue
        try:
            subprocess.Popen(command, cwd=path, close_fds=True)
            launched.append(name)
        except OSError:
            return {"success": False, "error": "launcher_not_found", "launcher": name, "launched": launched}
    return {"success": True, "project": project["name"], "path": str(path), "launched": launched}
