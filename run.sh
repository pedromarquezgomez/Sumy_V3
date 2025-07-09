#!/bin/bash

# Script para ejecutar la flota de agentes gastronómicos con Vertex AI

echo "🚀 Iniciando flota de agentes gastronómicos..."

# Verificar que las credenciales de Google Cloud existen
if [ ! -f ~/.config/gcloud/application_default_credentials.json ]; then
    echo "❌ Error: No se encontraron las credenciales de Google Cloud."
    echo "Por favor, ejecuta: gcloud auth application-default login"
    exit 1
fi

# --- PASO AÑADIDO: Reconstruir las bases de conocimiento ---
echo "🧠 Reconstruyendo las bases de conocimiento (índices vectoriales)..."
python data_ingestion/ingest.py

# Verificar que la ingesta de datos fue exitosa
if [ $? -ne 0 ]; then
    echo "❌ Error: Falló el script de ingesta de conocimiento (ingest.py). Abortando."
    exit 1
fi
echo "✅ Bases de conocimiento actualizadas."
# ---------------------------------------------------------

# Detener contenedores existentes para evitar conflictos
echo "🛑 Deteniendo contenedores 'gastronomy-fleet' existentes..."
docker stop $(docker ps -q --filter ancestor=gastronomy-fleet) 2>/dev/null || true

# Ejecutar el nuevo contenedor
echo "🐳 Ejecutando el contenedor con la configuración de Vertex AI..."
docker run -d --name gastronomy-fleet \
  -p 8080:8080 \
  -e GOOGLE_CLOUD_PROJECT=maitre-digital \
  -e GOOGLE_CLOUD_LOCATION=us-central1 \
  -e VERTEX_AI_LOCATION=us-central1 \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  -e GOOGLE_GENAI_USE_VERTEXAI=true \
  -v ~/.config/gcloud/application_default_credentials.json:/app/credentials.json:ro \
  gastronomy-fleet

# Esperar un momento a que el contenedor se inicie completamente
echo "⏳ Esperando a que el contenedor se inicie..."
sleep 10

# Verificar que el servicio está respondiendo
echo "🔍 Verificando estado del servicio..."
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ ¡Flota de agentes funcionando correctamente!"
    echo "🌐 Interfaz web disponible en: http://localhost:8080"
    echo "🔧 Interfaz de desarrollo en: http://localhost:8080/dev-ui"
    echo "📚 Documentación de la API en: http://localhost:8080/docs"
else
    echo "❌ Error: El contenedor no está respondiendo como se esperaba."
    echo "Puedes revisar los logs para más detalles con el comando: docker logs gastronomy-fleet"
fi