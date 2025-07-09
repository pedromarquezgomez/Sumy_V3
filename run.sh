#!/bin/bash

# Script para ejecutar la flota de agentes gastronómicos con Vertex AI

echo "🚀 Iniciando flota de agentes gastronómicos..."

# Variables de configuración
GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT:-"maitre-digital"}
GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION:-"us-central1"}
VERTEX_AI_LOCATION=${VERTEX_AI_LOCATION:-"us-central1"}
CONTAINER_NAME="gastronomy-fleet"
IMAGE_NAME="gastronomy-fleet"
PORT=8080

# Verificar que las credenciales de Google Cloud existen
if [ ! -f ~/.config/gcloud/application_default_credentials.json ]; then
    echo "❌ Error: No se encontraron las credenciales de Google Cloud."
    echo "Por favor, ejecuta: gcloud auth application-default login"
    exit 1
fi

# --- PASO AÑADIDO: Reconstruir las bases de conocimiento ---
echo "🧠 Reconstruyendo las bases de conocimiento (índices vectoriales)..."
python3 -m data_ingestion.ingest

# Verificar que la ingesta de datos fue exitosa
if [ $? -ne 0 ]; then
    echo "❌ Error: Falló el script de ingesta de conocimiento. Abortando."
    exit 1
fi
echo "✅ Bases de conocimiento actualizadas."
# ---------------------------------------------------------

# Detener y eliminar contenedor anterior si existe
echo "🛑 Deteniendo contenedor existente (si existe)..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Construir la imagen Docker
echo "🏗️  Construyendo la imagen Docker..."
docker build -t $IMAGE_NAME .
if [ $? -ne 0 ]; then
    echo "❌ Error construyendo la imagen Docker"
    exit 1
fi

# Ejecutar el nuevo contenedor
echo "🐳 Ejecutando el contenedor con la configuración de Vertex AI..."
docker run -d --name $CONTAINER_NAME \
  -p $PORT:8080 \
  -e GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT \
  -e GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION \
  -e VERTEX_AI_LOCATION=$VERTEX_AI_LOCATION \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  -e GOOGLE_GENAI_USE_VERTEXAI=true \
  -v ~/.config/gcloud/application_default_credentials.json:/app/credentials.json:ro \
  $IMAGE_NAME

if [ $? -eq 0 ]; then
    # Esperar un momento a que el contenedor se inicie completamente
    echo "⏳ Esperando a que el contenedor se inicie..."
    sleep 10

    # Verificar que el servicio está respondiendo
    echo "🔍 Verificando estado del servicio..."
    if curl -s http://localhost:$PORT/health > /dev/null; then
        echo "✅ ¡Flota de agentes funcionando correctamente!"
        echo ""
        echo "🌐 Interfaces disponibles:"
        echo "   - Web UI: http://localhost:$PORT"
        echo "   - Dev UI: http://localhost:$PORT/dev-ui/"
        echo "   - API Docs: http://localhost:$PORT/docs"
        echo "   - Health: http://localhost:$PORT/health"
        echo ""
        echo "📊 Agentes disponibles:"
        echo "   - coordinator: Maître digital (coordinador principal)"
        echo "   - culinary: Especialista en cocina y recetas" 
        echo "   - nutrition: Especialista en nutrición y dietas"
        echo "   - sumiller: Especialista en vinos y maridajes"
        echo ""
        echo "🎯 Prueba con: ¿Qué ingredientes lleva una paella valenciana?"
        echo "🔍 Para ver logs: docker logs $CONTAINER_NAME"
        echo "🛑 Para parar: docker stop $CONTAINER_NAME"
    else
        echo "❌ Error: El contenedor no está respondiendo como se esperaba."
        echo "Puedes revisar los logs para más detalles con el comando: docker logs $CONTAINER_NAME"
        exit 1
    fi
else
    echo "❌ Error iniciando el contenedor"
    exit 1
fi