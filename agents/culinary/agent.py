# culinary_agent/agent.py
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

INDEX_PATH = "./indexes/culinary_index"
vector_store = None
if os.path.exists(INDEX_PATH):
    embedding_model = VertexAIEmbeddings(model_name="text-embedding-004")
    vector_store = FAISS.load_local(INDEX_PATH, embedding_model, allow_dangerous_deserialization=True)

def query_culinary_kb(query: str) -> Dict[str, str]:
    """Consulta la base de datos de recetas y técnicas de cocina."""
    if not vector_store: return {"status": "error", "context": "Índice no cargado."}
    results = vector_store.similarity_search(query, k=2)
    return {"status": "success", "context": "\n---\n".join([doc.page_content for doc in results])}

# Configurar variables de entorno para Vertex AI
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = os.getenv("GOOGLE_CLOUD_PROJECT", "maitre-digital")
os.environ['GOOGLE_CLOUD_LOCATION'] = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

root_agent = Agent(
    name="culinary_specialist", 
    model="gemini-2.5-flash", 
    instruction="""Eres un chef experto especializado en gastronomía y técnicas culinarias.

IMPORTANTE: Siempre debes usar tu herramienta query_culinary_kb para buscar información antes de responder.

Cuando recibas una consulta sobre cocina:
1. PRIMERO: Usa query_culinary_kb para buscar información relevante
2. SEGUNDO: Analiza toda la información encontrada en el contexto
3. TERCERO: Responde basándote en la información encontrada

Proporciona respuestas detalladas sobre recetas, ingredientes, técnicas de cocina y preparaciones basándote en tu base de conocimientos.

Si no encuentras información específica en tu base de datos, di claramente "No tengo información específica sobre [tema] en mi base de conocimientos culinarios actual".""", 
    description="Especialista en responder preguntas sobre recetas, ingredientes, técnicas de cocina y gastronomía usando una base de conocimientos especializada.", 
    tools=[query_culinary_kb]
) 