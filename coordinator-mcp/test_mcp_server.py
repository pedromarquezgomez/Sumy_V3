#!/usr/bin/env python3
"""
Script para probar el servidor MCP
"""
import asyncio
import json
import sys
from coordinator_server import handle_list_tools, handle_call_tool

async def test_server():
    """Prueba el servidor MCP"""
    print("=== Probando servidor MCP ===")
    
    # Listar herramientas
    print("\n1. Listando herramientas disponibles:")
    tools = await handle_list_tools()
    print(f"Total de herramientas: {len(tools)}")
    
    for tool in tools[:5]:  # Mostrar solo las primeras 5
        print(f"- {tool.name}: {tool.description}")
    
    # Probar health check
    print("\n2. Probando health check:")
    try:
        result = await handle_call_tool("health_check", {})
        print(f"Health check: {result[0].text}")
    except Exception as e:
        print(f"Error en health check: {e}")
    
    # Probar list_apps
    print("\n3. Probando list_apps:")
    try:
        result = await handle_call_tool("list_apps", {})
        print(f"Apps disponibles: {result[0].text}")
    except Exception as e:
        print(f"Error en list_apps: {e}")
    
    print("\n=== Pruebas completadas ===")

if __name__ == "__main__":
    # Configurar la URL de la API si se proporciona
    if len(sys.argv) > 1:
        from coordinator_server import API_BASE_URL
        API_BASE_URL = sys.argv[1].rstrip('/')
    
    asyncio.run(test_server())