#!/bin/bash

# Ir al directorio del proyecto
cd /Users/pedro/Sumy_V3/coordinator-mcp

# Crear entorno virtual si no existe
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias
pip install mcp

# Hacer ejecutable el launcher
chmod +x run_server.sh

# Probar que el servidor se puede importar
echo "Probando el servidor..."
python3 -c "
import sys
import os
sys.path.insert(0, '.')
try:
    import server
    print('✓ Servidor se puede importar correctamente')
except Exception as e:
    print(f'✗ Error: {e}')
"

echo ""
echo "Configuración para Claude Desktop:"
echo "Agrega esto a ~/Library/Application Support/Claude/claude_desktop_config.json:"
echo ""
echo "{"
echo "  \"mcpServers\": {"
echo "    \"hola-mundo-server\": {"
echo "      \"command\": \"/Users/pedro/Sumy_V3/coordinator-mcp/run_server.sh\","
echo "      \"args\": []"
echo "    }"
echo "  }"
echo "}"