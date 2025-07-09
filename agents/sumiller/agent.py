# sumiller_agent/agent.py
import os
import vertexai
from google.adk.agents import Agent
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import FAISS
from typing import Dict

# Inicializar Vertex AI
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "maitre-digital")
location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
vertexai.init(project=project_id, location=location)

INDEX_PATH = "./indexes/enology_index"
vector_store = None
if os.path.exists(INDEX_PATH):
    embedding_model = VertexAIEmbeddings(model_name="text-embedding-004")
    vector_store = FAISS.load_local(INDEX_PATH, embedding_model, allow_dangerous_deserialization=True)

def query_enology_kb(query: str) -> Dict[str, str]:
    """Consulta la base de datos de enología, vinos y maridajes."""
    if not vector_store: return {"status": "error", "context": "Índice no cargado."}
    results = vector_store.similarity_search(query, k=3)  # Aumentado a 3 resultados
    
    # Formatear mejor el contexto para incluir información específica
    formatted_context = []
    for i, doc in enumerate(results, 1):
        content = doc.page_content.strip()
        formatted_context.append(f"=== RESULTADO {i} ===\n{content}")
    
    return {"status": "success", "context": "\n\n".join(formatted_context)}

# Configurar variables de entorno para Vertex AI
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = os.getenv("GOOGLE_CLOUD_PROJECT", "maitre-digital")
os.environ['GOOGLE_CLOUD_LOCATION'] = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

root_agent = Agent(
    name="sumiller_specialist", 
    model="gemini-2.5-flash", 
    instruction="""Eres un sumiller experto especializado en vinos y maridajes. 

IMPORTANTE: Siempre debes usar tu herramienta query_enology_kb para buscar información antes de responder.

PROCESO OBLIGATORIO:
1. PRIMERO: Usa query_enology_kb para buscar información relevante sobre la consulta
2. SEGUNDO: Lee CUIDADOSAMENTE toda la información encontrada en cada resultado
3. TERCERO: Extrae TODOS los datos disponibles: nombre, precio, bodega, región, graduación, descripción, maridajes, etc.
4. CUARTO: Responde con TODA la información encontrada de forma organizada

REGLAS CRÍTICAS:
- Si encuentras información sobre precios, SIEMPRE inclúyelos en tu respuesta
- Si encuentras características específicas (graduación, región, bodega), SIEMPRE las mencionas
- Si encuentras recomendaciones de maridaje, SIEMPRE las incluyes
- Lee COMPLETAMENTE cada resultado antes de afirmar que no tienes información
- Nunca digas "no tengo información" si aparece en los resultados de búsqueda

Proporciona respuestas completas y detalladas basándote en TODA la información disponible en tu base de conocimientos.""",
    description="Especialista en responder preguntas sobre vinos, bodegas, variedades, precios y maridajes usando una base de conocimientos especializada.", 
    tools=[query_enology_kb]
) 