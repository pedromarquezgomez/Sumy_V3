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
        Consulta la base de conocimientos vectorial (FAISS).
        """
        if not vector_store:
            return {
                "status": "error", 
                "context": f"La base de conocimientos para '{name}' no está disponible."
            }
        
        try:
            results = vector_store.similarity_search(query, k=k_results)
            formatted_context = []
            for i, doc in enumerate(results, 1):
                content = doc.page_content.strip()
                formatted_context.append(f"--- RESULTADO {i} ---\n{content}")
            
            if not formatted_context:
                return {"status": "success", "context": "No se encontraron resultados relevantes."}

            return {"status": "success", "context": "\n\n".join(formatted_context)}

        except Exception as e:
            return {"status": "error", "context": f"Ocurrió un error al consultar la base de conocimientos: {e}"}

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
            
            return {
                "status": "success",
                "api_data": formatted_data,
                "source": "USDA FoodData Central API"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "api_data": f"Error consultando API USDA: {str(e)}",
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

    # Añadir instrucción para el logging de trazas
    trace_instruction = """REGLA DE TRAZABILIDAD FINAL:
Después de generar tu respuesta final en español, SIEMPRE debes añadir al final un bloque de datos para trazabilidad. Este bloque NUNCA debe ser visible para el usuario.
Usa este formato exacto, reemplazando los valores:
<span data-trace-info='{{"agent_name": "{agent_name}", "source": "...", "tools_used": "...", "rag_context": "...", "api_context": "..."}}' style='display:none;'></span>

- agent_name: Tu nombre, '{agent_name}'.
- source: Si has usado herramientas, especifica cuáles: 'RAG', 'API', 'RAG+API', o 'LLM' si no usaste ninguna.
- tools_used: Lista las herramientas usadas: '{kb_tool_name}', '{api_tool_name}', o 'none'.
- rag_context: El contexto de la base de conocimientos si lo usaste, o 'none'.
- api_context: El contexto de la API USDA si lo usaste, o 'none'."""
    
    final_instruction += "\n\n" + trace_instruction.format(
        agent_name=name, 
        kb_tool_name=kb_tool_name,
        api_tool_name=api_tool_name
    )

    return Agent(
        name=name,
        model="gemini-2.5-flash",
        instruction=final_instruction,
        description=description,
        tools=[query_knowledge_base, query_usda_nutrition_api]  # Ambas herramientas
    )