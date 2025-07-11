import os
import requests
import json
from typing import Dict, List, Optional
import time

class USDAFoodDataAPI:
    """Cliente para la API USDA FoodData Central"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("USDA_API_KEY", "ToxKfxHz0Twh1ED6COLu4gYkdRjQYLpzEfVH6JsT")
        self.base_url = "https://api.nal.usda.gov/fdc/v1"
        self.session = requests.Session()
        
        # Rate limiting: 1000 requests/hour = ~16 requests/minute
        self.last_request_time = 0
        self.min_request_interval = 4  # seconds between requests (safe margin)
        
        # Diccionario de traducción español -> inglés para alimentos comunes
        self.translation_dict = {
            'salmón': 'salmon',
            'salmon': 'salmon',
            'pollo': 'chicken',
            'pechuga de pollo': 'chicken breast',
            'pecho de pollo': 'chicken breast',
            'ternera': 'beef',
            'carne de res': 'beef',
            'cerdo': 'pork',
            'pescado': 'fish',
            'atún': 'tuna',
            'bacalao': 'cod',
            'merluza': 'hake',
            'arroz': 'rice',
            'pasta': 'pasta',
            'pan': 'bread',
            'huevo': 'egg',
            'huevos': 'eggs',
            'leche': 'milk',
            'queso': 'cheese',
            'yogur': 'yogurt',
            'mantequilla': 'butter',
            'aceite': 'oil',
            'aceite de oliva': 'olive oil',
            'tomate': 'tomato',
            'tomates': 'tomatoes',
            'cebolla': 'onion',
            'ajo': 'garlic',
            'patata': 'potato',
            'papa': 'potato',
            'patatas': 'potatoes',
            'papas': 'potatoes',
            'zanahoria': 'carrot',
            'brócoli': 'broccoli',
            'espinacas': 'spinach',
            'lechuga': 'lettuce',
            'manzana': 'apple',
            'naranja': 'orange',
            'plátano': 'banana',
            'fresa': 'strawberry',
            'fresas': 'strawberries',
            'uva': 'grape',
            'uvas': 'grapes',
            'almendras': 'almonds',
            'nueces': 'walnuts',
            'avena': 'oats',
            'quinoa': 'quinoa',
            'lentejas': 'lentils',
            'garbanzos': 'chickpeas',
            'frijoles': 'beans',
            'judías': 'beans'
        }
    
    def _translate_query(self, query: str) -> str:
        """
        Traduce términos comunes del español al inglés para la API USDA
        """
        query_lower = query.lower().strip()
        
        # Buscar coincidencia exacta primero
        if query_lower in self.translation_dict:
            return self.translation_dict[query_lower]
        
        # Buscar coincidencias parciales
        for spanish_term, english_term in self.translation_dict.items():
            if spanish_term in query_lower:
                return english_term
        
        # Si no encuentra traducción, devolver original (podría ya estar en inglés)
        return query
    
    def _rate_limit(self):
        """Implementa rate limiting simple"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def search_foods(self, query: str, data_types: List[str] = None, page_size: int = 5) -> Dict:
        """
        Busca alimentos en la API USDA
        
        Args:
            query: Término de búsqueda en español o inglés (se traduce automáticamente)
            data_types: Tipos de datos a incluir ["Foundation", "SR Legacy", "Survey", "Branded"]
            page_size: Número de resultados (máximo 200)
        """
        self._rate_limit()
        
        # Traducir consulta al inglés
        english_query = self._translate_query(query)
        
        url = f"{self.base_url}/foods/search"
        
        payload = {
            "query": english_query,  # Usar consulta traducida
            "pageSize": min(page_size, 10),  # Limitar para no saturar respuestas
            "requireAllWords": False
        }
        
        if data_types:
            payload["dataType"] = data_types
        else:
            # Por defecto, usar datos más confiables
            payload["dataType"] = ["Foundation", "SR Legacy"]
        
        params = {"api_key": self.api_key}
        
        try:
            response = self.session.post(
                url, 
                json=payload, 
                params=params,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            # Agregar información de traducción al resultado
            if english_query != query:
                result['translation_info'] = f"Consulta traducida: '{query}' → '{english_query}'"
            
            return result
        except requests.exceptions.RequestException as e:
            return {"error": f"Error en API USDA: {str(e)}", "foods": []}
    
    def format_nutrition_data(self, food_data: Dict) -> str:
        """
        Formatea los datos nutricionales de la API en texto legible
        """
        if "error" in food_data:
            return f"Error: {food_data['error']}"
        
        # Mostrar información de traducción si está disponible
        result_header = ""
        if "translation_info" in food_data:
            result_header = f"📝 {food_data['translation_info']}\n\n"
        
        if "foods" in food_data:
            # Es resultado de búsqueda
            foods = food_data.get("foods", [])
            if not foods:
                return result_header + "No se encontraron alimentos para la búsqueda."
            
            formatted_results = [result_header] if result_header else []
            for food in foods[:3]:  # Solo primeros 3 resultados
                result = f"**{food.get('description', 'Sin nombre')}**\n"
                result += f"- FDC ID: {food.get('fdcId')}\n"
                result += f"- Tipo: {food.get('dataType', 'N/A')}\n"
                
                # Nutrientes principales si están disponibles
                nutrients = food.get('foodNutrients', [])
                key_nutrients = {}
                
                for nutrient in nutrients:
                    name = nutrient.get('nutrientName', '').lower()
                    value = nutrient.get('value')
                    unit = nutrient.get('unitName', '')
                    
                    if value is not None:
                        if 'energy' in name or 'calorie' in name:
                            key_nutrients['Calorías'] = f"{value} {unit}"
                        elif 'protein' in name:
                            key_nutrients['Proteína'] = f"{value}g"
                        elif 'carbohydrate' in name and 'by difference' in name:
                            key_nutrients['Carbohidratos'] = f"{value}g"
                        elif 'total lipid' in name or ('fat' in name and 'saturated' not in name):
                            key_nutrients['Grasas totales'] = f"{value}g"
                        elif 'fiber' in name:
                            key_nutrients['Fibra'] = f"{value}g"
                        elif 'sodium' in name:
                            key_nutrients['Sodio'] = f"{value}mg"
                
                if key_nutrients:
                    result += "- Nutrientes principales:\n"
                    for nutrient, value in key_nutrients.items():
                        result += f"  - {nutrient}: {value}\n"
                
                formatted_results.append(result)
            
            return "\n".join(formatted_results)
        
        else:
            # Es detalle de un alimento específico
            result = f"**{food_data.get('description', 'Alimento')}**\n"
            result += f"- FDC ID: {food_data.get('fdcId')}\n"
            result += f"- Categoría: {food_data.get('foodCategory', {}).get('description', 'N/A')}\n"
            
            nutrients = food_data.get('foodNutrients', [])
            if nutrients:
                result += "- Información nutricional por 100g:\n"
                for nutrient in nutrients[:15]:  # Primeros 15 nutrientes
                    name = nutrient.get('nutrient', {}).get('name')
                    value = nutrient.get('amount')
                    unit = nutrient.get('nutrient', {}).get('unitName')
                    
                    if name and value is not None:
                        result += f"  - {name}: {value} {unit}\n"
            
            return result

# Instancia global del cliente
usda_client = USDAFoodDataAPI()