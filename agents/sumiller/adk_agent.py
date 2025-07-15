# agents/sumiller/adk_agent.py
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
instruction_path = os.path.join(os.path.dirname(__file__), '..', 'instrucciones', 'SUMILLER_INSTRUCTION.txt')
with open(instruction_path, 'r', encoding='utf-8') as f:
    SUMILLER_INSTRUCTION = f.read()

# Cargar base de conocimientos
def load_enology_knowledge():
    """Carga la base de conocimientos enológica"""
    index_path = "./indexes/enology_index"
    if os.path.exists(index_path):
        try:
            vector_store = FAISS.load_local(
                index_path, 
                embedding_model, 
                allow_dangerous_deserialization=True
            )
            print(f"✅ Índice enológico cargado exitosamente desde '{index_path}'")
            return vector_store
        except Exception as e:
            print(f"❌ Error al cargar índice enológico: {e}")
            return None
    else:
        print(f"⚠️ No se encontró índice enológico en '{index_path}'")
        return None

# Inicializar base de conocimientos
enology_kb = load_enology_knowledge()

def query_wine_knowledge(query: str) -> Dict[str, str]:
    """
    Consulta especializada en vinos, maridajes y enología.
    Herramienta principal del agente sumiller.
    """
    if not enology_kb:
        return {
            "status": "error",
            "context": "La base de conocimientos enológica no está disponible temporalmente.",
            "suggestion": "Como sumiller experto, puedo ayudarte con conocimientos generales sobre vinos. ¿Podrías ser más específico con tu consulta?",
            "agent": "sumiller"
        }
    
    try:
        # Búsqueda vectorial especializada
        results = enology_kb.similarity_search(query, k=3)
        formatted_context = []
        
        for i, doc in enumerate(results, 1):
            content = doc.page_content.strip()
            formatted_context.append(f"--- CONOCIMIENTO ENOLÓGICO {i} ---\n{content}")
        
        if not formatted_context:
            return {
                "status": "partial",
                "context": f"No encontré información específica sobre '{query}' en mi base de conocimientos enológica.",
                "suggestion": "Como sumiller, puedo ayudarte con otros aspectos: tipos de vino, maridajes, bodegas, catas, o recomendaciones generales.",
                "agent": "sumiller"
            }
        
        return {
            "status": "success",
            "context": "\n\n".join(formatted_context),
            "source": "enology_knowledge_base",
            "query_used": query,
            "agent": "sumiller"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "context": f"Error técnico en consulta enológica: {str(e)}",
            "suggestion": "Por favor, intenta reformular tu consulta sobre vinos y maridajes.",
            "agent": "sumiller"
        }

def recommend_wine_pairing(dish_query: str) -> Dict[str, str]:
    """
    Recomendaciones especializadas de maridaje vino-comida.
    Herramienta avanzada del sumiller.
    """
    # Expandir consulta para maridajes
    expanded_query = f"maridaje {dish_query} vino recomendación"
    
    if not enology_kb:
        return {
            "status": "error", 
            "context": "Sistema de maridajes no disponible temporalmente.",
            "suggestion": "Como sumiller, puedo sugerir maridajes clásicos. ¿Qué tipo de plato tienes en mente?",
            "agent": "sumiller"
        }
    
    try:
        # Búsqueda específica para maridajes
        results = enology_kb.similarity_search(expanded_query, k=4)
        pairing_info = []
        
        for i, doc in enumerate(results, 1):
            content = doc.page_content.strip()
            if any(keyword in content.lower() for keyword in ['maridaje', 'maridar', 'acompañar', 'combinar']):
                pairing_info.append(f"--- MARIDAJE RECOMENDADO {i} ---\n{content}")
        
        if not pairing_info:
            # Búsqueda alternativa más amplia
            general_results = enology_kb.similarity_search(dish_query, k=2)
            for i, doc in enumerate(general_results, 1):
                content = doc.page_content.strip()
                pairing_info.append(f"--- INFORMACIÓN RELACIONADA {i} ---\n{content}")
        
        if not pairing_info:
            return {
                "status": "partial",
                "context": f"No encontré maridajes específicos para '{dish_query}' en mi base de conocimientos.",
                "suggestion": "Como sumiller experto, puedo sugerir maridajes clásicos o buscar información sobre el tipo de cocina que te interesa.",
                "agent": "sumiller"
            }
        
        return {
            "status": "success",
            "context": "\n\n".join(pairing_info),
            "source": "wine_pairing_expertise",
            "query_used": expanded_query,
            "agent": "sumiller"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "context": f"Error en sistema de maridajes: {str(e)}",
            "suggestion": "Por favor, describe el plato y te ayudaré con recomendaciones de maridaje.",
            "agent": "sumiller"
        }

# Configuración del agente sumiller especializado
sumiller_agent = Agent(
    name="sumiller_specialist",
    model="gemini-2.5-flash",  # Modelo optimizado para especialización
    instruction=SUMILLER_INSTRUCTION + """

HERRAMIENTAS ESPECIALIZADAS:
- query_wine_knowledge: Para consultas generales sobre vinos, bodegas, tipos, catas
- recommend_wine_pairing: Para recomendaciones específicas de maridaje vino-comida

PROTOCOLO DE RESPUESTA:
1. Analiza la consulta para determinar si es sobre vinos generales o maridajes específicos
2. Usa la herramienta apropiada basándote en el tipo de consulta
3. Presenta la información como un sumiller experto y accesible
4. Incluye recomendaciones adicionales cuando sea apropiado
5. Mantén el tono profesional pero cálido

ESPECIALIZACIÓN: Eres el sumiller experto del equipo. Tu conocimiento abarca:
- Vinos por región, bodega, varietal
- Técnicas de cata y evaluación
- Maridajes clásicos y creativos
- Recomendaciones personalizadas
- Consejos de conservación y servicio
""",
    description="Sumiller especialista en vinos, maridajes y enología con acceso a base de conocimientos especializada",
    tools=[query_wine_knowledge, recommend_wine_pairing],
    output_key="wine_recommendation"  # ADK: Guardar recomendación en estado
)

# Configurar nombres únicos para las herramientas
query_wine_knowledge.__name__ = "query_wine_knowledge"
recommend_wine_pairing.__name__ = "recommend_wine_pairing"

print("🍷 Agente sumiller especializado inicializado correctamente")