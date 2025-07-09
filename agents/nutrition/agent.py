# nutrition_agent/agent.py
import os
import vertexai
from google.adk.agents import Agent
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import FAISS
from typing import Dict

# Configurar variables de entorno para Vertex AI
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = os.getenv("GOOGLE_CLOUD_PROJECT", "maitre-digital")
os.environ['GOOGLE_CLOUD_LOCATION'] = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# Inicializar Vertex AI
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "maitre-digital")
location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
vertexai.init(project=project_id, location=location)

INDEX_PATH = "./indexes/nutrition_index"
vector_store = None
if os.path.exists(INDEX_PATH):
    embedding_model = VertexAIEmbeddings(model_name="text-embedding-004")
    vector_store = FAISS.load_local(INDEX_PATH, embedding_model, allow_dangerous_deserialization=True)

def query_nutrition_kb(query: str) -> Dict[str, str]:
    """Consulta la base de datos de nutrición."""
    if not vector_store: return {"status": "error", "context": "Índice no cargado."}
    results = vector_store.similarity_search(query, k=2)
    return {"status": "success", "context": "\n---\n".join([doc.page_content for doc in results])}

root_agent = Agent(
    name="nutrition_specialist", 
    model="gemini-2.5-flash", 
    instruction="""Eres un nutricionista experto especializado en alimentación y nutrición.

IMPORTANTE: Siempre debes usar tu herramienta query_nutrition_kb para buscar información antes de responder.

Cuando recibas una consulta sobre nutrición:
1. PRIMERO: Usa query_nutrition_kb para buscar información relevante
2. SEGUNDO: Analiza toda la información encontrada en el contexto
3. TERCERO: Responde basándote en la información encontrada

Proporciona respuestas detalladas sobre nutrición, dietas, calorías, vitaminas, minerales y alimentación saludable basándote en tu base de conocimientos.

Si no encuentras información específica en tu base de datos, di claramente "No tengo información específica sobre [tema] en mi base de conocimientos nutricionales actual".""", 
    description="Especialista en responder preguntas sobre nutrición, dietas, calorías, vitaminas y alimentación saludable usando una base de conocimientos especializada.", 
    tools=[query_nutrition_kb]
) 