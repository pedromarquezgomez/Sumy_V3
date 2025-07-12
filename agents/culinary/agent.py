# agents/culinary/agent.py
import sys
import os

# Añadir el directorio de agentes al path para poder importar el builder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_builder import create_specialist_agent

# Construir la ruta al archivo de instrucciones
instruction_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instrucciones', 'CULINARY_INSTRUCTION.txt')

# Leer las instrucciones desde el archivo
with open(instruction_path, 'r', encoding='utf-8') as f:
    CULINARY_INSTRUCTION = f.read()

# Crear el agente usando el constructor centralizado
root_agent = create_specialist_agent(
    name="culinary_specialist",
    description="Chef Ejecutivo especialista en responder preguntas sobre recetas, ingredientes, técnicas de cocina y gastronomía usando una base de conocimientos especializada.",
    instruction=CULINARY_INSTRUCTION,
    index_path="./indexes/culinary_index"
)
