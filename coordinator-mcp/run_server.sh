#!/bin/bash

# Script launcher para el servidor MCP del Coordinador
cd /Users/pedro/Sumy_V3/coordinator-mcp

# Activar entorno virtual
source .venv/bin/activate

# Ejecutar el servidor del coordinador con la URL de la API
# Puedes cambiar la URL aquí si tu API está en otro puerto/host
exec python3 coordinator_server.py http://localhost:8080