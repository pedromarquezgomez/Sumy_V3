# 🍷 Sumy_V3 ADK - Sistema Gastronómico Inteligente

**Sumy_V3 ADK** es un sistema gastronómico avanzado que utiliza la arquitectura **Google ADK (Agent Development Kit)** para proporcionar recomendaciones especializadas en vinos, cocina y nutrición a través de un coordinador inteligente con múltiples agentes especializados.


## 🏗️ Arquitectura del Sistema

### **Coordinador Central**
- **Gastronomy Coordinator**: Agente principal que analiza consultas y delega a especialistas
- **Delegación inteligente**: Determina automáticamente qué especialista consultar
- **Gestión de estado**: Mantiene conversaciones y preferencias del usuario

### **Agentes Especializados**
- 🍷 **Sumiller Specialist**: Experto en vinos y maridajes
- 🍳 **Chef Specialist**: Especialista en cocina y recetas
- 🥗 **Nutrition Specialist**: Nutricionista especializado

## 📁 Estructura del Proyecto

```
Sumy_V3/
├── 📱 main.py                    # Aplicación principal con ADK UI
├── 🚀 simple_main.py             # Aplicación simple sin ADK UI
├── ⚡ hybrid_main.py             # Aplicación híbrida con fallback
├── 🏃 adk_runner.py              # Runner estateful del sistema ADK
├── ⚙️ adk_config.py              # Configuración Vertex AI
├── 🛡️ rate_limit_handler.py     # Manejador de límites de velocidad
├── 📋 requirements.txt           # Dependencias del proyecto
├── 🐳 Dockerfile                # Configuración Docker
│
├── 🤖 agents/                    # Agentes especializados
│   ├── coordinator/
│   │   └── adk_coordinator.py    # Coordinador principal
│   ├── sumiller/
│   │   └── adk_agent.py          # Agente sumiller
│   ├── culinary/
│   │   └── adk_agent.py          # Agente chef
│   ├── nutrition/
│   │   └── adk_agent.py          # Agente nutricionista
│   ├── instrucciones/            # Instrucciones de cada agente
│   │   ├── COORDINATOR_INSTRUCTION.txt
│   │   ├── CULINARY_INSTRUCTION.txt
│   │   ├── NUTRITION_INSTRUCTION.txt
│   │   └── SUMILLER_INSTRUCTION.txt
│   └── usda_api_client.py        # Cliente API USDA
│
├── 🗂️ knowledge_base/            # Bases de conocimiento
│   ├── culinary/
│   │   └── structured/
│   │       └── carta_restaurante.json
│   ├── enology/
│   │   ├── structured/
│   │   │   └── higueron_vinos.json
│   │   └── unstructured/
│   │       └── maestria_enologica.txt
│   └── nutrition/
│       └── manual_nutricion_aplicada_chefs.txt
│
├── 🔍 indexes/                   # Índices FAISS
│   ├── culinary_index/
│   ├── enology_index/
│   └── nutrition_index/
│
├── 🌐 templates/                 # Templates web
│   └── web_ui.html               # Interfaz web principal
│
├── 🔧 scripts/                   # Scripts de utilidad
│   └── docker-build.sh           # Script de construcción Docker
│
├── 🧪 tests/                     # Pruebas del sistema
│   └── simple_test_adk.py        # Pruebas de validación ADK
│
├── 📡 coordinator-mcp/           # Servidor MCP
│   ├── coordinator_server.py     # Servidor MCP principal
│   ├── requirements.txt          # Dependencias MCP
│   ├── install.sh               # Script de instalación
│   ├── run_server.sh            # Script de ejecución
│   ├── test_mcp_server.py       # Pruebas MCP
│   └── claude_desktop_config     # Configuración Claude Desktop
│
└── 📚 docs/                      # Documentación (preparado)
```

## 🚀 Instalación y Configuración

### **Prerrequisitos**
- Python 3.9+
- Google Cloud Project configurado
- Vertex AI habilitado
- Variables de entorno configuradas

### **Variables de Entorno**
```bash
export GOOGLE_CLOUD_PROJECT="tu-proyecto-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI="true"
```

### **Instalación**
```bash
# Clonar el repositorio
git clone <repository-url>
cd Sumy_V3

# Instalar dependencias
pip install -r requirements.txt

# Configurar Google Cloud
gcloud auth application-default login
gcloud config set project tu-proyecto-id
```

## 🏃 Ejecución

### **Opción 1: Aplicación Principal (con ADK UI)**
```bash
python main.py
```
- **Puerto**: 8000
- **Interfaz**: ADK UI completa
- **Documentación**: http://localhost:8000/docs

### **Opción 2: Aplicación Simple**
```bash
python simple_main.py
```
- **Puerto**: 8000
- **Interfaz**: API + Web UI básica
- **Documentación**: http://localhost:8000/docs

### **Opción 3: Aplicación Híbrida**
```bash
python hybrid_main.py
```
- **Puerto**: 8080
- **Interfaz**: ADK UI con fallback
- **Panel de desarrollo**: http://localhost:8080/dev-ui

### **Ejecución con Docker**
```bash
# Construir imagen
./scripts/docker-build.sh

# O manualmente
docker build -t sumy-v3-adk .
docker run -p 8000:8000 sumy-v3-adk
```

## 🔧 Configuración del Servidor MCP

El sistema incluye un servidor MCP para integración con Claude Desktop:

```bash
cd coordinator-mcp
./install.sh
./run_server.sh
```

## 🌐 Endpoints de la API

### **Endpoints Principales**
- `GET /` - Interfaz web interactiva
- `POST /gastronomy/query` - Consulta gastronómica principal
- `GET /health` - Estado del sistema
- `GET /info` - Información del sistema

### **Gestión de Sesiones**
- `GET /gastronomy/sessions` - Listar sesiones activas
- `GET /gastronomy/session/{session_id}/state` - Estado de sesión
- `DELETE /gastronomy/session/{session_id}` - Limpiar sesión

### **Pruebas**
- `GET /gastronomy/test` - Endpoint de prueba del sistema

## 📝 Uso del Sistema

### **Consulta Básica**
```bash
curl -X POST "http://localhost:8000/gastronomy/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "¿Puedes recomendarme un vino tinto para acompañar pasta?",
       "user_id": "usuario_123"
     }'
```

### **Ejemplos de Consultas**
- 🍷 **Vinos**: "¿Qué vino recomendarías para una cena romántica?"
- 🍳 **Cocina**: "¿Cómo puedo preparar una paella para 6 personas?"
- 🥗 **Nutrición**: "¿Cuáles son los beneficios nutricionales del salmón?"

## 🧪 Pruebas

### **Ejecutar Pruebas**
```bash
# Pruebas básicas del sistema
python tests/simple_test_adk.py

# Pruebas del servidor MCP
python coordinator-mcp/test_mcp_server.py
```

### **Validación de Endpoints**
```bash
# Verificar salud del sistema
curl http://localhost:8000/health

# Ejecutar prueba integrada
curl http://localhost:8000/gastronomy/test
```

## 🔍 Características Avanzadas

### **Gestión de Estado**
- **Sesiones persistentes**: Mantiene contexto entre consultas
- **Preferencias de usuario**: Aprende de interacciones previas
- **Historial de conversaciones**: Contexto completo disponible

### **Delegación Inteligente**
- **Análisis automático**: Determina qué especialista consultar
- **Combinación de especialistas**: Respuestas multi-agente
- **Síntesis de respuestas**: Combina conocimiento de múltiples fuentes

### **Bases de Conocimiento**
- **Índices FAISS**: Búsqueda vectorial eficiente
- **Datos estructurados**: JSON con información especializada
- **Textos especializados**: Documentos de referencia

## 🛠️ Desarrollo

### **Estructura de Agentes**
Cada agente sigue la estructura ADK:
- **Configuración**: Instrucciones específicas del dominio
- **Herramientas**: Funciones especializadas
- **Índices**: Bases de conocimiento FAISS

### **Agregar Nuevo Agente**
1. Crear carpeta en `agents/nuevo_agente/`
2. Implementar `adk_agent.py`
3. Crear archivo de instrucciones
4. Preparar base de conocimiento
5. Registrar en el coordinador

### **Configurar Nuevo Dominio**
1. Preparar datos en `knowledge_base/`
2. Generar índice FAISS
3. Configurar agente especializado
4. Actualizar coordinador

## 📊 Monitoreo

### **Métricas del Sistema**
- **Sesiones activas**: Número de sesiones concurrentes
- **Interacciones por especialista**: Estadísticas de uso
- **Tiempo de respuesta**: Métricas de rendimiento

### **Logs del Sistema**
```bash
# Logs detallados en salida estándar
python main.py

# Logs del servidor MCP
tail -f coordinator-mcp/logs/server.log
```

## 🚨 Manejo de Errores

### **Rate Limiting**
- **Límites automáticos**: Prevención de sobrecarga
- **Mensajes amigables**: Experiencia de usuario mejorada
- **Reintentos inteligentes**: Gestión automática de límites

### **Fallbacks**
- **Coordinador híbrido**: Múltiples estrategias de ejecución
- **Agentes alternativos**: Respaldo en caso de fallos
- **Respuestas de error**: Manejo elegante de excepciones

## 🤝 Contribución

### **Convenciones de Código**
- **Docstrings**: Documentación completa de funciones
- **Tipos**: Anotaciones de tipos para mayor claridad
- **Logging**: Información detallada del sistema

### **Pull Requests**
1. Fork del repositorio
2. Crear branch para nueva funcionalidad
3. Implementar cambios con pruebas
4. Enviar pull request con descripción

## 📜 Licencia

Este proyecto está licenciado bajo [LICENSE] - ver archivo LICENSE para detalles.

## 🙏 Agradecimientos

- **Google ADK**: Framework de desarrollo de agentes
- **Vertex AI**: Plataforma de IA de Google Cloud
- **FAISS**: Biblioteca de búsqueda vectorial
- **FastAPI**: Framework web moderno para APIs

---

**Desarrollado con 💙 usando Google ADK y Vertex AI**

*Para soporte técnico y consultas, contactar al equipo de desarrollo.*