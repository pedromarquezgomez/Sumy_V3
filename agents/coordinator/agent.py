# coordinator_agent/agent.py
import os
from google.adk.agents import Agent
from agents.culinary.agent import root_agent as culinary_agent
from agents.nutrition.agent import root_agent as nutrition_agent
from agents.sumiller.agent import root_agent as sumiller_agent

# Configurar variables de entorno para Vertex AI
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = os.getenv("GOOGLE_CLOUD_PROJECT", "maitre-digital")
os.environ['GOOGLE_CLOUD_LOCATION'] = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

root_agent = Agent(
    name="gastronomy_coordinator",
    model="gemini-2.5-flash",  # Modelo actualizado a 2.5
    instruction="Eres un 'Maître' digital experto. Tu función es dirigir las preguntas del usuario al especialista correcto de tu equipo. No respondas a las preguntas tú mismo. Analiza la pregunta y delega la tarea al especialista más adecuado:\n"
                "- Si la pregunta es sobre nutrición, dietas o salud, delega al 'nutrition_specialist'.\n"
                "- Si la pregunta es sobre recetas o cocina, delega al 'culinary_specialist'.\n"
                "- Si la pregunta es sobre vino o maridajes, delega al 'sumiller_specialist'.",
    sub_agents=[nutrition_agent, culinary_agent, sumiller_agent]
) 