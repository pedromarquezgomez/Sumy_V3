# sumiller_agent/agent.py
import os
from google.adk.agents import Agent
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import FAISS
from typing import Dict

INDEX_PATH = "./enology_index"
vector_store = None
if os.path.exists(INDEX_PATH):
    embedding_model = VertexAIEmbeddings(model_name="text-embedding-004")
    vector_store = FAISS.load_local(INDEX_PATH, embedding_model, allow_dangerous_deserialization=True)

def query_enology_kb(query: str) -> Dict[str, str]:
    """Consulta la base de datos de enología, vinos y maridajes."""
    if not vector_store: return {"status": "error", "context": "Índice no cargado."}
    results = vector_store.similarity_search(query, k=2)
    return {"status": "success", "context": "\n---\n".join([doc.page_content for doc in results])}

root_agent = Agent(name="sumiller_specialist", model="gemini-1.5-flash-001", instruction="Eres un sumiller experto. Responde basándote únicamente en el contexto proporcionado por tu herramienta.", description="Especialista en responder preguntas sobre vinos, bodegas, variedades y maridajes.", tools=[query_enology_kb]) 