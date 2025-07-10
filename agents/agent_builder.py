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

    return Agent(
        name=name,
        model="gemini-2.5-flash",
        instruction=final_instruction,
        description=description,
        tools=[query_knowledge_base]
    )
