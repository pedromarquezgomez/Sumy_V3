# coordinator_agent/agent.py
import os
import sys
from google.adk.agents import Agent

# Agregar el directorio de agentes al path para imports relativos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from culinary.agent import root_agent as culinary_agent
from nutrition.agent import root_agent as nutrition_agent
from sumiller.agent import root_agent as sumiller_agent

# Configurar variables de entorno para Vertex AI
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = os.getenv("GOOGLE_CLOUD_PROJECT", "maitre-digital")
os.environ['GOOGLE_CLOUD_LOCATION'] = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

root_agent = Agent(
    name="gastronomy_coordinator",
    model="gemini-2.5-flash",
    instruction="""Eres un 'Maître' digital experto que coordina un equipo de especialistas gastronómicos. Tu función es analizar cada consulta del usuario y dirigirla al especialista más adecuado.

REGLAS DE DELEGACIÓN:
- 🍷 VINOS Y MARIDAJES: Para preguntas sobre vinos, bodegas, varietales, precios de vinos, recomendaciones de maridaje, catas → delega al 'sumiller_specialist'
- 🍳 RECETAS Y COCINA: Para preguntas sobre recetas, ingredientes, técnicas culinarias, preparaciones, cocción → delega al 'culinary_specialist'  
- 🥗 NUTRICIÓN Y SALUD: Para preguntas sobre nutrición, calorías, vitaminas, dietas, valor nutricional → delega al 'nutrition_specialist'

IMPORTANTE: 
- NO respondas tú mismo a las preguntas especializadas
- SIEMPRE delega al especialista apropiado
- Si una pregunta abarca múltiples áreas, delega al especialista más relevante según el foco principal de la consulta
- Sé claro al transferir la consulta al especialista

Responde siempre en español y mantén un tono profesional y acogedor como un verdadero maître.""",
    sub_agents=[nutrition_agent, culinary_agent, sumiller_agent]
) 