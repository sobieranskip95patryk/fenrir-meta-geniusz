import shutil
import subprocess

def run_ps(command: str) -> dict:
    executable = shutil.which("pwsh") or shutil.which("powershell")
    if not executable:
        return {"stdout": "", "stderr": "PowerShell nie jest dostępny w PATH.", "returncode": -1}
    try:
        result = subprocess.run([executable, "-NoProfile", "-NonInteractive", "-Command", command],
                                capture_output=True, text=True, encoding="utf-8", errors="replace",
                                timeout=30, check=False)
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Polecenie PowerShell przekroczyło limit 30 sekund.", "returncode": -1}
    return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
