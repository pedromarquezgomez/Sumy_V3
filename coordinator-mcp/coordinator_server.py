#!/usr/bin/env python3
"""
MCP Server para interactuar con la API de Coordinación de Agentes
Permite a un agente gestionar sesiones, ejecutar agentes, manejar artefactos y evaluaciones
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import aiohttp
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL base de la API (configurable)
API_BASE_URL = "http://localhost:8080"

# Crear servidor MCP
server = Server("coordinator-mcp")

# Sesión HTTP global
http_session = None

async def init_http_session():
    """Inicializa la sesión HTTP"""
    global http_session
    if http_session is None:
        http_session = aiohttp.ClientSession()

async def close_http_session():
    """Cierra la sesión HTTP"""
    global http_session
    if http_session:
        await http_session.close()
        http_session = None

async def make_request(method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
    """Realiza una petición HTTP a la API"""
    await init_http_session()
    
    url = urljoin(API_BASE_URL, endpoint)
    
    try:
        async with http_session.request(method, url, **kwargs) as response:
            if response.content_type == 'application/json':
                result = await response.json()
            else:
                result = {"content": await response.text(), "status_code": response.status}
            
            if response.status >= 400:
                raise Exception(f"HTTP {response.status}: {result}")
            
            return result
    except Exception as e:
        logger.error(f"Error en petición {method} {url}: {e}")
        raise

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """Lista todas las herramientas disponibles"""
    tools = [
        # === GESTIÓN DE APLICACIONES ===
        types.Tool(
            name="list_apps",
            description="Lista todas las aplicaciones disponibles",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        
        # === GESTIÓN DE SESIONES ===
        types.Tool(
            name="create_session",
            description="Crea una nueva sesión para un usuario en una app",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "user_id": {"type": "string", "description": "ID del usuario"},
                    "session_data": {"type": "object", "description": "Datos de la sesión (opcional)"}
                },
                "required": ["app_name", "user_id"]
            }
        ),
        
        types.Tool(
            name="create_session_with_id",
            description="Crea una nueva sesión con un ID específico",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "user_id": {"type": "string", "description": "ID del usuario"},
                    "session_id": {"type": "string", "description": "ID específico para la sesión"},
                    "session_data": {"type": "object", "description": "Datos de la sesión (opcional)"}
                },
                "required": ["app_name", "user_id", "session_id"]
            }
        ),
        
        types.Tool(
            name="get_session",
            description="Obtiene información de una sesión específica",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "user_id": {"type": "string", "description": "ID del usuario"},
                    "session_id": {"type": "string", "description": "ID de la sesión"}
                },
                "required": ["app_name", "user_id", "session_id"]
            }
        ),
        
        types.Tool(
            name="list_sessions",
            description="Lista todas las sesiones de un usuario",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "user_id": {"type": "string", "description": "ID del usuario"}
                },
                "required": ["app_name", "user_id"]
            }
        ),
        
        types.Tool(
            name="delete_session",
            description="Elimina una sesión específica",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "user_id": {"type": "string", "description": "ID del usuario"},
                    "session_id": {"type": "string", "description": "ID de la sesión"}
                },
                "required": ["app_name", "user_id", "session_id"]
            }
        ),
        
        # === EJECUCIÓN DE AGENTES ===
        types.Tool(
            name="run_agent",
            description="Ejecuta un agente con un mensaje",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "user_id": {"type": "string", "description": "ID del usuario"},
                    "session_id": {"type": "string", "description": "ID de la sesión"},
                    "message": {"type": "string", "description": "Mensaje para el agente"},
                    "streaming": {"type": "boolean", "description": "Si usar streaming", "default": False}
                },
                "required": ["app_name", "user_id", "session_id", "message"]
            }
        ),
        
        types.Tool(
            name="run_agent_sse",
            description="Ejecuta un agente con respuesta en streaming (SSE)",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "user_id": {"type": "string", "description": "ID del usuario"},
                    "session_id": {"type": "string", "description": "ID de la sesión"},
                    "message": {"type": "string", "description": "Mensaje para el agente"}
                },
                "required": ["app_name", "user_id", "session_id", "message"]
            }
        ),
        
        # === GESTIÓN DE ARTEFACTOS ===
        types.Tool(
            name="list_artifacts",
            description="Lista los artefactos de una sesión",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "user_id": {"type": "string", "description": "ID del usuario"},
                    "session_id": {"type": "string", "description": "ID de la sesión"}
                },
                "required": ["app_name", "user_id", "session_id"]
            }
        ),
        
        types.Tool(
            name="get_artifact",
            description="Obtiene un artefacto específico",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "user_id": {"type": "string", "description": "ID del usuario"},
                    "session_id": {"type": "string", "description": "ID de la sesión"},
                    "artifact_name": {"type": "string", "description": "Nombre del artefacto"}
                },
                "required": ["app_name", "user_id", "session_id", "artifact_name"]
            }
        ),
        
        types.Tool(
            name="delete_artifact",
            description="Elimina un artefacto",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "user_id": {"type": "string", "description": "ID del usuario"},
                    "session_id": {"type": "string", "description": "ID de la sesión"},
                    "artifact_name": {"type": "string", "description": "Nombre del artefacto"}
                },
                "required": ["app_name", "user_id", "session_id", "artifact_name"]
            }
        ),
        
        types.Tool(
            name="get_artifact_version",
            description="Obtiene una versión específica de un artefacto",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "user_id": {"type": "string", "description": "ID del usuario"},
                    "session_id": {"type": "string", "description": "ID de la sesión"},
                    "artifact_name": {"type": "string", "description": "Nombre del artefacto"},
                    "version_id": {"type": "string", "description": "ID de la versión"}
                },
                "required": ["app_name", "user_id", "session_id", "artifact_name", "version_id"]
            }
        ),
        
        types.Tool(
            name="list_artifact_versions",
            description="Lista todas las versiones de un artefacto",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "user_id": {"type": "string", "description": "ID del usuario"},
                    "session_id": {"type": "string", "description": "ID de la sesión"},
                    "artifact_name": {"type": "string", "description": "Nombre del artefacto"}
                },
                "required": ["app_name", "user_id", "session_id", "artifact_name"]
            }
        ),
        
        # === GESTIÓN DE EVALUACIONES ===
        types.Tool(
            name="create_eval_set",
            description="Crea un conjunto de evaluación",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "eval_set_id": {"type": "string", "description": "ID del conjunto de evaluación"},
                    "eval_data": {"type": "object", "description": "Datos de la evaluación"}
                },
                "required": ["app_name", "eval_set_id", "eval_data"]
            }
        ),
        
        types.Tool(
            name="list_eval_sets",
            description="Lista todos los conjuntos de evaluación de una app",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"}
                },
                "required": ["app_name"]
            }
        ),
        
        types.Tool(
            name="add_session_to_eval_set",
            description="Añade una sesión a un conjunto de evaluación",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "eval_set_id": {"type": "string", "description": "ID del conjunto de evaluación"},
                    "session_data": {"type": "object", "description": "Datos de la sesión a añadir"}
                },
                "required": ["app_name", "eval_set_id", "session_data"]
            }
        ),
        
        types.Tool(
            name="list_evals_in_eval_set",
            description="Lista todas las evaluaciones en un conjunto",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "eval_set_id": {"type": "string", "description": "ID del conjunto de evaluación"}
                },
                "required": ["app_name", "eval_set_id"]
            }
        ),
        
        types.Tool(
            name="get_eval",
            description="Obtiene una evaluación específica",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "eval_set_id": {"type": "string", "description": "ID del conjunto de evaluación"},
                    "eval_case_id": {"type": "string", "description": "ID del caso de evaluación"}
                },
                "required": ["app_name", "eval_set_id", "eval_case_id"]
            }
        ),
        
        types.Tool(
            name="update_eval",
            description="Actualiza una evaluación específica",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "eval_set_id": {"type": "string", "description": "ID del conjunto de evaluación"},
                    "eval_case_id": {"type": "string", "description": "ID del caso de evaluación"},
                    "eval_data": {"type": "object", "description": "Datos actualizados de la evaluación"}
                },
                "required": ["app_name", "eval_set_id", "eval_case_id", "eval_data"]
            }
        ),
        
        types.Tool(
            name="delete_eval",
            description="Elimina una evaluación específica",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "eval_set_id": {"type": "string", "description": "ID del conjunto de evaluación"},
                    "eval_case_id": {"type": "string", "description": "ID del caso de evaluación"}
                },
                "required": ["app_name", "eval_set_id", "eval_case_id"]
            }
        ),
        
        types.Tool(
            name="run_evaluation",
            description="Ejecuta una evaluación",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "eval_set_id": {"type": "string", "description": "ID del conjunto de evaluación"},
                    "eval_request": {"type": "object", "description": "Parámetros de la evaluación"}
                },
                "required": ["app_name", "eval_set_id", "eval_request"]
            }
        ),
        
        types.Tool(
            name="get_eval_result",
            description="Obtiene resultados de evaluación",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "eval_result_id": {"type": "string", "description": "ID del resultado de evaluación"}
                },
                "required": ["app_name", "eval_result_id"]
            }
        ),
        
        types.Tool(
            name="list_eval_results",
            description="Lista todos los resultados de evaluación de una app",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"}
                },
                "required": ["app_name"]
            }
        ),
        
        # === DEBUG Y TRAZAS ===
        types.Tool(
            name="get_trace",
            description="Obtiene la traza de un evento",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "ID del evento"}
                },
                "required": ["event_id"]
            }
        ),
        
        types.Tool(
            name="get_session_trace",
            description="Obtiene la traza de una sesión",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "ID de la sesión"}
                },
                "required": ["session_id"]
            }
        ),
        
        types.Tool(
            name="get_event_graph",
            description="Obtiene el grafo de eventos de una sesión",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nombre de la aplicación"},
                    "user_id": {"type": "string", "description": "ID del usuario"},
                    "session_id": {"type": "string", "description": "ID de la sesión"},
                    "event_id": {"type": "string", "description": "ID del evento"}
                },
                "required": ["app_name", "user_id", "session_id", "event_id"]
            }
        ),
        
        # === UTILIDADES ===
        types.Tool(
            name="health_check",
            description="Verifica el estado de salud de la API",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]
    
    return tools

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Ejecuta una herramienta específica"""
    args = arguments or {}
    
    try:
        # === GESTIÓN DE APLICACIONES ===
        if name == "list_apps":
            result = await make_request("GET", "/list-apps")
        
        # === GESTIÓN DE SESIONES ===
        elif name == "create_session":
            app_name = args["app_name"]
            user_id = args["user_id"]
            session_data = args.get("session_data", {})
            
            result = await make_request(
                "POST", 
                f"/apps/{app_name}/users/{user_id}/sessions",
                json=session_data
            )
        
        elif name == "create_session_with_id":
            app_name = args["app_name"]
            user_id = args["user_id"]
            session_id = args["session_id"]
            session_data = args.get("session_data", {})
            
            result = await make_request(
                "POST", 
                f"/apps/{app_name}/users/{user_id}/sessions/{session_id}",
                json=session_data
            )
        
        elif name == "get_session":
            app_name = args["app_name"]
            user_id = args["user_id"]
            session_id = args["session_id"]
            
            result = await make_request(
                "GET", 
                f"/apps/{app_name}/users/{user_id}/sessions/{session_id}"
            )
        
        elif name == "list_sessions":
            app_name = args["app_name"]
            user_id = args["user_id"]
            
            result = await make_request(
                "GET", 
                f"/apps/{app_name}/users/{user_id}/sessions"
            )
        
        elif name == "delete_session":
            app_name = args["app_name"]
            user_id = args["user_id"]
            session_id = args["session_id"]
            
            result = await make_request(
                "DELETE", 
                f"/apps/{app_name}/users/{user_id}/sessions/{session_id}"
            )
        
        # === EJECUCIÓN DE AGENTES ===
        elif name == "run_agent":
            payload = {
                "appName": args["app_name"],
                "userId": args["user_id"],
                "sessionId": args["session_id"],
                "newMessage": {
                    "parts": [{"text": args["message"]}],
                    "role": "user"
                },
                "streaming": args.get("streaming", False)
            }
            
            result = await make_request("POST", "/run", json=payload)
        
        elif name == "run_agent_sse":
            payload = {
                "appName": args["app_name"],
                "userId": args["user_id"],
                "sessionId": args["session_id"],
                "newMessage": {
                    "parts": [{"text": args["message"]}],
                    "role": "user"
                },
                "streaming": True
            }
            
            result = await make_request("POST", "/run_sse", json=payload)
        
        # === GESTIÓN DE ARTEFACTOS ===
        elif name == "list_artifacts":
            app_name = args["app_name"]
            user_id = args["user_id"]
            session_id = args["session_id"]
            
            result = await make_request(
                "GET", 
                f"/apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts"
            )
        
        elif name == "get_artifact":
            app_name = args["app_name"]
            user_id = args["user_id"]
            session_id = args["session_id"]
            artifact_name = args["artifact_name"]
            
            result = await make_request(
                "GET", 
                f"/apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}"
            )
        
        elif name == "delete_artifact":
            app_name = args["app_name"]
            user_id = args["user_id"]
            session_id = args["session_id"]
            artifact_name = args["artifact_name"]
            
            result = await make_request(
                "DELETE", 
                f"/apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}"
            )
        
        elif name == "get_artifact_version":
            app_name = args["app_name"]
            user_id = args["user_id"]
            session_id = args["session_id"]
            artifact_name = args["artifact_name"]
            version_id = args["version_id"]
            
            result = await make_request(
                "GET", 
                f"/apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}/versions/{version_id}"
            )
        
        elif name == "list_artifact_versions":
            app_name = args["app_name"]
            user_id = args["user_id"]
            session_id = args["session_id"]
            artifact_name = args["artifact_name"]
            
            result = await make_request(
                "GET", 
                f"/apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}/versions"
            )
        
        # === GESTIÓN DE EVALUACIONES ===
        elif name == "create_eval_set":
            app_name = args["app_name"]
            eval_set_id = args["eval_set_id"]
            eval_data = args["eval_data"]
            
            result = await make_request(
                "POST", 
                f"/apps/{app_name}/eval_sets/{eval_set_id}",
                json=eval_data
            )
        
        elif name == "list_eval_sets":
            app_name = args["app_name"]
            
            result = await make_request(
                "GET", 
                f"/apps/{app_name}/eval_sets"
            )
        
        elif name == "add_session_to_eval_set":
            app_name = args["app_name"]
            eval_set_id = args["eval_set_id"]
            session_data = args["session_data"]
            
            result = await make_request(
                "POST", 
                f"/apps/{app_name}/eval_sets/{eval_set_id}/add_session",
                json=session_data
            )
        
        elif name == "list_evals_in_eval_set":
            app_name = args["app_name"]
            eval_set_id = args["eval_set_id"]
            
            result = await make_request(
                "GET", 
                f"/apps/{app_name}/eval_sets/{eval_set_id}/evals"
            )
        
        elif name == "get_eval":
            app_name = args["app_name"]
            eval_set_id = args["eval_set_id"]
            eval_case_id = args["eval_case_id"]
            
            result = await make_request(
                "GET", 
                f"/apps/{app_name}/eval_sets/{eval_set_id}/evals/{eval_case_id}"
            )
        
        elif name == "update_eval":
            app_name = args["app_name"]
            eval_set_id = args["eval_set_id"]
            eval_case_id = args["eval_case_id"]
            eval_data = args["eval_data"]
            
            result = await make_request(
                "PUT", 
                f"/apps/{app_name}/eval_sets/{eval_set_id}/evals/{eval_case_id}",
                json=eval_data
            )
        
        elif name == "delete_eval":
            app_name = args["app_name"]
            eval_set_id = args["eval_set_id"]
            eval_case_id = args["eval_case_id"]
            
            result = await make_request(
                "DELETE", 
                f"/apps/{app_name}/eval_sets/{eval_set_id}/evals/{eval_case_id}"
            )
        
        elif name == "run_evaluation":
            app_name = args["app_name"]
            eval_set_id = args["eval_set_id"]
            eval_request = args["eval_request"]
            
            result = await make_request(
                "POST", 
                f"/apps/{app_name}/eval_sets/{eval_set_id}/run_eval",
                json=eval_request
            )
        
        elif name == "get_eval_result":
            app_name = args["app_name"]
            eval_result_id = args["eval_result_id"]
            
            result = await make_request(
                "GET", 
                f"/apps/{app_name}/eval_results/{eval_result_id}"
            )
        
        elif name == "list_eval_results":
            app_name = args["app_name"]
            
            result = await make_request(
                "GET", 
                f"/apps/{app_name}/eval_results"
            )
        
        # === DEBUG Y TRAZAS ===
        elif name == "get_trace":
            event_id = args["event_id"]
            result = await make_request("GET", f"/debug/trace/{event_id}")
        
        elif name == "get_session_trace":
            session_id = args["session_id"]
            result = await make_request("GET", f"/debug/trace/session/{session_id}")
        
        elif name == "get_event_graph":
            app_name = args["app_name"]
            user_id = args["user_id"]
            session_id = args["session_id"]
            event_id = args["event_id"]
            
            result = await make_request(
                "GET", 
                f"/apps/{app_name}/users/{user_id}/sessions/{session_id}/events/{event_id}/graph"
            )
        
        # === UTILIDADES ===
        elif name == "health_check":
            result = await make_request("GET", "/health")
        
        else:
            raise ValueError(f"Herramienta desconocida: {name}")
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        error_msg = f"Error ejecutando {name}: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(type="text", text=error_msg)]

async def main():
    """Función principal del servidor MCP"""
    global API_BASE_URL
    
    # Permitir configurar la URL base desde argumentos
    if len(sys.argv) > 1:
        API_BASE_URL = sys.argv[1].rstrip('/')
    
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="coordinator-mcp",
                    server_version="2.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    finally:
        await close_http_session()

if __name__ == "__main__":
    asyncio.run(main())