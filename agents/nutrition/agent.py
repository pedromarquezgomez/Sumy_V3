# agents/nutrition/agent.py
import sys
import os

# Añadir el directorio de agentes al path para poder importar el builder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_builder import create_specialist_agent

# Construir la ruta al archivo de instrucciones
instruction_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instrucciones', 'NUTRITION_INSTRUCTION.txt')

# Leer las instrucciones desde el archivo
with open(instruction_path, 'r', encoding='utf-8') as f:
    NUTRITION_INSTRUCTION = f.read()

# Crear el agente usando el constructor centralizado
root_agent = create_specialist_agent(
    name="nutrition_specialist",
    description="Nutricionista Especializado en responder preguntas sobre nutrición, dietas, calorías, vitaminas y alimentación saludable usando una base de conocimientos especializada y API USDA.",
    instruction=NUTRITION_INSTRUCTION,
    index_path="./indexes/nutrition_index"
)