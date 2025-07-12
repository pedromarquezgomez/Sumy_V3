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

# Construir la ruta al archivo de instrucciones
instruction_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instrucciones', 'COORDINATOR_INSTRUCTION.txt')

# Leer las instrucciones desde el archivo
with open(instruction_path, 'r', encoding='utf-8') as f:
    COORDINATOR_INSTRUCTION = f.read()


root_agent = Agent(
    name="gastronomy_coordinator",
    model="gemini-2.5-flash",
    instruction=COORDINATOR_INSTRUCTION,
    sub_agents=[nutrition_agent, culinary_agent, sumiller_agent]
) 