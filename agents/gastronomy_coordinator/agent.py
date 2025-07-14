# coordinator_agent/agent.py
import os
import sys
import vertexai
from google.adk.agents import Agent
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import FAISS
from typing import Dict

# Agregar el directorio de agentes al path para imports relativos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.usda_api_client import usda_client

# Configurar variables de entorno para Vertex AI
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = os.getenv("GOOGLE_CLOUD_PROJECT", "maitre-digital")
os.environ['GOOGLE_CLOUD_LOCATION'] = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# Configuración centralizada de Vertex AI
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "maitre-digital")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
vertexai.init(project=project_id, location=location)

# Modelo de embeddings compartido
embedding_model = VertexAIEmbeddings(model_name="text-embedding-004")

# Estado compartido del coordinador
shared_state = {
    "conversation_context": [],
    "user_preferences": {},
    "session_metadata": {}
}

# Construir la ruta al archivo de instrucciones
instruction_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instrucciones', 'COORDINATOR_INSTRUCTION.txt')

# Leer las instrucciones desde el archivo
with open(instruction_path, 'r', encoding='utf-8') as f:
    COORDINATOR_INSTRUCTION = f.read()

# --- TOOLS ESPECIALIZADAS INTEGRADAS ---
def load_knowledge_base(index_path: str, agent_name: str):
    """Carga una base de conocimientos vectorial específica"""
    if os.path.exists(index_path):
        try:
            vector_store = FAISS.load_local(
                index_path, 
                embedding_model, 
                allow_dangerous_deserialization=True
            )
            print(f"Índice cargado exitosamente para {agent_name} desde '{index_path}'")
            return vector_store
        except Exception as e:
            print(f"Error al cargar el índice para {agent_name}: {e}")
            return None
    else:
        print(f"Advertencia: No se encontró el directorio del índice en '{index_path}' para {agent_name}.")
        return None

# Cargar bases de conocimientos especializadas
sumiller_kb = load_knowledge_base("./indexes/enology_index", "sumiller")
culinary_kb = load_knowledge_base("./indexes/culinary_index", "culinario")
nutrition_kb = load_knowledge_base("./indexes/nutrition_index", "nutrición")

def query_sumiller_tool(query: str) -> Dict[str, str]:
    """Tool integrada del sumiller para consultas de vinos y maridajes"""
    if not sumiller_kb:
        return {
            "status": "error",
            "context": "La base de conocimientos de vinos no está disponible temporalmente.",
            "tool": "sumiller"
        }
    
    try:
        results = sumiller_kb.similarity_search(query, k=3)
        formatted_context = []
        for i, doc in enumerate(results, 1):
            content = doc.page_content.strip()
            formatted_context.append(f"--- RESULTADO {i} ---\n{content}")
        
        if not formatted_context:
            return {
                "status": "partial",
                "context": f"No encontré información específica sobre '{query}' en la base de conocimientos de vinos.",
                "tool": "sumiller"
            }
        
        # Actualizar estado compartido
        shared_state["conversation_context"].append({
            "type": "sumiller_query",
            "query": query,
            "timestamp": "now"
        })
        
        return {
            "status": "success",
            "context": "\n\n".join(formatted_context),
            "tool": "sumiller",
            "source": "knowledge_base"
        }
    except Exception as e:
        return {
            "status": "error",
            "context": f"Error técnico en consulta de vinos: {str(e)}",
            "tool": "sumiller"
        }

def query_culinary_tool(query: str) -> Dict[str, str]:
    """Tool integrada del chef para consultas culinarias"""
    if not culinary_kb:
        return {
            "status": "error",
            "context": "La base de conocimientos culinaria no está disponible temporalmente.",
            "tool": "culinary"
        }
    
    try:
        results = culinary_kb.similarity_search(query, k=2)
        formatted_context = []
        for i, doc in enumerate(results, 1):
            content = doc.page_content.strip()
            formatted_context.append(f"--- RESULTADO {i} ---\n{content}")
        
        if not formatted_context:
            return {
                "status": "partial",
                "context": f"No encontré información específica sobre '{query}' en la base de conocimientos culinaria.",
                "tool": "culinary"
            }
        
        # Actualizar estado compartido
        shared_state["conversation_context"].append({
            "type": "culinary_query",
            "query": query,
            "timestamp": "now"
        })
        
        return {
            "status": "success",
            "context": "\n\n".join(formatted_context),
            "tool": "culinary",
            "source": "knowledge_base"
        }
    except Exception as e:
        return {
            "status": "error",
            "context": f"Error técnico en consulta culinaria: {str(e)}",
            "tool": "culinary"
        }

def query_nutrition_tool(query: str) -> Dict[str, str]:
    """Tool integrada del nutricionista con acceso a base de conocimientos y API USDA"""
    # Primero intentar con la base de conocimientos
    kb_result = None
    if nutrition_kb:
        try:
            results = nutrition_kb.similarity_search(query, k=2)
            if results:
                formatted_context = []
                for i, doc in enumerate(results, 1):
                    content = doc.page_content.strip()
                    formatted_context.append(f"--- RESULTADO {i} ---\n{content}")
                kb_result = "\n\n".join(formatted_context)
        except Exception as e:
            print(f"Error en knowledge base de nutrición: {e}")
    
    # Intentar también con API USDA para datos específicos
    api_result = None
    try:
        search_results = usda_client.search_foods(
            query=query,
            data_types=["Foundation", "SR Legacy"],
            page_size=2
        )
        api_result = usda_client.format_nutrition_data(search_results)
        if "No se encontraron alimentos" in api_result:
            api_result = None
    except Exception as e:
        print(f"Error en API USDA: {e}")
    
    # Combinar resultados
    combined_context = []
    if kb_result:
        combined_context.append(f"=== INFORMACIÓN NUTRICIONAL ESPECIALIZADA ===\n{kb_result}")
    if api_result:
        combined_context.append(f"=== DATOS NUTRICIONALES USDA ===\n{api_result}")
    
    if not combined_context:
        return {
            "status": "partial",
            "context": f"No encontré información específica sobre '{query}' en las bases de datos nutricionales.",
            "tool": "nutrition"
        }
    
    # Actualizar estado compartido
    shared_state["conversation_context"].append({
        "type": "nutrition_query",
        "query": query,
        "timestamp": "now"
    })
    
    return {
        "status": "success",
        "context": "\n\n".join(combined_context),
        "tool": "nutrition",
        "source": "knowledge_base_and_api"
    }

def coordinator_presenter(query: str) -> str:
    """
    El coordinador analiza la consulta y usa sus tools integradas para responder directamente.
    """
    # Saludo inicial del Maître
    intro = "Bienvenido/a, soy Claude, su Maître Digital. "
    
    # Analizar consulta y usar tool apropiada
    if any(palabra in query.lower() for palabra in ["vino", "maridaje", "bodega", "albariño", "tinto", "blanco", "pescado"]):
        intro += "Excelente consulta sobre vinos y maridajes. 🍷 Consultando mi base de conocimientos enológica...\n\n"
        respuesta = query_sumiller_tool(query)
        respuesta_especialista = respuesta.get('context', str(respuesta))
        
        return f"{intro}Basándome en mi expertise enológico, me complace ofrecerle la siguiente recomendación:\n\n{respuesta_especialista}\n\nComo su Maître Digital, puedo asegurarle que esta selección ha sido cuidadosamente elegida para complementar perfectamente su experiencia gastronómica. ¿Hay algo más en lo que pueda asistirle hoy?"
        
    elif any(palabra in query.lower() for palabra in ["receta", "cocina", "ingrediente", "preparación", "chef", "paella", "plato", "hacer", "como se hace"]):
        intro += "Una consulta culinaria fascinante. 🍳 Consultando mi base de conocimientos gastronómica...\n\n"
        respuesta = query_culinary_tool(query)
        respuesta_especialista = respuesta.get('context', str(respuesta))
        
        return f"{intro}Con mi expertise culinario, puedo proporcionarle la siguiente información especializada:\n\n{respuesta_especialista}\n\nEstoy seguro de que encontrará esta información culinaria de gran utilidad. Como Maître Digital, siempre busco asegurar la excelencia en cada aspecto de su experiencia gastronómica. ¿Necesita alguna recomendación adicional?"
        
    elif any(palabra in query.lower() for palabra in ["caloría", "nutrición", "vitamina", "dieta", "salud"]):
        intro += "Una consulta muy importante sobre nutrición y salud. 🥗 Consultando mis bases de datos nutricionales especializadas...\n\n"
        respuesta = query_nutrition_tool(query)
        respuesta_especialista = respuesta.get('context', str(respuesta))
        
        return f"{intro}Con mi conocimiento nutricional especializado, puedo facilitarle esta información detallada:\n\n{respuesta_especialista}\n\nComo su Maître Digital, me preocupo tanto por el placer gastronómico como por el bienestar de nuestros clientes. ¿Puedo ayudarle con alguna consulta adicional sobre nutrición o maridajes saludables?"
        
    else:
        return f"{intro}Me complace recibir su consulta. Para brindarle el mejor servicio posible, ¿podría especificar más sobre qué aspecto gastronómico le interesa? Puedo asistirle con vinos y maridajes 🍷, consultas culinarias 🍳, o aspectos nutricionales 🥗. Como Maître Digital integrado, tengo acceso directo a todas mis bases de conocimientos especializadas para garantizar una experiencia gastronómica excepcional."

root_agent = Agent(
    name="gastronomy_coordinator",
    model="gemini-2.5-flash",
    instruction=COORDINATOR_INSTRUCTION + "\n\nIMPORTANTE: Debes usar ÚNICAMENTE la herramienta coordinator_presenter para responder a las consultas. Como Maître Digital integrado, tienes acceso directo a todas las bases de conocimientos especializadas a través de esta herramienta. NO necesitas transferir a otros agentes - responde siempre directamente usando tus tools integradas.",
    tools=[coordinator_presenter, query_sumiller_tool, query_culinary_tool, query_nutrition_tool]
) 