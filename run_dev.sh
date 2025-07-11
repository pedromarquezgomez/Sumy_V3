#!/bin/bash

# Script de desarrollo rápido - Sin rebuilds
echo "🚀 Modo desarrollo rápido - Montando código como volúmenes..."

GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT:-"maitre-digital"}
GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION:-"us-central1"}
VERTEX_AI_LOCATION=${VERTEX_AI_LOCATION:-"us-central1"}
CONTAINER_NAME="gastronomy-fleet-dev"
IMAGE_NAME="gastronomy-fleet"
PORT=8080

# Verificar credenciales
if [ ! -f ~/.config/gcloud/application_default_credentials.json ]; then
    echo "❌ Error: No se encontraron las credenciales de Google Cloud."
    echo "Por favor, ejecuta: gcloud auth application-default login"
    exit 1
fi

# Detener contenedor anterior si existe
echo "🛑 Deteniendo contenedor de desarrollo anterior (si existe)..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Verificar que existe la imagen base
if ! docker image inspect $IMAGE_NAME >/dev/null 2>&1; then
    echo "⚠️  La imagen base no existe. Construyendo por primera vez..."
    docker build -t $IMAGE_NAME .
fi

# Ejecutar contenedor con volúmenes montados (DESARROLLO RÁPIDO)
echo "🐳 Ejecutando contenedor de desarrollo con código montado..."
docker run -d --name $CONTAINER_NAME \
  -p $PORT:8080 \
  -e GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT \
  -e GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION \
  -e VERTEX_AI_LOCATION=$VERTEX_AI_LOCATION \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  -e GOOGLE_GENAI_USE_VERTEXAI=true \
  -v ~/.config/gcloud/application_default_credentials.json:/app/credentials.json:ro \
  -v "$(pwd)/agents":/app/agents \
  -v "$(pwd)/main.py":/app/main.py \
  -v "$(pwd)/adk_config.py":/app/adk_config.py \
  -v "$(pwd)/fleet.yaml":/app/fleet.yaml \
  -v "$(pwd)/indexes":/app/indexes \
  $IMAGE_NAME

if [ $? -eq 0 ]; then
    echo "⏳ Esperando a que el contenedor se inicie..."
    sleep 8

    if curl -s http://localhost:$PORT/health > /dev/null; then
        echo "✅ ¡Desarrollo rápido funcionando!"
        echo ""
        echo "🔥 MODO DESARROLLO ACTIVO:"
        echo "   - Los cambios en agents/ se reflejan INMEDIATAMENTE"
        echo "   - No necesitas rebuild para cambios de código"
        echo "   - Solo reinicia el contenedor: docker restart $CONTAINER_NAME"
        echo ""
        echo "🌐 Interfaces:"
        echo "   - Web UI: http://localhost:$PORT"
        echo "   - Dev UI: http://localhost:$PORT/dev-ui/"
        echo ""
        echo "📝 Para cambios:"
        echo "   1. Edita archivos localmente"
        echo "   2. docker restart $CONTAINER_NAME (3 segundos)"
        echo "   3. ¡Listo!"
        echo ""
        echo "🔍 Logs: docker logs -f $CONTAINER_NAME"
        echo "🛑 Parar: docker stop $CONTAINER_NAME"
    else
        echo "❌ Error: El contenedor no está respondiendo."
        echo "Logs: docker logs $CONTAINER_NAME"
        exit 1
    fi
else
    echo "❌ Error iniciando el contenedor de desarrollo"
    exit 1
fi 