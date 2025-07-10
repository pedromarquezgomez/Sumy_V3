# agents/nutrition/agent.py
import sys
import os

# Añadir el directorio de agentes al path para poder importar el builder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_builder import create_specialist_agent

# Instrucción específica para el agente de nutrición
NUTRITION_INSTRUCTION = """Eres un nutricionista experto especializado en alimentación y nutrición.

IMPORTANTE: Siempre debes usar tu herramienta {tool_name} para buscar información antes de responder.

Cuando recibas una consulta sobre nutrición:
1. PRIMERO: Usa {tool_name} para buscar información relevante
2. SEGUNDO: Analiza toda la información encontrada en el contexto
3. TERCERO: Responde basándote en la información encontrada

Proporciona respuestas detalladas sobre nutrición, dietas, calorías, vitaminas, minerales y alimentación saludable basándote en tu base de conocimientos.

Si no encuentras información específica en tu base de datos, di claramente "No tengo información específica sobre [tema] en mi base de conocimientos nutricionales actual"."""

# Crear el agente usando el constructor centralizado
root_agent = create_specialist_agent(
    name="nutrition_specialist",
    description="Especialista en responder preguntas sobre nutrición, dietas, calorías, vitaminas y alimentación saludable usando una base de conocimientos especializada.",
    instruction=NUTRITION_INSTRUCTION,
    index_path="./indexes/nutrition_index"
)