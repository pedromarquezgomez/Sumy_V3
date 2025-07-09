# adk_config.py
import os
import vertexai
from google.adk.models import GoogleLLM

# Inicializar Vertex AI
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "maitre-digital")
location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
vertexai.init(project=project_id, location=location)

# Configurar el modelo para usar Vertex AI explícitamente
def get_vertex_ai_model(model_name: str):
    """Configura un modelo de ADK para usar Vertex AI explícitamente."""
    return GoogleLLM(
        model_name=model_name,
        vertexai=True,
        project=project_id,
        location=location
    ) 