#!/bin/bash

# Quick rebuild - Solo reconstruye las capas necesarias
echo "⚡ Quick rebuild - Aprovechando cache de Docker..."

CONTAINER_NAME="gastronomy-fleet"
IMAGE_NAME="gastronomy-fleet"
PORT=8080

# Detener contenedor actual
echo "🛑 Deteniendo contenedor actual..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Build con cache optimizado
echo "🏗️  Rebuilding solo capas modificadas..."
docker build --cache-from $IMAGE_NAME -t $IMAGE_NAME -f Dockerfile.dev .

if [ $? -ne 0 ]; then
    echo "❌ Error en el build"
    exit 1
fi

# Ejecutar nuevo contenedor
echo "🐳 Ejecutando contenedor actualizado..."
docker run -d --name $CONTAINER_NAME \
  -p $PORT:8080 \
  -e GOOGLE_CLOUD_PROJECT=maitre-digital \
  -e GOOGLE_CLOUD_LOCATION=us-central1 \
  -e VERTEX_AI_LOCATION=us-central1 \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  -e GOOGLE_GENAI_USE_VERTEXAI=true \
  -v ~/.config/gcloud/application_default_credentials.json:/app/credentials.json:ro \
  $IMAGE_NAME

echo "⏳ Esperando inicio..."
sleep 8

if curl -s http://localhost:$PORT/health > /dev/null; then
    echo "✅ ¡Quick rebuild completado!"
    echo "🌐 Disponible en: http://localhost:$PORT"
else
    echo "❌ Error en el inicio"
    echo "Ver logs: docker logs $CONTAINER_NAME"
fi 