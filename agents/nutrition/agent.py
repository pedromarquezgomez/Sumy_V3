# nutrition_agent/agent.py
import os
from google.adk.agents import Agent
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import FAISS
from typing import Dict

# Configurar variables de entorno para Vertex AI
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = os.getenv("GOOGLE_CLOUD_PROJECT", "maitre-digital")
os.environ['GOOGLE_CLOUD_LOCATION'] = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

INDEX_PATH = "./indexes/nutrition"
vector_store = None
if os.path.exists(INDEX_PATH):
    embedding_model = VertexAIEmbeddings(model_name="text-embedding-004")
    vector_store = FAISS.load_local(INDEX_PATH, embedding_model, allow_dangerous_deserialization=True)

def query_nutrition_kb(query: str) -> Dict[str, str]:
    """Consulta la base de datos de nutrición."""
    if not vector_store: return {"status": "error", "context": "Índice no cargado."}
    results = vector_store.similarity_search(query, k=2)
    return {"status": "success", "context": "\n---\n".join([doc.page_content for doc in results])}

root_agent = Agent(name="nutrition_specialist", model="gemini-2.5-flash", instruction="Eres un nutricionista experto. Responde basándote únicamente en el contexto proporcionado por tu herramienta.", description="Especialista en responder preguntas sobre nutrición, dietas, calorías y alimentación saludable.", tools=[query_nutrition_kb]) 