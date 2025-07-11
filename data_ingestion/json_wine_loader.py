import json
from langchain_core.documents import Document
from langchain_community.document_loaders.base import BaseLoader
from typing import List, Iterator

class VinosJsonLoader(BaseLoader):
    """Carga un archivo JSON de vinos, tratando cada vino como un documento.
    Soporta múltiples formatos de estructura JSON."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path

    def _format_wine_higueron(self, vino: dict) -> str:
        """Formatea vinos con estructura del archivo higueron_vinos.json"""
        content = f"Nombre del Vino: {vino.get('nombre', 'N/A')}\n"
        content += f"Ubicación: {vino.get('ubicación', 'N/A')}\n"
        content += f"Categoría: {vino.get('categoría', 'N/A')}\n"
        content += f"Bodega: {vino.get('bodega', 'N/A')}\n"
        content += f"Variedad: {vino.get('variedad', 'N/A')}\n"
        
        # Precios (pueden ser copa y/o botella)
        if vino.get('precio_copa'):
            content += f"Precio por copa: {vino.get('precio_copa')}\n"
        if vino.get('precio_botella'):
            content += f"Precio por botella: {vino.get('precio_botella')}\n"
        
        content += f"Descripción corta: {vino.get('descripción_corta', 'N/A')}\n"
        content += f"Descripción: {vino.get('descripción_larga', 'N/A')}\n"
        
        # Aromas (puede ser lista)
        aromas = vino.get('aromas', [])
        if aromas:
            content += f"Aromas: {', '.join(aromas)}\n"
        else:
            content += "Aromas: N/A\n"
        
        # Elaboración (puede ser lista)
        elaboracion = vino.get('elaboración', [])
        if elaboracion:
            content += f"Elaboración: {', '.join(elaboracion)}\n"
        else:
            content += "Elaboración: N/A\n"
        
        return content

    def _format_wine_legacy(self, vino: dict) -> str:
        """Formatea vinos con estructura legacy"""
        content = f"Nombre del Vino: {vino.get('name', 'N/A')}\n"
        content += f"Tipo: {vino.get('type', 'N/A')}, Región: {vino.get('region', 'N/A')}\n"
        content += f"Bodega: {vino.get('winery', 'N/A')}\n"
        content += f"Graduación: {vino.get('alcohol', 'N/A')}% vol.\n"
        content += f"Precio: {vino.get('price', 'N/A')}€\n"
        content += f"Temperatura de servicio: {vino.get('temperature', 'N/A')}\n"
        content += f"Varietal: {vino.get('grape', 'N/A')}\n"
        content += f"Puntuación: {vino.get('rating', 'N/A')}/100\n"
        content += f"Crianza: {vino.get('crianza', 'N/A')}\n"
        content += f"Maridaje: {vino.get('pairing', 'N/A')}\n"
        content += f"Descripción: {vino.get('description', 'N/A')}"
        return content

    def lazy_load(self) -> Iterator[Document]:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for vino in data:
            # Detectar el formato basándose en los campos presentes
            if 'nombre' in vino:
                # Formato nuevo (higueron_vinos.json)
                content = self._format_wine_higueron(vino)
                wine_name = vino.get('nombre', 'N/A')
                metadata = {
                    "source": self.file_path, 
                    "wine_name": wine_name,
                    "format": "higueron",
                    "category": vino.get('categoría', 'N/A'),
                    "bodega": vino.get('bodega', 'N/A')
                }
            else:
                # Formato legacy
                content = self._format_wine_legacy(vino)
                wine_name = vino.get('name', 'N/A')
                metadata = {
                    "source": self.file_path, 
                    "wine_name": wine_name,
                    "format": "legacy"
                }
            
            yield Document(page_content=content, metadata=metadata)
    
    def load(self) -> List[Document]:
        return list(self.lazy_load())