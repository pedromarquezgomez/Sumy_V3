#!/bin/bash

# Script para ejecutar la flota de agentes gastronómicos con Vertex AI

echo "🚀 Iniciando flota de agentes gastronómicos..."

# Verificar que las credenciales existen
if [ ! -f ~/.config/gcloud/application_default_credentials.json ]; then
    echo "❌ Error: No se encontraron las credenciales de Google Cloud"
    echo "Ejecuta: gcloud auth application-default login"
    exit 1
fi

# Detener contenedores existentes
echo "🛑 Deteniendo contenedores existentes..."
docker stop $(docker ps -q --filter ancestor=gastronomy-fleet) 2>/dev/null || true

# Ejecutar el contenedor
echo "🐳 Ejecutando contenedor con Vertex AI..."
docker run -d --name gastronomy-fleet \
  -p 8080:8080 \
  -e GOOGLE_CLOUD_PROJECT=maitre-digital \
  -e GOOGLE_CLOUD_LOCATION=us-central1 \
  -e VERTEX_AI_LOCATION=us-central1 \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  -e GOOGLE_GENAI_USE_VERTEXAI=true \
  -v ~/.config/gcloud/application_default_credentials.json:/app/credentials.json \
  gastronomy-fleet

# Esperar a que el contenedor se inicie
echo "⏳ Esperando a que el contenedor se inicie..."
sleep 10

# Verificar que esté funcionando
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ ¡Flota de agentes funcionando correctamente!"
    echo "🌐 Interfaz web: http://localhost:8080"
    echo "🔧 Interfaz de desarrollo: http://localhost:8080/dev-ui"
    echo "📚 Documentación API: http://localhost:8080/docs"
else
    echo "❌ Error: El contenedor no está respondiendo"
    echo "Revisa los logs con: docker logs gastronomy-fleet"
fi 