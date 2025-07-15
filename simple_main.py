# simple_main.py - Servidor FastAPI sin ADK Web UI
import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Importar nuestro runner
from adk_runner import StatefulGastronomyRunner

# Crear aplicación FastAPI simple
app = FastAPI(title="Sumy_V3 ADK Gastronomy API", version="2.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Endpoints
@app.get("/", response_class=HTMLResponse)
def root():
    """Interfaz web interactiva"""
    with open("web_ui.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "system": "Sumy_V3_ADK_Simple",
        "coordinator": gastronomy_runner.runner.agent.name,
        "sub_agents": len(gastronomy_runner.runner.agent.sub_agents),
        "active_sessions": len(gastronomy_runner.active_sessions)
    }

@app.post("/gastronomy/query", response_model=GastronomyResponse)
async def gastronomy_query(query_data: GastronomyQuery):
    """
    Endpoint principal para consultas gastronómicas usando la arquitectura ADK simple.
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
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando consulta gastronómica: {str(e)}"
        )

@app.get("/gastronomy/sessions")
async def list_sessions():
    """Lista todas las sesiones activas"""
    return await gastronomy_runner.list_active_sessions()

@app.get("/gastronomy/test")
async def test_system():
    """Endpoint de prueba para validar el sistema"""
    try:
        # Ejecutar una consulta de prueba
        test_query = "¿Puedes recomendarme un vino tinto?"
        events = await gastronomy_runner.run_query(
            query=test_query,
            user_id="test_user",
            session_id="test_session"
        )
        
        response_text = " ".join([str(event.content) for event in events if hasattr(event, 'content') and event.content])
        
        return {
            "test_query": test_query,
            "response": response_text,
            "events_count": len(events),
            "system_status": "operational"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "system_status": "error"
        }

@app.get("/info")
def system_info():
    """Información sobre el sistema ADK"""
    return {
        "system": "Sumy_V3 con Google ADK (Simple)",
        "version": "2.0.0",
        "architecture": "Multi-Agent with Coordination",
        "coordinator": gastronomy_runner.runner.agent.name,
        "specialists": [agent.name for agent in gastronomy_runner.runner.agent.sub_agents],
        "features": [
            "Delegación inteligente",
            "Gestión de estado",
            "Sesiones persistentes",
            "Coordinación multi-agente",
            "API simple sin Web UI"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando Sumy_V3 ADK Simple Server...")
    print("🌐 Servidor disponible en: http://localhost:8000")
    print("📚 Documentación: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)