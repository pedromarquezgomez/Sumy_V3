import json
from langchain_core.documents import Document
from langchain_community.document_loaders.base import BaseLoader
from typing import List, Iterator

class VinosJsonLoader(BaseLoader):
    """Carga un archivo JSON de vinos, tratando cada vino como un documento."""
    def __init__(self, file_path: str):
        self.file_path = file_path

    def lazy_load(self) -> Iterator[Document]:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for vino in data:
            content = f"Nombre del Vino: {vino.get('name', 'N/A')}\n"
            content += f"Tipo: {vino.get('type', 'N/A')}, Región: {vino.get('region', 'N/A')}\n"
            content += f"Bodega: {vino.get('winery', 'N/A')}\n"
            content += f"Maridaje: {vino.get('pairing', 'N/A')}\n"
            content += f"Descripción: {vino.get('description', 'N/A')}"
            metadata = {"source": self.file_path, "wine_name": vino.get('name', 'N/A')}
            yield Document(page_content=content, metadata=metadata)
    
    def load(self) -> List[Document]:
        return list(self.lazy_load())