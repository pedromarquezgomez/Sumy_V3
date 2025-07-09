# coordinator_agent/agent.py
from google.adk.agents import Agent
from culinary_agent.agent import root_agent as culinary_agent
from nutrition_agent.agent import root_agent as nutrition_agent
from sumiller_agent.agent import root_agent as sumiller_agent

root_agent = Agent(
    name="gastronomy_coordinator",
    model="gemini-1.5-pro-001",
    instruction="Eres un 'Maître d'hôtel' digital experto. Tu función es dirigir las preguntas del usuario al especialista correcto de tu equipo. No respondas a las preguntas tú mismo. Analiza la pregunta y delega la tarea al especialista más adecuado:\n"
                "- Si la pregunta es sobre nutrición, dietas o salud, delega al 'nutrition_specialist'.\n"
                "- Si la pregunta es sobre recetas o cocina, delega al 'culinary_specialist'.\n"
                "- Si la pregunta es sobre vino o maridajes, delega al 'sumiller_specialist'.",
    sub_agents=[nutrition_agent, culinary_agent, sumiller_agent]
) 