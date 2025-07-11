# agents/agent_builder.py
import os
import vertexai
from google.adk.agents import Agent
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import FAISS
from typing import Dict, Callable
from agents.usda_api_client import usda_client


# --- Configuración Centralizada de Vertex AI ---
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "maitre-digital")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
vertexai.init(project=project_id, location=location)

embedding_model = VertexAIEmbeddings(model_name="text-embedding-004")

def create_specialist_agent(name: str, description: str, instruction: str, index_path: str, k_results: int = 2) -> Agent:
    """
    Crea y configura un agente especialista con su base de conocimientos y API USDA.
    """
    vector_store = None
    if os.path.exists(index_path):
        try:
            vector_store = FAISS.load_local(
                index_path, 
                embedding_model, 
                allow_dangerous_deserialization=True
            )
            print(f"Índice cargado exitosamente para el agente '{name}' desde '{index_path}'")
        except Exception as e:
            print(f"Error al cargar el índice para el agente '{name}': {e}")
    else:
        print(f"Advertencia: No se encontró el directorio del índice en '{index_path}' para el agente '{name}'.")

    def query_knowledge_base(query: str) -> Dict[str, str]:
        """
        Consulta la base de conocimientos vectorial (FAISS) con manejo de errores mejorado.
        """
        if not vector_store:
            return {
                "status": "error", 
                "context": f"La base de conocimientos para '{name}' no está disponible temporalmente.",
                "suggestion": "Como especialista, puedo intentar ayudarte con información general sobre el tema. ¿Podrías reformular tu consulta de manera más específica?"
            }
        
        try:
            results = vector_store.similarity_search(query, k=k_results)
            formatted_context = []
            for i, doc in enumerate(results, 1):
                content = doc.page_content.strip()
                formatted_context.append(f"--- RESULTADO {i} ---\n{content}")
            
            if not formatted_context:
                return {
                    "status": "partial", 
                    "context": f"No encontré información específica sobre '{query}' en mi base de conocimientos actual.",
                    "suggestion": f"Como especialista en {name.replace('_specialist', '')}, puedo sugerir consultas relacionadas o ayudarte con aspectos generales del tema."
                }

            return {
                "status": "success", 
                "context": "\n\n".join(formatted_context),
                "source": "knowledge_base",
                "query_used": query
            }

        except Exception as e:
            return {
                "status": "error", 
                "context": f"Ocurrió un problema técnico al consultar mi base de conocimientos: {str(e)}",
                "suggestion": "Por favor, intenta reformular tu consulta o pregúntame algo más general sobre el tema."
            }

    def query_usda_nutrition_api(food_query: str) -> Dict[str, str]:
        """
        Consulta la API USDA FoodData Central para información nutricional específica.
        Úsala cuando necesites datos nutricionales precisos de alimentos específicos.
        """
        try:
            # Buscar en la API USDA
            search_results = usda_client.search_foods(
                query=food_query,
                data_types=["Foundation", "SR Legacy"],  # Datos más confiables
                page_size=3
            )
            
            # Formatear resultados
            formatted_data = usda_client.format_nutrition_data(search_results)
            
            if "No se encontraron alimentos" in formatted_data:
                return {
                    "status": "partial",
                    "api_data": f"No encontré datos específicos para '{food_query}' en la base de datos USDA.",
                    "suggestion": "Puedo buscar alimentos similares o proporcionarte información nutricional general. ¿Podrías ser más específico con el nombre del alimento?",
                    "source": "USDA FoodData Central API"
                }
            
            return {
                "status": "success",
                "api_data": formatted_data,
                "source": "USDA FoodData Central API",
                "query_used": food_query
            }
            
        except Exception as e:
            return {
                "status": "error",
                "api_data": f"No pude acceder a la base de datos USDA en este momento: {str(e)}",
                "suggestion": "Puedo proporcionarte información nutricional general basada en mi conocimiento. ¿Te gustaría que consulte mi base de conocimientos interna?",
                "source": "API Error"
            }

    # Crear nombres únicos para las herramientas
    kb_tool_name = f"query_{name}_kb"
    api_tool_name = f"query_usda_nutrition_api"
    
    # Asignar nombres únicos a las funciones
    query_knowledge_base.__name__ = kb_tool_name
    query_usda_nutrition_api.__name__ = api_tool_name
    
    # Actualizar instrucción para incluir ambas herramientas
    final_instruction = instruction.format(
        kb_tool_name=kb_tool_name,
        api_tool_name=api_tool_name
    )

    # Añadir instrucción mejorada para el logging de trazas
    trace_instruction = f"""
SISTEMA DE TRAZABILIDAD PROFESIONAL:
Después de tu respuesta final, añade información de trazabilidad invisible para mejorar el servicio:

<span data-trace='{{
    "agent": "{name}",
    "tools_used": ["herramientas_utilizadas"],
    "confidence": "alta/media/baja",
    "sources": ["fuentes_consultadas"],
    "response_type": "completa/parcial/derivada",
    "suggestions": ["posibles_seguimientos"]
}}' style='display:none;'></span>

- agent: Tu nombre, '{name}'
- tools_used: Lista las herramientas usadas: '{kb_tool_name}', '{api_tool_name}', o 'none'
- confidence: Evalúa tu nivel de confianza en la respuesta
- sources: Especifica las fuentes: 'knowledge_base', 'usda_api', 'general_knowledge', o 'multiple'
- response_type: 'completa' si proporcionaste toda la información, 'parcial' si falta algo, 'derivada' si usaste conocimiento general
- suggestions: Sugiere posibles consultas de seguimiento que podrían interesar al usuario

Esto nos ayuda a mejorar continuamente la experiencia gastronómica."""
    
    final_instruction += "\n\n" + trace_instruction

    return Agent(
        name=name,
        model="gemini-2.5-flash",
        instruction=final_instruction,
        description=description,
        tools=[query_knowledge_base, query_usda_nutrition_api]  # Ambas herramientas
    )