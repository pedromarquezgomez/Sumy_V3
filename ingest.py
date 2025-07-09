# ingest.py
import os
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS

def create_index_for_domain(domain: str):
    print(f"--- Creando índice para el dominio: {domain} ---")
    local_docs_path = f"./knowledge_base/{domain}"
    index_save_path = f"./{domain}_index"

    if not os.path.exists(local_docs_path) or not os.listdir(local_docs_path):
        print(f"ADVERTENCIA: No se encontraron documentos en '{local_docs_path}'. Saltando.")
        return

    loader = DirectoryLoader(local_docs_path, glob="**/*.txt", show_progress=True)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    
    print(f"Creando embeddings y el índice FAISS para {len(docs)} trozos...")
    embedding_model = VertexAIEmbeddings(model_name="text-embedding-004")
    vector_store = FAISS.from_documents(docs, embedding_model)
    vector_store.save_local(index_save_path)
    print(f"Índice para '{domain}' guardado en '{index_save_path}'\n")

if __name__ == "__main__":
    knowledge_domains = ["nutrition", "culinary", "enology"]
    for domain in knowledge_domains:
        create_index_for_domain(domain)
    print("¡Proceso de ingesta de todos los índices completado!") 