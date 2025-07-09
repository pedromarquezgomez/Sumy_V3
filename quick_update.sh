#!/bin/bash

# Script de actualización rápida para cambios menores en las bases de conocimiento
# Regenera índices y reinicia el contenedor sin reconstruir la imagen Docker
# Uso: ./quick_update.sh

echo "⚡ Actualización rápida de bases de conocimiento..."
echo "================================================"

# Variables de configuración
CONTAINER_NAME="gastronomy-fleet"
PORT=8080

# --- PASO 1: Regenerar índices vectoriales ---
echo "🧠 Regenerando índices vectoriales..."
python3 -m data_ingestion.ingest
if [ $? -ne 0 ]; then
    echo "❌ Error: Falló la regeneración de índices"
    exit 1
fi
echo "✅ Índices actualizados"

# --- PASO 2: Reiniciar contenedor para cargar nuevos índices ---
echo ""
echo "🔄 Reiniciando contenedor para aplicar cambios..."
docker restart $CONTAINER_NAME
if [ $? -ne 0 ]; then
    echo "❌ Error: No se pudo reiniciar el contenedor"
    echo "💡 Tip: Ejecuta './update_knowledge.sh' para una actualización completa"
    exit 1
fi

# --- PASO 3: Verificar funcionamiento ---
echo "⏳ Esperando que el sistema se reinicie..."
sleep 8

echo "🔍 Verificando estado..."
if curl -s http://localhost:$PORT/health > /dev/null; then
    echo "✅ ¡Actualización rápida completada!"
    echo ""
    echo "🌐 Sistema disponible en: http://localhost:$PORT"
    echo "🔄 Para actualización completa: ./update_knowledge.sh"
else
    echo "⚠️  El sistema está iniciándose... Puede tardar unos segundos más"
    echo "🔍 Verifica con: docker logs $CONTAINER_NAME"
fi 