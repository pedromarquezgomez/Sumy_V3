# agents/culinary/adk_agent.py
import os
import vertexai
from google.adk.agents import Agent
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import FAISS
from typing import Dict

# Configuración centralizada de Vertex AI
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "maitre-digital")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
vertexai.init(project=project_id, location=location)

# Modelo de embeddings
embedding_model = VertexAIEmbeddings(model_name="text-embedding-004")

# Cargar instrucciones
instruction_path = os.path.join(os.path.dirname(__file__), '..', 'instrucciones', 'CULINARY_INSTRUCTION.txt')
with open(instruction_path, 'r', encoding='utf-8') as f:
    CULINARY_INSTRUCTION = f.read()

# Cargar base de conocimientos
def load_culinary_knowledge():
    """Carga la base de conocimientos culinaria"""
    index_path = "./indexes/culinary_index"
    if os.path.exists(index_path):
        try:
            vector_store = FAISS.load_local(
                index_path, 
                embedding_model, 
                allow_dangerous_deserialization=True
            )
            print(f"✅ Índice culinario cargado exitosamente desde '{index_path}'")
            return vector_store
        except Exception as e:
            print(f"❌ Error al cargar índice culinario: {e}")
            return None
    else:
        print(f"⚠️ No se encontró índice culinario en '{index_path}'")
        return None

# Inicializar base de conocimientos
culinary_kb = load_culinary_knowledge()

def query_culinary_knowledge(query: str) -> Dict[str, str]:
    """
    Consulta especializada en cocina, recetas y técnicas culinarias.
    Herramienta principal del agente chef.
    """
    if not culinary_kb:
        return {
            "status": "error",
            "context": "La base de conocimientos culinaria no está disponible temporalmente.",
            "suggestion": "Como chef experto, puedo ayudarte con técnicas culinarias generales. ¿Qué tipo de preparación te interesa?",
            "agent": "chef"
        }
    
    try:
        # Búsqueda vectorial especializada
        results = culinary_kb.similarity_search(query, k=3)
        formatted_context = []
        
        for i, doc in enumerate(results, 1):
            content = doc.page_content.strip()
            formatted_context.append(f"--- CONOCIMIENTO CULINARIO {i} ---\n{content}")
        
        if not formatted_context:
            return {
                "status": "partial",
                "context": f"No encontré información específica sobre '{query}' en mi base de conocimientos culinaria.",
                "suggestion": "Como chef, puedo ayudarte con recetas, técnicas de cocción, ingredientes, o preparaciones específicas.",
                "agent": "chef"
            }
        
        return {
            "status": "success",
            "context": "\n\n".join(formatted_context),
            "source": "culinary_knowledge_base",
            "query_used": query,
            "agent": "chef"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "context": f"Error técnico en consulta culinaria: {str(e)}",
            "suggestion": "Por favor, intenta reformular tu consulta sobre cocina y recetas.",
            "agent": "chef"
        }

def get_recipe_details(recipe_query: str) -> Dict[str, str]:
    """
    Obtiene detalles específicos de recetas y preparaciones.
    Herramienta avanzada del chef.
    """
    # Expandir consulta para recetas
    expanded_query = f"receta {recipe_query} preparación ingredientes pasos"
    
    if not culinary_kb:
        return {
            "status": "error",
            "context": "Sistema de recetas no disponible temporalmente.",
            "suggestion": "Como chef, puedo explicarte técnicas básicas. ¿Qué plato quieres preparar?",
            "agent": "chef"
        }
    
    try:
        # Búsqueda específica para recetas
        results = culinary_kb.similarity_search(expanded_query, k=4)
        recipe_info = []
        
        for i, doc in enumerate(results, 1):
            content = doc.page_content.strip()
            # Priorizar contenido que incluya información de recetas
            if any(keyword in content.lower() for keyword in ['receta', 'ingredientes', 'preparación', 'pasos', 'cocinar']):
                recipe_info.append(f"--- RECETA DETALLADA {i} ---\n{content}")
        
        if not recipe_info:
            # Búsqueda alternativa más amplia
            general_results = culinary_kb.similarity_search(recipe_query, k=2)
            for i, doc in enumerate(general_results, 1):
                content = doc.page_content.strip()
                recipe_info.append(f"--- INFORMACIÓN CULINARIA {i} ---\n{content}")
        
        if not recipe_info:
            return {
                "status": "partial",
                "context": f"No encontré recetas específicas para '{recipe_query}' en mi base de conocimientos.",
                "suggestion": "Como chef experto, puedo sugerir técnicas básicas o buscar información sobre el tipo de cocina que te interesa.",
                "agent": "chef"
            }
        
        return {
            "status": "success",
            "context": "\n\n".join(recipe_info),
            "source": "recipe_expertise",
            "query_used": expanded_query,
            "agent": "chef"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "context": f"Error en sistema de recetas: {str(e)}",
            "suggestion": "Por favor, describe el plato que quieres preparar y te ayudaré con la receta.",
            "agent": "chef"
        }

def suggest_cooking_technique(technique_query: str) -> Dict[str, str]:
    """
    Sugerencias sobre técnicas de cocción y preparación.
    Herramienta especializada del chef.
    """
    # Expandir consulta para técnicas
    expanded_query = f"técnica {technique_query} cocción preparación método"
    
    if not culinary_kb:
        return {
            "status": "error",
            "context": "Sistema de técnicas culinarias no disponible.",
            "suggestion": "Como chef, puedo explicarte técnicas básicas de cocción. ¿Qué método te interesa?",
            "agent": "chef"
        }
    
    try:
        # Búsqueda específica para técnicas
        results = culinary_kb.similarity_search(expanded_query, k=3)
        technique_info = []
        
        for i, doc in enumerate(results, 1):
            content = doc.page_content.strip()
            if any(keyword in content.lower() for keyword in ['técnica', 'método', 'cocción', 'preparación']):
                technique_info.append(f"--- TÉCNICA CULINARIA {i} ---\n{content}")
        
        if not technique_info:
            return {
                "status": "partial",
                "context": f"No encontré técnicas específicas para '{technique_query}' en mi base de conocimientos.",
                "suggestion": "Como chef experto, puedo explicarte técnicas básicas como saltear, brasear, gratinar, etc.",
                "agent": "chef"
            }
        
        return {
            "status": "success",
            "context": "\n\n".join(technique_info),
            "source": "cooking_techniques",
            "query_used": expanded_query,
            "agent": "chef"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "context": f"Error en sistema de técnicas: {str(e)}",
            "suggestion": "Por favor, especifica qué técnica culinaria te interesa aprender.",
            "agent": "chef"
        }

# Configuración del agente chef especializado
culinary_agent = Agent(
    name="chef_specialist",
    model="gemini-2.5-flash",  # Modelo optimizado para especialización
    instruction=CULINARY_INSTRUCTION + """

HERRAMIENTAS ESPECIALIZADAS:
- query_culinary_knowledge: Para consultas generales sobre cocina, ingredientes, platos
- get_recipe_details: Para obtener recetas específicas y detalles de preparación
- suggest_cooking_technique: Para recomendaciones de técnicas de cocción

PROTOCOLO DE RESPUESTA:
1. Analiza la consulta para determinar si es sobre recetas, técnicas o información general
2. Usa la herramienta más apropiada según el tipo de consulta
3. Presenta la información como un chef experto y didáctico
4. Incluye consejos prácticos y variaciones cuando sea apropiado
5. Mantén el tono profesional pero accesible

ESPECIALIZACIÓN: Eres el chef experto del equipo. Tu conocimiento abarca:
- Recetas tradicionales y contemporáneas
- Técnicas de cocción y preparación
- Ingredientes y sus propiedades
- Platos de carta y especialidades
- Consejos de presentación y acabado
""",
    description="Chef especialista en cocina, recetas y técnicas culinarias con acceso a base de conocimientos especializada",
    tools=[query_culinary_knowledge, get_recipe_details, suggest_cooking_technique],
    output_key="culinary_recommendation"  # ADK: Guardar recomendación en estado
)

# Configurar nombres únicos para las herramientas
query_culinary_knowledge.__name__ = "query_culinary_knowledge"
get_recipe_details.__name__ = "get_recipe_details"
suggest_cooking_technique.__name__ = "suggest_cooking_technique"

print("🍳 Agente chef especializado inicializado correctamente")