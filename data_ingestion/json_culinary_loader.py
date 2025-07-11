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
        
        # Verificar si es la estructura antigua (array) o nueva (objeto)
        if isinstance(data, list):
            # Estructura antigua: array de categorías
            return self._process_array_format(data)
        else:
            # Estructura nueva: objeto anidado del restaurante
            return self._process_restaurant_format(data)
    
    def _process_array_format(self, data: List) -> List[Document]:
        """Procesa formato de array (estructura antigua)"""
        documents = []
        
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
            
            # También crear documentos individuales por plato
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
    
    def _process_restaurant_format(self, data: dict) -> List[Document]:
        """Procesa formato de objeto del restaurante (estructura nueva)"""
        documents = []
        
        # Obtener el nombre del restaurante
        restaurant_name = data.get('restaurante', {}).get('nombre', 'Restaurante')
        carta = data.get('restaurante', {}).get('carta', {})
        
        # Procesar cada sección de la carta
        for section_key, section_data in carta.items():
            if not isinstance(section_data, dict):
                continue
                
            section_name = section_data.get('nombre', section_key.replace('_', ' ').title())
            items = section_data.get('items', [])
            
            # Crear un documento por sección con todos sus platos
            section_content = f"RESTAURANTE: {restaurant_name}\n"
            section_content += f"SECCIÓN: {section_name}\n\n"
            
            for item in items:
                item_name = item.get('nombre', 'Sin nombre')
                description = item.get('descripcion', 'Sin descripción')
                price = item.get('precio', 'Sin precio')
                
                item_text = f"PLATO: {item_name}\n"
                item_text += f"DESCRIPCIÓN: {description}\n"
                item_text += f"PRECIO: {price}€\n\n"
                
                section_content += item_text
            
            # Crear documento para la sección
            if items:  # Solo crear documento si hay items
                doc = Document(
                    page_content=section_content,
                    metadata={
                        "restaurant": restaurant_name,
                        "section": section_name,
                        "section_key": section_key,
                        "source": "carta_restaurante",
                        "type": "menu_section",
                        "dishes_count": len(items)
                    }
                )
                documents.append(doc)
                
                # También crear documentos individuales por plato
                for item in items:
                    item_name = item.get('nombre', 'Sin nombre')
                    description = item.get('descripcion', 'Sin descripción')
                    price = item.get('precio', 'Sin precio')
                    
                    item_content = f"CARTA DE {restaurant_name} - {section_name}\n\n"
                    item_content += f"PLATO: {item_name}\n"
                    item_content += f"DESCRIPCIÓN: {description}\n"
                    item_content += f"PRECIO: {price}€\n"
                    item_content += f"SECCIÓN: {section_name}\n"
                    item_content += f"RESTAURANTE: {restaurant_name}\n"
                    
                    item_doc = Document(
                        page_content=item_content,
                        metadata={
                            "dish_name": item_name,
                            "section": section_name,
                            "restaurant": restaurant_name,
                            "price": price,
                            "source": "carta_restaurante",
                            "type": "individual_dish"
                        }
                    )
                    documents.append(item_doc)
        
        return documents 