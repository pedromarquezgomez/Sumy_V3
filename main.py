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

# Montar el directorio 'public' para servir archivos estáticos
app.mount("/public", StaticFiles(directory="public"), name="public")

# Middleware para inyectar el script de logging en las respuestas HTML
class InjectTraceLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if isinstance(response, HTMLResponse):
            # Leer el contenido de la respuesta HTML
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # Convertir a string, inyectar el script y volver a bytes
            html_content = response_body.decode('utf-8')
            script_tag = '<script src="/public/trace_logger.js"></script>'
            # Inyectar el script justo antes del cierre de la etiqueta </body>
            if '</body>' in html_content:
                html_content = html_content.replace('</body>', f'{script_tag}</body>')
            else:
                html_content += script_tag # Si no hay </body>, añadir al final
            
            return HTMLResponse(content=html_content, status_code=response.status_code)
        return response

app.add_middleware(InjectTraceLoggerMiddleware)

@app.get("/health")
def health_check():
    return {"status": "ok"} 