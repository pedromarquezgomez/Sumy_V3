import os
import shutil
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS
# Importación actualizada desde el mismo directorio de ingesta
from .json_wine_loader import VinosJsonLoader
# --- Constantes de Rutas ---
# Rutas relativas desde la raíz del proyecto
KNOWLEDGE_BASE_DIR = "./knowledge_base"
INDEXES_DIR = "./indexes"


def ingest_text_files(domain_path: str, chunk_strategy: str) -> list:
    """Carga y divide documentos de texto de un directorio."""
    print(f"-> Procesando archivos de texto desde: {domain_path}")
    loader = DirectoryLoader(domain_path, glob="**/*.txt", show_progress=True)
    documents = loader.load()

    if not documents:
        print("-> No se encontraron archivos de texto.")
        return []

    if chunk_strategy == "semantic":
        print("--> Aplicando estrategia de chunking semántico (párrafos).")
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ". ", " "],
            chunk_size=1500,
            chunk_overlap=250
        )
    else:
        print("--> Aplicando estrategia de chunking por defecto.")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )

    chunks = splitter.split_documents(documents)
    print(f"--> Se dividieron en {len(chunks)} chunks.")
    return chunks

def ingest_structured_json(domain_path: str) -> list:
    """Carga documentos desde un archivo JSON estructurado (un doc por item)."""
    print(f"-> Procesando archivo JSON desde: {domain_path}")
    # Asumimos que solo hay un archivo JSON en el directorio
    try:
        json_file_name = os.listdir(domain_path)[0]
        json_file_path = os.path.join(domain_path, json_file_name)
        loader = VinosJsonLoader(file_path=json_file_path)
        docs = loader.load()
        print(f"--> Se cargaron {len(docs)} documentos estructurados.")
        return docs
    except (FileNotFoundError, IndexError):
        print(f"-> No se encontró ningún archivo JSON en {domain_path}.")
        return []


if __name__ == "__main__":
    print("🚀 Iniciando proceso de ingesta de conocimiento...")

    # Asegurarse de que el directorio de índices exista
    os.makedirs(INDEXES_DIR, exist_ok=True)
    
    embedding_model = VertexAIEmbeddings(model_name="text-embedding-004")

    # --- 1. Ingesta para Enología (Sumiller) ---
    print("\n--- 🍷 Procesando dominio: Enología ---")
    enology_index_path = os.path.join(INDEXES_DIR, "enology_index")
    if os.path.exists(enology_index_path):
        shutil.rmtree(enology_index_path)

    unstructured_path = os.path.join(KNOWLEDGE_BASE_DIR, "enology", "unstructured")
    structured_path = os.path.join(KNOWLEDGE_BASE_DIR, "enology", "structured")

    unstructured_docs = ingest_text_files(unstructured_path, "semantic")
    structured_docs = ingest_structured_json(structured_path)
    
    all_enology_docs = unstructured_docs + structured_docs
    
    if all_enology_docs:
        enology_store = FAISS.from_documents(all_enology_docs, embedding_model)
        enology_store.save_local(enology_index_path)
        print(f"✅ Índice de Enología unificado creado con {len(all_enology_docs)} documentos en: {enology_index_path}")
    else:
        print("⚠️ No se encontraron documentos para crear el índice de Enología.")

    # --- 2. Ingesta para Cocina (Culinario) ---
    print("\n--- 🍳 Procesando dominio: Culinario ---")
    culinary_index_path = os.path.join(INDEXES_DIR, "culinary_index")
    if os.path.exists(culinary_index_path):
        shutil.rmtree(culinary_index_path)

    culinary_docs_path = os.path.join(KNOWLEDGE_BASE_DIR, "culinary")
    culinary_docs = ingest_text_files(culinary_docs_path, "default")

    if culinary_docs:
        culinary_store = FAISS.from_documents(culinary_docs, embedding_model)
        culinary_store.save_local(culinary_index_path)
        print(f"✅ Índice Culinario creado con {len(culinary_docs)} chunks en: {culinary_index_path}")
    else:
        print("⚠️ No se encontraron documentos para crear el índice Culinario.")

    # --- 3. Ingesta para Nutrición ---
    print("\n--- 🥗 Procesando dominio: Nutrición ---")
    nutrition_index_path = os.path.join(INDEXES_DIR, "nutrition_index")
    if os.path.exists(nutrition_index_path):
        shutil.rmtree(nutrition_index_path)

    nutrition_docs_path = os.path.join(KNOWLEDGE_BASE_DIR, "nutrition")
    nutrition_docs = ingest_text_files(nutrition_docs_path, "default")
    
    if nutrition_docs:
        nutrition_store = FAISS.from_documents(nutrition_docs, embedding_model)
        nutrition_store.save_local(nutrition_index_path)
        print(f"✅ Índice de Nutrición creado con {len(nutrition_docs)} chunks en: {nutrition_index_path}")
    else:
        print("⚠️ No se encontraron documentos para crear el índice de Nutrición.")

    print("\n✨ ¡Proceso de ingesta completado exitosamente! ✨")