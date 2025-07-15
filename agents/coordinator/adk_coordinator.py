# agents/coordinator/adk_coordinator.py
import os
import sys
import vertexai
from google.adk.agents import Agent
from typing import Dict

# Añadir el directorio padre para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar agentes especializados
from agents.sumiller.adk_agent import sumiller_agent
from agents.culinary.adk_agent import culinary_agent
from agents.nutrition.adk_agent import nutrition_agent

# Resetear parent agents para evitar conflictos
sumiller_agent.parent_agent = None
culinary_agent.parent_agent = None
nutrition_agent.parent_agent = None

# Configuración centralizada de Vertex AI
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "maitre-digital")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
vertexai.init(project=project_id, location=location)

# Cargar instrucciones del coordinador
instruction_path = os.path.join(os.path.dirname(__file__), '..', 'instrucciones', 'COORDINATOR_INSTRUCTION.txt')
with open(instruction_path, 'r', encoding='utf-8') as f:
    COORDINATOR_INSTRUCTION = f.read()

# Estado compartido del coordinador mejorado
coordinator_state = {
    "conversation_history": [],
    "user_preferences": {},
    "session_metadata": {},
    "agent_interactions": [],
    "last_recommendations": {}
}

def coordinate_gastronomy_experience(query: str) -> Dict[str, str]:
    """
    Herramienta principal del coordinador que analiza consultas y coordina respuestas.
    Utiliza delegación inteligente a sub-agentes especializados.
    """
    
    try:
        # Saludo y contexto inicial
        intro = "Bienvenido/a, soy Claude, su Maître Digital. "
        
        # Actualizar historial de conversación
        coordinator_state["conversation_history"].append({
            "query": query,
            "timestamp": "now",
            "type": "user_query"
        })
        
        # Análisis inteligente de la consulta
        query_lower = query.lower()
        
        # Determinar tipo de consulta y agente apropiado
        if any(palabra in query_lower for palabra in [
            "vino", "maridaje", "bodega", "albariño", "tinto", "blanco", 
            "rosado", "espumoso", "champagne", "cava", "sommelier", "cata"
        ]):
            intro += "Excelente consulta sobre vinos y maridajes. 🍷 "
            intro += "Permíteme consultar con nuestro sumiller especialista para ofrecerle la mejor recomendación...\n\n"
            
            # Registrar interacción con sumiller
            coordinator_state["agent_interactions"].append({
                "agent": "sumiller_specialist",
                "query": query,
                "reason": "wine_and_pairing_expertise"
            })
            
            return {
                "status": "delegate_to_sumiller",
                "context": intro,
                "delegation_reason": "Consulta especializada en vinos y maridajes",
                "coordinator": "gastronomy_coordinator"
            }
        
        elif any(palabra in query_lower for palabra in [
            "receta", "cocina", "ingrediente", "preparación", "chef", "plato",
            "cocinar", "hacer", "como se hace", "técnica", "saltear", "brasear"
        ]):
            intro += "Una consulta culinaria fascinante. 🍳 "
            intro += "Consultaré con nuestro chef especialista para proporcionarle información culinaria experta...\n\n"
            
            # Registrar interacción con chef
            coordinator_state["agent_interactions"].append({
                "agent": "chef_specialist",
                "query": query,
                "reason": "culinary_expertise"
            })
            
            return {
                "status": "delegate_to_chef",
                "context": intro,
                "delegation_reason": "Consulta especializada en cocina y recetas",
                "coordinator": "gastronomy_coordinator"
            }
        
        elif any(palabra in query_lower for palabra in [
            "caloría", "nutrición", "vitamina", "dieta", "salud", "proteína",
            "carbohidrato", "grasa", "fibra", "mineral", "nutricional"
        ]):
            intro += "Una consulta muy importante sobre nutrición y salud. 🥗 "
            intro += "Consultaré con nuestro nutricionista especialista para proporcionarle información nutricional precisa...\n\n"
            
            # Registrar interacción con nutricionista
            coordinator_state["agent_interactions"].append({
                "agent": "nutrition_specialist",
                "query": query,
                "reason": "nutritional_expertise"
            })
            
            return {
                "status": "delegate_to_nutritionist",
                "context": intro,
                "delegation_reason": "Consulta especializada en nutrición y salud",
                "coordinator": "gastronomy_coordinator"
            }
        
        # Consultas mixtas o complejas
        elif any(combo in query_lower for combo in [
            "vino con", "maridaje con", "acompañar con", "dieta y vino",
            "receta nutritiva", "plato saludable", "menú completo"
        ]):
            intro += "Una consulta gastronómica integral muy interesante. 🍽️ "
            intro += "Esto requiere la coordinación de múltiples especialistas. Permíteme organizar una respuesta completa...\n\n"
            
            # Registrar interacción compleja
            coordinator_state["agent_interactions"].append({
                "agents": ["multiple_specialists"],
                "query": query,
                "reason": "complex_multi_domain_query"
            })
            
            return {
                "status": "coordinate_multiple_agents",
                "context": intro,
                "delegation_reason": "Consulta que requiere múltiples especialistas",
                "coordinator": "gastronomy_coordinator"
            }
        
        # Consultas generales o de bienvenida
        else:
            intro += "Me complace recibir su consulta. Para brindarle el mejor servicio posible, "
            intro += "¿podría especificar más sobre qué aspecto gastronómico le interesa?\n\n"
            intro += "Puedo coordinar con nuestros especialistas para asistirle con:\n"
            intro += "🍷 **Vinos y maridajes** - Nuestro sumiller experto\n"
            intro += "🍳 **Cocina y recetas** - Nuestro chef especialista\n"
            intro += "🥗 **Nutrición y salud** - Nuestro nutricionista certificado\n\n"
            intro += "Como Maître Digital, mi rol es coordinar la experiencia gastronómica perfecta para usted."
            
            return {
                "status": "general_guidance",
                "context": intro,
                "delegation_reason": "Consulta general requiere aclaración",
                "coordinator": "gastronomy_coordinator"
            }
    
    except Exception as e:
        error_str = str(e)
        
        # Detectar errores de rate limiting
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "Resource exhausted" in error_str:
            return {
                "status": "rate_limited",
                "context": "⏳ **Nivel gratuito de la app** - Estás usando el nivel gratuito de Sumy_V3 ADK. "
                          "Para evitar saturar los servidores, espera un minuto y vuelve a intentarlo. "
                          "¡Tu consulta gastronómica será procesada en breve! 🍷✨",
                "delegation_reason": "Rate limiting - nivel gratuito",
                "coordinator": "gastronomy_coordinator"
            }
        else:
            return {
                "status": "error",
                "context": f"Error procesando consulta: {error_str}",
                "coordinator": "gastronomy_coordinator"
            }

def synthesize_multi_agent_response(responses: str) -> Dict[str, str]:
    """
    Sintetiza respuestas de múltiples agentes en una experiencia unificada.
    Herramienta avanzada del coordinador.
    """
    
    intro = "Basándome en la consulta con nuestros especialistas, "
    intro += "me complace presentarle una respuesta gastronómica integral:\n\n"
    
    # Procesar y sintetizar respuestas
    try:
        # Analizar respuestas y crear síntesis
        synthesis = f"{intro}=== EXPERIENCIA GASTRONÓMICA COMPLETA ===\n\n{responses}\n\n"
        synthesis += "Como su Maître Digital, he coordinado esta información para garantizar "
        synthesis += "una experiencia gastronómica excepcional y completa. "
        synthesis += "¿Hay algún aspecto adicional en el que pueda asistirle?"
        
        # Actualizar estado
        coordinator_state["last_recommendations"]["synthesis"] = synthesis
        
        return {
            "status": "success",
            "context": synthesis,
            "source": "multi_agent_coordination",
            "coordinator": "gastronomy_coordinator"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "context": f"Error en síntesis de respuestas: {str(e)}",
            "coordinator": "gastronomy_coordinator"
        }

def get_conversation_context() -> Dict[str, str]:
    """
    Proporciona contexto de la conversación actual.
    Herramienta de gestión del coordinador.
    """
    
    try:
        context_summary = "=== CONTEXTO DE LA CONVERSACIÓN ===\n\n"
        
        # Resumen de interacciones
        if coordinator_state["agent_interactions"]:
            context_summary += "**Especialistas consultados:**\n"
            for interaction in coordinator_state["agent_interactions"][-3:]:  # Últimas 3 interacciones
                agent_name = interaction.get("agent", "multiple")
                reason = interaction.get("reason", "consulta")
                context_summary += f"- {agent_name}: {reason}\n"
        
        # Preferencias del usuario
        if coordinator_state["user_preferences"]:
            context_summary += "\n**Preferencias identificadas:**\n"
            for key, value in coordinator_state["user_preferences"].items():
                context_summary += f"- {key}: {value}\n"
        
        context_summary += "\nEste contexto me permite ofrecer recomendaciones más personalizadas."
        
        return {
            "status": "success",
            "context": context_summary,
            "source": "conversation_context",
            "coordinator": "gastronomy_coordinator"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "context": f"Error al obtener contexto: {str(e)}",
            "coordinator": "gastronomy_coordinator"
        }

# Configuración del coordinador principal con sub-agentes
root_coordinator = Agent(
    name="gastronomy_coordinator",
    model="gemini-2.0-flash-exp",  # Modelo más avanzado para coordinación
    instruction=COORDINATOR_INSTRUCTION + """

ARQUITECTURA ADK MEJORADA:
Como Maître Digital coordinador, tienes acceso a un equipo de especialistas expertos:

1. **SUMILLER ESPECIALISTA** (sumiller_specialist)
   - Experto en vinos, maridajes, bodegas, catas
   - Acceso a base de conocimientos enológica especializada
   - Herramientas: consulta vinos, recomendaciones de maridaje

2. **CHEF ESPECIALISTA** (chef_specialist)  
   - Experto en cocina, recetas, técnicas culinarias
   - Acceso a base de conocimientos culinaria
   - Herramientas: consulta recetas, técnicas de cocción

3. **NUTRICIONISTA ESPECIALISTA** (nutrition_specialist)
   - Experto en nutrición, dietas, análisis nutricional
   - Acceso a base de conocimientos + API USDA
   - Herramientas: análisis nutricional, datos USDA

HERRAMIENTAS DEL COORDINADOR:
- coordinate_gastronomy_experience: Análisis principal y delegación inteligente
- synthesize_multi_agent_response: Síntesis de respuestas múltiples
- get_conversation_context: Gestión del contexto conversacional

PROTOCOLO DE COORDINACIÓN:
1. Usa coordinate_gastronomy_experience para analizar cada consulta
2. Delega automáticamente al especialista apropiado basándote en la respuesta
3. Para consultas complejas, coordina múltiples especialistas
4. Sintetiza respuestas manteniendo el rol de Maître Digital
5. Mantén el contexto conversacional a lo largo de la sesión

DELEGACIÓN INTELIGENTE:
- Vinos/maridajes → sumiller_specialist
- Cocina/recetas → chef_specialist  
- Nutrición/salud → nutrition_specialist
- Consultas mixtas → coordinación múltiple

Actúa siempre como el Maître Digital que coordina la experiencia gastronómica perfecta.
""",
    description="Coordinador principal que actúa como Maître Digital, delegando inteligentemente a especialistas en vinos, cocina y nutrición",
    tools=[coordinate_gastronomy_experience, synthesize_multi_agent_response, get_conversation_context],
    sub_agents=[sumiller_agent, culinary_agent, nutrition_agent],  # ADK: Sub-agentes especializados
    output_key="coordination_result"  # ADK: Guardar resultado de coordinación
)

# Configurar nombres únicos para las herramientas
coordinate_gastronomy_experience.__name__ = "coordinate_gastronomy_experience"
synthesize_multi_agent_response.__name__ = "synthesize_multi_agent_response"
get_conversation_context.__name__ = "get_conversation_context"

print("🎩 Coordinador ADK optimizado con sub-agentes inicializado correctamente")
print(f"📋 Sub-agentes disponibles: {[agent.name for agent in root_coordinator.sub_agents]}")
print(f"🛠️ Herramientas del coordinador: {[tool.__name__ for tool in root_coordinator.tools]}")