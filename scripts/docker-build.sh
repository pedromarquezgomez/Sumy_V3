#!/bin/bash

# Script para construir y ejecutar el contenedor Docker de Sumy_V3 ADK

echo "🚀 Construyendo imagen Docker de Sumy_V3 ADK..."

# Variables
IMAGE_NAME="sumy_v3_adk"
CONTAINER_NAME="sumy_v3_adk_container"
PORT=8080

# Detener contenedor existente si está corriendo
echo "🛑 Deteniendo contenedor existente..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Construir la imagen
echo "🏗️  Construyendo imagen Docker..."
docker build -t $IMAGE_NAME .

if [ $? -ne 0 ]; then
    echo "❌ Error construyendo la imagen Docker"
    exit 1
fi

echo "✅ Imagen Docker construida exitosamente"

# Ejecutar el contenedor
echo "🐳 Ejecutando contenedor..."
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:8080 \
    -e GOOGLE_CLOUD_PROJECT=maitre-digital \
    -e GOOGLE_CLOUD_LOCATION=us-central1 \
    -e GOOGLE_GENAI_USE_VERTEXAI=true \
    -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
    -v ~/.config/gcloud/application_default_credentials.json:/app/credentials.json:ro \
    $IMAGE_NAME

if [ $? -ne 0 ]; then
    echo "❌ Error ejecutando el contenedor"
    exit 1
fi

echo "✅ Contenedor ejecutándose exitosamente"

# Esperar a que el servicio esté listo
echo "⏳ Esperando a que el servicio esté listo..."
sleep 10

# Verificar que el servicio está funcionando
echo "🔍 Verificando estado del servicio..."
if curl -s http://localhost:$PORT/health > /dev/null; then
    echo "✅ ¡Servicio funcionando correctamente!"
    echo ""
    echo "🌐 Interfaces disponibles:"
    echo "   - API: http://localhost:$PORT"
    echo "   - Documentación: http://localhost:$PORT/docs"
    echo "   - Health Check: http://localhost:$PORT/health"
    echo "   - System Info: http://localhost:$PORT/info"
    echo ""
    echo "🔧 Comandos útiles:"
    echo "   - Ver logs: docker logs $CONTAINER_NAME"
    echo "   - Detener: docker stop $CONTAINER_NAME"
    echo "   - Reiniciar: docker restart $CONTAINER_NAME"
else
    echo "❌ El servicio no está respondiendo"
    echo "📋 Ver logs con: docker logs $CONTAINER_NAME"
fi