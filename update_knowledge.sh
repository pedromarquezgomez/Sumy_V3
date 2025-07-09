#!/bin/bash

# Script para actualizar la flota de agentes gastronómicos cuando se modifica el contenido
# Uso: ./update_knowledge.sh

echo "🔄 Actualizando flota de agentes gastronómicos..."
echo "================================================="

# Variables de configuración
GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT:-"maitre-digital"}
GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION:-"us-central1"}
VERTEX_AI_LOCATION=${VERTEX_AI_LOCATION:-"us-central1"}
CONTAINER_NAME="gastronomy-fleet"
IMAGE_NAME="gastronomy-fleet"
PORT=8080

# Función para mostrar errores y salir
error_exit() {
    echo "❌ Error: $1"
    exit 1
}

# Función para verificar credenciales
check_credentials() {
    if [ ! -f ~/.config/gcloud/application_default_credentials.json ]; then
        echo "❌ Error: No se encontraron las credenciales de Google Cloud."
        echo "Por favor, ejecuta: gcloud auth application-default login"
        exit 1
    fi
}

# Verificar credenciales al inicio
check_credentials

# --- PASO 1: Verificar cambios en la base de conocimiento ---
echo "📚 Verificando base de conocimiento..."
if [ ! -d "knowledge_base" ]; then
    error_exit "Directorio 'knowledge_base' no encontrado"
fi

# Mostrar estadísticas de archivos
echo "📊 Contenido actual:"
echo "   🍷 Enología:"
if [ -d "knowledge_base/enology/unstructured" ]; then
    echo "      - Archivos no estructurados: $(find knowledge_base/enology/unstructured -type f | wc -l)"
fi
if [ -d "knowledge_base/enology/structured" ]; then
    echo "      - Archivos estructurados: $(find knowledge_base/enology/structured -name "*.json" | wc -l)"
fi

echo "   🍳 Culinario:"
if [ -d "knowledge_base/culinary" ]; then
    echo "      - Archivos: $(find knowledge_base/culinary -type f | wc -l)"
fi

echo "   🥗 Nutrición:"
if [ -d "knowledge_base/nutrition" ]; then
    echo "      - Archivos: $(find knowledge_base/nutrition -type f | wc -l)"
fi

# --- PASO 2: Regenerar índices vectoriales ---
echo ""
echo "🧠 Regenerando índices vectoriales con nuevo contenido..."
python3 -m data_ingestion.ingest
if [ $? -ne 0 ]; then
    error_exit "Falló la regeneración de índices vectoriales"
fi
echo "✅ Índices vectoriales actualizados"

# --- PASO 3: Detener contenedor existente ---
echo ""
echo "🛑 Deteniendo contenedor existente..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true
echo "✅ Contenedor anterior eliminado"

# --- PASO 4: Reconstruir imagen Docker ---
echo ""
echo "🏗️  Reconstruyendo imagen Docker con nuevos índices..."
docker build -t $IMAGE_NAME .
if [ $? -ne 0 ]; then
    error_exit "Falló la construcción de la imagen Docker"
fi
echo "✅ Imagen Docker reconstruida"

# --- PASO 5: Ejecutar nuevo contenedor ---
echo ""
echo "🚀 Iniciando nuevo contenedor..."
docker run -d --name $CONTAINER_NAME \
  -p $PORT:8080 \
  -e GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT \
  -e GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION \
  -e VERTEX_AI_LOCATION=$VERTEX_AI_LOCATION \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  -e GOOGLE_GENAI_USE_VERTEXAI=true \
  -v ~/.config/gcloud/application_default_credentials.json:/app/credentials.json:ro \
  $IMAGE_NAME

if [ $? -ne 0 ]; then
    error_exit "Falló el inicio del contenedor"
fi

# --- PASO 6: Verificar funcionamiento ---
echo ""
echo "⏳ Esperando inicialización del sistema..."
sleep 10

echo "🔍 Verificando estado del servicio..."
if curl -s http://localhost:$PORT/health > /dev/null; then
    echo "✅ ¡Sistema actualizado y funcionando correctamente!"
    
    # --- PASO 7: Verificar contenido RAG ---
    echo ""
    echo "🧪 Verificando acceso a bases de conocimiento actualizadas..."
    
    # Test rápido del sistema RAG
    docker exec $CONTAINER_NAME python3 -c "
import sys
sys.stdout.reconfigure(encoding='utf-8')
print('Verificando bases de conocimiento...')

try:
    from agents.sumiller.agent import query_enology_kb
    result = query_enology_kb('vino')
    print('🍷 Enología: ✅ {} caracteres de contenido'.format(len(result.get('context', ''))))
except Exception as e:
    print('🍷 Enología: ❌ Error -', str(e))

try:
    from agents.culinary.agent import query_culinary_kb  
    result = query_culinary_kb('receta')
    print('🍳 Culinario: ✅ {} caracteres de contenido'.format(len(result.get('context', ''))))
except Exception as e:
    print('🍳 Culinario: ❌ Error -', str(e))

try:
    from agents.nutrition.agent import query_nutrition_kb
    result = query_nutrition_kb('nutrición')
    print('🥗 Nutrición: ✅ {} caracteres de contenido'.format(len(result.get('context', ''))))
except Exception as e:
    print('🥗 Nutrición: ❌ Error -', str(e))
    " 2>/dev/null || echo "⚠️  Verificación RAG no disponible (normal en primeros segundos)"
    
    echo ""
    echo "🎉 ¡ACTUALIZACIÓN COMPLETADA EXITOSAMENTE!"
    echo "================================================="
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
    echo "🔍 Para ver logs: docker logs $CONTAINER_NAME"
    echo "🛑 Para parar: docker stop $CONTAINER_NAME"
    echo "🔄 Para actualizar de nuevo: ./update_knowledge.sh"
    
else
    error_exit "El sistema no está respondiendo correctamente. Revisa los logs con: docker logs $CONTAINER_NAME"
fi 