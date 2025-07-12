# agents/sumiller/agent.py
import sys
import os

# Añadir el directorio de agentes al path para poder importar el builder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_builder import create_specialist_agent

# Construir la ruta al archivo de instrucciones
instruction_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instrucciones', 'SUMILLER_INSTRUCTION.txt')

# Leer las instrucciones desde el archivo
with open(instruction_path, 'r', encoding='utf-8') as f:
    SUMILLER_INSTRUCTION = f.read()

# Crear el agente usando el constructor centralizado
root_agent = create_specialist_agent(
    name="sumiller_specialist",
    description="Sumiller Experto especialista en responder preguntas sobre vinos, bodegas, variedades, precios y maridajes usando una base de conocimientos especializada.",
    instruction=SUMILLER_INSTRUCTION,
    index_path="./indexes/enology_index",
    k_results=3  # Pedir 3 resultados como en la versión original
)