import json
from typing import List
from langchain.docstore.document import Document

class CulinaryJsonLoader:
    """Loader para archivos JSON con datos culinarios/carta de restaurante"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def load(self) -> List[Document]:
        """Carga y convierte los datos de la carta en documentos"""
        with open(self.file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        documents = []
        
        # Procesar cada categoría
        for category_data in data:
            category = category_data.get('category', 'Sin categoría')
            dishes = category_data.get('dishes', [])
            
            # Crear un documento por categoría con todos sus platos
            category_content = f"CATEGORÍA: {category}\n\n"
            
            for dish in dishes:
                dish_name = dish.get('dish_name', 'Sin nombre')
                description = dish.get('description', 'Sin descripción')
                price = dish.get('price_eur', 'Sin precio')
                
                dish_text = f"PLATO: {dish_name}\n"
                dish_text += f"DESCRIPCIÓN: {description}\n"
                dish_text += f"PRECIO: {price}€\n\n"
                
                category_content += dish_text
            
            # Crear documento para la categoría
            doc = Document(
                page_content=category_content,
                metadata={
                    "category": category,
                    "source": "carta_restaurante",
                    "type": "culinary_menu",
                    "dishes_count": len(dishes)
                }
            )
            documents.append(doc)
            
            # También crear documentos individuales por plato para búsquedas específicas
            for dish in dishes:
                dish_name = dish.get('dish_name', 'Sin nombre')
                description = dish.get('description', 'Sin descripción')
                price = dish.get('price_eur', 'Sin precio')
                
                dish_content = f"CARTA DEL RESTAURANTE - {category}\n\n"
                dish_content += f"PLATO: {dish_name}\n"
                dish_content += f"DESCRIPCIÓN: {description}\n"
                dish_content += f"PRECIO: {price}€\n"
                dish_content += f"CATEGORÍA: {category}\n"
                
                dish_doc = Document(
                    page_content=dish_content,
                    metadata={
                        "dish_name": dish_name,
                        "category": category,
                        "price_eur": price,
                        "source": "carta_restaurante",
                        "type": "individual_dish"
                    }
                )
                documents.append(dish_doc)
        
        return documents 