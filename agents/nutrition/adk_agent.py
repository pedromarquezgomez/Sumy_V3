# agents/nutrition/adk_agent.py
import os
import sys
import vertexai
from google.adk.agents import Agent
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import FAISS
from typing import Dict

# Añadir el directorio padre para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.usda_api_client import usda_client

# Configuración centralizada de Vertex AI
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "maitre-digital")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
vertexai.init(project=project_id, location=location)

# Modelo de embeddings
embedding_model = VertexAIEmbeddings(model_name="text-embedding-004")

# Cargar instrucciones
instruction_path = os.path.join(os.path.dirname(__file__), '..', 'instrucciones', 'NUTRITION_INSTRUCTION.txt')
with open(instruction_path, 'r', encoding='utf-8') as f:
    NUTRITION_INSTRUCTION = f.read()

# Cargar base de conocimientos
def load_nutrition_knowledge():
    """Carga la base de conocimientos nutricional"""
    index_path = "./indexes/nutrition_index"
    if os.path.exists(index_path):
        try:
            vector_store = FAISS.load_local(
                index_path, 
                embedding_model, 
                allow_dangerous_deserialization=True
            )
            print(f"✅ Índice nutricional cargado exitosamente desde '{index_path}'")
            return vector_store
        except Exception as e:
            print(f"❌ Error al cargar índice nutricional: {e}")
            return None
    else:
        print(f"⚠️ No se encontró índice nutricional en '{index_path}'")
        return None

# Inicializar base de conocimientos
nutrition_kb = load_nutrition_knowledge()

def query_nutrition_knowledge(query: str) -> Dict[str, str]:
    """
    Consulta especializada en nutrición, dietas y salud.
    Herramienta principal del agente nutricionista.
    """
    if not nutrition_kb:
        return {
            "status": "error",
            "context": "La base de conocimientos nutricional no está disponible temporalmente.",
            "suggestion": "Como nutricionista experto, puedo ayudarte con información nutricional general. ¿Qué aspecto de la nutrición te interesa?",
            "agent": "nutricionista"
        }
    
    try:
        # Búsqueda vectorial especializada
        results = nutrition_kb.similarity_search(query, k=3)
        formatted_context = []
        
        for i, doc in enumerate(results, 1):
            content = doc.page_content.strip()
            formatted_context.append(f"--- CONOCIMIENTO NUTRICIONAL {i} ---\n{content}")
        
        if not formatted_context:
            return {
                "status": "partial",
                "context": f"No encontré información específica sobre '{query}' en mi base de conocimientos nutricional.",
                "suggestion": "Como nutricionista, puedo ayudarte con calorías, macronutrientes, dietas, o análisis nutricional.",
                "agent": "nutricionista"
            }
        
        return {
            "status": "success",
            "context": "\n\n".join(formatted_context),
            "source": "nutrition_knowledge_base",
            "query_used": query,
            "agent": "nutricionista"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "context": f"Error técnico en consulta nutricional: {str(e)}",
            "suggestion": "Por favor, intenta reformular tu consulta sobre nutrición y dietas.",
            "agent": "nutricionista"
        }

def get_usda_nutrition_data(food_query: str) -> Dict[str, str]:
    """
    Obtiene datos nutricionales precisos desde la API USDA.
    Herramienta avanzada del nutricionista.
    """
    try:
        # Búsqueda en la API USDA
        search_results = usda_client.search_foods(
            query=food_query,
            data_types=["Foundation", "SR Legacy"],  # Datos más confiables
            page_size=3
        )
        
        # Formatear resultados
        formatted_data = usda_client.format_nutrition_data(search_results)
        
        if "No se encontraron alimentos" in formatted_data:
            return {
                "status": "partial",
                "context": f"No encontré datos específicos para '{food_query}' en la base de datos USDA.",
                "suggestion": "Como nutricionista, puedo buscar alimentos similares o proporcionarte información nutricional general. ¿Podrías ser más específico?",
                "agent": "nutricionista"
            }
        
        return {
            "status": "success",
            "context": formatted_data,
            "source": "USDA_FoodData_Central_API",
            "query_used": food_query,
            "agent": "nutricionista"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "context": f"No pude acceder a la base de datos USDA: {str(e)}",
            "suggestion": "Como nutricionista, puedo proporcionarte información nutricional general. ¿Te gustaría que consulte mi base de conocimientos?",
            "agent": "nutricionista"
        }

def analyze_nutritional_content(food_list: str) -> Dict[str, str]:
    """
    Analiza el contenido nutricional de múltiples alimentos.
    Herramienta especializada del nutricionista.
    """
    # Combinar base de conocimientos con datos USDA
    combined_analysis = []
    
    try:
        # Análisis desde base de conocimientos
        if nutrition_kb:
            kb_query = f"análisis nutricional {food_list} calorías proteínas carbohidratos"
            kb_results = nutrition_kb.similarity_search(kb_query, k=2)
            
            if kb_results:
                kb_info = []
                for i, doc in enumerate(kb_results, 1):
                    content = doc.page_content.strip()
                    kb_info.append(f"--- ANÁLISIS NUTRICIONAL {i} ---\n{content}")
                
                if kb_info:
                    combined_analysis.append("=== ANÁLISIS NUTRICIONAL ESPECIALIZADO ===\n" + "\n\n".join(kb_info))
        
        # Análisis desde API USDA
        try:
            usda_results = usda_client.search_foods(
                query=food_list,
                data_types=["Foundation", "SR Legacy"],
                page_size=2
            )
            usda_data = usda_client.format_nutrition_data(usda_results)
            
            if "No se encontraron alimentos" not in usda_data:
                combined_analysis.append(f"=== DATOS NUTRICIONALES USDA ===\n{usda_data}")
        
        except Exception as e:
            print(f"Error en API USDA para análisis: {e}")
        
        if not combined_analysis:
            return {
                "status": "partial",
                "context": f"No pude encontrar análisis nutricional específico para '{food_list}'.",
                "suggestion": "Como nutricionista, puedo ayudarte con análisis nutricional general o de alimentos específicos.",
                "agent": "nutricionista"
            }
        
        return {
            "status": "success",
            "context": "\n\n".join(combined_analysis),
            "source": "nutritional_analysis_combined",
            "query_used": food_list,
            "agent": "nutricionista"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "context": f"Error en análisis nutricional: {str(e)}",
            "suggestion": "Por favor, especifica los alimentos que quieres analizar nutricionalmente.",
            "agent": "nutricionista"
        }

# Configuración del agente nutricionista especializado
nutrition_agent = Agent(
    name="nutrition_specialist",
    model="gemini-2.5-flash",  # Modelo optimizado para especialización
    instruction=NUTRITION_INSTRUCTION + """

HERRAMIENTAS ESPECIALIZADAS:
- query_nutrition_knowledge: Para consultas generales sobre nutrición, dietas, salud
- get_usda_nutrition_data: Para obtener datos nutricionales precisos de alimentos específicos
- analyze_nutritional_content: Para análisis nutricional completo de múltiples alimentos

PROTOCOLO DE RESPUESTA:
1. Analiza la consulta para determinar si es sobre información general, datos específicos o análisis
2. Usa la herramienta más apropiada según el tipo de consulta
3. Presenta la información como un nutricionista experto y accesible
4. Incluye recomendaciones de salud cuando sea apropiado
5. Mantén el tono profesional pero comprensible

ESPECIALIZACIÓN: Eres el nutricionista experto del equipo. Tu conocimiento abarca:
- Análisis nutricional de alimentos y platos
- Dietas especiales y restricciones alimentarias
- Macronutrientes y micronutrientes
- Calorías y valores nutricionales
- Recomendaciones de salud y bienestar
""",
    description="Nutricionista especialista en análisis nutricional, dietas y salud con acceso a base de conocimientos y API USDA",
    tools=[query_nutrition_knowledge, get_usda_nutrition_data, analyze_nutritional_content],
    output_key="nutrition_analysis"  # ADK: Guardar análisis en estado
)

# Configurar nombres únicos para las herramientas
query_nutrition_knowledge.__name__ = "query_nutrition_knowledge"
get_usda_nutrition_data.__name__ = "get_usda_nutrition_data"
analyze_nutritional_content.__name__ = "analyze_nutritional_content"

print("🥗 Agente nutricionista especializado inicializado correctamente")