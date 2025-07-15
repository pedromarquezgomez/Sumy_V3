# hybrid_main.py - Servidor con ADK UI y fallback
import os
import asyncio
import signal
from google.adk.cli.fast_api import get_fast_api_app
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import threading
import time

# Importar el runner ADK
from adk_runner import StatefulGastronomyRunner
from rate_limit_handler import rate_handler

# Configuración de directorios
AGENTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agents")

# Flag para controlar el timeout
startup_completed = False
startup_timeout = 60  # 60 segundos timeout

def timeout_handler():
    """Maneja el timeout de startup"""
    global startup_completed
    time.sleep(startup_timeout)
    if not startup_completed:
        print("⚠️  ADK UI startup timeout - el sistema se está colgando")
        os._exit(1)

# Iniciar thread de timeout
timeout_thread = threading.Thread(target=timeout_handler, daemon=True)
timeout_thread.start()

try:
    print("🚀 Iniciando ADK UI - esto puede tomar un momento...")
    
    # Crear la aplicación FastAPI base de ADK con timeout
    app = get_fast_api_app(
        agents_dir=AGENTS_DIR,
        web=True
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Montar archivos estáticos
    try:
        app.mount("/static", StaticFiles(directory="static"), name="static")
    except:
        pass  # No pasa nada si no existe el directorio
    
    # Inicializar el runner gastronómico
    gastronomy_runner = StatefulGastronomyRunner()
    
    # Modelos para la API
    class GastronomyQuery(BaseModel):
        query: str
        user_id: str = "guest"
        session_id: str = None
    
    class GastronomyResponse(BaseModel):
        response: str
        session_id: str
        user_id: str
        agent_used: str = "gastronomy_coordinator"
    
    # Endpoints adicionales para el sistema gastronómico
    @app.get("/health")
    def health_check():
        return {
            "status": "ok",
            "system": "Sumy_V3_ADK_Hybrid",
            "coordinator": gastronomy_runner.runner.agent.name,
            "sub_agents": len(gastronomy_runner.runner.agent.sub_agents),
            "active_sessions": len(gastronomy_runner.active_sessions),
            "adk_ui": "enabled"
        }
    
    @app.post("/gastronomy/query", response_model=GastronomyResponse)
    async def gastronomy_query(query_data: GastronomyQuery):
        """
        Endpoint principal para consultas gastronómicas usando la arquitectura ADK.
        """
        try:
            # Generar session_id si no se proporciona
            session_id = query_data.session_id or f"session_{len(gastronomy_runner.active_sessions) + 1}"
            
            # Ejecutar consulta
            events = await gastronomy_runner.run_query(
                query=query_data.query,
                user_id=query_data.user_id,
                session_id=session_id
            )
            
            # Compilar respuesta
            response_parts = []
            for event in events:
                if hasattr(event, 'content') and event.content:
                    response_parts.append(str(event.content))
            
            response_text = "\\n".join(response_parts) if response_parts else "No se pudo generar una respuesta."
            
            return GastronomyResponse(
                response=response_text,
                session_id=session_id,
                user_id=query_data.user_id,
                agent_used="gastronomy_coordinator"
            )
            
        except Exception as e:
            error_str = str(e)
            
            # Usar el manejador de rate limiting
            if rate_handler.is_rate_limit_error(error_str):
                response = rate_handler.handle_rate_limit_response(error_str)
                raise HTTPException(
                    status_code=429,
                    detail=response["message"],
                    headers={"Retry-After": "60"}
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error procesando consulta gastronómica: {error_str}"
                )
    
    @app.get("/gastronomy/sessions")
    async def list_sessions():
        """Lista todas las sesiones activas"""
        return await gastronomy_runner.list_active_sessions()
    
    @app.get("/info")
    def system_info():
        """Información sobre el sistema ADK"""
        return {
            "system": "Sumy_V3 con Google ADK (Hybrid UI)",
            "version": "2.0.0",
            "architecture": "Multi-Agent with Coordination",
            "coordinator": gastronomy_runner.runner.agent.name,
            "specialists": [agent.name for agent in gastronomy_runner.runner.agent.sub_agents],
            "features": [
                "ADK Web UI integrada",
                "Delegación inteligente",
                "Gestión de estado",
                "Sesiones persistentes",
                "Coordinación multi-agente"
            ]
        }
    
    # Marcar startup como completado
    startup_completed = True
    print("✅ ADK UI inicializada exitosamente")
    print("🌐 ADK UI disponible en: http://localhost:8080")
    print("📊 Panel de desarrollo en: http://localhost:8080/dev-ui")
    print("📚 Documentación: http://localhost:8080/docs")
    
    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8080)

except Exception as e:
    print(f"❌ Error inicializando ADK UI: {str(e)}")
    print("🔄 Cayendo al modo simple...")
    
    # Fallback: usar simple_main.py
    import subprocess
    import sys
    
    # Ejecutar simple_main.py como fallback
    os.execv(sys.executable, ['python', 'simple_main.py'])