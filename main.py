# main.py
import os
from google.adk.cli.fast_api import get_fast_api_app
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

AGENTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agents")

app = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    web=True
)

@app.get("/health")
def health_check():
    return {"status": "ok"} 