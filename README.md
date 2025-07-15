# 🍽️ Sumy_V3 - Sistema Gastronómico con Google ADK

## 📋 Resumen Ejecutivo

**Sumy_V3** es un sistema gastronómico inteligente refactorizado con **Google ADK (Agent Development Kit)** que implementa una arquitectura multi-agente optimizada para brindar experiencias gastronómicas excepcionales a través de especialistas en vinos, cocina y nutrición.

### 🎯 Arquitectura ADK Implementada

```
┌─────────────────────────────────────────────┐
│         COORDINADOR PRINCIPAL               │
│    gastronomy_coordinator (Gemini 2.0)     │
│                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  │  SUMILLER   │ │    CHEF     │ │NUTRICIONISTA│
│  │ SPECIALIST  │ │ SPECIALIST  │ │ SPECIALIST  │
│  │(Gemini 2.5) │ │(Gemini 2.5) │ │(Gemini 2.5) │
│  └─────────────┘ └─────────────┘ └─────────────┘
│                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  │  FAISS KB   │ │  FAISS KB   │ │  FAISS KB   │
│  │ Enología    │ │ Culinaria   │ │ Nutrición   │
│  │             │ │             │ │ + USDA API  │
│  └─────────────┘ └─────────────┘ └─────────────┘
└─────────────────────────────────────────────┘
```

### ✨ **Arquitectura Ultra-Limpia**

**Refactorización completa con Google ADK** - Sistema optimizado con solo **4 archivos Python esenciales**:

- 📱 **main.py** - Servidor principal ADK
- 🚀 **adk_runner.py** - Runner stateful con gestión de sesiones  
- ⚙️ **adk_config.py** - Configuración Vertex AI
- 🧪 **simple_test_adk.py** - Suite de pruebas completa

**Beneficios**: Mantenimiento simplificado, onboarding rápido, estructura clara, rendimiento optimizado.

---

## 🏗️ Componentes Principales

### 1. **Coordinador Principal** (`gastronomy_coordinator`)
- **Rol**: Maître Digital que gestiona la experiencia gastronómica
- **Modelo**: Gemini 2.0 Flash Experimental
- **Funcionalidades**:
  - Análisis inteligente de consultas
  - Delegación automática a especialistas
  - Síntesis de respuestas multi-agente
  - Gestión de contexto conversacional

### 2. **Agentes Especializados**

#### 🍷 **Sumiller Specialist**
- **Especialidad**: Vinos, maridajes, enología
- **Base de Conocimientos**: Índice vectorial enológico (FAISS)
- **Herramientas**:
  - `query_wine_knowledge`: Consultas generales sobre vinos
  - `recommend_wine_pairing`: Recomendaciones de maridaje

#### 🍳 **Chef Specialist**
- **Especialidad**: Cocina, recetas, técnicas culinarias
- **Base de Conocimientos**: Índice vectorial culinario (FAISS)
- **Herramientas**:
  - `query_culinary_knowledge`: Consultas culinarias generales
  - `get_recipe_details`: Detalles de recetas específicas
  - `suggest_cooking_technique`: Recomendaciones de técnicas

#### 🥗 **Nutrition Specialist**
- **Especialidad**: Nutrición, dietas, análisis nutricional
- **Base de Conocimientos**: Índice vectorial nutricional + API USDA
- **Herramientas**:
  - `query_nutrition_knowledge`: Consultas nutricionales generales
  - `get_usda_nutrition_data`: Datos nutricionales precisos
  - `analyze_nutritional_content`: Análisis nutricional completo

### 3. **Runner Stateful** (`StatefulGastronomyRunner`)
- **Gestión de Sesiones**: `InMemorySessionService`
- **Persistencia de Estado**: Contexto conversacional y preferencias
- **Gestión de Artefactos**: `InMemoryArtifactService`
- **Coordinación**: Orquestación de agentes y herramientas

---

## 🚀 Instalación y Configuración

### 1. **Dependencias**
```bash
pip install google-adk
pip install langchain-google-vertexai
pip install langchain-community
pip install faiss-cpu
```

### 2. **Variables de Entorno**
```bash
export GOOGLE_CLOUD_PROJECT="maitre-digital"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI="true"
```

### 3. **Inicialización**
```bash
# Servidor principal
python main.py

# Runner interactivo
python adk_runner.py

# Suite de pruebas
python simple_test_adk.py
```

---

## 🔧 Uso del Sistema

### 1. **API Endpoints**

#### Consulta Gastronómica Principal
```bash
POST /gastronomy/query
{
    "query": "¿Qué vino recomiendan para salmón?",
    "user_id": "guest",
    "session_id": "session_123"
}
```

#### Gestión de Sesiones
```bash
GET /gastronomy/sessions                    # Listar sesiones activas
GET /gastronomy/session/{id}/state          # Estado de sesión
DELETE /gastronomy/session/{id}             # Limpiar sesión
```

#### Sistema de Salud
```bash
GET /health                                 # Estado del sistema
GET /info                                   # Información arquitectónica
GET /gastronomy/test                        # Prueba del sistema ADK
```

### 2. **Uso Programático**

#### Consulta Rápida
```python
from adk_runner import quick_gastronomy_query

# Consulta directa
events = await quick_gastronomy_query(
    "¿Cómo hacer paella valenciana?",
    user_id="chef_user"
)
```

#### Sesión Interactiva
```python
from adk_runner import interactive_gastronomy_session

# Sesión de desarrollo
await interactive_gastronomy_session()
```

#### Runner Personalizado
```python
from adk_runner import StatefulGastronomyRunner

runner = StatefulGastronomyRunner()
await runner.create_session("user123", "session456")
events = await runner.run_query(
    "¿Qué vino tinto recomiendan?",
    "user123",
    "session456"
)
```

---

## 📁 Estructura del Proyecto

```
Sumy_V3/
├── 📱 main.py                    # Servidor principal ADK
├── 🚀 adk_runner.py              # Runner stateful
├── ⚙️ adk_config.py              # Configuración Vertex AI
├── 📦 requirements.txt           # Dependencias Python
├── 🧪 simple_test_adk.py         # Suite de pruebas
├── 📚 README.md                  # Esta documentación
├── 🤖 agents/                    # Agentes ADK
│   ├── coordinator/
│   │   └── adk_coordinator.py    # Coordinador principal
│   ├── sumiller/
│   │   └── adk_agent.py          # Especialista en vinos
│   ├── culinary/
│   │   └── adk_agent.py          # Especialista culinario
│   ├── nutrition/
│   │   └── adk_agent.py          # Especialista nutricional
│   ├── instrucciones/            # Instrucciones de agentes
│   └── usda_api_client.py        # Cliente API USDA
├── 📊 indexes/                   # Índices FAISS optimizados
│   ├── enology_index/
│   ├── culinary_index/
│   └── nutrition_index/
├── 🗃️ knowledge_base/            # Bases de conocimiento
│   ├── enology/
│   ├── culinary/
│   └── nutrition/
└── 🔧 coordinator-mcp/           # Servidor MCP (opcional)
```

---

## 🎯 Patrones ADK Implementados

### 1. **Delegación Inteligente**
```python
# El coordinador analiza la consulta y delega automáticamente
if "vino" in query:
    # Delegación a sumiller_specialist
    return delegate_to_sumiller(query)
elif "receta" in query:
    # Delegación a chef_specialist
    return delegate_to_chef(query)
```

### 2. **Sub-Agentes Especializados**
```python
root_coordinator = Agent(
    name="gastronomy_coordinator",
    sub_agents=[sumiller_agent, culinary_agent, nutrition_agent],
    tools=[coordination_tools],
    output_key="coordination_result"
)
```

### 3. **Gestión de Estado**
```python
# Cada agente mantiene estado con output_key
sumiller_agent = Agent(
    name="sumiller_specialist",
    tools=[wine_tools],
    output_key="wine_recommendation"
)
```

### 4. **Runner con Session Service**
```python
runner = Runner(
    agent=root_coordinator,
    session_service=InMemorySessionService(),
    artifact_service=InMemoryArtifactService()
)
```

---

## 📊 Métricas y Monitoreo

### 1. **Métricas del Sistema**
- **Agentes Activos**: 4 (1 coordinador + 3 especialistas)
- **Herramientas Disponibles**: 9 herramientas especializadas
- **Bases de Conocimientos**: 3 índices FAISS + 1 API externa
- **Modelos**: Gemini 2.0 (coordinador) + Gemini 2.5 (especialistas)

### 2. **Endpoints de Monitoreo**
```bash
GET /health                    # Estado general
GET /info                      # Información arquitectónica
GET /gastronomy/sessions       # Sesiones activas
GET /gastronomy/test           # Prueba funcional
```

### 3. **Logging y Trazabilidad**
```python
# Cada respuesta incluye trazabilidad
<span data-trace='{
    "agent": "sumiller_specialist",
    "tools_used": ["query_wine_knowledge"],
    "confidence": "alta",
    "sources": ["enology_knowledge_base"]
}' style='display:none;'></span>
```

---

## 🧪 Testing y Validación

### 1. **Suite de Pruebas**
```bash
python simple_test_adk.py
```

**Pruebas Incluidas**:
- ✅ Inicialización del coordinador
- ✅ Creación de sesiones
- ✅ Delegación a sumiller
- ✅ Delegación a chef
- ✅ Delegación a nutricionista
- ✅ Persistencia de estado
- ✅ Coordinación multi-agente

### 2. **Pruebas de Rendimiento**
```bash
# Incluidas en simple_test_adk.py
await performance_test()
```

### 3. **Validación en Producción**
```bash
curl -X GET http://localhost:8000/gastronomy/test
```

---

## 🔐 Seguridad y Mejores Prácticas

### 1. **Configuración Segura**
- Variables de entorno para credenciales
- Validación de entrada con Pydantic
- Manejo de errores robusto
- Logging estructurado

### 2. **Gestión de Sesiones**
- Sesiones con estado persistente
- Limpieza automática de sesiones
- Aislamiento de datos por usuario

### 3. **Acceso a Datos**
- Deserialization controlada para FAISS
- Validación de consultas API
- Timeout y retry para servicios externos

---

## 🚀 Despliegue y Escalabilidad

### 1. **Despliegue Directo**
```bash
# Instalación y ejecución directa
pip install -r requirements.txt
python main.py
```

### 2. **Escalabilidad**
- **Horizontal**: Múltiples instancias del coordinador
- **Vertical**: Modelos especializados por dominio
- **Caching**: Índices FAISS pre-cargados
- **Session Service**: Configurable para Redis/PostgreSQL

### 3. **Monitoreo en Producción**
```python
# Métricas incluidas en endpoints
{
    "active_sessions": 15,
    "queries_processed": 1250,
    "avg_response_time": "1.2s",
    "specialist_utilization": {
        "sumiller": 45,
        "chef": 35,
        "nutrition": 20
    }
}
```

---

## 📚 Recursos Adicionales

### 1. **Documentación ADK**
- [Google ADK Documentation](https://github.com/google/adk-docs)
- [Vertex AI Integration](https://cloud.google.com/vertex-ai)
- [Agent Development Patterns](https://github.com/google/adk-samples)

### 2. **Archivos de Configuración**
- `adk_config.py`: Configuración de Vertex AI
- `adk_runner.py`: Runner stateful principal
- `simple_test_adk.py`: Suite de pruebas
- `main.py`: Servidor FastAPI integrado

### 3. **Estructura de Archivos**
```
Sumy_V3/
├── agents/
│   ├── coordinator/
│   │   ├── adk_coordinator.py      # Coordinador ADK
│   │   └── agent.py                # Implementación original
│   ├── sumiller/
│   │   └── adk_agent.py            # Sumiller especializado
│   ├── culinary/
│   │   └── adk_agent.py            # Chef especializado
│   ├── nutrition/
│   │   └── adk_agent.py            # Nutricionista especializado
│   └── instrucciones/              # Instrucciones de agentes
├── adk_config.py                   # Configuración ADK
├── adk_runner.py                   # Runner stateful
├── simple_test_adk.py              # Suite de pruebas
├── main.py                         # Servidor principal
└── README.md                       # Esta documentación
```

---

## 🎉 Ventajas de la Arquitectura ADK

### 1. **Antes (Monolítico)**
```python
# Un solo agente con herramientas integradas
coordinator_agent = Agent(
    name="coordinator",
    tools=[wine_tool, culinary_tool, nutrition_tool]
)
```

### 2. **Después (Multi-Agente ADK)**
```python
# Coordinador con sub-agentes especializados
coordinator = Agent(
    name="coordinator",
    sub_agents=[sumiller_agent, chef_agent, nutrition_agent],
    tools=[coordination_tools]
)
```

### 3. **Beneficios Obtenidos**
- ✅ **Especialización**: Cada agente es experto en su dominio
- ✅ **Escalabilidad**: Fácil agregar nuevos especialistas
- ✅ **Mantenibilidad**: Código modular y organizado
- ✅ **Rendimiento**: Modelos optimizados por especialidad
- ✅ **Flexibilidad**: Delegación inteligente y adaptativa
- ✅ **Estado**: Persistencia y contexto conversacional

---

**🎩 Sumy_V3 con Google ADK - Experiencia Gastronómica Inteligente**

*Implementación realizada siguiendo mejores prácticas de Agent Development Kit*