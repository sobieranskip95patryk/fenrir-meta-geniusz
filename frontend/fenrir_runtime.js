const FENRIR_API =
  "http://127.0.0.1:8000";

async function openApplication(app) {
    const response = await fetch(`${FENRIR_API}/open/${encodeURIComponent(app)}`);
    if (!response.ok) throw new Error(`Runtime API: HTTP ${response.status}`);
    return response.json();
}

async function getSystemStatus() {

    const response = await fetch(`${FENRIR_API}/system/status`);
    if (!response.ok) throw new Error(`Runtime API: HTTP ${response.status}`);
    return response.json();
}

async function getFenrirState() {

    const response = await fetch(`${FENRIR_API}/fenrir`);
    if (!response.ok) throw new Error(`Runtime API: HTTP ${response.status}`);
    return response.json();
}
