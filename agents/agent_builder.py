# agents/agent_builder.py
import os
import vertexai
from google.adk.agents import Agent
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import FAISS
from typing import Dict, Callable

# --- Configuración Centralizada de Vertex AI ---
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "maitre-digital")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
vertexai.init(project=project_id, location=location)

embedding_model = VertexAIEmbeddings(model_name="text-embedding-004")

def create_specialist_agent(name: str, description: str, instruction: str, index_path: str, k_results: int = 2) -> Agent:
    """
    Crea y configura un agente especialista con su base de conocimientos.
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

    tool_name = f"query_{name}_kb"
    query_knowledge_base.__name__ = tool_name
    
    final_instruction = instruction.format(tool_name=tool_name)

    # Añadir instrucción para el logging de trazas en el frontend
    trace_instruction = """REGLA DE TRAZABILIDAD FINAL:
Después de generar tu respuesta final en español, SIEMPRE debes añadir al final un bloque de datos para trazabilidad. Este bloque NUNCA debe ser visible para el usuario.
Usa este formato exacto, reemplazando los valores:
<span data-trace-info='{{"agent_name": "{agent_name}", "source": "...", "tool_used": "...", "rag_context": "..."}}' style='display:none;'></span>

- agent_name: Tu nombre, '{agent_name}'.
- source: Si has usado la herramienta {tool_name} para obtener la respuesta, pon 'RAG'. Si no la has usado o no has encontrado nada, pon 'LLM'.
- tool_used: El nombre de la herramienta que has usado, '{tool_name}', o 'none' si no la usaste.
- rag_context: El CONTEXTO COMPLETO que obtuviste de la herramienta. Debe ser el texto exacto, escapando las comillas dobles con \"\". Si no obtuviste contexto, pon 'none'."""
    final_instruction += "\n\n" + trace_instruction.format(agent_name=name, tool_name=tool_name)

    return Agent(
        name=name,
        model="gemini-2.5-flash",
        instruction=final_instruction,
        description=description,
        tools=[query_knowledge_base]
    )
