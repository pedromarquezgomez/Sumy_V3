# 🔄 Guía de Actualización de Bases de Conocimiento

Esta guía explica cómo actualizar el sistema cuando modificas el contenido de las bases de conocimiento.

## 📁 Estructura de Bases de Conocimiento

```
knowledge_base/
├── 🍷 enology/
│   ├── unstructured/     # Archivos de texto (.txt, .md, etc.)
│   └── structured/       # Archivos JSON estructurados
├── 🍳 culinary/          # Archivos de recetas y técnicas culinarias
└── 🥗 nutrition/         # Archivos de información nutricional
```

## 🛠️ Scripts de Actualización Disponibles

### 1. `./update_knowledge.sh` - **Actualización Completa**

**Cuándo usar:** 
- Cuando añades archivos nuevos
- Cambios importantes en el contenido
- Primera instalación
- Problemas con el contenedor

**Qué hace:**
1. ✅ Verifica credenciales de Google Cloud
2. 📊 Muestra estadísticas del contenido actual
3. 🧠 Regenera todos los índices vectoriales
4. 🛑 Detiene y elimina el contenedor actual
5. 🏗️ Reconstruye la imagen Docker con nuevos índices
6. 🚀 Ejecuta el nuevo contenedor
7. 🧪 Verifica que todo funcione correctamente

**Uso:**
```bash
./update_knowledge.sh
```

### 2. `./quick_update.sh` - **Actualización Rápida**

**Cuándo usar:**
- Modificaciones menores en archivos existentes
- Correcciones de contenido
- Cuando el contenedor ya funciona bien

**Qué hace:**
1. 🧠 Regenera índices vectoriales
2. 🔄 Reinicia el contenedor existente
3. 🔍 Verifica funcionamiento

**Uso:**
```bash
./quick_update.sh
```

## 📋 Flujo de Trabajo Recomendado

### Para Añadir Nuevo Contenido:

1. **Añade tus archivos** en la carpeta correcta:
   ```bash
   # Ejemplo: nuevo archivo de vinos
   echo "Contenido sobre Rioja..." > knowledge_base/enology/unstructured/vinos_rioja.txt
   
   # Ejemplo: nueva receta
   echo "Receta de gazpacho..." > knowledge_base/culinary/gazpacho.txt
   ```

2. **Ejecuta actualización completa:**
   ```bash
   ./update_knowledge.sh
   ```

### Para Modificar Contenido Existente:

1. **Edita el archivo** que necesites modificar

2. **Ejecuta actualización rápida:**
   ```bash
   ./quick_update.sh
   ```

## 🆘 Resolución de Problemas

### ❌ Error: "No se encontraron credenciales de Google Cloud"
```bash
gcloud auth application-default login
```

### ❌ Error en la regeneración de índices
- Verifica que los archivos estén en el formato correcto
- Archivos de texto: `.txt`, `.md`
- Archivos estructurados: `.json` (solo en `enology/structured/`)

### ❌ El contenedor no responde
```bash
# Ver logs del contenedor
docker logs gastronomy-fleet

# Si persiste el problema, usa actualización completa
./update_knowledge.sh
```

### ❌ Docker no disponible
- Asegúrate de que Docker Desktop esté ejecutándose
- Verifica permisos de Docker

## 📊 Verificar Estado del Sistema

```bash
# Estado del contenedor
docker ps | grep gastronomy-fleet

# Estado de la aplicación
curl http://localhost:8080/health

# Ver logs en tiempo real
docker logs -f gastronomy-fleet
```

## 🎯 Ejemplos de Uso

### Añadir nueva información de vinos:
```bash
# 1. Crear archivo
cat > knowledge_base/enology/unstructured/vinos_blancos.txt << EOF
Los vinos blancos son ideales para pescados y mariscos.
Temperatura de servicio: 8-12°C.
Varietales principales: Chardonnay, Sauvignon Blanc, Albariño.
EOF

# 2. Actualizar sistema
./update_knowledge.sh
```

### Corregir una receta existente:
```bash
# 1. Editar archivo
nano knowledge_base/culinary/receta_paella.txt

# 2. Actualizar rápidamente
./quick_update.sh
```

## 🌐 Interfaces Disponibles

Después de cualquier actualización, el sistema estará disponible en:

- **Web UI**: http://localhost:8080
- **Dev UI**: http://localhost:8080/dev-ui/
- **API Docs**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health

---

💡 **Tip**: Usa `./quick_update.sh` para cambios menores y `./update_knowledge.sh` para cambios importantes o cuando tengas dudas. 