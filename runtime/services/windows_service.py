import subprocess


def open_application(app_name: str) -> dict:
    try:
        subprocess.Popen([app_name], close_fds=True)
        return {"success": True, "application": app_name}
    except OSError as exc:
        return {"success": False, "application": app_name, "error": str(exc)}
